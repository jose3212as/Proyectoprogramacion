import { AuditoriaResponse, ModoControl, NivelRiesgo } from "../types/finguard";

const API_BASE =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

export const DEMO_OFFLINE_MOBILE: AuditoriaResponse = {
  audit_id: "mobile-demo-offline",
  archivo: "estado_cuenta_demo.csv",
  formato: "csv",
  fecha_auditoria: "2026-10-20T10:30:00Z",
  perfil: {
    ciudad_habitual: "Ica",
    modo: "normal",
    presupuesto_mensual: 2500,
  },
  resumen_gastos: {
    gasto_total: 2198.97,
    promedio_diario: 115.74,
    cantidad_movimientos: 24,
    presupuesto_consumido_pct: 87.96,
    estado_presupuesto: "precaucion",
    media_transaccion: 91.62,
    desviacion_estandar: 191.21,
    por_categoria: [
      { categoria: "Compras", total: 1270, porcentaje: 57.75, cantidad: 2 },
      { categoria: "Comida", total: 453, porcentaje: 20.6, cantidad: 11 },
      { categoria: "Servicios", total: 144, porcentaje: 6.55, cantidad: 2 },
      { categoria: "Suscripciones", total: 138.47, porcentaje: 6.3, cantidad: 4 },
      { categoria: "Transporte", total: 109, porcentaje: 4.96, cantidad: 3 },
    ],
  },
  radar_fugas: {
    total_fugas_estimado: 351.84,
    gastos_hormiga: [
      {
        comercio: "Cafe Tostado Ica",
        categoria: "Comida",
        cantidad: 6,
        monto_promedio: 11.92,
        total_acumulado: 71.5,
        explicacion:
          "6 compras pequeñas frecuentes en Cafe Tostado Ica acumulando S/ 71.50.",
      },
    ],
    cobros_duplicados: [
      {
        ids_transacciones: ["TX007", "TX008"],
        comercio: "Supermercado Metro Ica",
        monto: 142.5,
        fecha: "2026-10-04",
        diferencia_minutos: 3,
        explicacion:
          "Posible cobro duplicado de S/ 142.50 en Supermercado Metro Ica con 3 minutos de diferencia.",
      },
    ],
    suscripciones_recurrentes: [
      {
        comercio: "Netflix.com",
        monto_mensual: 44.9,
        frecuencia_detectada: "2 cargos en el periodo",
        transacciones: ["TX004", "TX024"],
        explicacion: "Suscripción activa en Netflix.com: S/ 44.90 por ciclo.",
      },
    ],
  },
  escudo_antifraude: {
    nivel_riesgo_general: "critico",
    total_alertas: 3,
    alertas_activas: 3,
    alertas: [
      {
        alerta_id: "mob-TX020",
        transaccion_id: "TX020",
        fecha: "2026-10-15",
        hora: "03:15",
        comercio: "TechStore Importaciones",
        ciudad: "Miami",
        canal: "online",
        monto_pen: 950.0,
        severidad: "critica",
        regla_activada: "compra_nocturna_atipica/6",
        titulo: "Compra online nocturna atípica",
        explicacion:
          "Compra online atípica de S/ 950.00 a las 03:15 AM en TechStore Importaciones (Miami).",
        traza_prolog: [
          "transaccion(TX020, 2026-10-15, 03:15, TechStore Importaciones, Miami, online, 950.00)",
          "hora_madrugada(03:15) -> true",
        ],
        z_score: 4.49,
        verificada_fui_yo: false,
      },
      {
        alerta_id: "mob-TX018",
        transaccion_id: "TX018",
        fecha: "2026-10-12",
        hora: "14:45",
        comercio: "Tienda Mall Aventura",
        ciudad: "Trujillo",
        canal: "presencial",
        monto_pen: 320.0,
        severidad: "critica",
        regla_activada: "viaje_imposible/8",
        titulo: "Posible clonación (Viaje imposible)",
        explicacion:
          "Compra presencial en Ica a las 14:00 y otra en Trujillo a las 14:45 (45 min de diferencia).",
        traza_prolog: [
          "ciudades_distintas(Ica, Trujillo) -> true",
          "diferencia_minutos(14:00, 14:45, 45) -> 45 < 180 min",
        ],
        z_score: 1.19,
        verificada_fui_yo: false,
      },
    ],
  },
  metadatos_motor: {
    tiempo_procesamiento_ms: 48.0,
    motor_prolog_activo: "modo-demo-offline",
  },
};

export async function auditarArchivoMobile(params: {
  uri: string;
  nombre: string;
  mimeType?: string;
  ciudadHabitual: string;
  modo: ModoControl;
  presupuestoMensual: number;
}): Promise<AuditoriaResponse> {
  const form = new FormData();
  form.append("archivo", {
    uri: params.uri,
    name: params.nombre,
    type: params.mimeType ?? "application/octet-stream",
  } as unknown as Blob);
  form.append("ciudad_habitual", params.ciudadHabitual);
  form.append("modo", params.modo);
  form.append("presupuesto_mensual", String(params.presupuestoMensual));

  const res = await fetch(`${API_BASE}/api/auditar-cuenta`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    throw new Error(`No se pudo auditar el archivo (HTTP ${res.status}).`);
  }
  return res.json();
}

export async function auditarDemoMobile(params: {
  formato: "csv" | "pdf";
  ciudadHabitual: string;
  modo: ModoControl;
  presupuestoMensual: number;
}): Promise<AuditoriaResponse> {
  const query = new URLSearchParams({
    formato: params.formato,
    ciudad_habitual: params.ciudadHabitual,
    modo: params.modo,
    presupuesto_mensual: String(params.presupuestoMensual),
  });
  const res = await fetch(`${API_BASE}/api/demo?${query.toString()}`);
  if (!res.ok) {
    throw new Error(`Error al consultar demo (HTTP ${res.status}).`);
  }
  return res.json();
}

export async function marcarFuiYoMobile(
  alertaId: string,
  verificada: boolean
): Promise<{
  alerta_id: string;
  verificada_fui_yo: boolean;
  alertas_activas: number;
  nivel_riesgo_general: NivelRiesgo;
}> {
  const res = await fetch(
    `${API_BASE}/api/alertas/${encodeURIComponent(alertaId)}/marcar-fui-yo`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ verificada }),
    }
  );
  if (!res.ok) {
    throw new Error(`No se pudo actualizar alerta (HTTP ${res.status}).`);
  }
  return res.json();
}

export function urlReportePdfMobile(auditId: string): string {
  return `${API_BASE}/api/auditorias/${encodeURIComponent(auditId)}/reporte-pdf`;
}
