"use client";

import React from "react";
import { Coffee, CopyCheck, Repeat, TrendingDown } from "lucide-react";
import { RadarFugas } from "@/types/finguard";

interface Props {
  radar: RadarFugas;
}

export function RadarFugasCard({ radar }: Props) {
  const sinFugas =
    radar.gastos_hormiga.length === 0 &&
    radar.cobros_duplicados.length === 0 &&
    radar.suscripciones_recurrentes.length === 0;

  return (
    <article className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
            <TrendingDown className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
              Bloque 2
            </span>
            <h3 className="text-base font-bold text-slate-900">
              Radar de Fugas de Dinero (¿Dónde pierdo plata?)
            </h3>
          </div>
        </div>
        <div className="rounded-xl bg-amber-50 px-3 py-1.5 text-right">
          <p className="text-[11px] font-medium text-amber-700">Fuga estimada</p>
          <p className="text-base font-extrabold text-amber-900">
            S/ {radar.total_fugas_estimado.toFixed(2)}
          </p>
        </div>
      </div>

      {sinFugas ? (
        <p className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800">
          No se detectaron gastos hormiga recurrentes ni cobros duplicados relevantes.
        </p>
      ) : (
        <div className="space-y-4">
          {radar.gastos_hormiga.length > 0 && (
            <div>
              <h4 className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-slate-600">
                <Coffee className="h-3.5 w-3.5 text-amber-600" />
                Gastos Hormiga Acumulados
              </h4>
              <div className="space-y-2">
                {radar.gastos_hormiga.map((item) => (
                  <div
                    key={item.comercio}
                    className="rounded-xl border border-amber-200 bg-amber-50/60 p-3"
                  >
                    <div className="flex items-center justify-between text-sm font-bold text-slate-900">
                      <span>{item.comercio}</span>
                      <span className="text-amber-800">S/ {item.total_acumulado.toFixed(2)}</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-600">{item.explicacion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {radar.cobros_duplicados.length > 0 && (
            <div>
              <h4 className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-slate-600">
                <CopyCheck className="h-3.5 w-3.5 text-rose-600" />
                Posibles Cobros Duplicados
              </h4>
              <div className="space-y-2">
                {radar.cobros_duplicados.map((dup) => (
                  <div
                    key={dup.ids_transacciones.join("-")}
                    className="rounded-xl border border-rose-200 bg-rose-50/60 p-3"
                  >
                    <div className="flex items-center justify-between text-sm font-bold text-slate-900">
                      <span>{dup.comercio}</span>
                      <span className="text-rose-700">S/ {dup.monto.toFixed(2)}</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-600">{dup.explicacion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {radar.suscripciones_recurrentes.length > 0 && (
            <div>
              <h4 className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-slate-600">
                <Repeat className="h-3.5 w-3.5 text-indigo-600" />
                Suscripciones Recurrentes Detectadas
              </h4>
              <div className="space-y-2">
                {radar.suscripciones_recurrentes.map((sub) => (
                  <div
                    key={sub.comercio}
                    className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-3"
                  >
                    <div className="flex items-center justify-between text-sm font-bold text-slate-900">
                      <span>{sub.comercio}</span>
                      <span className="text-indigo-800">S/ {sub.monto_mensual.toFixed(2)}/ciclo</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-600">{sub.explicacion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </article>
  );
}
