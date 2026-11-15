"use client";

import React, { useState } from "react";
import { TransaccionProcesada } from "@/types/finguard";

interface Props {
  transacciones: TransaccionProcesada[];
}

export function TransaccionesTable({ transacciones }: Props) {
  const [soloSospechosas, setSoloSospechosas] = useState(false);

  if (transacciones.length === 0) return null;

  const filtradas = soloSospechosas
    ? transacciones.filter((t) => t.es_sospechosa)
    : transacciones;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Detalle Inmutable de Movimientos Auditados ({filtradas.length})
          </h3>
          <p className="text-xs text-slate-500">
            Conversión automática de divisas (USD/EUR &rarr; PEN), categoría funcional y Z-Score estadístico.
          </p>
        </div>
        <label className="inline-flex cursor-pointer items-center gap-2 text-xs font-semibold text-slate-700">
          <input
            type="checkbox"
            checked={soloSospechosas}
            onChange={(e) => setSoloSospechosas(e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 text-teal-600"
          />
          Mostrar solo sospechosas
        </label>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-slate-600">
              <th className="px-3 py-2.5 font-semibold">ID</th>
              <th className="px-3 py-2.5 font-semibold">Fecha / Hora</th>
              <th className="px-3 py-2.5 font-semibold">Comercio</th>
              <th className="px-3 py-2.5 font-semibold">Ciudad / Canal</th>
              <th className="px-3 py-2.5 font-semibold">Categoría</th>
              <th className="px-3 py-2.5 font-semibold text-right">Original</th>
              <th className="px-3 py-2.5 font-semibold text-right">Monto (PEN)</th>
              <th className="px-3 py-2.5 font-semibold text-right">Z-Score</th>
              <th className="px-3 py-2.5 font-semibold">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtradas.map((tx) => (
              <tr
                key={tx.id}
                className={tx.es_sospechosa ? "bg-rose-50/50" : "hover:bg-slate-50/70"}
              >
                <td className="px-3 py-2 font-mono font-semibold text-slate-700">{tx.id}</td>
                <td className="px-3 py-2 text-slate-600">
                  {tx.fecha} <span className="text-slate-400">{tx.hora}</span>
                </td>
                <td className="px-3 py-2 font-semibold text-slate-900">{tx.comercio}</td>
                <td className="px-3 py-2 text-slate-600">
                  {tx.ciudad} • <span className="capitalize">{tx.canal}</span>
                </td>
                <td className="px-3 py-2">
                  <span className="rounded bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                    {tx.categoria}
                  </span>
                </td>
                <td className="px-3 py-2 text-right text-slate-500">
                  {tx.monto_original.toFixed(2)} {tx.moneda_original}
                </td>
                <td className="px-3 py-2 text-right font-bold text-slate-900">
                  S/ {tx.monto_pen.toFixed(2)}
                </td>
                <td className="px-3 py-2 text-right font-mono">
                  <span
                    className={
                      tx.z_score >= 2
                        ? "font-bold text-rose-700"
                        : tx.z_score >= 1.5
                        ? "font-semibold text-amber-700"
                        : "text-slate-500"
                    }
                  >
                    {tx.z_score.toFixed(2)}
                  </span>
                </td>
                <td className="px-3 py-2">
                  {tx.es_sospechosa ? (
                    <span className="rounded-full bg-rose-100 px-2 py-0.5 font-bold text-rose-800">
                      Alerta activa
                    </span>
                  ) : (
                    <span className="rounded-full bg-emerald-50 px-2 py-0.5 font-medium text-emerald-700">
                      {tx.etiqueta_modo}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
