"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { BookmarkCheck, CheckCircle2, LogOut, UserCircle2 } from "lucide-react";
import { useAudit } from "@/context/AuditContext";

export default function CuentaPage() {
  const router = useRouter();
  const {
    usuario,
    auditoria,
    cargando,
    error,
    aviso,
    limpiarError,
    limpiarAviso,
    iniciarSesion,
    registrarCuenta,
    cerrarSesion,
    guardarRevisionActual,
  } = useAudit();

  const [pestana, setPestana] = useState<"login" | "registro">("login");
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [ciudad, setCiudad] = useState("Ica");
  const [presupuesto, setPresupuesto] = useState("2500");

  const manejarLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    limpiarError();
    limpiarAviso();
    const ok = await iniciarSesion({ correo, password });
    if (ok) {
      router.push("/historial");
    }
  };

  const manejarRegistro = async (e: React.FormEvent) => {
    e.preventDefault();
    limpiarError();
    limpiarAviso();
    const ok = await registrarCuenta({
      nombre,
      correo,
      password,
      ciudadHabitual: ciudad.trim() || "Ica",
      presupuestoMensual: Math.max(Number(presupuesto) || 2500, 100),
    });
    if (ok) {
      router.push("/historial");
    }
  };

  if (usuario) {
    return (
      <div className="mx-auto max-w-xl space-y-6">
        <div className="border-b border-[#E7E3DA] pb-5">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
            Tu espacio personal
          </span>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
            Hola, {usuario.nombre}
          </h1>
          <p className="mt-1 text-sm text-[#616B75]">
            Tus revisiones y preferencias se guardan automáticamente en tu cuenta.
          </p>
        </div>

        {aviso && (
          <div className="flex items-center gap-2 rounded-2xl bg-[#DDF0E8] px-4 py-3 text-sm font-medium text-[#1E4F41]">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            {aviso}
          </div>
        )}

        <div className="rounded-3xl bg-white p-6 space-y-5">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#DDF0E8] text-[#1E4F41]">
              <UserCircle2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-base font-bold text-[#1E252B]">{usuario.nombre}</p>
              <p className="text-xs text-[#616B75]">{usuario.correo}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 rounded-2xl bg-[#FAF9F6] p-4 text-xs">
            <div>
              <p className="text-[#616B75]">Ciudad habitual</p>
              <p className="mt-1 font-bold text-[#1E252B]">{usuario.ciudad_habitual}</p>
            </div>
            <div>
              <p className="text-[#616B75]">Meta mensual</p>
              <p className="mt-1 font-bold text-[#1E252B]">
                S/ {usuario.presupuesto_mensual.toLocaleString("es-PE")}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 pt-1">
            {auditoria && auditoria.audit_id !== "demo-offline-001" && (
              <button
                type="button"
                disabled={cargando}
                onClick={guardarRevisionActual}
                className="inline-flex items-center gap-2 rounded-xl bg-[#2D6A5B] px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-[#235448] disabled:opacity-50"
              >
                <BookmarkCheck className="h-4 w-4" />
                Guardar revisión actual
              </button>
            )}

            <button
              type="button"
              onClick={cerrarSesion}
              className="inline-flex items-center gap-2 rounded-xl bg-[#F3F1EB] px-4 py-2.5 text-xs font-semibold text-[#545E68] transition hover:bg-[#E7E3DA]"
            >
              <LogOut className="h-4 w-4" />
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div className="border-b border-[#E7E3DA] pb-5">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#2D6A5B]">
          Guarda tus revisiones
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">Tu cuenta</h1>
        <p className="mt-1 text-sm text-[#616B75]">
          Inicia sesión o crea tu perfil personal si deseas guardar tu historial para consultarlo
          cuando quieras.
        </p>
      </div>

      <div className="inline-flex rounded-xl bg-[#F3F1EB] p-1">
        <button
          type="button"
          onClick={() => {
            limpiarError();
            setPestana("login");
          }}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            pestana === "login"
              ? "bg-white text-[#1E252B]"
              : "text-[#616B75] hover:text-[#1E252B]"
          }`}
        >
          Ya tengo cuenta
        </button>
        <button
          type="button"
          onClick={() => {
            limpiarError();
            setPestana("registro");
          }}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            pestana === "registro"
              ? "bg-white text-[#1E252B]"
              : "text-[#616B75] hover:text-[#1E252B]"
          }`}
        >
          Crear mi cuenta
        </button>
      </div>

      {error && (
        <div className="rounded-2xl bg-[#FCE8EC] px-4 py-3 text-sm font-medium text-[#8E263D]">
          {error}
        </div>
      )}

      {aviso && (
        <div className="rounded-2xl bg-[#DDF0E8] px-4 py-3 text-sm font-medium text-[#1E4F41]">
          {aviso}
        </div>
      )}

      {pestana === "login" ? (
        <form onSubmit={manejarLogin} className="space-y-4 rounded-3xl bg-white p-6">
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">Tu correo</label>
            <input
              type="email"
              required
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              placeholder="ejemplo@correo.com"
              className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">
              Tu contraseña
            </label>
            <input
              type="password"
              required
              minLength={4}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••"
              className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={cargando}
            className="w-full rounded-2xl bg-[#2D6A5B] py-3 text-sm font-bold text-white transition hover:bg-[#235448] disabled:opacity-50"
          >
            {cargando ? "Entrando..." : "Iniciar sesión"}
          </button>
        </form>
      ) : (
        <form onSubmit={manejarRegistro} className="space-y-4 rounded-3xl bg-white p-6">
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">Tu nombre</label>
            <input
              type="text"
              required
              minLength={2}
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Ej. Carlos"
              className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">Tu correo</label>
            <input
              type="email"
              required
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              placeholder="ejemplo@correo.com"
              className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">
              Elige una contraseña (mín. 4 caracteres)
            </label>
            <input
              type="password"
              required
              minLength={4}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••"
              className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">
                Ciudad habitual
              </label>
              <input
                type="text"
                value={ciudad}
                onChange={(e) => setCiudad(e.target.value)}
                className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-semibold text-[#545E68]">
                Meta mensual (S/)
              </label>
              <input
                type="number"
                min={100}
                step={50}
                value={presupuesto}
                onChange={(e) => setPresupuesto(e.target.value)}
                className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={cargando}
            className="w-full rounded-2xl bg-[#2D6A5B] py-3 text-sm font-bold text-white transition hover:bg-[#235448] disabled:opacity-50"
          >
            {cargando ? "Creando tu cuenta..." : "Crear mi cuenta y guardar"}
          </button>
        </form>
      )}
    </div>
  );
}
