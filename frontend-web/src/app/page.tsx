"use client";

import React from "react";
import Link from "next/link";
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
import { ArrowUpRight, BookmarkPlus, ListOrdered, ShieldAlert, TrendingDown } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { EmptyAuditState } from "@/components/EmptyAuditState";

const PASTEL_CATEGORIAS = [
  "#5B9A8B",
  "#8A83C5",
  "#DF9A78",
  "#699EC2",
  "#CE7B91",
  "#84AE7B",
  "#9BA4AE",
];

export default function ResumenGeneralPage() {
  const { auditoria, usuario } = useAudit();

  if (!auditoria) {
    return (
      <EmptyAuditState
        titulo="Bienvenido a FinGuard"
        descripcion="Sube tu estado de cuenta mensual en PDF o CSV para ver en qué se fue tu dinero, descubrir gastos repetidos y verificar que no haya cobros extraños en tu tarjeta."
      />
    );
  }

  const { resumen_gastos: resumen, radar_fugas: radar, escudo_antifraude: escudo, perfil } = auditoria;

  const estadoBg =
    resumen.estado_presupuesto === "excedido"
      ? "bg-[#FCE8EC] text-[#8E263D]"
      : resumen.estado_presupuesto === "precaucion"
      ? "bg-[#FDEEE4] text-[#9A4D23]"
      : "bg-[#DDF0E8] text-[#1E4F41]";

  const barraColor =
    resumen.estado_presupuesto === "excedido"
      ? "bg-[#CE7B91]"
      : resumen.estado_presupuesto === "precaucion"
      ? "bg-[#DF9A78]"
      : "bg-[#5B9A8B]";

  return (
    <div className="space-y-9">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#E7E3DA] pb-6">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
            Tu resumen del mes
          </span>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
            ¿En qué se fue tu dinero?
          </h1>
          <p className="mt-1 text-sm text-[#616B75]">
            Archivo <strong className="text-[#1E252B]">{auditoria.archivo}</strong> • Ciudad:{" "}
            <strong className="text-[#1E252B]">{perfil.ciudad_habitual}</strong>
          </p>
        </div>

        <span className={`rounded-full px-3.5 py-1.5 text-xs font-semibold ${estadoBg}`}>
          Llevas {resumen.presupuesto_consumido_pct.toFixed(1)}% de tu meta mensual
        </span>
      </div>

      {!usuario && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-[#E6EFF8] px-5 py-3.5 text-xs text-[#234F73]">
          <span>
            ¿Quieres guardar esta revisión para verla otro día? Inicia sesión o crea tu cuenta en
            segundos.
          </span>
          <Link
            href="/cuenta"
            className="inline-flex items-center gap-1.5 rounded-xl bg-white px-3.5 py-1.5 font-semibold text-[#1D4363] transition hover:bg-[#F5F9FD]"
          >
            <BookmarkPlus className="h-3.5 w-3.5" />
            Guardar en mi cuenta
          </Link>
        </div>
      )}

      <section className="grid grid-cols-2 divide-y divide-[#E7E3DA] rounded-3xl bg-white sm:grid-cols-4 sm:divide-x sm:divide-y-0">
        <div className="p-6">
          <p className="text-xs font-medium text-[#616B75]">Total gastado</p>
          <p className="mt-2 text-2xl font-extrabold tabular-nums text-[#1E252B]">
            S/ {resumen.gasto_total.toLocaleString("es-PE", { minimumFractionDigits: 2 })}
          </p>
        </div>

        <div className="p-6">
          <p className="text-xs font-medium text-[#616B75]">Gasto por día</p>
          <p className="mt-2 text-2xl font-extrabold tabular-nums text-[#1E252B]">
            S/ {resumen.promedio_diario.toFixed(2)}
          </p>
        </div>

        <div className="p-6">
          <p className="text-xs font-medium text-[#616B75]">Compra promedio</p>
          <p className="mt-2 text-2xl font-extrabold tabular-nums text-[#1E252B]">
            S/ {resumen.media_transaccion.toFixed(2)}
          </p>
        </div>

        <div className="p-6">
          <p className="text-xs font-medium text-[#616B75]">Compras revisadas</p>
          <p className="mt-2 text-2xl font-extrabold tabular-nums text-[#1E252B]">
            {resumen.cantidad_movimientos}
          </p>
        </div>
      </section>

      <section className="space-y-2">
        <div className="flex justify-between text-xs font-medium text-[#616B75]">
          <span>
            Meta de gasto mensual: S/ {perfil.presupuesto_mensual.toLocaleString("es-PE")}
          </span>
          <span className="font-semibold text-[#1E252B]">
            {resumen.presupuesto_consumido_pct.toFixed(1)}%
          </span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-[#ECE8DF]">
          <div
            className={`h-full rounded-full transition-all ${barraColor}`}
            style={{ width: `${Math.min(resumen.presupuesto_consumido_pct, 100)}%` }}
          />
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-12">
        <div className="rounded-3xl bg-white p-6 lg:col-span-5">
          <h2 className="text-sm font-bold text-[#1E252B]">Por tipo de gasto</h2>
          <p className="mt-0.5 text-xs text-[#616B75]">Así se reparten tus compras</p>
          <div className="mt-4 h-60">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={resumen.por_categoria}
                  dataKey="total"
                  nameKey="categoria"
                  cx="50%"
                  cy="50%"
                  innerRadius={52}
                  outerRadius={84}
                  paddingAngle={2}
                >
                  {resumen.por_categoria.map((cat, idx) => (
                    <Cell
                      key={cat.categoria}
                      fill={PASTEL_CATEGORIAS[idx % PASTEL_CATEGORIAS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`S/ ${Number(value).toFixed(2)}`, "Total"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-2">
            {resumen.por_categoria.map((cat, idx) => (
              <div key={cat.categoria} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2 text-[#545E68]">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: PASTEL_CATEGORIAS[idx % PASTEL_CATEGORIAS.length] }}
                  />
                  {cat.categoria}
                </span>
                <span className="font-semibold tabular-nums text-[#1E252B]">
                  S/ {cat.total.toFixed(2)}{" "}
                  <span className="font-normal text-[#616B75]">({cat.porcentaje.toFixed(1)}%)</span>
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl bg-white p-6 lg:col-span-7">
          <h2 className="text-sm font-bold text-[#1E252B]">Tus gastos día a día</h2>
          <p className="mt-0.5 text-xs text-[#616B75]">
            Fechas en las que hiciste compras mayores
          </p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={resumen.gasto_diario}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EFECE5" vertical={false} />
                <XAxis
                  dataKey="fecha"
                  tickFormatter={(v) => String(v).slice(5)}
                  tick={{ fontSize: 11, fill: "#616B75" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "#616B75" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip formatter={(value) => [`S/ ${Number(value).toFixed(2)}`, "Gasto"]} />
                <Bar dataKey="total" fill="#5B9A8B" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <Link
          href="/fugas"
          className="group flex items-center justify-between rounded-2xl bg-[#FDEEE4] p-5 transition hover:bg-[#FCE3D3]"
        >
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-[#9A4D23]">
              <TrendingDown className="h-4 w-4" />
              Gastos invisibles
            </div>
            <p className="mt-1.5 text-lg font-extrabold tabular-nums text-[#5D2C12]">
              S/ {radar.total_fugas_estimado.toFixed(2)}
            </p>
            <p className="mt-0.5 text-xs text-[#804322]">
              {radar.gastos_hormiga.length} repetidos • {radar.cobros_duplicados.length} duplicados
            </p>
          </div>
          <ArrowUpRight className="h-5 w-5 text-[#9A4D23] transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </Link>

        <Link
          href="/seguridad"
          className="group flex items-center justify-between rounded-2xl bg-[#FCE8EC] p-5 transition hover:bg-[#FADBE2]"
        >
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-[#8E263D]">
              <ShieldAlert className="h-4 w-4" />
              Seguridad
            </div>
            <p className="mt-1.5 text-lg font-extrabold text-[#5C1727]">
              {escudo.alertas_activas === 0
                ? "Todo en orden"
                : `${escudo.alertas_activas} avisos por revisar`}
            </p>
            <p className="mt-0.5 text-xs text-[#8E263D]">
              {escudo.alertas_activas === 0
                ? "Sin movimientos sospechosos"
                : "Revisa si reconoces estas compras"}
            </p>
          </div>
          <ArrowUpRight className="h-5 w-5 text-[#8E263D] transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </Link>

        <Link
          href="/movimientos"
          className="group flex items-center justify-between rounded-2xl bg-[#EAE7F8] p-5 transition hover:bg-[#E0DCF5]"
        >
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-[#4B3F8F]">
              <ListOrdered className="h-4 w-4" />
              Mis compras
            </div>
            <p className="mt-1.5 text-lg font-extrabold text-[#2F275E]">
              {resumen.cantidad_movimientos} movimientos
            </p>
            <p className="mt-0.5 text-xs text-[#4B3F8F]">Ver lista completa del mes</p>
          </div>
          <ArrowUpRight className="h-5 w-5 text-[#4B3F8F] transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </Link>
      </section>
    </div>
  );
}
