"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Download, LogIn } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { urlReportePdf } from "@/lib/api";

export default function HistorialPage() {
  const router = useRouter();
  const { historial, usuario, cargarDesdeHistorial } = useAudit();

  const abrirRevision = async (auditId: string) => {
    const ok = await cargarDesdeHistorial(auditId);
    if (ok) {
      router.push("/");
    }
  };

  return (
    <div className="space-y-8">
      <div className="border-b border-[#E7E3DA] pb-6">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
          Revisiones guardadas
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">Mi historial</h1>
        <p className="mt-1 text-sm text-[#616B75]">
          Aquí aparecen los estados de cuenta que guardaste en tu perfil para volver a consultarlos.
        </p>
      </div>

      {!usuario ? (
        <div className="mx-auto max-w-xl rounded-3xl bg-[#F3F1EB] p-8">
          <h2 className="text-lg font-bold text-[#1E252B]">
            Inicia sesión para guardar tu historial
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-[#616B75]">
            Puedes revisar tus archivos sin cuenta cuando quieras, pero si deseas guardar tus meses
            anteriores en un solo lugar, inicia sesión o crea tu perfil personal.
          </p>
          <Link
            href="/cuenta"
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-[#2D6A5B] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#235448]"
          >
            <LogIn className="h-4 w-4" />
            Ir a Mi cuenta
          </Link>
        </div>
      ) : historial.length === 0 ? (
        <div className="rounded-3xl bg-white p-8 text-center">
          <p className="text-sm text-[#616B75]">
            Todavía no tienes revisiones guardadas en tu cuenta, <strong>{usuario.nombre}</strong>.
          </p>
          <Link
            href="/auditar"
            className="mt-4 inline-flex items-center gap-2 rounded-xl bg-[#2D6A5B] px-4 py-2 text-xs font-semibold text-white hover:bg-[#235448]"
          >
            Revisar mi primer archivo
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      ) : (
        <div className="divide-y divide-[#EFECE5] rounded-3xl bg-white">
          {historial.map((h) => (
            <div
              key={h.audit_id}
              className="flex flex-wrap items-center justify-between gap-4 px-6 py-4"
            >
              <div>
                <div className="flex items-center gap-2.5">
                  <span className="text-sm font-bold text-[#1E252B]">{h.archivo}</span>
                  <span className="rounded-full bg-[#E6EFF8] px-2 py-0.5 text-[10px] font-bold uppercase text-[#234F73]">
                    {h.formato}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-[#616B75]">
                  {h.ciudad_habitual} •{" "}
                  {h.modo === "ahorro_estricto" ? "Modo ahorro" : "Modo tranquilo"} • Total: S/{" "}
                  {h.gasto_total.toFixed(2)} •{" "}
                  {h.alertas_activas === 0 ? "Sin avisos" : `${h.alertas_activas} avisos`}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href={urlReportePdf(h.audit_id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 rounded-xl bg-[#F3F1EB] px-3 py-1.5 text-xs font-semibold text-[#464F59] hover:bg-[#E7E3DA]"
                >
                  <Download className="h-3.5 w-3.5" />
                  Resumen PDF
                </a>
                <button
                  type="button"
                  onClick={() => abrirRevision(h.audit_id)}
                  className="inline-flex items-center gap-1 rounded-xl bg-[#2D6A5B] px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-[#235448]"
                >
                  Abrir
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
