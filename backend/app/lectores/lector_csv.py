"""Implementación concreta para estados de cuenta en formato CSV (Unidad 3 - POO)."""

from __future__ import annotations

import csv
import io

from app.config import CIUDAD_HABITUAL_DEFAULT
from app.lectores.base import LectorEstadoCuenta, Movimiento


class LectorCSV(LectorEstadoCuenta):
    """Lector polimórfico especializado en extractos bancarios CSV."""

    formato = "csv"

    def leer(
        self,
        contenido: bytes,
        nombre_archivo: str,
        ciudad_default: str = CIUDAD_HABITUAL_DEFAULT,
    ) -> tuple[Movimiento, ...]:
        texto = self._decodificar_texto(contenido)
        muestra = texto[:2048]
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t")
        except csv.Error:
            dialecto = csv.excel

        reader = csv.DictReader(io.StringIO(texto), dialect=dialecto)
        if not reader.fieldnames:
            raise ValueError(f"El archivo CSV '{nombre_archivo}' no contiene encabezados válidos.")

        return self._construir_movimientos_desde_filas(reader, ciudad_default=ciudad_default)

    @staticmethod
    def _decodificar_texto(contenido: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return contenido.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("No fue posible decodificar el archivo CSV con UTF-8 ni Latin-1.")
