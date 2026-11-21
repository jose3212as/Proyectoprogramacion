"use client";

import React, { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, Download, ShieldCheck } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { EmptyAuditState } from "@/components/EmptyAuditState";
import { urlReportePdf } from "@/lib/api";

const ESTILO_RIESGO: Record<string, { clase: string; texto: string }> = {
  critico: { clase: "bg-[#FCE8EC] text-[#8E263D]", texto: "Atención urgente" },
  alto: { clase: "bg-[#FDEEE4] text-[#9A4D23]", texto: "Revisar pronto" },
  medio: { clase: "bg-[#FDF6DF] text-[#856414]", texto: "Precaución" },
  bajo: { clase: "bg-[#DDF0E8] text-[#1E4F41]", texto: "Todo tranquilo" },
};

const ETIQUETA_MOTIVO: Record<string, string> = {
  "viaje_imposible/8": "Dos ciudades en poco tiempo",
  "compra_nocturna_atipica/6": "Compra de madrugada",
  "cobro_duplicado_regla/6": "Cobro repetido",
  "monto_anomalo_zscore/5": "Monto muy alto para tu perfil",
  "presencial_fuera_ciudad/4": "Compra en otra ciudad",
};

const TEXTO_SEVERIDAD: Record<string, string> = {
  critica: "Importante",
  alta: "Revisar",
  media: "Aviso",
  baja: "Informativo",
};

export default function SeguridadPage() {
  const { auditoria, actualizandoAlertaId, toggleFuiYo, error } = useAudit();
  const [filtro, setFiltro] = useState<"todas" | "activas" | "verificadas">("todas");
  const [detalleAbierto, setDetalleAbierto] = useState<string | null>(null);

  if (!auditoria) {
    return (
      <EmptyAuditState
        titulo="Cuidado de tu tarjeta"
        descripcion="Revisamos horarios, ciudades y montos de tus compras para avisarte de inmediato si aparece algún movimiento que no parezca tuyo."
      />
    );
  }

  const { escudo_antifraude: escudo } = auditoria;
  const badgeRiesgo = ESTILO_RIESGO[escudo.nivel_riesgo_general] ?? ESTILO_RIESGO.bajo;

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
            Cuidado de tu tarjeta
          </span>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
            ¿Tu tarjeta está segura?
          </h1>
          <p className="mt-1 text-sm text-[#616B75]">
            Si reconoces alguna de estas compras, solo presiona <strong>&quot;Sí, fui yo&quot;</strong>{" "}
            para quitar el aviso.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span className={`rounded-full px-4 py-1.5 text-xs font-bold ${badgeRiesgo.clase}`}>
            {badgeRiesgo.texto}
          </span>
          <a
            href={urlReportePdf(auditoria.audit_id)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-xl bg-[#2D6A5B] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#235448]"
          >
            <Download className="h-3.5 w-3.5" />
            Descargar PDF para reclamo
          </a>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl bg-[#FCE8EC] px-5 py-3 text-sm font-medium text-[#8E263D]">
          {error}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-xl bg-[#F3F1EB] p-1">
          {[
            { id: "todas", label: `Todos (${escudo.total_alertas})` },
            { id: "activas", label: `Por revisar (${escudo.alertas_activas})` },
            {
              id: "verificadas",
              label: `Confirmados por ti (${escudo.total_alertas - escudo.alertas_activas})`,
            },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setFiltro(tab.id as "todas" | "activas" | "verificadas")}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
                filtro === tab.id
                  ? "bg-white text-[#1E252B]"
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
          No hay avisos pendientes en esta lista. Todo luce normal en tu cuenta.
        </div>
      ) : (
        <div className="space-y-4">
          {alertasFiltradas.map((alerta) => {
            const abierta = detalleAbierto === alerta.alerta_id;
            const ocupada = actualizandoAlertaId === alerta.alerta_id;
            const motivo = ETIQUETA_MOTIVO[alerta.regla_activada] ?? "Movimiento inusual";

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
                        className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                          alerta.verificada_fui_yo
                            ? "bg-[#DDF0E8] text-[#1E4F41]"
                            : "bg-[#FCE8EC] text-[#8E263D]"
                        }`}
                      >
                        {alerta.verificada_fui_yo
                          ? "Confirmado por ti"
                          : TEXTO_SEVERIDAD[alerta.severidad] ?? "Aviso"}
                      </span>
                      <span className="rounded-full bg-[#F3F1EB] px-2.5 py-0.5 text-[11px] font-medium text-[#545E68]">
                        {motivo}
                      </span>
                    </div>
                    <h2 className="text-base font-bold text-[#1E252B]">{alerta.titulo}</h2>
                  </div>

                  <div className="text-right">
                    <p className="text-xl font-extrabold tabular-nums text-[#1E252B]">
                      S/ {alerta.monto_pen.toFixed(2)}
                    </p>
                    <p className="text-xs text-[#616B75]">
                      {alerta.fecha} • {alerta.hora} • {alerta.ciudad} (
                      {alerta.canal === "online" ? "Por internet" : "En tienda"})
                    </p>
                  </div>
                </div>

                <p className="mt-3 text-sm leading-relaxed text-[#464F59]">{alerta.explicacion}</p>

                <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-[#EFECE5] pt-4">
                  <button
                    type="button"
                    onClick={() => setDetalleAbierto(abierta ? null : alerta.alerta_id)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#2D6A5B] hover:text-[#1E4F41]"
                  >
                    {abierta ? (
                      <ChevronUp className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                    {abierta ? "Ocultar detalles" : "¿Por qué te avisamos esto?"}
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
                      ? "Volver a marcar para revisar"
                      : "Sí, fui yo"}
                  </button>
                </div>

                {abierta && (
                  <div className="mt-4 rounded-2xl bg-[#FAF9F6] p-4 text-xs text-[#464F59] space-y-1.5">
                    <p className="font-semibold text-[#1E252B]">Resumen de la comprobación:</p>
                    <p>• Establecimiento: {alerta.comercio}</p>
                    <p>
                      • Ubicación y hora: {alerta.ciudad} a las {alerta.hora} ({alerta.fecha})
                    </p>
                    <p>
                      • Modalidad:{" "}
                      {alerta.canal === "online"
                        ? "Compra por internet"
                        : "Compra presencial con tarjeta"}
                    </p>
                    <p>• Motivo principal: {motivo}</p>
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
