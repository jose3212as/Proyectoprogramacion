"""Punto de entrada FastAPI de FinGuard (API REST multiplataforma)."""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.analitica import generar_reporte_auditoria_pdf
from app.config import (
    CIUDAD_HABITUAL_DEFAULT,
    DEMO_CSV_PATH,
    DEMO_PDF_PATH,
    MODO_DEFAULT,
    PRESUPUESTO_MENSUAL_DEFAULT,
)
from app.schemas import (
    AuditoriaResponse,
    AuthResponse,
    HistorialItem,
    LoginRequest,
    MarcarFuiYoRequest,
    MarcarFuiYoResponse,
    ModoControl,
    RegistroRequest,
    UsuarioInfo,
)
from app.services import ServicioAuditorFinGuard

app = FastAPI(
    title="FinGuard API",
    description=(
        "Asistente Inteligente de Finanzas Personales y Detección de Fraude mediante "
        "Paradigmas Híbridos (Funcional, Lógico SWI-Prolog, POO y Ciencia de Datos)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def obtener_servicio() -> ServicioAuditorFinGuard:
    """Instancia singleton del servicio auditor para reutilizar la base Prolog."""
    return ServicioAuditorFinGuard()


def _extraer_token(authorization: str | None = Header(default=None)) -> str | None:
    if not authorization:
        return None
    partes = authorization.split(" ", 1)
    if len(partes) == 2 and partes[0].lower() == "bearer":
        return partes[1].strip()
    return authorization.strip()


def obtener_usuario_opcional(
    token: str | None = Depends(_extraer_token),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> UsuarioInfo | None:
    return servicio.repositorio.obtener_usuario_por_token(token)


@app.get("/health")
def health_check(servicio: ServicioAuditorFinGuard = Depends(obtener_servicio)) -> dict[str, str]:
    return {
        "status": "ok",
        "servicio": "FinGuard API",
        "motor_prolog": servicio.motor_prolog.motor_activo,
    }


@app.post("/api/auth/registro", response_model=AuthResponse)
def registrar_usuario(
    body: RegistroRequest,
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> AuthResponse:
    try:
        return servicio.repositorio.registrar_usuario(
            nombre=body.nombre,
            correo=body.correo,
            password=body.password,
            ciudad_habitual=body.ciudad_habitual,
            presupuesto_mensual=body.presupuesto_mensual,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/auth/login", response_model=AuthResponse)
def iniciar_sesion(
    body: LoginRequest,
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> AuthResponse:
    try:
        return servicio.repositorio.autenticar_usuario(
            correo=body.correo,
            password=body.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.post("/api/auth/logout")
def cerrar_sesion(
    token: str | None = Depends(_extraer_token),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> dict[str, bool]:
    servicio.repositorio.cerrar_sesion(token)
    return {"ok": True}


@app.get("/api/auth/me", response_model=UsuarioInfo)
def obtener_perfil_actual(
    usuario: UsuarioInfo | None = Depends(obtener_usuario_opcional),
) -> UsuarioInfo:
    if usuario is None:
        raise HTTPException(status_code=401, detail="No hay sesión activa.")
    return usuario


@app.post("/api/auditar-cuenta", response_model=AuditoriaResponse)
async def auditar_cuenta(
    archivo: UploadFile = File(..., description="Estado de cuenta en formato .csv o .pdf"),
    ciudad_habitual: str = Form(default=CIUDAD_HABITUAL_DEFAULT),
    modo: ModoControl = Form(default=MODO_DEFAULT),
    presupuesto_mensual: float = Form(default=PRESUPUESTO_MENSUAL_DEFAULT, gt=0),
    usuario: UsuarioInfo | None = Depends(obtener_usuario_opcional),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> AuditoriaResponse:
    nombre = archivo.filename or "estado_cuenta.csv"
    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo subido está vacío.")

    try:
        return servicio.auditar_archivo(
            contenido=contenido,
            nombre_archivo=nombre,
            ciudad_habitual=ciudad_habitual.strip() or CIUDAD_HABITUAL_DEFAULT,
            modo=modo,
            presupuesto_mensual=presupuesto_mensual,
            usuario_id=usuario.usuario_id if usuario else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/demo", response_model=AuditoriaResponse)
def auditar_demo(
    formato: str = Query(default="csv", pattern="^(csv|pdf)$"),
    ciudad_habitual: str = Query(default=CIUDAD_HABITUAL_DEFAULT),
    modo: ModoControl = Query(default=MODO_DEFAULT),
    presupuesto_mensual: float = Query(default=PRESUPUESTO_MENSUAL_DEFAULT, gt=0),
    usuario: UsuarioInfo | None = Depends(obtener_usuario_opcional),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> AuditoriaResponse:
    ruta = DEMO_PDF_PATH if formato == "pdf" else DEMO_CSV_PATH
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail=f"No se encontró el dataset demo {ruta.name}.")

    return servicio.auditar_archivo(
        contenido=ruta.read_bytes(),
        nombre_archivo=ruta.name,
        ciudad_habitual=ciudad_habitual,
        modo=modo,
        presupuesto_mensual=presupuesto_mensual,
        usuario_id=usuario.usuario_id if usuario else None,
    )


@app.get("/api/historial", response_model=list[HistorialItem])
def listar_historial(
    usuario: UsuarioInfo | None = Depends(obtener_usuario_opcional),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> list[HistorialItem]:
    return servicio.repositorio.listar_historial(
        usuario_id=usuario.usuario_id if usuario else None
    )


@app.post("/api/auditorias/{audit_id}/guardar")
def guardar_auditoria_en_cuenta(
    audit_id: str,
    usuario: UsuarioInfo | None = Depends(obtener_usuario_opcional),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> dict[str, bool]:
    if usuario is None:
        raise HTTPException(status_code=401, detail="Inicia sesión para guardar esta revisión.")
    guardada = servicio.repositorio.asociar_auditoria_usuario(audit_id, usuario.usuario_id)
    if not guardada:
        raise HTTPException(status_code=404, detail="Revisión no encontrada.")
    return {"guardada": True}


@app.get("/api/auditorias/{audit_id}", response_model=AuditoriaResponse)
def obtener_auditoria(
    audit_id: str,
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> AuditoriaResponse:
    auditoria = servicio.repositorio.obtener_auditoria(audit_id)
    if auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada.")
    return auditoria


@app.delete("/api/auditorias/{audit_id}")
def eliminar_auditoria(
    audit_id: str,
    usuario: UsuarioInfo | None = Depends(obtener_usuario_opcional),
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> dict[str, str | bool]:
    if usuario is None:
        raise HTTPException(
            status_code=401, detail="Inicia sesión para eliminar revisiones de tu historial."
        )
    eliminada = servicio.repositorio.eliminar_auditoria(
        audit_id, usuario_id=usuario.usuario_id
    )
    if not eliminada:
        raise HTTPException(status_code=404, detail="Revisión no encontrada en tu historial.")
    return {"eliminada": True, "audit_id": audit_id}


@app.post("/api/alertas/{alerta_id}/marcar-fui-yo", response_model=MarcarFuiYoResponse)
def marcar_alerta_fui_yo(
    alerta_id: str,
    body: MarcarFuiYoRequest | None = None,
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> MarcarFuiYoResponse:
    verificada = True if body is None else body.verificada
    resultado = servicio.repositorio.actualizar_estado_fui_yo(alerta_id, verificada)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada.")
    return resultado


@app.get("/api/auditorias/{audit_id}/reporte-pdf")
def descargar_reporte_pdf(
    audit_id: str,
    servicio: ServicioAuditorFinGuard = Depends(obtener_servicio),
) -> Response:
    auditoria = servicio.repositorio.obtener_auditoria(audit_id)
    if auditoria is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada.")

    pdf_bytes = generar_reporte_auditoria_pdf(auditoria)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="FinGuard-Reporte-{audit_id}.pdf"'
        },
    )
