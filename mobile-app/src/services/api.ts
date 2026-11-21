import { AuditoriaResponse, ModoControl, NivelRiesgo } from "../types/finguard";

const API_BASE =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

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
