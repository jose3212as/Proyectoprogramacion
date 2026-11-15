"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, FileSpreadsheet, FileText } from "lucide-react";
import { useAudit } from "@/context/AuditContext";

interface EmptyAuditStateProps {
  titulo: string;
  descripcion: string;
}

export function EmptyAuditState({ titulo, descripcion }: EmptyAuditStateProps) {
  const router = useRouter();
  const { auditarDemo, cargando, usuario } = useAudit();

  const probarDemo = async (formato: "csv" | "pdf") => {
    const ok = await auditarDemo({
      formato,
      ciudadHabitual: usuario?.ciudad_habitual ?? "Ica",
      modo: "normal",
      presupuestoMensual: usuario?.presupuesto_mensual ?? 2500,
    });
    if (ok) {
      router.refresh();
    }
  };

  return (
    <div className="mx-auto max-w-2xl py-12">
      <div className="rounded-3xl bg-[#F3F1EB] p-8 sm:p-10">
        <span className="inline-block rounded-full bg-[#DDF0E8] px-3 py-1 text-xs font-semibold text-[#1E4F41]">
          Aún no subes tu estado de cuenta
        </span>
        <h1 className="mt-4 text-2xl font-bold tracking-tight text-[#1E252B]">{titulo}</h1>
        <p className="mt-2 text-sm leading-relaxed text-[#616B75]">{descripcion}</p>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Link
            href="/auditar"
            className="inline-flex items-center gap-2 rounded-xl bg-[#2D6A5B] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#235448]"
          >
            Subir mi archivo
            <ArrowRight className="h-4 w-4" />
          </Link>

          <button
            type="button"
            disabled={cargando}
            onClick={() => probarDemo("csv")}
            className="inline-flex items-center gap-2 rounded-xl bg-[#E3F1EC] px-4 py-2.5 text-sm font-semibold text-[#1E4F41] transition hover:bg-[#D5EAE2] disabled:opacity-50"
          >
            <FileSpreadsheet className="h-4 w-4" />
            Probar con ejemplo CSV
          </button>

          <button
            type="button"
            disabled={cargando}
            onClick={() => probarDemo("pdf")}
            className="inline-flex items-center gap-2 rounded-xl bg-[#E6EFF8] px-4 py-2.5 text-sm font-semibold text-[#234F73] transition hover:bg-[#D8E7F5] disabled:opacity-50"
          >
            <FileText className="h-4 w-4" />
            Probar con ejemplo PDF
          </button>
        </div>
      </div>
    </div>
  );
}
