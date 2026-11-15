"use client";

import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Wallet } from "lucide-react";
import { ResumenGastos } from "@/types/finguard";

const COLORES = ["#0d9488", "#0284c7", "#f59e0b", "#6366f1", "#ec4899", "#10b981", "#64748b"];

interface Props {
  resumen: ResumenGastos;
  presupuesto: number;
}

export function ResumenGastosCard({ resumen, presupuesto }: Props) {
  const estadoBadge =
    resumen.estado_presupuesto === "excedido"
      ? "bg-rose-100 text-rose-800 border-rose-200"
      : resumen.estado_presupuesto === "precaucion"
      ? "bg-amber-100 text-amber-800 border-amber-200"
      : "bg-emerald-100 text-emerald-800 border-emerald-200";

  const barraColor =
    resumen.estado_presupuesto === "excedido"
      ? "bg-rose-600"
      : resumen.estado_presupuesto === "precaucion"
      ? "bg-amber-500"
      : "bg-emerald-500";

  return (
    <article className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
            <Wallet className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-teal-700">
              Bloque 1
            </span>
            <h3 className="text-base font-bold text-slate-900">
              Resumen de Gastos (¿A dónde fue mi dinero?)
            </h3>
          </div>
        </div>
        <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${estadoBadge}`}>
          {resumen.presupuesto_consumido_pct.toFixed(1)}% del presupuesto
        </span>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Gasto Total</p>
          <p className="text-lg font-extrabold text-slate-900">
            S/ {resumen.gasto_total.toLocaleString("es-PE", { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Promedio Diario</p>
          <p className="text-lg font-extrabold text-slate-900">
            S/ {resumen.promedio_diario.toFixed(2)}
          </p>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Media / Desv. Est.</p>
          <p className="text-sm font-bold text-slate-800">
            S/ {resumen.media_transaccion.toFixed(0)} &plusmn; {resumen.desviacion_estandar.toFixed(0)}
          </p>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs text-slate-500">Movimientos</p>
          <p className="text-lg font-extrabold text-slate-900">{resumen.cantidad_movimientos}</p>
        </div>
      </div>

      <div className="mb-5">
        <div className="mb-1 flex justify-between text-xs text-slate-500">
          <span>Consumo respecto a S/ {presupuesto.toLocaleString("es-PE")}</span>
          <span>{resumen.presupuesto_consumido_pct.toFixed(1)}%</span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className={`h-full rounded-full transition-all ${barraColor}`}
            style={{ width: `${Math.min(resumen.presupuesto_consumido_pct, 100)}%` }}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="h-56">
          <p className="mb-1 text-xs font-semibold text-slate-600">Distribución por Categoría</p>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={resumen.por_categoria}
                dataKey="total"
                nameKey="categoria"
                cx="50%"
                cy="50%"
                innerRadius={42}
                outerRadius={72}
                paddingAngle={2}
              >
                {resumen.por_categoria.map((cat, idx) => (
                  <Cell key={cat.categoria} fill={COLORES[idx % COLORES.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`S/ ${Number(value).toFixed(2)}`, "Total"]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="h-56">
          <p className="mb-1 text-xs font-semibold text-slate-600">Evolución de Gasto Diario</p>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={resumen.gasto_diario}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="fecha"
                tickFormatter={(v) => String(v).slice(5)}
                tick={{ fontSize: 10 }}
              />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip formatter={(value) => [`S/ ${Number(value).toFixed(2)}`, "Gasto"]} />
              <Bar dataKey="total" fill="#0d9488" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {resumen.por_categoria.map((cat, idx) => (
          <span
            key={cat.categoria}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs text-slate-700"
          >
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: COLORES[idx % COLORES.length] }}
            />
            <strong>{cat.categoria}:</strong> S/ {cat.total.toFixed(2)} ({cat.porcentaje.toFixed(1)}%)
          </span>
        ))}
      </div>
    </article>
  );
}
