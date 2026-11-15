"use client";

import React, { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { FileSpreadsheet, FileText, MapPin, ShieldCheck, Sliders, UploadCloud } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { ModoControl } from "@/types/finguard";

const CIUDADES_SUGERIDAS = ["Ica", "Lima", "Trujillo", "Arequipa", "Cusco", "Piura"];

export function AuditForm() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const { auditarArchivo, auditarDemo, cargando, error, limpiarError } = useAudit();

  const [archivo, setArchivo] = useState<File | null>(null);
  const [arrastrando, setArrastrando] = useState(false);
  const [ciudadHabitual, setCiudadHabitual] = useState("Ica");
  const [modo, setModo] = useState<ModoControl>("normal");
  const [presupuestoMensual, setPresupuestoMensual] = useState("2500");

  const presupuestoNum = Math.max(Number(presupuestoMensual) || 2500, 100);

  const manejarSeleccion = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    limpiarError();
    setArchivo(fileList[0]);
  };

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!archivo) return;
    const ok = await auditarArchivo({
      archivo,
      ciudadHabitual: ciudadHabitual.trim() || "Ica",
      modo,
      presupuestoMensual: presupuestoNum,
    });
    if (ok) {
      router.push("/");
    }
  };

  const ejecutarDemo = async (formato: "csv" | "pdf") => {
    const ok = await auditarDemo({
      formato,
      ciudadHabitual: ciudadHabitual.trim() || "Ica",
      modo,
      presupuestoMensual: presupuestoNum,
    });
    if (ok) {
      router.push("/");
    }
  };

  return (
    <div className="space-y-8">
      {error && (
        <div className="rounded-2xl bg-[#FCE8EC] px-5 py-4 text-sm font-medium text-[#8E263D]">
          {error}
        </div>
      )}

      <form onSubmit={enviar} className="grid gap-10 lg:grid-cols-12">
        {/* Columna izquierda: zona de carga limpia */}
        <div className="lg:col-span-6 space-y-4">
          <div>
            <h2 className="text-base font-bold text-[#1E252B]">1. Selecciona tu extracto</h2>
            <p className="mt-1 text-xs text-[#616B75]">
              Acepta archivos .CSV o estados de cuenta bancarios en .PDF.
            </p>
          </div>

          <div
            onDragOver={(e) => {
              e.preventDefault();
              setArrastrando(true);
            }}
            onDragLeave={() => setArrastrando(false)}
            onDrop={(e) => {
              e.preventDefault();
              setArrastrando(false);
              manejarSeleccion(e.dataTransfer.files);
            }}
            onClick={() => inputRef.current?.click()}
            className={`flex min-h-[240px] cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed p-8 text-center transition ${
              arrastrando
                ? "border-[#2D6A5B] bg-[#E3F2EC]"
                : archivo
                ? "border-[#5B9A8B] bg-[#EEF7F3]"
                : "border-[#D7D2C8] bg-[#F3F1EB]/70 hover:border-[#9EB8AF] hover:bg-[#F3F1EB]"
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".csv,.pdf"
              className="hidden"
              onChange={(e) => manejarSeleccion(e.target.files)}
            />
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-[#2D6A5B]">
              <UploadCloud className="h-6 w-6" />
            </div>
            {archivo ? (
              <>
                <p className="text-sm font-bold text-[#1E252B]">{archivo.name}</p>
                <p className="mt-1 text-xs text-[#616B75]">
                  {(archivo.size / 1024).toFixed(1)} KB • Archivo listo para procesar
                </p>
              </>
            ) : (
              <>
                <p className="text-sm font-semibold text-[#1E252B]">
                  Arrastra tu archivo aquí o haz clic para explorar
                </p>
                <p className="mt-1 text-xs text-[#616B75]">
                  Procesamiento local sin contraseñas bancarias
                </p>
              </>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2.5 pt-1">
            <span className="text-xs font-medium text-[#616B75]">¿Quieres probar rápido?</span>
            <button
              type="button"
              disabled={cargando}
              onClick={() => ejecutarDemo("csv")}
              className="inline-flex items-center gap-1.5 rounded-xl bg-[#E3F1EC] px-3 py-1.5 text-xs font-semibold text-[#1E4F41] transition hover:bg-[#D5EAE2] disabled:opacity-50"
            >
              <FileSpreadsheet className="h-3.5 w-3.5" />
              Demo CSV
            </button>
            <button
              type="button"
              disabled={cargando}
              onClick={() => ejecutarDemo("pdf")}
              className="inline-flex items-center gap-1.5 rounded-xl bg-[#E6EFF8] px-3 py-1.5 text-xs font-semibold text-[#234F73] transition hover:bg-[#D8E7F5] disabled:opacity-50"
            >
              <FileText className="h-3.5 w-3.5" />
              Demo PDF
            </button>
          </div>
        </div>

        {/* Columna derecha: configuración del perfil */}
        <div className="lg:col-span-6 space-y-6">
          <div>
            <h2 className="text-base font-bold text-[#1E252B]">2. Parámetros del perfil</h2>
            <p className="mt-1 text-xs text-[#616B75]">
              SWI-Prolog y el pipeline funcional ajustan sus umbrales según estas preferencias.
            </p>
          </div>

          <div className="space-y-5 rounded-3xl bg-white p-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-[#545E68]">
                  <MapPin className="h-3.5 w-3.5 text-[#2D6A5B]" />
                  Ciudad Habitual
                </label>
                <input
                  type="text"
                  list="ciudades-peru"
                  value={ciudadHabitual}
                  onChange={(e) => setCiudadHabitual(e.target.value)}
                  placeholder="Ej. Ica"
                  className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
                />
                <datalist id="ciudades-peru">
                  {CIUDADES_SUGERIDAS.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              </div>

              <div>
                <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-[#545E68]">
                  <Sliders className="h-3.5 w-3.5 text-[#2D6A5B]" />
                  Presupuesto Mensual (S/)
                </label>
                <input
                  type="number"
                  min={100}
                  step={50}
                  value={presupuestoMensual}
                  onChange={(e) => setPresupuestoMensual(e.target.value)}
                  className="w-full rounded-xl border border-[#E2DDD3] bg-[#FAF9F6] px-3.5 py-2.5 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:bg-white focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold text-[#545E68]">
                Modo de Control
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setModo("normal")}
                  className={`rounded-2xl p-3.5 text-left transition ${
                    modo === "normal"
                      ? "bg-[#E6EFF8] text-[#1D4363] ring-1 ring-[#9DC0DF]"
                      : "bg-[#FAF9F6] text-[#545E68] hover:bg-[#F3F1EB]"
                  }`}
                >
                  <div className="text-xs font-bold">Normal</div>
                  <div className="mt-1 text-[11px] opacity-80">
                    Alertas de fraude crítico y Z-Score &ge; 2.0
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setModo("ahorro_estricto")}
                  className={`rounded-2xl p-3.5 text-left transition ${
                    modo === "ahorro_estricto"
                      ? "bg-[#DDF0E8] text-[#1E4F41] ring-1 ring-[#98CEB8]"
                      : "bg-[#FAF9F6] text-[#545E68] hover:bg-[#F3F1EB]"
                  }`}
                >
                  <div className="text-xs font-bold">Ahorro Estricto</div>
                  <div className="mt-1 text-[11px] opacity-80">
                    Control riguroso de gastos hormiga y Z &ge; 1.5
                  </div>
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={!archivo || cargando}
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#2D6A5B] px-4 py-3.5 text-sm font-bold text-white transition hover:bg-[#235448] disabled:cursor-not-allowed disabled:bg-[#D5D1C8] disabled:text-[#7D7A73]"
            >
              <ShieldCheck className="h-4 w-4" />
              {cargando ? "Auditando estado de cuenta..." : "Auditar Cuenta Ahora"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
