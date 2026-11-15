"use client";

import React from "react";
import { AuditForm } from "@/components/AuditForm";

export default function AuditarPage() {
  return (
    <div className="space-y-8">
      <div className="border-b border-[#E7E3DA] pb-6">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
          Revisión mensual
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
          Revisa tu estado de cuenta
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-[#616B75]">
          Sube el archivo de tu banco en PDF o CSV para ordenar tus gastos, detectar cobros
          repetidos y cuidar tu tarjeta.
        </p>
      </div>

      <AuditForm />
    </div>
  );
}
