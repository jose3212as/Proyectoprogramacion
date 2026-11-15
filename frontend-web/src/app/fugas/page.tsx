"use client";

import React from "react";
import { Coffee, CopyCheck, Repeat } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { EmptyAuditState } from "@/components/EmptyAuditState";

export default function RadarFugasPage() {
  const { auditoria } = useAudit();

  if (!auditoria) {
    return (
      <EmptyAuditState
        titulo="Radar de Fugas de Dinero"
        descripcion="Carga un estado de cuenta para detectar automáticamente gastos hormiga acumulados, cobros duplicados y suscripciones recurrentes."
      />
    );
  }

  const { radar_fugas: radar, perfil } = auditoria;
  const totalFugas =
    radar.gastos_hormiga.length +
    radar.cobros_duplicados.length +
    radar.suscripciones_recurrentes.length;

  return (
    <div className="space-y-10">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#E7E3DA] pb-6">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-[#9A4D23]">
            Bloque 2 • Radar de Fugas de Dinero
          </span>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
            ¿Dónde estoy perdiendo plata?
          </h1>
          <p className="mt-1 text-sm text-[#616B75]">
            Evaluado en modo{" "}
            <strong className="text-[#1E252B]">
              {perfil.modo === "ahorro_estricto" ? "Ahorro Estricto" : "Normal"}
            </strong>{" "}
            • {totalFugas} patrones detectados
          </p>
        </div>

        <div className="rounded-2xl bg-[#FDEEE4] px-5 py-3 text-right">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-[#9A4D23]">
            Impacto Estimado
          </p>
          <p className="text-2xl font-extrabold tabular-nums text-[#5D2C12]">
            S/ {radar.total_fugas_estimado.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Sección 1: Gastos Hormiga */}
      <section className="space-y-4">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#FDEEE4] text-[#9A4D23]">
            <Coffee className="h-4 w-4" />
          </span>
          <div>
            <h2 className="text-base font-bold text-[#1E252B]">Gastos Hormiga Acumulados</h2>
            <p className="text-xs text-[#616B75]">
              Compras pequeñas repetitivas en un mismo establecimiento
            </p>
          </div>
        </div>

        {radar.gastos_hormiga.length === 0 ? (
          <p className="rounded-2xl bg-[#EEF7F3] px-5 py-4 text-sm text-[#1E4F41]">
            No se detectaron gastos hormiga recurrentes bajo los umbrales actuales.
          </p>
        ) : (
          <div className="divide-y divide-[#EFECE5] rounded-3xl bg-white">
            {radar.gastos_hormiga.map((h) => (
              <div
                key={h.comercio}
                className="flex flex-wrap items-center justify-between gap-4 px-6 py-5"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm font-bold text-[#1E252B]">{h.comercio}</span>
                    <span className="rounded-full bg-[#FDEEE4] px-2.5 py-0.5 text-[11px] font-semibold text-[#9A4D23]">
                      {h.cantidad} compras • {h.categoria}
                    </span>
                  </div>
                  <p className="text-xs text-[#616B75]">{h.explicacion}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-extrabold tabular-nums text-[#9A4D23]">
                    S/ {h.total_acumulado.toFixed(2)}
                  </p>
                  <p className="text-[11px] text-[#616B75]">
                    Promedio S/ {h.monto_promedio.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Sección 2: Cobros Duplicados */}
      <section className="space-y-4">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#FCE8EC] text-[#8E263D]">
            <CopyCheck className="h-4 w-4" />
          </span>
          <div>
            <h2 className="text-base font-bold text-[#1E252B]">Posibles Cobros Duplicados</h2>
            <p className="text-xs text-[#616B75]">
              Cargos idénticos en el mismo comercio o doble facturación en el periodo
            </p>
          </div>
        </div>

        {radar.cobros_duplicados.length === 0 ? (
          <p className="rounded-2xl bg-[#EEF7F3] px-5 py-4 text-sm text-[#1E4F41]">
            No se encontraron cargos duplicados en el extracto.
          </p>
        ) : (
          <div className="divide-y divide-[#EFECE5] rounded-3xl bg-white">
            {radar.cobros_duplicados.map((dup) => (
              <div
                key={dup.ids_transacciones.join("-")}
                className="flex flex-wrap items-center justify-between gap-4 px-6 py-5"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm font-bold text-[#1E252B]">{dup.comercio}</span>
                    <span className="rounded-full bg-[#FCE8EC] px-2.5 py-0.5 text-[11px] font-semibold text-[#8E263D]">
                      {dup.ids_transacciones.join(" + ")}
                    </span>
                  </div>
                  <p className="text-xs text-[#616B75]">{dup.explicacion}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-extrabold tabular-nums text-[#8E263D]">
                    S/ {dup.monto.toFixed(2)}
                  </p>
                  <p className="text-[11px] text-[#616B75]">{dup.fecha}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Sección 3: Suscripciones Recurrentes */}
      <section className="space-y-4">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#EAE7F8] text-[#4B3F8F]">
            <Repeat className="h-4 w-4" />
          </span>
          <div>
            <h2 className="text-base font-bold text-[#1E252B]">Suscripciones Recurrentes</h2>
            <p className="text-xs text-[#616B75]">
              Servicios digitales identificados (incluye conversión de USD/EUR a soles)
            </p>
          </div>
        </div>

        {radar.suscripciones_recurrentes.length === 0 ? (
          <p className="rounded-2xl bg-[#F3F1EB] px-5 py-4 text-sm text-[#616B75]">
            No se identificaron suscripciones recurrentes en este extracto.
          </p>
        ) : (
          <div className="divide-y divide-[#EFECE5] rounded-3xl bg-white">
            {radar.suscripciones_recurrentes.map((sub) => (
              <div
                key={sub.comercio}
                className="flex flex-wrap items-center justify-between gap-4 px-6 py-5"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm font-bold text-[#1E252B]">{sub.comercio}</span>
                    <span className="rounded-full bg-[#EAE7F8] px-2.5 py-0.5 text-[11px] font-semibold text-[#4B3F8F]">
                      {sub.frecuencia_detectada}
                    </span>
                  </div>
                  <p className="text-xs text-[#616B75]">{sub.explicacion}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-extrabold tabular-nums text-[#4B3F8F]">
                    S/ {sub.monto_mensual.toFixed(2)}
                  </p>
                  <p className="text-[11px] text-[#616B75]">por ciclo</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
