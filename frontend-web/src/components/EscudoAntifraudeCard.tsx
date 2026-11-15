"use client";

import React, { useState } from "react";
import { AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, ShieldAlert, ShieldCheck } from "lucide-react";
import { AlertaFraude, EscudoAntifraude } from "@/types/finguard";

interface Props {
  escudo: EscudoAntifraude;
  actualizandoId: string | null;
  onMarcarFuiYo: (alertaId: string, verificada: boolean) => Promise<void>;
}

const BADGE_RIESGO: Record<string, string> = {
  critico: "bg-rose-600 text-white",
  alto: "bg-orange-500 text-white",
  medio: "bg-amber-500 text-white",
  bajo: "bg-emerald-600 text-white",
};

const BADGE_SEVERIDAD: Record<string, string> = {
  critica: "bg-rose-100 text-rose-800 border-rose-300",
  alta: "bg-orange-100 text-orange-800 border-orange-300",
  media: "bg-amber-100 text-amber-800 border-amber-300",
  baja: "bg-slate-100 text-slate-700 border-slate-300",
};

function TarjetaAlerta({
  alerta,
  ocupado,
  onMarcarFuiYo,
}: {
  alerta: AlertaFraude;
  ocupado: boolean;
  onMarcarFuiYo: (alertaId: string, verificada: boolean) => Promise<void>;
}) {
  const [mostrarTraza, setMostrarTraza] = useState(false);

  return (
    <div
      className={`rounded-xl border p-4 transition ${
        alerta.verificada_fui_yo
          ? "border-emerald-200 bg-emerald-50/40 opacity-85"
          : "border-rose-200 bg-rose-50/50"
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full border px-2 py-0.5 text-[11px] font-bold uppercase ${
                alerta.verificada_fui_yo
                  ? "border-emerald-300 bg-emerald-100 text-emerald-800"
                  : BADGE_SEVERIDAD[alerta.severidad]
              }`}
            >
              {alerta.verificada_fui_yo ? "Verificada (Fui yo)" : alerta.severidad}
            </span>
            <code className="rounded bg-slate-900 px-2 py-0.5 text-[11px] font-mono text-teal-300">
              {alerta.regla_activada}
            </code>
            {alerta.z_score !== null && (
              <span className="text-xs font-medium text-slate-500">
                Z-Score: <strong>{alerta.z_score.toFixed(2)}</strong>
              </span>
            )}
          </div>
          <h4 className="text-sm font-bold text-slate-900">{alerta.titulo}</h4>
        </div>

        <div className="text-right">
          <p className="text-base font-extrabold text-slate-900">
            S/ {alerta.monto_pen.toFixed(2)}
          </p>
          <p className="text-[11px] text-slate-500">
            {alerta.fecha} • {alerta.hora} • {alerta.ciudad}
          </p>
        </div>
      </div>

      <p className="mt-2 text-sm leading-relaxed text-slate-700">{alerta.explicacion}</p>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <button
          type="button"
          onClick={() => setMostrarTraza((prev) => !prev)}
          className="inline-flex items-center gap-1 text-xs font-semibold text-slate-600 hover:text-slate-900"
        >
          {mostrarTraza ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          {mostrarTraza ? "Ocultar traza SWI-Prolog" : "Ver traza lógica SWI-Prolog"}
        </button>

        <button
          type="button"
          disabled={ocupado}
          onClick={() => onMarcarFuiYo(alerta.alerta_id, !alerta.verificada_fui_yo)}
          className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition disabled:opacity-50 ${
            alerta.verificada_fui_yo
              ? "border border-slate-300 bg-white text-slate-700 hover:bg-slate-100"
              : "bg-slate-900 text-white hover:bg-slate-800"
          }`}
        >
          <CheckCircle2 className="h-3.5 w-3.5" />
          {ocupado
            ? "Actualizando..."
            : alerta.verificada_fui_yo
            ? "Deshacer 'Fui yo'"
            : "Fui yo (Descartar alerta)"}
        </button>
      </div>

      {mostrarTraza && (
        <div className="mt-3 rounded-lg bg-slate-950 p-3 font-mono text-[11px] text-emerald-300">
          <div className="mb-1 text-[10px] uppercase tracking-wider text-slate-400">
            Traza de unificación y backtracking (reglas_fraude.pl)
          </div>
          {alerta.traza_prolog.map((paso, idx) => (
            <div key={idx} className="leading-5">
              ?- {paso}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function EscudoAntifraudeCard({ escudo, actualizandoId, onMarcarFuiYo }: Props) {
  return (
    <article className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-xl ${
              escudo.alertas_activas > 0
                ? "bg-rose-50 text-rose-700"
                : "bg-emerald-50 text-emerald-700"
            }`}
          >
            {escudo.alertas_activas > 0 ? (
              <ShieldAlert className="h-5 w-5" />
            ) : (
              <ShieldCheck className="h-5 w-5" />
            )}
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-700">
              Bloque 3
            </span>
            <h3 className="text-base font-bold text-slate-900">
              Escudo Antifraude (¿Mi tarjeta está segura?)
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-3 py-1 text-xs font-extrabold uppercase ${
              BADGE_RIESGO[escudo.nivel_riesgo_general] ?? BADGE_RIESGO.bajo
            }`}
          >
            Riesgo: {escudo.nivel_riesgo_general}
          </span>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
            {escudo.alertas_activas} activas / {escudo.total_alertas}
          </span>
        </div>
      </div>

      {escudo.alertas.length === 0 ? (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800">
          <ShieldCheck className="h-5 w-5 shrink-0" />
          Tu estado de cuenta no activó ninguna regla de anomalía o fraude en SWI-Prolog.
        </div>
      ) : (
        <div className="space-y-3">
          {escudo.alertas_activas === 0 && (
            <div className="flex items-center gap-2 rounded-xl bg-emerald-50 p-3 text-xs font-medium text-emerald-800">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              Todas las alertas fueron verificadas manualmente como operaciones propias (&quot;Fui yo&quot;).
            </div>
          )}
          {escudo.alertas.map((alerta) => (
            <TarjetaAlerta
              key={alerta.alerta_id}
              alerta={alerta}
              ocupado={actualizandoId === alerta.alerta_id}
              onMarcarFuiYo={onMarcarFuiYo}
            />
          ))}
        </div>
      )}
    </article>
  );
}
