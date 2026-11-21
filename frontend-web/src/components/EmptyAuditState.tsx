"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  Clock,
  FileText,
  Lock,
  LogIn,
  ShieldCheck,
  SlidersHorizontal,
  UploadCloud,
} from "lucide-react";
import { useAudit } from "@/context/AuditContext";

interface EmptyAuditStateProps {
  titulo: string;
  descripcion: string;
}

const PASOS = [
  {
    numero: "1",
    titulo: "Exporta tu extracto",
    texto: "Descarga tu estado de cuenta mensual en PDF o CSV desde la web o app de tu banco.",
    icon: FileText,
    color: "bg-[#E3F1EC] text-[#1E4F41]",
  },
  {
    numero: "2",
    titulo: "Define tu perfil",
    texto: "Indica tu ciudad habitual y meta mensual para adaptar las alertas a tu rutina.",
    icon: SlidersHorizontal,
    color: "bg-[#E6EFF8] text-[#234F73]",
  },
  {
    numero: "3",
    titulo: "Recibe tu análisis",
    texto: "Detecta gastos hormiga, cobros duplicados y cargos sospechosos en segundos.",
    icon: ShieldCheck,
    color: "bg-[#EAE7F8] text-[#4B3F8F]",
  },
];

export function EmptyAuditState({ titulo, descripcion }: EmptyAuditStateProps) {
  const { usuario } = useAudit();

  return (
    <div className="mx-auto max-w-4xl space-y-6 py-8">
      <div className="rounded-3xl border border-[#E7E3DA] bg-white p-8 sm:p-10">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-[#DDF0E8] px-3 py-1 text-xs font-semibold text-[#1E4F41]">
          <Lock className="h-3.5 w-3.5" />
          Privacidad garantizada • Sin claves bancarias
        </span>

        <h1 className="mt-4 text-3xl font-bold tracking-tight text-[#1E252B]">{titulo}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[#616B75]">{descripcion}</p>

        <div className="mt-7 flex flex-wrap items-center gap-3">
          <Link
            href="/auditar"
            className="inline-flex items-center gap-2 rounded-xl bg-[#2D6A5B] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#235448]"
          >
            <UploadCloud className="h-4 w-4" />
            Subir estado de cuenta
            <ArrowRight className="h-4 w-4" />
          </Link>

          {usuario ? (
            <Link
              href="/historial"
              className="inline-flex items-center gap-2 rounded-xl bg-[#F3F1EB] px-4 py-2.5 text-sm font-semibold text-[#464F59] transition hover:bg-[#E7E3DA]"
            >
              <Clock className="h-4 w-4" />
              Ver mi historial
            </Link>
          ) : (
            <Link
              href="/cuenta"
              className="inline-flex items-center gap-2 rounded-xl bg-[#F3F1EB] px-4 py-2.5 text-sm font-semibold text-[#464F59] transition hover:bg-[#E7E3DA]"
            >
              <LogIn className="h-4 w-4" />
              Iniciar sesión
            </Link>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {PASOS.map((paso) => {
          const Icon = paso.icon;
          return (
            <div
              key={paso.numero}
              className="rounded-2xl border border-[#E7E3DA]/80 bg-[#F3F1EB]/70 p-5"
            >
              <div
                className={`flex h-9 w-9 items-center justify-center rounded-xl ${paso.color}`}
              >
                <Icon className="h-4 w-4" />
              </div>
              <h2 className="mt-3.5 text-sm font-bold text-[#1E252B]">
                {paso.numero}. {paso.titulo}
              </h2>
              <p className="mt-1 text-xs leading-relaxed text-[#616B75]">{paso.texto}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
