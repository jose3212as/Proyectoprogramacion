"use client";

import React, { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { useAudit } from "@/context/AuditContext";
import { EmptyAuditState } from "@/components/EmptyAuditState";

const ETIQUETA_AMIGABLE: Record<string, string> = {
  regular: "Normal",
  gasto_hormiga: "Gasto pequeño",
  atencion_seguridad: "Revisar horario",
  suscripcion_revisar: "Suscripción",
  recorte_sugerido: "Gasto alto",
};

export default function MovimientosPage() {
  const { auditoria } = useAudit();
  const [busqueda, setBusqueda] = useState("");
  const [categoria, setCategoria] = useState("Todas");
  const [soloSospechosas, setSoloSospechosas] = useState(false);

  const transacciones = auditoria?.transacciones ?? [];

  const categoriasDisponibles = useMemo(() => {
    const unicas = Array.from(new Set(transacciones.map((t) => t.categoria)));
    return ["Todas", ...unicas];
  }, [transacciones]);

  const filtradas = useMemo(() => {
    const q = busqueda.trim().toLowerCase();
    return transacciones.filter((tx) => {
      if (soloSospechosas && !tx.es_sospechosa) return false;
      if (categoria !== "Todas" && tx.categoria !== categoria) return false;
      if (!q) return true;
      return (
        tx.comercio.toLowerCase().includes(q) ||
        tx.ciudad.toLowerCase().includes(q) ||
        tx.id.toLowerCase().includes(q)
      );
    });
  }, [transacciones, busqueda, categoria, soloSospechosas]);

  if (!auditoria) {
    return (
      <EmptyAuditState
        titulo="Detalle de tus compras"
        descripcion="Sube tu estado de cuenta para ver cada compra ordenada por fecha, categoría y monto en soles."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="border-b border-[#E7E3DA] pb-6">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#4B3F8F]">
          Lista del mes
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#1E252B]">
          Mis compras ({filtradas.length})
        </h1>
        <p className="mt-1 text-sm text-[#616B75]">
          Si tenías compras en dólares o euros, aquí ya aparecen convertidas a soles.
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="relative min-w-[260px] flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#7D8590]" />
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar tienda o ciudad..."
            className="w-full rounded-xl border border-[#E2DDD3] bg-white py-2.5 pl-10 pr-4 text-sm text-[#1E252B] focus:border-[#2D6A5B] focus:outline-none"
          />
        </div>

        <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-[#F3F1EB] px-3.5 py-2 text-xs font-semibold text-[#464F59]">
          <input
            type="checkbox"
            checked={soloSospechosas}
            onChange={(e) => setSoloSospechosas(e.target.checked)}
            className="h-4 w-4 rounded accent-[#2D6A5B]"
          />
          Solo compras con aviso
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        {categoriasDisponibles.map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setCategoria(cat)}
            className={`rounded-full px-3.5 py-1 text-xs font-semibold transition ${
              categoria === cat
                ? "bg-[#2D6A5B] text-white"
                : "bg-[#F3F1EB] text-[#545E68] hover:bg-[#E7E3DA]"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {filtradas.length === 0 ? (
        <div className="rounded-3xl bg-white p-8 text-center text-sm text-[#616B75]">
          No encontramos compras con ese filtro.
        </div>
      ) : (
        <div className="overflow-hidden rounded-3xl bg-white">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-[#EFECE5] bg-[#F8F7F3] text-[#616B75]">
                  <th className="px-4 py-3.5 font-semibold">Fecha y hora</th>
                  <th className="px-4 py-3.5 font-semibold">Lugar / Tienda</th>
                  <th className="px-4 py-3.5 font-semibold">Ciudad y tipo</th>
                  <th className="px-4 py-3.5 font-semibold">Categoría</th>
                  <th className="px-4 py-3.5 font-semibold text-right">Monto original</th>
                  <th className="px-4 py-3.5 font-semibold text-right">En soles</th>
                  <th className="px-4 py-3.5 font-semibold">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F3F0EA]">
                {filtradas.map((tx) => (
                  <tr
                    key={tx.id}
                    className={tx.es_sospechosa ? "bg-[#FCE8EC]/45" : "hover:bg-[#FAF9F6]"}
                  >
                    <td className="px-4 py-3 text-[#616B75]">
                      {tx.fecha} <span className="text-[#8E969E]">{tx.hora}</span>
                    </td>
                    <td className="px-4 py-3 font-semibold text-[#1E252B]">{tx.comercio}</td>
                    <td className="px-4 py-3 text-[#616B75]">
                      {tx.ciudad} • {tx.canal === "online" ? "Por internet" : "En tienda"}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-[#F3F1EB] px-2.5 py-0.5 font-medium text-[#464F59]">
                        {tx.categoria}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-[#616B75]">
                      {tx.monto_original.toFixed(2)} {tx.moneda_original}
                    </td>
                    <td className="px-4 py-3 text-right font-bold tabular-nums text-[#1E252B]">
                      S/ {tx.monto_pen.toFixed(2)}
                    </td>
                    <td className="px-4 py-3">
                      {tx.es_sospechosa ? (
                        <span className="rounded-full bg-[#FCE8EC] px-2.5 py-0.5 font-bold text-[#8E263D]">
                          Aviso por revisar
                        </span>
                      ) : (
                        <span className="rounded-full bg-[#EEF7F3] px-2.5 py-0.5 font-medium text-[#1E4F41]">
                          {ETIQUETA_AMIGABLE[tx.etiqueta_modo] ?? "Normal"}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
