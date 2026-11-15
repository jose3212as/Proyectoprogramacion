"""Puente Python <-> SWI-Prolog usando PySwip con soporte seguro multi-hilo."""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.config import PROLOG_RULES_PATH, resolver_ruta_swipl
from app.funcional.modelos import TransaccionClasificada


@dataclass(frozen=True, slots=True)
class ResultadoInferenciaLogica:
    """Resultado individual emitido por la base de conocimiento SWI-Prolog."""

    alerta_id: str
    transaccion_id: str
    regla_activada: str
    severidad: str
    titulo: str
    explicacion: str
    traza_prolog: tuple[str, ...]


_PROLOG_LOCK = threading.Lock()


def _preparar_entorno_swipl() -> None:
    """Asegura que el directorio binario de SWI-Prolog esté visible para libswipl."""
    swipl_bin = resolver_ruta_swipl()
    if swipl_bin:
        bin_dir = str(Path(swipl_bin).parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(bin_dir)
            except OSError:
                pass


def _escapar_atomo(valor: str) -> str:
    """Escapa comillas simples para construir átomos Prolog válidos."""
    limpio = str(valor).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{limpio}'"


def _a_texto(valor: object) -> str:
    """Normaliza átomos, bytes o strings devueltos por PySwip."""
    if isinstance(valor, bytes):
        return valor.decode("utf-8", errors="replace")
    return str(valor)


class MotorInferenciaProlog:
    """Encapsula la carga de reglas y consulta de anomalías en SWI-Prolog."""

    def __init__(self, ruta_reglas: Path = PROLOG_RULES_PATH) -> None:
        self.ruta_reglas = ruta_reglas
        self._prolog = None
        self.motor_activo = "no_inicializado"
        self._inicializar()

    def _inicializar(self) -> None:
        _preparar_entorno_swipl()
        from pyswip import Prolog

        self._prolog = Prolog()
        ruta_posix = self.ruta_reglas.resolve().as_posix()
        self._prolog.consult(ruta_posix)
        self.motor_activo = "pyswip"

    def inferir_alertas(
        self,
        transacciones: Iterable[TransaccionClasificada],
        z_scores: dict[str, float],
        ciudad_habitual: str,
        modo: str,
    ) -> tuple[ResultadoInferenciaLogica, ...]:
        """Exporta hechos transaccion/7, ejecuta backtracking y retorna alertas explicables."""
        if self._prolog is None:
            raise RuntimeError("El motor SWI-Prolog no está inicializado.")

        umbral_z = 1.5 if modo == "ahorro_estricto" else 2.0

        with _PROLOG_LOCK:
            list(self._prolog.query("limpiar_hechos"))

            self._prolog.assertz(
                f"perfil_usuario({_escapar_atomo(ciudad_habitual)}, {_escapar_atomo(modo)}, {umbral_z:.2f})"
            )

            for tx in transacciones:
                hecho_tx = (
                    f"transaccion({_escapar_atomo(tx.id)}, "
                    f"{_escapar_atomo(tx.fecha)}, "
                    f"{_escapar_atomo(tx.hora)}, "
                    f"{_escapar_atomo(tx.comercio)}, "
                    f"{_escapar_atomo(tx.ciudad)}, "
                    f"{tx.canal}, "
                    f"{tx.monto_pen:.2f})"
                )
                self._prolog.assertz(hecho_tx)

                z = z_scores.get(tx.id, 0.0)
                self._prolog.assertz(f"z_score_tx({_escapar_atomo(tx.id)}, {z:.4f})")

            resultados_crudos = list(
                self._prolog.query(
                    "alerta_detectada(IdTx, Regla, Severidad, Titulo, Explicacion, Traza)"
                )
            )

        alertas: list[ResultadoInferenciaLogica] = []
        vistos: set[tuple[str, str]] = set()
        for fila in resultados_crudos:
            tx_id = _a_texto(fila["IdTx"])
            regla = _a_texto(fila["Regla"])
            clave = (tx_id, regla)
            if clave in vistos:
                continue
            vistos.add(clave)

            traza_raw = fila.get("Traza") or []
            traza = tuple(_a_texto(paso) for paso in traza_raw)
            regla_slug = regla.split("/")[0]

            alertas.append(
                ResultadoInferenciaLogica(
                    alerta_id=f"ALR-{tx_id}-{regla_slug}",
                    transaccion_id=tx_id,
                    regla_activada=regla,
                    severidad=_a_texto(fila["Severidad"]),
                    titulo=_a_texto(fila["Titulo"]),
                    explicacion=_a_texto(fila["Explicacion"]),
                    traza_prolog=traza,
                )
            )

        return tuple(alertas)
