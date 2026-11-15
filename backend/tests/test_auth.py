"""Pruebas de registro, inicio de sesión y guardado de historial personal en SQLite."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.db import RepositorioSQLite
from app.main import app, obtener_servicio
from app.services import ServicioAuditorFinGuard


def test_registro_login_y_guardado_historial_usuario(tmp_path: Path) -> None:
    repo = RepositorioSQLite(db_path=tmp_path / "auth_test.db")
    servicio = ServicioAuditorFinGuard(repositorio=repo)
    app.dependency_overrides[obtener_servicio] = lambda: servicio
    client = TestClient(app)

    # 1. Revisión inicial sin sesión
    resp_demo = client.get("/api/demo?formato=csv")
    assert resp_demo.status_code == 200
    audit_id = resp_demo.json()["audit_id"]

    # 2. Registro de usuario personal
    resp_reg = client.post(
        "/api/auth/registro",
        json={
            "nombre": "Carlos Mendoza",
            "correo": "carlos@ejemplo.com",
            "password": "clave-segura-123",
            "ciudad_habitual": "Ica",
            "presupuesto_mensual": 2500.0,
        },
    )
    assert resp_reg.status_code == 200
    token = resp_reg.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Guardar la revisión actual en su cuenta
    resp_guardar = client.post(f"/api/auditorias/{audit_id}/guardar", headers=headers)
    assert resp_guardar.status_code == 200
    assert resp_guardar.json()["guardada"] is True

    # 4. Historial privado del usuario contiene su revisión
    resp_hist = client.get("/api/historial", headers=headers)
    assert resp_hist.status_code == 200
    assert len(resp_hist.json()) == 1
    assert resp_hist.json()[0]["audit_id"] == audit_id

    # 5. Cerrar sesión e iniciar sesión nuevamente
    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401

    resp_login = client.post(
        "/api/auth/login",
        json={"correo": "carlos@ejemplo.com", "password": "clave-segura-123"},
    )
    assert resp_login.status_code == 200
    nuevo_token = resp_login.json()["token"]
    resp_hist_reingreso = client.get(
        "/api/historial", headers={"Authorization": f"Bearer {nuevo_token}"}
    )
    assert resp_hist_reingreso.status_code == 200
    assert len(resp_hist_reingreso.json()) == 1

    app.dependency_overrides.clear()
