"""Implementación concreta para estados de cuenta en PDF con pdfplumber (Unidad 3 - POO)."""

from __future__ import annotations

import io
import re
from typing import Any

import pdfplumber

from app.config import CIUDAD_HABITUAL_DEFAULT
from app.lectores.base import LectorEstadoCuenta, Movimiento

_PATRON_FILA_TEXTO = re.compile(
    r"^(?P<id>TX\d+)?\s*"
    r"(?P<fecha>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\s+"
    r"(?P<hora>\d{2}:\d{2})?\s*"
    r"(?P<comercio>.+?)\s+"
    r"(?P<ciudad>[A-Za-zÁÉÍÓÚáéíóúÑñ]+)\s+"
    r"(?P<canal>presencial|online)\s+"
    r"(?P<monto>[\d.,]+)\s*"
    r"(?P<moneda>PEN|USD|EUR|S/)?\s*"
    r"(?P<tipo>compra|suscripcion|servicio)?$",
    re.IGNORECASE,
)


class LectorPDF(LectorEstadoCuenta):
    """Lector polimórfico especializado en extraer tablas de estados de cuenta PDF."""

    formato = "pdf"

    def leer(
        self,
        contenido: bytes,
        nombre_archivo: str,
        ciudad_default: str = CIUDAD_HABITUAL_DEFAULT,
    ) -> tuple[Movimiento, ...]:
        filas_extraidas: list[dict[str, Any]] = []

        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            for pagina in pdf.pages:
                tablas = pagina.extract_tables() or []
                for tabla in tablas:
                    filas_extraidas.extend(self._convertir_tabla_a_filas(tabla))

                if not filas_extraidas:
                    texto_pagina = pagina.extract_text() or ""
                    filas_extraidas.extend(self._extraer_desde_texto_plano(texto_pagina))

        if not filas_extraidas:
            raise ValueError(
                f"El PDF '{nombre_archivo}' no contiene tablas de movimientos legibles."
            )

        return self._construir_movimientos_desde_filas(
            filas_extraidas, ciudad_default=ciudad_default
        )

    @staticmethod
    def _convertir_tabla_a_filas(tabla: list[list[str | None]]) -> list[dict[str, str]]:
        """Transforma una tabla de pdfplumber descartando títulos o pies publicitarios."""
        if len(tabla) < 2:
            return []

        indice_header = -1
        for idx, fila in enumerate(tabla):
            celdas = [str(c or "").strip().lower() for c in fila]
            texto_fila = " ".join(celdas)
            if ("fecha" in texto_fila or "date" in texto_fila) and (
                "monto" in texto_fila or "importe" in texto_fila or "comercio" in texto_fila
            ):
                indice_header = idx
                break

        if indice_header == -1:
            return []

        encabezados = [
            str(col or f"col_{i}").strip() for i, col in enumerate(tabla[indice_header])
        ]
        resultado: list[dict[str, str]] = []
        for fila in tabla[indice_header + 1 :]:
            if not fila or all(not (c or "").strip() for c in fila):
                continue
            registro = {
                encabezados[i]: str(fila[i] or "").replace("\n", " ").strip()
                for i in range(min(len(encabezados), len(fila)))
            }
            resultado.append(registro)
        return resultado

    @staticmethod
    def _extraer_desde_texto_plano(texto: str) -> list[dict[str, str]]:
        filas: list[dict[str, str]] = []
        for linea in texto.splitlines():
            match = _PATRON_FILA_TEXTO.match(linea.strip())
            if match:
                filas.append({k: v or "" for k, v in match.groupdict().items()})
        return filas
