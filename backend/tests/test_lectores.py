"""Pruebas unitarias para la capa POO de lectores CSV y PDF (Unidad 3)."""

from __future__ import annotations

import pytest

from app.config import DEMO_CSV_PATH, DEMO_PDF_PATH
from app.lectores import (
    CompraOnline,
    CompraPresencial,
    LectorCSV,
    LectorPDF,
    ServicioBasico,
    Suscripcion,
    obtener_lector,
)


def test_fabrica_polimorfica_lectores() -> None:
    assert isinstance(obtener_lector("extracto.csv"), LectorCSV)
    assert isinstance(obtener_lector("EXTRACT.PDF"), LectorPDF)
    with pytest.raises(ValueError, match="no soportado"):
        obtener_lector("extracto.xlsx")


def test_lector_csv_demo_y_jerarquia_movimientos() -> None:
    lector = LectorCSV()
    movimientos = lector.leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    assert len(movimientos) == 24
    assert isinstance(movimientos[0], CompraPresencial)
    assert isinstance(movimientos[3], Suscripcion)
    assert isinstance(movimientos[10], CompraOnline)
    assert isinstance(movimientos[11], ServicioBasico)


def test_lector_pdf_extrae_misma_cantidad_que_csv() -> None:
    lector_csv = LectorCSV()
    lector_pdf = LectorPDF()
    movs_csv = lector_csv.leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    movs_pdf = lector_pdf.leer(DEMO_PDF_PATH.read_bytes(), "estado_cuenta_demo.pdf")

    assert len(movs_pdf) == len(movs_csv)
    assert movs_pdf[0].comercio == movs_csv[0].comercio
    assert movs_pdf[19].monto == movs_csv[19].monto
