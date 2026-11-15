"""Modelos Pydantic que implementan el Contrato JSON oficial de FinGuard."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


ModoControl = Literal["normal", "ahorro_estricto"]
CanalTransaccion = Literal["presencial", "online"]
SeveridadAlerta = Literal["critica", "alta", "media", "baja"]


class PerfilConfig(BaseModel):
    ciudad_habitual: str
    modo: ModoControl
    presupuesto_mensual: float


class CategoriaResumen(BaseModel):
    categoria: str
    total: float
    porcentaje: float
    cantidad: int


class GastoDiario(BaseModel):
    fecha: str
    total: float


class ResumenGastos(BaseModel):
    gasto_total: float
    promedio_diario: float
    cantidad_movimientos: int
    presupuesto_consumido_pct: float
    estado_presupuesto: Literal["saludable", "precaucion", "excedido"]
    media_transaccion: float
    desviacion_estandar: float
    por_categoria: list[CategoriaResumen]
    gasto_diario: list[GastoDiario]


class GastoHormiga(BaseModel):
    comercio: str
    categoria: str
    cantidad: int
    monto_promedio: float
    total_acumulado: float
    explicacion: str


class CobroDuplicado(BaseModel):
    ids_transacciones: list[str]
    comercio: str
    monto: float
    fecha: str
    diferencia_minutos: int
    explicacion: str


class SuscripcionRecurrente(BaseModel):
    comercio: str
    monto_mensual: float
    frecuencia_detectada: str
    transacciones: list[str]
    explicacion: str


class RadarFugas(BaseModel):
    total_fugas_estimado: float
    gastos_hormiga: list[GastoHormiga]
    cobros_duplicados: list[CobroDuplicado]
    suscripciones_recurrentes: list[SuscripcionRecurrente]


class AlertaFraude(BaseModel):
    alerta_id: str
    transaccion_id: str
    fecha: str
    hora: str
    comercio: str
    ciudad: str
    canal: CanalTransaccion
    monto_pen: float
    severidad: SeveridadAlerta
    regla_activada: str
    titulo: str
    explicacion: str
    traza_prolog: list[str]
    z_score: float | None = None
    verificada_fui_yo: bool = False


class EscudoAntifraude(BaseModel):
    nivel_riesgo_general: Literal["bajo", "medio", "alto", "critico"]
    total_alertas: int
    alertas_activas: int
    alertas: list[AlertaFraude]


class TransaccionProcesada(BaseModel):
    id: str
    fecha: str
    hora: str
    comercio: str
    ciudad: str
    canal: CanalTransaccion
    monto_original: float
    moneda_original: str
    monto_pen: float
    tipo: str
    categoria: str
    etiqueta_modo: str
    z_score: float
    es_sospechosa: bool


class ParadigmasInfo(BaseModel):
    funcional: str
    logico: str
    multiparadigma_datos: str


class MetadatosMotor(BaseModel):
    paradigmas: ParadigmasInfo
    tiempo_procesamiento_ms: float
    motor_prolog_activo: str


class AuditoriaResponse(BaseModel):
    audit_id: str
    archivo: str
    formato: Literal["csv", "pdf"]
    fecha_auditoria: str
    perfil: PerfilConfig
    resumen_gastos: ResumenGastos
    radar_fugas: RadarFugas
    escudo_antifraude: EscudoAntifraude
    transacciones: list[TransaccionProcesada]
    metadatos_motor: MetadatosMotor


class HistorialItem(BaseModel):
    audit_id: str
    archivo: str
    formato: str
    fecha_auditoria: str
    ciudad_habitual: str
    modo: str
    gasto_total: float
    alertas_activas: int
    nivel_riesgo_general: str


class MarcarFuiYoRequest(BaseModel):
    verificada: bool = Field(default=True, description="True para marcar 'Fui yo', False para reactivar.")


class MarcarFuiYoResponse(BaseModel):
    alerta_id: str
    verificada_fui_yo: bool
    alertas_activas: int
    nivel_riesgo_general: str


class UsuarioInfo(BaseModel):
    usuario_id: str
    nombre: str
    correo: str
    ciudad_habitual: str
    presupuesto_mensual: float


class RegistroRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str = Field(min_length=4, max_length=120)
    password: str = Field(min_length=4, max_length=120)
    ciudad_habitual: str = Field(default="Ica", min_length=2, max_length=60)
    presupuesto_mensual: float = Field(default=2500.0, gt=0)


class LoginRequest(BaseModel):
    correo: str = Field(min_length=4, max_length=120)
    password: str = Field(min_length=4, max_length=120)


class AuthResponse(BaseModel):
    token: str
    usuario: UsuarioInfo

