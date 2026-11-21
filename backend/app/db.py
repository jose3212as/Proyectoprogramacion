"""Persistencia ligera en SQLite para usuarios, sesiones, historial y 'Fui yo'."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import uuid
from pathlib import Path
from typing import Iterable

from app.config import DB_PATH
from app.schemas import (
    AlertaFraude,
    AuditoriaResponse,
    AuthResponse,
    HistorialItem,
    MarcarFuiYoResponse,
    UsuarioInfo,
)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    sal = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, 120_000)
    return f"{sal.hex()}${digest.hex()}"


def _verificar_password(password: str, stored_hash: str) -> bool:
    try:
        sal_hex, digest_hex = stored_hash.split("$", 1)
        sal = bytes.fromhex(sal_hex)
        esperado = bytes.fromhex(digest_hex)
    except ValueError:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, 120_000)
    return hmac.compare_digest(actual, esperado)


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
                CREATE TABLE IF NOT EXISTS usuarios (
                    usuario_id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    correo TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    ciudad_habitual TEXT NOT NULL DEFAULT 'Ica',
                    presupuesto_mensual REAL NOT NULL DEFAULT 2500.0,
                    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sesiones (
                    token TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS auditorias (
                    audit_id TEXT PRIMARY KEY,
                    usuario_id TEXT,
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
            columnas = {
                row["name"] for row in conn.execute("PRAGMA table_info(auditorias)").fetchall()
            }
            if "usuario_id" not in columnas:
                conn.execute("ALTER TABLE auditorias ADD COLUMN usuario_id TEXT")
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

    def registrar_usuario(
        self,
        *,
        nombre: str,
        correo: str,
        password: str,
        ciudad_habitual: str,
        presupuesto_mensual: float,
    ) -> AuthResponse:
        correo_norm = correo.strip().lower()
        usuario_id = f"usr-{uuid.uuid4().hex[:10]}"
        password_hash = _hash_password(password)
        token = secrets.token_urlsafe(32)

        with self._conectar() as conn:
            existente = conn.execute(
                "SELECT usuario_id FROM usuarios WHERE correo = ?", (correo_norm,)
            ).fetchone()
            if existente is not None:
                raise ValueError("Ya existe una cuenta con ese correo. Inicia sesión.")

            conn.execute(
                """
                INSERT INTO usuarios (
                    usuario_id, nombre, correo, password_hash, ciudad_habitual, presupuesto_mensual
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    usuario_id,
                    nombre.strip(),
                    correo_norm,
                    password_hash,
                    ciudad_habitual.strip() or "Ica",
                    presupuesto_mensual,
                ),
            )
            conn.execute(
                "INSERT INTO sesiones (token, usuario_id) VALUES (?, ?)",
                (token, usuario_id),
            )
            conn.commit()

        return AuthResponse(
            token=token,
            usuario=UsuarioInfo(
                usuario_id=usuario_id,
                nombre=nombre.strip(),
                correo=correo_norm,
                ciudad_habitual=ciudad_habitual.strip() or "Ica",
                presupuesto_mensual=presupuesto_mensual,
            ),
        )

    def autenticar_usuario(self, *, correo: str, password: str) -> AuthResponse:
        correo_norm = correo.strip().lower()
        with self._conectar() as conn:
            fila = conn.execute(
                """
                SELECT usuario_id, nombre, correo, password_hash, ciudad_habitual, presupuesto_mensual
                FROM usuarios
                WHERE correo = ?
                """,
                (correo_norm,),
            ).fetchone()
            if fila is None or not _verificar_password(password, fila["password_hash"]):
                raise ValueError("Correo o contraseña incorrectos.")

            token = secrets.token_urlsafe(32)
            conn.execute(
                "INSERT INTO sesiones (token, usuario_id) VALUES (?, ?)",
                (token, fila["usuario_id"]),
            )
            conn.commit()

        return AuthResponse(
            token=token,
            usuario=UsuarioInfo(
                usuario_id=fila["usuario_id"],
                nombre=fila["nombre"],
                correo=fila["correo"],
                ciudad_habitual=fila["ciudad_habitual"],
                presupuesto_mensual=fila["presupuesto_mensual"],
            ),
        )

    def obtener_usuario_por_token(self, token: str | None) -> UsuarioInfo | None:
        if not token:
            return None
        with self._conectar() as conn:
            fila = conn.execute(
                """
                SELECT u.usuario_id, u.nombre, u.correo, u.ciudad_habitual, u.presupuesto_mensual
                FROM sesiones s
                JOIN usuarios u ON u.usuario_id = s.usuario_id
                WHERE s.token = ?
                """,
                (token,),
            ).fetchone()
        if fila is None:
            return None
        return UsuarioInfo(**dict(fila))

    def cerrar_sesion(self, token: str | None) -> None:
        if not token:
            return
        with self._conectar() as conn:
            conn.execute("DELETE FROM sesiones WHERE token = ?", (token,))
            conn.commit()

    def asociar_auditoria_usuario(self, audit_id: str, usuario_id: str) -> bool:
        with self._conectar() as conn:
            cur = conn.execute(
                "UPDATE auditorias SET usuario_id = ? WHERE audit_id = ?",
                (usuario_id, audit_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def guardar_auditoria(
        self, auditoria: AuditoriaResponse, usuario_id: str | None = None
    ) -> None:
        payload = auditoria.model_dump_json()
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO auditorias (
                    audit_id, usuario_id, archivo, formato, fecha_auditoria,
                    ciudad_habitual, modo, gasto_total, alertas_activas,
                    nivel_riesgo_general, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    auditoria.audit_id,
                    usuario_id,
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

    def eliminar_auditoria(self, audit_id: str, usuario_id: str | None = None) -> bool:
        """Elimina una auditoría del historial y sus alertas verificadas asociadas."""
        with self._conectar() as conn:
            if usuario_id is not None:
                cur = conn.execute(
                    "DELETE FROM auditorias WHERE audit_id = ? AND usuario_id = ?",
                    (audit_id, usuario_id),
                )
            else:
                cur = conn.execute(
                    "DELETE FROM auditorias WHERE audit_id = ? AND usuario_id IS NULL",
                    (audit_id,),
                )
            if cur.rowcount > 0:
                conn.execute(
                    "DELETE FROM alertas_verificadas WHERE audit_id = ?", (audit_id,)
                )
            conn.commit()
            return cur.rowcount > 0

    def listar_historial(
        self, limite: int = 20, usuario_id: str | None = None
    ) -> list[HistorialItem]:
        with self._conectar() as conn:
            if usuario_id is not None:
                filas = conn.execute(
                    """
                    SELECT audit_id, archivo, formato, fecha_auditoria,
                           ciudad_habitual, modo, gasto_total, alertas_activas,
                           nivel_riesgo_general
                    FROM auditorias
                    WHERE usuario_id = ?
                    ORDER BY fecha_auditoria DESC
                    LIMIT ?
                    """,
                    (usuario_id, limite),
                ).fetchall()
            else:
                filas = conn.execute(
                    """
                    SELECT audit_id, archivo, formato, fecha_auditoria,
                           ciudad_habitual, modo, gasto_total, alertas_activas,
                           nivel_riesgo_general
                    FROM auditorias
                    WHERE usuario_id IS NULL
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
