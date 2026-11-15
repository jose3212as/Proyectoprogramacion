"""Persistencia ligera en SQLite para historial de auditorías y falsos positivos ('Fui yo')."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from app.config import DB_PATH
from app.schemas import AlertaFraude, AuditoriaResponse, HistorialItem, MarcarFuiYoResponse


def calcular_nivel_riesgo(alertas: Iterable[AlertaFraude]) -> str:
    """Calcula el nivel de riesgo global considerando solo alertas activas (no verificadas)."""
    activas = [a for a in alertas if not a.verificada_fui_yo]
    if not activas:
        return "bajo"

    severidades = {a.severidad for a in activas}
    if "critica" in severidades:
        return "critico"
    if "alta" in severidades:
        return "alto"
    if "media" in severidades:
        return "medio"
    return "bajo"


class RepositorioSQLite:
    """Gestiona auditorías y estado de verificación de alertas en SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._inicializar_tablas()

    def _conectar(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_tablas(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conectar() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS auditorias (
                    audit_id TEXT PRIMARY KEY,
                    archivo TEXT NOT NULL,
                    formato TEXT NOT NULL,
                    fecha_auditoria TEXT NOT NULL,
                    ciudad_habitual TEXT NOT NULL,
                    modo TEXT NOT NULL,
                    gasto_total REAL NOT NULL,
                    alertas_activas INTEGER NOT NULL,
                    nivel_riesgo_general TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alertas_verificadas (
                    alerta_id TEXT PRIMARY KEY,
                    audit_id TEXT NOT NULL,
                    verificada INTEGER NOT NULL DEFAULT 1,
                    actualizado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (audit_id) REFERENCES auditorias(audit_id) ON DELETE CASCADE
                )
                """
            )
            conn.commit()

    def guardar_auditoria(self, auditoria: AuditoriaResponse) -> None:
        payload = auditoria.model_dump_json()
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO auditorias (
                    audit_id, archivo, formato, fecha_auditoria,
                    ciudad_habitual, modo, gasto_total, alertas_activas,
                    nivel_riesgo_general, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    auditoria.audit_id,
                    auditoria.archivo,
                    auditoria.formato,
                    auditoria.fecha_auditoria,
                    auditoria.perfil.ciudad_habitual,
                    auditoria.perfil.modo,
                    auditoria.resumen_gastos.gasto_total,
                    auditoria.escudo_antifraude.alertas_activas,
                    auditoria.escudo_antifraude.nivel_riesgo_general,
                    payload,
                ),
            )
            conn.commit()

    def obtener_auditoria(self, audit_id: str) -> AuditoriaResponse | None:
        with self._conectar() as conn:
            fila = conn.execute(
                "SELECT payload_json FROM auditorias WHERE audit_id = ?", (audit_id,)
            ).fetchone()
        if fila is None:
            return None
        return AuditoriaResponse.model_validate_json(fila["payload_json"])

    def listar_historial(self, limite: int = 20) -> list[HistorialItem]:
        with self._conectar() as conn:
            filas = conn.execute(
                """
                SELECT audit_id, archivo, formato, fecha_auditoria,
                       ciudad_habitual, modo, gasto_total, alertas_activas,
                       nivel_riesgo_general
                FROM auditorias
                ORDER BY fecha_auditoria DESC
                LIMIT ?
                """,
                (limite,),
            ).fetchall()
        return [HistorialItem(**dict(f)) for f in filas]

    def actualizar_estado_fui_yo(self, alerta_id: str, verificada: bool) -> MarcarFuiYoResponse | None:
        """Actualiza una alerta dentro de su auditoría y recalcula riesgo global."""
        with self._conectar() as conn:
            filas = conn.execute("SELECT audit_id, payload_json FROM auditorias").fetchall()
            for fila in filas:
                datos = json.loads(fila["payload_json"])
                auditoria = AuditoriaResponse.model_validate(datos)
                encontrada = False
                for alerta in auditoria.escudo_antifraude.alertas:
                    if alerta.alerta_id == alerta_id:
                        alerta.verificada_fui_yo = verificada
                        encontrada = True
                        break

                if not encontrada:
                    continue

                activas = sum(
                    1 for al in auditoria.escudo_antifraude.alertas if not al.verificada_fui_yo
                )
                nuevo_riesgo = calcular_nivel_riesgo(auditoria.escudo_antifraude.alertas)
                auditoria.escudo_antifraude.alertas_activas = activas
                auditoria.escudo_antifraude.nivel_riesgo_general = nuevo_riesgo  # type: ignore[assignment]

                ids_sospechosas_activas = {
                    al.transaccion_id
                    for al in auditoria.escudo_antifraude.alertas
                    if not al.verificada_fui_yo
                }
                for tx in auditoria.transacciones:
                    tx.es_sospechosa = tx.id in ids_sospechosas_activas

                conn.execute(
                    """
                    UPDATE auditorias
                    SET alertas_activas = ?, nivel_riesgo_general = ?, payload_json = ?
                    WHERE audit_id = ?
                    """,
                    (activas, nuevo_riesgo, auditoria.model_dump_json(), auditoria.audit_id),
                )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO alertas_verificadas (alerta_id, audit_id, verificada)
                    VALUES (?, ?, ?)
                    """,
                    (alerta_id, auditoria.audit_id, int(verificada)),
                )
                conn.commit()
                return MarcarFuiYoResponse(
                    alerta_id=alerta_id,
                    verificada_fui_yo=verificada,
                    alertas_activas=activas,
                    nivel_riesgo_general=nuevo_riesgo,
                )
        return None
