"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Cpu, Download } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { urlReportePdf } from "@/lib/api";

export default function HistorialPage() {
  const router = useRouter();
  const { historial, auditoria, cargarDesdeHistorial, backendOnline } = useAudit();

  const abrirAuditoria = async (auditId: string) => {
    const ok = await cargarDesdeHistorial(auditId);
    if (ok) {
      router.push("/");
    }
  };

  return (
    <div className="space-y-10">
      <div className="border-b border-[#E7E3DA] pb-6">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
          SQLite Local y Arquitectura
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
          Historial y Paradigmas del Motor
        </h1>
        <p className="mt-1 text-sm text-[#616B75]">
          Consulta auditorías anteriores almacenadas en SQLite y revisa cómo intervienen los tres
          paradigmas del curso.
        </p>
      </div>

      {/* Historial de auditorías */}
      <section className="space-y-4">
        <h2 className="text-base font-bold text-[#1E252B]">Auditorías Guardadas</h2>

        {!backendOnline ? (
          <p className="rounded-2xl bg-[#FDEEE4] px-5 py-4 text-sm text-[#9A4D23]">
            El backend FastAPI no está conectado en este momento; el historial persistente requiere
            el servidor en <code>http://127.0.0.1:8000</code>.
          </p>
        ) : historial.length === 0 ? (
          <p className="rounded-2xl bg-[#F3F1EB] px-5 py-4 text-sm text-[#616B75]">
            Aún no hay auditorías guardadas. Ejecuta una en <strong>Nueva Auditoría</strong>.
          </p>
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
                    {h.ciudad_habitual} • {h.modo} • Gasto total: S/ {h.gasto_total.toFixed(2)} •{" "}
                    {h.alertas_activas} alertas activas
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
                    PDF
                  </a>
                  <button
                    type="button"
                    onClick={() => abrirAuditoria(h.audit_id)}
                    className="inline-flex items-center gap-1 rounded-xl bg-[#2D6A5B] px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-[#235448]"
                  >
                    Cargar
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Desglose académico de paradigmas en tonos pastel */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-[#2D6A5B]" />
          <h2 className="text-base font-bold text-[#1E252B]">
            Integración de los 3 Paradigmas (Curso Lenguajes de Programación)
          </h2>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-3xl bg-[#DDF0E8] p-6">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#1E4F41]">
              Unidad 1
            </span>
            <h3 className="mt-1 text-base font-bold text-[#14392F]">Programación Funcional</h3>
            <p className="mt-2 text-xs leading-relaxed text-[#255447]">
              {auditoria?.metadatos_motor.paradigmas.funcional ??
                "Registros inmutables (frozen dataclasses), funciones puras de conversión de divisas, map/filter/reduce con lambdas y orden superior por modo."}
            </p>
          </div>

          <div className="rounded-3xl bg-[#EAE7F8] p-6">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#4B3F8F]">
              Unidad 2
            </span>
            <h3 className="mt-1 text-base font-bold text-[#2F275E]">Programación Lógica</h3>
            <p className="mt-2 text-xs leading-relaxed text-[#43397A]">
              {auditoria?.metadatos_motor.paradigmas.logico ??
                "Base de hechos transaccion/7 en SWI-Prolog con unificación, resolución y backtracking para deducir fraudes explicables."}
            </p>
          </div>

          <div className="rounded-3xl bg-[#E6EFF8] p-6">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#234F73]">
              Unidad 3
            </span>
            <h3 className="mt-1 text-base font-bold text-[#193A55]">
              Multiparadigma y Ciencia de Datos
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-[#2B5374]">
              {auditoria?.metadatos_motor.paradigmas.multiparadigma_datos ??
                "Ingesta polimórfica POO (LectorPDF con pdfplumber y LectorCSV) + agrupaciones Pandas y Z-Score con NumPy."}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
