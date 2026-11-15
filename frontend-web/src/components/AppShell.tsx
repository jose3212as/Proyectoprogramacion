"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookmarkCheck,
  Clock,
  Download,
  FilePlus2,
  LayoutDashboard,
  ListOrdered,
  LogIn,
  Menu,
  Shield,
  ShieldAlert,
  TrendingDown,
  UserCircle2,
  X,
} from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { urlReportePdf } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/", label: "Resumen", icon: LayoutDashboard },
  { href: "/auditar", label: "Revisar cuenta", icon: FilePlus2 },
  { href: "/fugas", label: "Gastos invisibles", icon: TrendingDown },
  { href: "/seguridad", label: "Seguridad", icon: ShieldAlert },
  { href: "/movimientos", label: "Mis compras", icon: ListOrdered },
  { href: "/historial", label: "Mi historial", icon: Clock },
  { href: "/cuenta", label: "Mi cuenta", icon: UserCircle2 },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [menuMovil, setMenuMovil] = useState(false);
  const { auditoria, usuario, guardarRevisionActual, cargando } = useAudit();

  const alertasActivas = auditoria?.escudo_antifraude.alertas_activas ?? 0;

  return (
    <div className="flex min-h-screen bg-[#FAF9F6] text-[#1E252B]">
      {menuMovil && (
        <div
          className="fixed inset-0 z-30 bg-black/20 lg:hidden"
          onClick={() => setMenuMovil(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-[#E7E3DA] bg-[#F3F1EB] transition-transform duration-200 lg:static lg:translate-x-0 ${
          menuMovil ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-6 py-6">
          <Link href="/" className="flex items-center gap-3" onClick={() => setMenuMovil(false)}>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#DDF0E8] text-[#225B4B]">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <span className="block text-base font-bold tracking-tight text-[#1E252B]">
                FinGuard
              </span>
              <span className="block text-[11px] font-medium text-[#6C757D]">
                Tu aliado financiero
              </span>
            </div>
          </Link>
          <button
            type="button"
            onClick={() => setMenuMovil(false)}
            className="rounded-lg p-1 text-[#6C757D] lg:hidden"
            aria-label="Cerrar menú"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map((item) => {
            const activo = pathname === item.href;
            const Icon = item.icon;
            const mostrarBadge = item.href === "/seguridad" && alertasActivas > 0;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuMovil(false)}
                className={`flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-colors ${
                  activo
                    ? "bg-[#DDF0E8] font-semibold text-[#1E4F41]"
                    : "text-[#545E68] hover:bg-[#EAE7DF] hover:text-[#1E252B]"
                }`}
              >
                <span className="flex items-center gap-3">
                  <Icon className="h-4 w-4 shrink-0" />
                  {item.label}
                </span>
                {mostrarBadge && (
                  <span className="rounded-full bg-[#F8D7DE] px-2 py-0.5 text-[11px] font-bold text-[#8E263D]">
                    {alertasActivas}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-[#E7E3DA] p-4 space-y-3">
          {auditoria && (
            <div className="rounded-xl bg-[#FAF9F6] p-3 text-xs space-y-2">
              <div>
                <p className="font-semibold text-[#1E252B] truncate">{auditoria.archivo}</p>
                <p className="mt-0.5 text-[#616B75]">
                  {auditoria.perfil.ciudad_habitual} •{" "}
                  {auditoria.perfil.modo === "ahorro_estricto" ? "Modo ahorro" : "Modo tranquilo"}
                </p>
              </div>
              {auditoria.audit_id !== "demo-offline-001" && (
                <div className="flex flex-col gap-1.5">
                  <a
                    href={urlReportePdf(auditoria.audit_id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-[#2D6A5B] px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-[#235448]"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Descargar resumen PDF
                  </a>
                  {usuario && (
                    <button
                      type="button"
                      disabled={cargando}
                      onClick={guardarRevisionActual}
                      className="inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-[#E3F1EC] px-3 py-1.5 text-xs font-semibold text-[#1E4F41] transition hover:bg-[#D5EAE2] disabled:opacity-50"
                    >
                      <BookmarkCheck className="h-3.5 w-3.5" />
                      Guardar en mi historial
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {usuario ? (
            <Link
              href="/cuenta"
              onClick={() => setMenuMovil(false)}
              className="flex items-center gap-2.5 rounded-xl bg-[#EAE7DF] px-3 py-2 text-xs transition hover:bg-[#E1DDD3]"
            >
              <UserCircle2 className="h-4 w-4 shrink-0 text-[#2D6A5B]" />
              <div className="min-w-0">
                <p className="font-semibold text-[#1E252B] truncate">{usuario.nombre}</p>
                <p className="text-[11px] text-[#616B75] truncate">Historial activado</p>
              </div>
            </Link>
          ) : (
            <Link
              href="/cuenta"
              onClick={() => setMenuMovil(false)}
              className="flex items-center justify-center gap-2 rounded-xl bg-[#E6EFF8] px-3 py-2 text-xs font-semibold text-[#234F73] transition hover:bg-[#D8E7F5]"
            >
              <LogIn className="h-3.5 w-3.5" />
              Iniciar sesión para guardar
            </Link>
          )}
        </div>
      </aside>

      <div className="flex flex-1 flex-col min-w-0">
        <header className="flex items-center justify-between border-b border-[#E7E3DA] bg-[#FAF9F6]/90 px-5 py-3.5 backdrop-blur lg:px-10">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMenuMovil(true)}
              className="rounded-lg border border-[#E7E3DA] bg-white p-2 text-[#1E252B] lg:hidden"
              aria-label="Abrir navegación"
            >
              <Menu className="h-4 w-4" />
            </button>
            <p className="text-xs font-medium text-[#616B75]">
              Tus datos son privados: nunca te pedimos claves de tu banco
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            {!usuario && (
              <Link
                href="/cuenta"
                className="hidden rounded-lg bg-[#F3F1EB] px-3 py-1.5 text-xs font-semibold text-[#464F59] transition hover:bg-[#E7E3DA] sm:inline-block"
              >
                Iniciar sesión
              </Link>
            )}
            <Link
              href="/auditar"
              className="rounded-lg bg-[#2D6A5B] px-3.5 py-1.5 text-xs font-semibold text-white transition hover:bg-[#235448]"
            >
              + Revisar archivo
            </Link>
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-8 lg:px-10">{children}</main>
      </div>
    </div>
  );
}
