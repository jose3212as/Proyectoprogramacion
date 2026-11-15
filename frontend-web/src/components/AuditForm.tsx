"use client";

import React, { useRef, useState } from "react";
import { FileSpreadsheet, FileText, MapPin, ShieldCheck, Sliders, UploadCloud } from "lucide-react";
import { ModoControl } from "@/types/finguard";

interface AuditFormProps {
  cargando: boolean;
  onAuditarArchivo: (params: {
    archivo: File;
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => Promise<void>;
  onAuditarDemo: (params: {
    formato: "csv" | "pdf";
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => Promise<void>;
}

const CIUDADES_SUGERIDAS = ["Ica", "Lima", "Trujillo", "Arequipa", "Cusco", "Piura"];

export function AuditForm({ cargando, onAuditarArchivo, onAuditarDemo }: AuditFormProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [arrastrando, setArrastrando] = useState(false);
  const [ciudadHabitual, setCiudadHabitual] = useState("Ica");
  const [modo, setModo] = useState<ModoControl>("normal");
  const [presupuestoMensual, setPresupuestoMensual] = useState("2500");

  const manejarSeleccion = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setArchivo(fileList[0]);
  };

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!archivo) return;
    await onAuditarArchivo({
      archivo,
      ciudadHabitual: ciudadHabitual.trim() || "Ica",
      modo,
      presupuestoMensual: Math.max(Number(presupuestoMensual) || 2500, 100),
    });
  };

  const presupuestoNum = Math.max(Number(presupuestoMensual) || 2500, 100);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-slate-900">
            Paso 1 y 2 — Carga tu Estado de Cuenta y Configura tu Perfil
          </h2>
          <p className="text-sm text-slate-500">
            Privacidad garantizada: procesamos solo tu archivo CSV o PDF sin solicitar claves bancarias.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={cargando}
            onClick={() =>
              onAuditarDemo({
                formato: "csv",
                ciudadHabitual: ciudadHabitual.trim() || "Ica",
                modo,
                presupuestoMensual: presupuestoNum,
              })
            }
            className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:opacity-50"
          >
            <FileSpreadsheet className="h-3.5 w-3.5" />
            Probar Demo CSV
          </button>
          <button
            type="button"
            disabled={cargando}
            onClick={() =>
              onAuditarDemo({
                formato: "pdf",
                ciudadHabitual: ciudadHabitual.trim() || "Ica",
                modo,
                presupuestoMensual: presupuestoNum,
              })
            }
            className="inline-flex items-center gap-1.5 rounded-lg border border-sky-200 bg-sky-50 px-3 py-1.5 text-xs font-semibold text-sky-800 transition hover:bg-sky-100 disabled:opacity-50"
          >
            <FileText className="h-3.5 w-3.5" />
            Probar Demo PDF
          </button>
        </div>
      </div>

      <form onSubmit={enviar} className="grid gap-6 lg:grid-cols-12">
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
          className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 text-center transition lg:col-span-5 ${
            arrastrando
              ? "border-teal-500 bg-teal-50"
              : archivo
              ? "border-emerald-400 bg-emerald-50/50"
              : "border-slate-300 bg-slate-50 hover:border-slate-400"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.pdf"
            className="hidden"
            onChange={(e) => manejarSeleccion(e.target.files)}
          />
          <UploadCloud className="mb-2 h-9 w-9 text-teal-600" />
          {archivo ? (
            <>
              <p className="text-sm font-semibold text-slate-900">{archivo.name}</p>
              <p className="mt-1 text-xs text-slate-500">
                {(archivo.size / 1024).toFixed(1)} KB — Listo para auditar
              </p>
            </>
          ) : (
            <>
              <p className="text-sm font-semibold text-slate-700">
                Arrastra tu estado de cuenta aquí o haz clic
              </p>
              <p className="mt-1 text-xs text-slate-500">Formatos soportados: .CSV y .PDF</p>
            </>
          )}
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:col-span-7">
          <div>
            <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-600">
              <MapPin className="h-3.5 w-3.5 text-teal-600" />
              Ciudad Habitual
            </label>
            <input
              type="text"
              list="ciudades-peru"
              value={ciudadHabitual}
              onChange={(e) => setCiudadHabitual(e.target.value)}
              placeholder="Ej. Ica"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-teal-500 focus:outline-none"
            />
            <datalist id="ciudades-peru">
              {CIUDADES_SUGERIDAS.map((c) => (
                <option key={c} value={c} />
              ))}
            </datalist>
          </div>

          <div>
            <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-600">
              <Sliders className="h-3.5 w-3.5 text-teal-600" />
              Presupuesto Mensual (S/)
            </label>
            <input
              type="number"
              min={100}
              step={50}
              value={presupuestoMensual}
              onChange={(e) => setPresupuestoMensual(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-teal-500 focus:outline-none"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-600">
              Modo de Control (Orden Superior)
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={() => setModo("normal")}
                className={`rounded-lg border px-3 py-2 text-left text-xs transition ${
                  modo === "normal"
                    ? "border-slate-900 bg-slate-900 text-white"
                    : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
                }`}
              >
                <div className="font-bold">Normal</div>
                <div className={modo === "normal" ? "text-slate-300" : "text-slate-500"}>
                  Prioriza fraude crítico y Z-Score &ge; 2.0
                </div>
              </button>
              <button
                type="button"
                onClick={() => setModo("ahorro_estricto")}
                className={`rounded-lg border px-3 py-2 text-left text-xs transition ${
                  modo === "ahorro_estricto"
                    ? "border-teal-700 bg-teal-700 text-white"
                    : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
                }`}
              >
                <div className="font-bold">Ahorro Estricto</div>
                <div className={modo === "ahorro_estricto" ? "text-teal-100" : "text-slate-500"}>
                  Control riguroso de gastos hormiga y Z &ge; 1.5
                </div>
              </button>
            </div>
          </div>

          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={!archivo || cargando}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-teal-600 px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              <ShieldCheck className="h-4 w-4" />
              {cargando ? "Ejecutando motor híbrido..." : "Auditar Cuenta"}
            </button>
          </div>
        </div>
      </form>
    </section>
  );
}
