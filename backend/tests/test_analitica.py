"""Pruebas unitarias para analítica Pandas/NumPy y exportación PDF (Unidad 3)."""

from __future__ import annotations

from app.analitica import calcular_analitica_y_fugas
from app.config import DEMO_CSV_PATH
from app.funcional import aplicar_pipeline_funcional
from app.lectores import LectorCSV


def test_analitica_pandas_numpy_y_radar_fugas() -> None:
    movs = LectorCSV().leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    clasificadas = aplicar_pipeline_funcional(movs, modo="normal")
    resumen, radar, z_scores = calcular_analitica_y_fugas(
        clasificadas, presupuesto_mensual=2500.0, modo="normal"
    )

    assert resumen.cantidad_movimientos == 24
    assert resumen.gasto_total > 2000.0
    assert resumen.desviacion_estandar > 0.0
    assert z_scores["TX020"] > 2.5  # Compra de S/ 950.00 claramente anómala

    assert any(h.comercio == "Cafe Tostado Ica" and h.cantidad == 6 for h in radar.gastos_hormiga)
    assert any(d.comercio == "Supermercado Metro Ica" for d in radar.cobros_duplicados)
    assert any(s.comercio == "Netflix.com" for s in radar.suscripciones_recurrentes)
