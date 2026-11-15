"""Pruebas integrales de API FastAPI, persistencia SQLite y rendimiento (RNF-03)."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import DEMO_CSV_PATH, DEMO_PDF_PATH
from app.db import RepositorioSQLite
from app.main import app, obtener_servicio
from app.services import ServicioAuditorFinGuard


def _crear_cliente_aislado(tmp_path: Path) -> TestClient:
    repo = RepositorioSQLite(db_path=tmp_path / "test_finguard.db")
    servicio = ServicioAuditorFinGuard(repositorio=repo)
    app.dependency_overrides[obtener_servicio] = lambda: servicio
    return TestClient(app)


def test_flujo_completo_auditoria_fui_yo_y_reporte_pdf(tmp_path: Path) -> None:
    client = _crear_cliente_aislado(tmp_path)

    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["motor_prolog"] == "pyswip"

    # Auditar PDF demo
    with DEMO_PDF_PATH.open("rb") as fh:
        resp_pdf = client.post(
            "/api/auditar-cuenta",
            files={"archivo": ("estado_cuenta_demo.pdf", fh, "application/pdf")},
            data={"ciudad_habitual": "Ica", "modo": "normal", "presupuesto_mensual": "2500"},
        )
    assert resp_pdf.status_code == 200
    datos = resp_pdf.json()
    assert datos["formato"] == "pdf"
    assert datos["escudo_antifraude"]["nivel_riesgo_general"] == "critico"
    assert datos["escudo_antifraude"]["alertas_activas"] >= 3

    audit_id = datos["audit_id"]
    primera_alerta_id = datos["escudo_antifraude"]["alertas"][0]["alerta_id"]

    # Marcar alerta como "Fui yo" (RF-09)
    resp_fui_yo = client.post(
        f"/api/alertas/{primera_alerta_id}/marcar-fui-yo",
        json={"verificada": True},
    )
    assert resp_fui_yo.status_code == 200
    assert resp_fui_yo.json()["verificada_fui_yo"] is True
    assert resp_fui_yo.json()["alertas_activas"] == datos["escudo_antifraude"]["alertas_activas"] - 1

    # Verificar historial
    resp_hist = client.get("/api/historial")
    assert resp_hist.status_code == 200
    assert len(resp_hist.json()) == 1
    assert resp_hist.json()[0]["audit_id"] == audit_id

    # Descargar reporte PDF (RF-10)
    resp_rep = client.get(f"/api/auditorias/{audit_id}/reporte-pdf")
    assert resp_rep.status_code == 200
    assert resp_rep.headers["content-type"] == "application/pdf"
    assert resp_rep.content.startswith(b"%PDF")

    app.dependency_overrides.clear()


def test_rendimiento_500_transacciones_menor_a_3_segundos(tmp_path: Path) -> None:
    """Verifica RNF-03: hasta 500 movimientos procesados en menos de 3 segundos."""
    client = _crear_cliente_aislado(tmp_path)

    lineas_base = DEMO_CSV_PATH.read_text(encoding="utf-8").splitlines()
    encabezado, cuerpo = lineas_base[0], lineas_base[1:]
    filas_500 = [encabezado]
    for i in range(500):
        partes = cuerpo[i % len(cuerpo)].split(",")
        partes[0] = f"TX{i + 1:04d}"
        filas_500.append(",".join(partes))

    csv_500 = "\n".join(filas_500).encode("utf-8")
    inicio = time.perf_counter()
    resp = client.post(
        "/api/auditar-cuenta",
        files={"archivo": ("500_movimientos.csv", csv_500, "text/csv")},
        data={"ciudad_habitual": "Ica", "modo": "normal", "presupuesto_mensual": "15000"},
    )
    transcurrido = time.perf_counter() - inicio

    assert resp.status_code == 200
    assert resp.json()["resumen_gastos"]["cantidad_movimientos"] == 500
    assert transcurrido < 3.0, f"Tardó {transcurrido:.2f}s (> 3.0s)"

    app.dependency_overrides.clear()
