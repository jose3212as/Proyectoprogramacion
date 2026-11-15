import { AuditoriaResponse } from "@/types/finguard";

/**
 * Datos simulados alineados al Contrato JSON oficial (docs/contrato_api.json)
 * para permitir vista previa inmediata incluso si el backend aún no está encendido.
 */
export const MOCK_AUDITORIA_DEMO: AuditoriaResponse = {
  audit_id: "demo-offline-001",
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
      { categoria: "Entretenimiento", total: 46, porcentaje: 2.09, cantidad: 1 },
      { categoria: "Salud", total: 38.5, porcentaje: 1.75, cantidad: 1 },
    ],
    gasto_diario: [
      { fecha: "2026-10-01", total: 35.5 },
      { fecha: "2026-10-02", total: 50.9 },
      { fecha: "2026-10-03", total: 50.5 },
      { fecha: "2026-10-04", total: 285.0 },
      { fecha: "2026-10-05", total: 26.21 },
      { fecha: "2026-10-08", total: 96.0 },
      { fecha: "2026-10-12", total: 416.0 },
      { fecha: "2026-10-15", total: 950.0 },
      { fecha: "2026-10-18", total: 46.0 },
      { fecha: "2026-10-19", total: 44.9 },
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
          "Se detectaron 6 compras pequeñas frecuentes en Cafe Tostado Ica (promedio S/ 11.92) acumulando S/ 71.50.",
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
          "Posible cobro duplicado de S/ 142.50 en Supermercado Metro Ica (TX007 y TX008, con 3 minutos de diferencia).",
      },
      {
        ids_transacciones: ["TX004", "TX024"],
        comercio: "Netflix.com",
        monto: 44.9,
        fecha: "2026-10-02 / 2026-10-19",
        diferencia_minutos: 23880,
        explicacion:
          "Doble cargo de suscripción por S/ 44.90 en Netflix.com (TX004 el 2026-10-02 y TX024 el 2026-10-19).",
      },
    ],
    suscripciones_recurrentes: [
      {
        comercio: "Netflix.com",
        monto_mensual: 44.9,
        frecuencia_detectada: "2 cargos en el periodo",
        transacciones: ["TX004", "TX024"],
        explicacion:
          "Suscripción activa en Netflix.com: S/ 44.90 por ciclo (acumulado en extracto: S/ 89.80).",
      },
      {
        comercio: "Spotify Premium",
        monto_mensual: 26.21,
        frecuencia_detectada: "Cargo mensual recurrente",
        transacciones: ["TX009"],
        explicacion: "Suscripción activa en Spotify Premium: S/ 26.21 por ciclo.",
      },
      {
        comercio: "Amazon Prime Video",
        monto_mensual: 22.46,
        frecuencia_detectada: "Cargo mensual recurrente",
        transacciones: ["TX015"],
        explicacion: "Suscripción activa en Amazon Prime Video: S/ 22.46 por ciclo.",
      },
    ],
  },
  escudo_antifraude: {
    nivel_riesgo_general: "critico",
    total_alertas: 3,
    alertas_activas: 3,
    alertas: [
      {
        alerta_id: "demo-offline-001-TX020-compra_nocturna_atipica",
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
          "Compra online atípica de S/ 950.00 a las 03:15 AM en TechStore Importaciones (Miami) el 2026-10-15, superando el umbral nocturno de S/ 200.00.",
        traza_prolog: [
          "transaccion(TX020, 2026-10-15, 03:15, TechStore Importaciones, Miami, online, 950.00)",
          "hora_madrugada(03:15) -> true (00:00 - 05:59)",
          "umbral_nocturno(normal, 200.00) -> 950.00 >= 200.00",
          "regla_activada: compra_nocturna_atipica(TX020, 03:15, 950.00)",
        ],
        z_score: 4.49,
        verificada_fui_yo: false,
      },
      {
        alerta_id: "demo-offline-001-TX018-viaje_imposible",
        transaccion_id: "TX018",
        fecha: "2026-10-12",
        hora: "14:45",
        comercio: "Tienda Mall Aventura",
        ciudad: "Trujillo",
        canal: "presencial",
        monto_pen: 320.0,
        severidad: "critica",
        regla_activada: "viaje_imposible/8",
        titulo: "Posible clonación de tarjeta (Viaje imposible)",
        explicacion:
          "Posible clonación: compra presencial en Ica a las 14:00 (TX017, S/ 85.00) y otra en Trujillo a las 14:45 (TX018, S/ 320.00) el 2026-10-12, con solo 45 minutos de diferencia.",
        traza_prolog: [
          "transaccion(TX017, 2026-10-12, 14:00, Grifo Primax Panamericana, Ica, presencial, 85.00)",
          "transaccion(TX018, 2026-10-12, 14:45, Tienda Mall Aventura, Trujillo, presencial, 320.00)",
          "ciudades_distintas(Ica, Trujillo) -> true",
          "diferencia_minutos(14:00, 14:45, 45) -> 45 < 180 min",
        ],
        z_score: 1.19,
        verificada_fui_yo: false,
      },
      {
        alerta_id: "demo-offline-001-TX008-cobro_duplicado_regla",
        transaccion_id: "TX008",
        fecha: "2026-10-04",
        hora: "11:18",
        comercio: "Supermercado Metro Ica",
        ciudad: "Ica",
        canal: "presencial",
        monto_pen: 142.5,
        severidad: "alta",
        regla_activada: "cobro_duplicado_regla/6",
        titulo: "Posible cobro duplicado en comercio",
        explicacion:
          "Se detectaron dos cargos idénticos de S/ 142.50 en Supermercado Metro Ica el 2026-10-04 (TX007 a las 11:15 y TX008 a las 11:18) separados por 3 minutos.",
        traza_prolog: [
          "transaccion(TX007, 2026-10-04, 11:15, Supermercado Metro Ica, ..., 142.50)",
          "transaccion(TX008, 2026-10-04, 11:18, Supermercado Metro Ica, ..., 142.50)",
          "diferencia_minutos(11:15, 11:18, 3) -> 3 =< 30 min",
        ],
        z_score: 0.27,
        verificada_fui_yo: false,
      },
    ],
  },
  transacciones: [],
  metadatos_motor: {
    paradigmas: {
      funcional:
        "Pipeline inmutable Python (frozen dataclasses, lambdas, map/filter/reduce, orden superior)",
      logico: "SWI-Prolog (hechos transaccion/7, unificación, backtracking y traza explicable)",
      multiparadigma_datos:
        "POO polimórfica (LectorPDF/LectorCSV + Movimiento) + Pandas & NumPy (Z-Score)",
    },
    tiempo_procesamiento_ms: 42.5,
    motor_prolog_activo: "modo-demo-offline",
  },
};
