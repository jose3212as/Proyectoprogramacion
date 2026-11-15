"use client";

import React, { useEffect, useState } from "react";
import { Cpu, Download, History, Shield, Sparkles } from "lucide-react";
import { AuditForm } from "@/components/AuditForm";
import { EscudoAntifraudeCard } from "@/components/EscudoAntifraudeCard";
import { RadarFugasCard } from "@/components/RadarFugasCard";
import { ResumenGastosCard } from "@/components/ResumenGastosCard";
import { TransaccionesTable } from "@/components/TransaccionesTable";
import {
  auditarCuentaArchivo,
  auditarDemoBackend,
  marcarAlertaFuiYo,
  obtenerAuditoriaPorId,
  obtenerHistorial,
  urlReportePdf,
  verificarSaludBackend,
} from "@/lib/api";
import { MOCK_AUDITORIA_DEMO } from "@/lib/mockData";
import { AuditoriaResponse, HistorialItem, ModoControl } from "@/types/finguard";

export default function HomePage() {
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [motorProlog, setMotorProlog] = useState<string>("verificando");
  const [auditoria, setAuditoria] = useState<AuditoriaResponse | null>(null);
  const [historial, setHistorial] = useState<HistorialItem[]>([]);
  const [mostrarHistorial, setMostrarHistorial] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [actualizandoAlertaId, setActualizandoAlertaId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refrescarEstado = async () => {
    const salud = await verificarSaludBackend();
    setBackendOnline(salud.online);
    setMotorProlog(salud.motorProlog ?? "offline");
    if (salud.online) {
      try {
        const items = await obtenerHistorial();
        setHistorial(items);
      } catch {
        // Historial opcional
      }
    }
  };

  useEffect(() => {
    refrescarEstado();
  }, []);

  const manejarAuditarArchivo = async (params: {
    archivo: File;
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => {
    setCargando(true);
    setError(null);
    try {
      const resultado = await auditarCuentaArchivo(params);
      setAuditoria(resultado);
      await refrescarEstado();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo conectar con el backend FastAPI en http://127.0.0.1:8000."
      );
    } finally {
      setCargando(false);
    }
  };

  const manejarAuditarDemo = async (params: {
    formato: "csv" | "pdf";
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => {
    setCargando(true);
    setError(null);
    try {
      const resultado = await auditarDemoBackend(params);
      setAuditoria(resultado);
      await refrescarEstado();
    } catch {
      // Fallback limpio al contrato JSON simulado si el usuario solo encendió Next.js
      setAuditoria({
        ...MOCK_AUDITORIA_DEMO,
        perfil: {
          ciudad_habitual: params.ciudadHabitual,
          modo: params.modo,
          presupuesto_mensual: params.presupuestoMensual,
        },
      });
    } finally {
      setCargando(false);
    }
  };

  const manejarMarcarFuiYo = async (alertaId: string, verificada: boolean) => {
    if (!auditoria) return;
    setActualizandoAlertaId(alertaId);
    try {
      if (auditoria.audit_id === "demo-offline-001") {
        const alertas = auditoria.escudo_antifraude.alertas.map((a) =>
          a.alerta_id === alertaId ? { ...a, verificada_fui_yo: verificada } : a
        );
        const activas = alertas.filter((a) => !a.verificada_fui_yo).length;
        setAuditoria({
          ...auditoria,
          escudo_antifraude: {
            ...auditoria.escudo_antifraude,
            alertas_activas: activas,
            nivel_riesgo_general: activas === 0 ? "bajo" : "critico",
            alertas,
          },
        });
        return;
      }

      const resp = await marcarAlertaFuiYo(alertaId, verificada);
      setAuditoria((prev) => {
        if (!prev) return prev;
        const alertas = prev.escudo_antifraude.alertas.map((a) =>
          a.alerta_id === alertaId ? { ...a, verificada_fui_yo: resp.verificada_fui_yo } : a
        );
        const idsActivos = new Set(
          alertas.filter((a) => !a.verificada_fui_yo).map((a) => a.transaccion_id)
        );
        return {
          ...prev,
          escudo_antifraude: {
            ...prev.escudo_antifraude,
            alertas_activas: resp.alertas_activas,
            nivel_riesgo_general: resp.nivel_riesgo_general,
            alertas,
          },
          transacciones: prev.transacciones.map((tx) => ({
            ...tx,
            es_sospechosa: idsActivos.has(tx.id),
          })),
        };
      });
      await refrescarEstado();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al actualizar alerta.");
    } finally {
      setActualizandoAlertaId(null);
    }
  };

  const cargarAuditoriaHistorial = async (auditId: string) => {
    setCargando(true);
    try {
      const data = await obtenerAuditoriaPorId(auditId);
      setAuditoria(data);
      setMostrarHistorial(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cargar la auditoría.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-teal-400 shadow-sm">
              <Shield className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight text-slate-900">FinGuard</h1>
              <p className="text-xs text-slate-500">
                Asistente Inteligente de Finanzas Personales y Escudo Antifraude
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
                backendOnline
                  ? "bg-emerald-50 text-emerald-800"
                  : "bg-amber-50 text-amber-800"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  backendOnline ? "bg-emerald-500" : "bg-amber-500"
                }`}
              />
              {backendOnline ? `API Conectada (${motorProlog})` : "Modo Demo Offline"}
            </span>

            {backendOnline && historial.length > 0 && (
              <button
                type="button"
                onClick={() => setMostrarHistorial((v) => !v)}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                <History className="h-3.5 w-3.5" />
                Historial ({historial.length})
              </button>
            )}

            {auditoria && auditoria.audit_id !== "demo-offline-001" && (
              <a
                href={urlReportePdf(auditoria.audit_id)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-bold text-white hover:bg-slate-800"
              >
                <Download className="h-3.5 w-3.5" />
                Exportar Reporte PDF
              </a>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-6 sm:px-6">
        {mostrarHistorial && (
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-3 text-sm font-bold text-slate-900">Historial de Auditorías</h2>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {historial.map((h) => (
                <button
                  key={h.audit_id}
                  type="button"
                  onClick={() => cargarAuditoriaHistorial(h.audit_id)}
                  className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-left transition hover:border-teal-400 hover:bg-white"
                >
                  <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                    <span>{h.archivo}</span>
                    <span className="uppercase text-teal-700">{h.formato}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {h.ciudad_habitual} • {h.modo} • S/ {h.gasto_total.toFixed(2)}
                  </p>
                </button>
              ))}
            </div>
          </section>
        )}

        <AuditForm
          cargando={cargando}
          onAuditarArchivo={manejarAuditarArchivo}
          onAuditarDemo={manejarAuditarDemo}
        />

        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800">
            {error}
          </div>
        )}

        {!auditoria ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
            <Sparkles className="mx-auto mb-3 h-10 w-10 text-teal-600" />
            <h2 className="text-lg font-bold text-slate-900">
              Listo para auditar tus movimientos bancarios
            </h2>
            <p className="mx-auto mt-1 max-w-xl text-sm text-slate-500">
              Sube un estado de cuenta en PDF o CSV arriba, o haz clic en{" "}
              <strong>Probar Demo CSV / PDF</strong> para visualizar los 3 bloques de diagnóstico
              (Resumen de Gastos, Radar de Fugas y Escudo Antifraude con SWI-Prolog).
            </p>
          </div>
        ) : (
          <>
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-600">
              <div>
                Archivo auditado: <strong className="text-slate-900">{auditoria.archivo}</strong> (
                {auditoria.formato.toUpperCase()}) • Ciudad base:{" "}
                <strong className="text-slate-900">{auditoria.perfil.ciudad_habitual}</strong> •
                Modo: <strong className="text-slate-900">{auditoria.perfil.modo}</strong>
              </div>
              <div className="inline-flex items-center gap-1.5 font-mono text-slate-700">
                <Cpu className="h-3.5 w-3.5 text-teal-600" />
                {auditoria.metadatos_motor.tiempo_procesamiento_ms.toFixed(1)} ms • Motor:{" "}
                {auditoria.metadatos_motor.motor_prolog_activo}
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className="xl:col-span-2">
                <ResumenGastosCard
                  resumen={auditoria.resumen_gastos}
                  presupuesto={auditoria.perfil.presupuesto_mensual}
                />
              </div>
              <RadarFugasCard radar={auditoria.radar_fugas} />
              <EscudoAntifraudeCard
                escudo={auditoria.escudo_antifraude}
                actualizandoId={actualizandoAlertaId}
                onMarcarFuiYo={manejarMarcarFuiYo}
              />
            </div>

            <TransaccionesTable transacciones={auditoria.transacciones} />

            <footer className="grid gap-3 rounded-2xl border border-slate-200 bg-slate-900 p-5 text-xs text-slate-300 md:grid-cols-3">
              <div>
                <p className="font-bold text-teal-400">Unidad 1 — Programación Funcional</p>
                <p className="mt-1">{auditoria.metadatos_motor.paradigmas.funcional}</p>
              </div>
              <div>
                <p className="font-bold text-teal-400">Unidad 2 — Programación Lógica</p>
                <p className="mt-1">{auditoria.metadatos_motor.paradigmas.logico}</p>
              </div>
              <div>
                <p className="font-bold text-teal-400">
                  Unidad 3 — Multiparadigma y Ciencia de Datos
                </p>
                <p className="mt-1">{auditoria.metadatos_motor.paradigmas.multiparadigma_datos}</p>
              </div>
            </footer>
          </>
        )}
      </main>
    </div>
  );
}
