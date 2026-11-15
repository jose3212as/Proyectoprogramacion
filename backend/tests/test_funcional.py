"""Pruebas unitarias para el pipeline funcional inmutable (Unidad 1)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.config import DEMO_CSV_PATH
from app.funcional import (
    aplicar_pipeline_funcional,
    calcular_total_funcional,
    convertir_a_pen,
    crear_filtro_modo,
)
from app.funcional.modelos import TransaccionNormalizada
from app.lectores import LectorCSV


def test_inmutabilidad_transacciones() -> None:
    movs = LectorCSV().leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    resultado = aplicar_pipeline_funcional(movs, modo="normal")

    assert isinstance(resultado, tuple)
    with pytest.raises(FrozenInstanceError):
        resultado[0].monto_pen = 9999.0  # type: ignore[misc]


def test_conversion_pura_divisas() -> None:
    assert convertir_a_pen(10.0, "USD") == 37.5
    assert convertir_a_pen(10.0, "EUR") == 40.5
    assert convertir_a_pen(50.0, "PEN") == 50.0


def test_orden_superior_diferencia_modos() -> None:
    movs = LectorCSV().leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    res_normal = aplicar_pipeline_funcional(movs, modo="normal")
    res_estricto = aplicar_pipeline_funcional(movs, modo="ahorro_estricto")

    assert calcular_total_funcional(res_normal) == calcular_total_funcional(res_estricto)

    etiquetas_normal = {tx.etiqueta_modo for tx in res_normal}
    etiquetas_estricto = {tx.etiqueta_modo for tx in res_estricto}
    assert "atencion_seguridad" in etiquetas_normal
    assert "suscripcion_revisar" in etiquetas_estricto
    assert "recorte_sugerido" in etiquetas_estricto

    filtro = crear_filtro_modo("ahorro_estricto")
    tx_ejemplo = TransaccionNormalizada(
        id="T1",
        fecha="2026-10-01",
        hora="10:00",
        comercio="Netflix.com",
        ciudad="Lima",
        canal="online",
        monto_original=44.9,
        moneda_original="PEN",
        monto_pen=44.9,
        tipo="suscripcion",
    )
    assert filtro(tx_ejemplo, "Suscripciones") == "suscripcion_revisar"
