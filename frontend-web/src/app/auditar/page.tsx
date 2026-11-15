"use client";

import React from "react";
import { AuditForm } from "@/components/AuditForm";

export default function AuditarPage() {
  return (
    <div className="space-y-8">
      <div className="border-b border-[#E7E3DA] pb-6">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
          Paso 1 y 2 • Ingesta y Perfil
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
          Nueva Auditoría de Cuenta
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-[#616B75]">
          Sube tu estado de cuenta mensual en CSV o PDF y define tu ciudad habitual y nivel de
          control para ejecutar el motor híbrido.
        </p>
      </div>

      <AuditForm />
    </div>
  );
}
