export type ModoControl = "normal" | "ahorro_estricto";
export type NivelRiesgo = "bajo" | "medio" | "alto" | "critico";
export type SeveridadAlerta = "critica" | "alta" | "media" | "baja";

export interface CategoriaResumen {
  categoria: string;
  total: number;
  porcentaje: number;
  cantidad: number;
}

export interface ResumenGastos {
  gasto_total: number;
  promedio_diario: number;
  cantidad_movimientos: number;
  presupuesto_consumido_pct: number;
  estado_presupuesto: "saludable" | "precaucion" | "excedido";
  media_transaccion: number;
  desviacion_estandar: number;
  por_categoria: CategoriaResumen[];
}

export interface GastoHormiga {
  comercio: string;
  categoria: string;
  cantidad: number;
  monto_promedio: number;
  total_acumulado: number;
  explicacion: string;
}

export interface CobroDuplicado {
  ids_transacciones: string[];
  comercio: string;
  monto: number;
  fecha: string;
  diferencia_minutos: number;
  explicacion: string;
}

export interface SuscripcionRecurrente {
  comercio: string;
  monto_mensual: number;
  frecuencia_detectada: string;
  transacciones: string[];
  explicacion: string;
}

export interface RadarFugas {
  total_fugas_estimado: number;
  gastos_hormiga: GastoHormiga[];
  cobros_duplicados: CobroDuplicado[];
  suscripciones_recurrentes: SuscripcionRecurrente[];
}

export interface AlertaFraude {
  alerta_id: string;
  transaccion_id: string;
  fecha: string;
  hora: string;
  comercio: string;
  ciudad: string;
  canal: "presencial" | "online";
  monto_pen: number;
  severidad: SeveridadAlerta;
  regla_activada: string;
  titulo: string;
  explicacion: string;
  traza_prolog: string[];
  z_score: number | null;
  verificada_fui_yo: boolean;
}

export interface EscudoAntifraude {
  nivel_riesgo_general: NivelRiesgo;
  total_alertas: number;
  alertas_activas: number;
  alertas: AlertaFraude[];
}

export interface AuditoriaResponse {
  audit_id: string;
  archivo: string;
  formato: "csv" | "pdf";
  fecha_auditoria: string;
  perfil: {
    ciudad_habitual: string;
    modo: ModoControl;
    presupuesto_mensual: number;
  };
  resumen_gastos: ResumenGastos;
  radar_fugas: RadarFugas;
  escudo_antifraude: EscudoAntifraude;
  metadatos_motor: {
    tiempo_procesamiento_ms: number;
    motor_prolog_activo: string;
  };
}
