"""Pruebas unitarias para el motor de inferencia SWI-Prolog (Unidad 2)."""

from __future__ import annotations

from app.analitica import calcular_analitica_y_fugas
from app.config import DEMO_CSV_PATH
from app.funcional import aplicar_pipeline_funcional
from app.lectores import LectorCSV
from app.logica import MotorInferenciaProlog


def test_prolog_detecta_viaje_imposible_y_compra_nocturna() -> None:
    movs = LectorCSV().leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    clasificadas = aplicar_pipeline_funcional(movs, modo="normal")
    _, _, z_scores = calcular_analitica_y_fugas(
        clasificadas, presupuesto_mensual=2500.0, modo="normal"
    )

    motor = MotorInferenciaProlog()
    alertas = motor.inferir_alertas(
        clasificadas, z_scores=z_scores, ciudad_habitual="Ica", modo="normal"
    )

    reglas = {a.regla_activada for a in alertas}
    assert "viaje_imposible/8" in reglas
    assert "compra_nocturna_atipica/6" in reglas
    assert "cobro_duplicado_regla/6" in reglas

    alerta_viaje = next(a for a in alertas if a.regla_activada == "viaje_imposible/8")
    assert "Ica" in alerta_viaje.explicacion
    assert "Trujillo" in alerta_viaje.explicacion
    assert "45 minutos" in alerta_viaje.explicacion
    assert len(alerta_viaje.traza_prolog) >= 4
