import {
  AuditoriaResponse,
  AuthResponse,
  HistorialItem,
  MarcarFuiYoResponse,
  ModoControl,
  UsuarioInfo,
} from "@/types/finguard";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

function headersConToken(token?: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function manejarError(res: Response): Promise<never> {
  let mensaje = "Ocurrió un problema al procesar la solicitud.";
  try {
    const data = await res.json();
    if (data?.detail) {
      mensaje = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    }
  } catch {
    // Mantiene el mensaje amigable por defecto.
  }
  throw new Error(mensaje);
}

export async function verificarSaludBackend(): Promise<{ online: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return { online: res.ok };
  } catch {
    return { online: false };
  }
}

export async function registrarUsuario(params: {
  nombre: string;
  correo: string;
  password: string;
  ciudadHabitual: string;
  presupuestoMensual: number;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/registro`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nombre: params.nombre,
      correo: params.correo,
      password: params.password,
      ciudad_habitual: params.ciudadHabitual,
      presupuesto_mensual: params.presupuestoMensual,
    }),
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function iniciarSesionUsuario(params: {
  correo: string;
  password: string;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function obtenerUsuarioActual(token: string): Promise<UsuarioInfo> {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: headersConToken(token),
    cache: "no-store",
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function cerrarSesionUsuario(token: string): Promise<void> {
  await fetch(`${API_BASE}/api/auth/logout`, {
    method: "POST",
    headers: headersConToken(token),
  }).catch(() => undefined);
}

export async function auditarCuentaArchivo(params: {
  archivo: File;
  ciudadHabitual: string;
  modo: ModoControl;
  presupuestoMensual: number;
  token?: string | null;
}): Promise<AuditoriaResponse> {
  const form = new FormData();
  form.append("archivo", params.archivo);
  form.append("ciudad_habitual", params.ciudadHabitual);
  form.append("modo", params.modo);
  form.append("presupuesto_mensual", String(params.presupuestoMensual));

  const res = await fetch(`${API_BASE}/api/auditar-cuenta`, {
    method: "POST",
    headers: headersConToken(params.token),
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
  token?: string | null;
}): Promise<AuditoriaResponse> {
  const query = new URLSearchParams({
    formato: params.formato,
    ciudad_habitual: params.ciudadHabitual,
    modo: params.modo,
    presupuesto_mensual: String(params.presupuestoMensual),
  });
  const res = await fetch(`${API_BASE}/api/demo?${query.toString()}`, {
    headers: headersConToken(params.token),
    cache: "no-store",
  });
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function guardarRevisionEnCuenta(
  auditId: string,
  token: string
): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/auditorias/${encodeURIComponent(auditId)}/guardar`,
    {
      method: "POST",
      headers: headersConToken(token),
    }
  );
  if (!res.ok) return manejarError(res);
}

export async function marcarAlertaFuiYo(
  alertaId: string,
  verificada: boolean
): Promise<MarcarFuiYoResponse> {
  const res = await fetch(
    `${API_BASE}/api/alertas/${encodeURIComponent(alertaId)}/marcar-fui-yo`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ verificada }),
    }
  );
  if (!res.ok) return manejarError(res);
  return res.json();
}

export async function obtenerHistorial(token?: string | null): Promise<HistorialItem[]> {
  const res = await fetch(`${API_BASE}/api/historial`, {
    headers: headersConToken(token),
    cache: "no-store",
  });
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
