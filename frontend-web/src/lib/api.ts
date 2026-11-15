import {
  AuditoriaResponse,
  HistorialItem,
  MarcarFuiYoResponse,
  ModoControl,
} from "@/types/finguard";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

async function manejarError(res: Response): Promise<never> {
  let mensaje = `Error HTTP ${res.status}`;
  try {
    const data = await res.json();
    if (data?.detail) {
      mensaje = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    }
  } catch {
    // Mantiene el mensaje de código HTTP por defecto.
  }
  throw new Error(mensaje);
}

export async function verificarSaludBackend(): Promise<{
  online: boolean;
  motorProlog?: string;
}> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: true, motorProlog: data.motor_prolog };
  } catch {
    return { online: false };
  }
}

export async function auditarCuentaArchivo(params: {
  archivo: File;
  ciudadHabitual: string;
  modo: ModoControl;
  presupuestoMensual: number;
}): Promise<AuditoriaResponse> {
  const form = new FormData();
  form.append("archivo", params.archivo);
  form.append("ciudad_habitual", params.ciudadHabitual);
  form.append("modo", params.modo);
  form.append("presupuesto_mensual", String(params.presupuestoMensual));

  const res = await fetch(`${API_BASE}/api/auditar-cuenta`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function auditarDemoBackend(params: {
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
  const res = await fetch(`${API_BASE}/api/demo?${query.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function marcarAlertaFuiYo(
  alertaId: string,
  verificada: boolean
): Promise<MarcarFuiYoResponse> {
  const res = await fetch(`${API_BASE}/api/alertas/${encodeURIComponent(alertaId)}/marcar-fui-yo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ verificada }),
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function obtenerHistorial(): Promise<HistorialItem[]> {
  const res = await fetch(`${API_BASE}/api/historial`, { cache: "no-store" });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function obtenerAuditoriaPorId(auditId: string): Promise<AuditoriaResponse> {
  const res = await fetch(`${API_BASE}/api/auditorias/${encodeURIComponent(auditId)}`, {
    cache: "no-store",
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export function urlReportePdf(auditId: string): string {
  return `${API_BASE}/api/auditorias/${encodeURIComponent(auditId)}/reporte-pdf`;
}
