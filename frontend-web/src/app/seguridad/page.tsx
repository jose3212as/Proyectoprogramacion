"use client";

import React, { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, Download, ShieldCheck } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { EmptyAuditState } from "@/components/EmptyAuditState";
import { urlReportePdf } from "@/lib/api";

const ESTILO_RIESGO: Record<string, string> = {
  critico: "bg-[#FCE8EC] text-[#8E263D]",
  alto: "bg-[#FDEEE4] text-[#9A4D23]",
  medio: "bg-[#FDF6DF] text-[#856414]",
  bajo: "bg-[#DDF0E8] text-[#1E4F41]",
};

export default function SeguridadPage() {
  const { auditoria, actualizandoAlertaId, toggleFuiYo, error } = useAudit();
  const [filtro, setFiltro] = useState<"todas" | "activas" | "verificadas">("todas");
  const [trazaAbierta, setTrazaAbierta] = useState<string | null>(null);

  if (!auditoria) {
    return (
      <EmptyAuditState
        titulo="Escudo Antifraude (SWI-Prolog)"
        descripcion="Sube tu extracto para ejecutar las reglas lógicas de detección de clonación (viaje imposible), compras nocturnas atípicas y anomalías Z-Score."
      />
    );
  }

  const { escudo_antifraude: escudo } = auditoria;
  const alertasFiltradas = escudo.alertas.filter((a) => {
    if (filtro === "activas") return !a.verificada_fui_yo;
    if (filtro === "verificadas") return a.verificada_fui_yo;
    return true;
  });

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#E7E3DA] pb-6">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-[#8E263D]">
            Bloque 3 • Escudo Antifraude SWI-Prolog
          </span>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
            ¿Mi tarjeta está segura?
          </h1>
          <p className="mt-1 text-sm text-[#616B75]">
            Cada alerta incluye la regla lógica activada y su traza de inferencia explicable.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`rounded-full px-4 py-1.5 text-xs font-bold uppercase ${
              ESTILO_RIESGO[escudo.nivel_riesgo_general] ?? ESTILO_RIESGO.bajo
            }`}
          >
            Riesgo {escudo.nivel_riesgo_general}
          </span>
          {auditoria.audit_id !== "demo-offline-001" && (
            <a
              href={urlReportePdf(auditoria.audit_id)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 rounded-xl bg-[#2D6A5B] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#235448]"
            >
              <Download className="h-3.5 w-3.5" />
              Descargar Reporte PDF
            </a>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-2xl bg-[#FCE8EC] px-5 py-3 text-sm font-medium text-[#8E263D]">
          {error}
        </div>
      )}

      {/* Pestañas de filtro suaves */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-xl bg-[#F3F1EB] p-1">
          {[
            { id: "todas", label: `Todas (${escudo.total_alertas})` },
            { id: "activas", label: `Activas (${escudo.alertas_activas})` },
            {
              id: "verificadas",
              label: `Verificadas (${escudo.total_alertas - escudo.alertas_activas})`,
            },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setFiltro(tab.id as "todas" | "activas" | "verificadas")}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
                filtro === tab.id
                  ? "bg-white text-[#1E252B] shadow-2xs"
                  : "text-[#616B75] hover:text-[#1E252B]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {alertasFiltradas.length === 0 ? (
        <div className="flex items-center gap-3 rounded-3xl bg-[#EEF7F3] p-6 text-sm text-[#1E4F41]">
          <ShieldCheck className="h-5 w-5 shrink-0" />
          No hay alertas en esta vista. Tu tarjeta no registra incidencias pendientes.
        </div>
      ) : (
        <div className="space-y-4">
          {alertasFiltradas.map((alerta) => {
            const abierta = trazaAbierta === alerta.alerta_id;
            const ocupada = actualizandoAlertaId === alerta.alerta_id;

            return (
              <article
                key={alerta.alerta_id}
                className={`rounded-3xl p-6 transition ${
                  alerta.verificada_fui_yo ? "bg-[#EEF7F3]/75" : "bg-white"
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase ${
                          alerta.verificada_fui_yo
                            ? "bg-[#DDF0E8] text-[#1E4F41]"
                            : "bg-[#FCE8EC] text-[#8E263D]"
                        }`}
                      >
                        {alerta.verificada_fui_yo ? "Verificada (Fui yo)" : alerta.severidad}
                      </span>
                      <code className="rounded-lg bg-[#F3F1EB] px-2.5 py-0.5 font-mono text-[11px] font-medium text-[#2D6A5B]">
                        {alerta.regla_activada}
                      </code>
                      {alerta.z_score !== null && (
                        <span className="text-xs text-[#616B75]">
                          Z-Score: <strong>{alerta.z_score.toFixed(2)}</strong>
                        </span>
                      )}
                    </div>
                    <h2 className="text-base font-bold text-[#1E252B]">{alerta.titulo}</h2>
                  </div>

                  <div className="text-right">
                    <p className="text-xl font-extrabold tabular-nums text-[#1E252B]">
                      S/ {alerta.monto_pen.toFixed(2)}
                    </p>
                    <p className="text-xs text-[#616B75]">
                      {alerta.fecha} • {alerta.hora} • {alerta.ciudad} ({alerta.canal})
                    </p>
                  </div>
                </div>

                <p className="mt-3 text-sm leading-relaxed text-[#464F59]">{alerta.explicacion}</p>

                <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-[#EFECE5] pt-4">
                  <button
                    type="button"
                    onClick={() => setTrazaAbierta(abierta ? null : alerta.alerta_id)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#2D6A5B] hover:text-[#1E4F41]"
                  >
                    {abierta ? (
                      <ChevronUp className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                    {abierta ? "Ocultar traza SWI-Prolog" : "Ver traza de reglas SWI-Prolog"}
                  </button>

                  <button
                    type="button"
                    disabled={ocupada}
                    onClick={() => toggleFuiYo(alerta.alerta_id, !alerta.verificada_fui_yo)}
                    className={`inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-semibold transition disabled:opacity-50 ${
                      alerta.verificada_fui_yo
                        ? "bg-[#F3F1EB] text-[#545E68] hover:bg-[#E7E3DA]"
                        : "bg-[#2D6A5B] text-white hover:bg-[#235448]"
                    }`}
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    {ocupada
                      ? "Guardando..."
                      : alerta.verificada_fui_yo
                      ? "Deshacer 'Fui yo'"
                      : "Fui yo (Marcar segura)"}
                  </button>
                </div>

                {abierta && (
                  <div className="mt-4 rounded-2xl bg-[#22282F] p-4 font-mono text-xs text-[#BFE8D7]">
                    <div className="mb-1.5 text-[10px] uppercase tracking-wider text-[#8C98A4]">
                      Inferencia lógica (backend/app/logica/reglas_fraude.pl)
                    </div>
                    {alerta.traza_prolog.map((paso, idx) => (
                      <div key={idx} className="leading-6">
                        ?- {paso}
                      </div>
                    ))}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
