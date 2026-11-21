import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import * as Linking from "expo-linking";
import { AuditoriaResponse } from "../types/finguard";
import { urlReportePdfMobile } from "../services/api";

interface Props {
  auditoria: AuditoriaResponse;
  onMarcarFuiYo: (alertaId: string, verificada: boolean) => Promise<void>;
}

export function DiagnosisCards({ auditoria, onMarcarFuiYo }: Props) {
  const [trazaAbierta, setTrazaAbierta] = useState<string | null>(null);
  const { resumen_gastos: resumen, radar_fugas: radar, escudo_antifraude: escudo } = auditoria;

  return (
    <View className="gap-4 pb-8">
      {/* Bloque 1: Resumen de Gastos */}
      <View className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <Text className="text-xs font-bold uppercase tracking-wider text-teal-700">
          Bloque 1 • ¿A dónde fue mi dinero?
        </Text>
        <Text className="mt-1 text-lg font-extrabold text-slate-900">Resumen de Gastos</Text>

        <View className="mt-3 flex-row gap-2">
          <View className="flex-1 rounded-xl bg-slate-50 p-3">
            <Text className="text-xs text-slate-500">Gasto Total</Text>
            <Text className="text-base font-extrabold text-slate-900">
              S/ {resumen.gasto_total.toFixed(2)}
            </Text>
          </View>
          <View className="flex-1 rounded-xl bg-slate-50 p-3">
            <Text className="text-xs text-slate-500">Promedio Diario</Text>
            <Text className="text-base font-extrabold text-slate-900">
              S/ {resumen.promedio_diario.toFixed(2)}
            </Text>
          </View>
        </View>

        <View className="mt-3">
          <View className="flex-row justify-between">
            <Text className="text-xs text-slate-500">Presupuesto consumido</Text>
            <Text className="text-xs font-bold text-slate-800">
              {resumen.presupuesto_consumido_pct.toFixed(1)}%
            </Text>
          </View>
          <View className="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
            <View
              className="h-full rounded-full bg-teal-600"
              style={{ width: `${Math.min(resumen.presupuesto_consumido_pct, 100)}%` }}
            />
          </View>
        </View>

        <View className="mt-3 gap-1.5">
          {resumen.por_categoria.map((cat) => (
            <View key={cat.categoria} className="flex-row items-center justify-between">
              <Text className="text-xs font-medium text-slate-700">
                {cat.categoria} ({cat.cantidad})
              </Text>
              <Text className="text-xs font-bold text-slate-900">
                S/ {cat.total.toFixed(2)} ({cat.porcentaje.toFixed(1)}%)
              </Text>
            </View>
          ))}
        </View>
      </View>

      {/* Bloque 2: Radar de Fugas */}
      <View className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <View className="flex-row items-center justify-between">
          <View>
            <Text className="text-xs font-bold uppercase tracking-wider text-amber-700">
              Bloque 2 • ¿Dónde pierdo plata?
            </Text>
            <Text className="mt-1 text-lg font-extrabold text-slate-900">
              Radar de Fugas de Dinero
            </Text>
          </View>
          <View className="rounded-xl bg-amber-50 px-3 py-1.5">
            <Text className="text-xs font-extrabold text-amber-900">
              S/ {radar.total_fugas_estimado.toFixed(2)}
            </Text>
          </View>
        </View>

        <View className="mt-3 gap-2">
          {radar.gastos_hormiga.map((h) => (
            <View key={h.comercio} className="rounded-xl border border-amber-200 bg-amber-50 p-3">
              <Text className="text-xs font-bold text-slate-900">
                Gasto hormiga: {h.comercio} (S/ {h.total_acumulado.toFixed(2)})
              </Text>
              <Text className="mt-0.5 text-xs text-slate-600">{h.explicacion}</Text>
            </View>
          ))}
          {radar.cobros_duplicados.map((d) => (
            <View
              key={d.ids_transacciones.join("-")}
              className="rounded-xl border border-rose-200 bg-rose-50 p-3"
            >
              <Text className="text-xs font-bold text-rose-900">
                Cobro duplicado: {d.comercio} (S/ {d.monto.toFixed(2)})
              </Text>
              <Text className="mt-0.5 text-xs text-slate-600">{d.explicacion}</Text>
            </View>
          ))}
          {radar.suscripciones_recurrentes.map((s) => (
            <View key={s.comercio} className="rounded-xl border border-indigo-100 bg-indigo-50 p-3">
              <Text className="text-xs font-bold text-indigo-950">
                Suscripción: {s.comercio} (S/ {s.monto_mensual.toFixed(2)})
              </Text>
              <Text className="mt-0.5 text-xs text-slate-600">{s.explicacion}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Bloque 3: Escudo Antifraude */}
      <View className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <View className="flex-row items-center justify-between">
          <View>
            <Text className="text-xs font-bold uppercase tracking-wider text-rose-700">
              Bloque 3 • ¿Mi tarjeta está segura?
            </Text>
            <Text className="mt-1 text-lg font-extrabold text-slate-900">Escudo Antifraude</Text>
          </View>
          <View className="rounded-full bg-rose-600 px-3 py-1">
            <Text className="text-xs font-extrabold uppercase text-white">
              Riesgo {escudo.nivel_riesgo_general}
            </Text>
          </View>
        </View>

        <View className="mt-3 gap-3">
          {escudo.alertas.map((alerta) => {
            const abierta = trazaAbierta === alerta.alerta_id;
            return (
              <View
                key={alerta.alerta_id}
                className={`rounded-xl border p-3 ${
                  alerta.verificada_fui_yo
                    ? "border-emerald-200 bg-emerald-50"
                    : "border-rose-200 bg-rose-50"
                }`}
              >
                <View className="flex-row items-center justify-between">
                  <Text className="text-xs font-bold uppercase text-slate-700">
                    {alerta.verificada_fui_yo ? "Verificada (Fui yo)" : alerta.regla_activada}
                  </Text>
                  <Text className="text-sm font-extrabold text-slate-900">
                    S/ {alerta.monto_pen.toFixed(2)}
                  </Text>
                </View>

                <Text className="mt-1 text-sm font-bold text-slate-900">{alerta.titulo}</Text>
                <Text className="mt-1 text-xs leading-5 text-slate-700">{alerta.explicacion}</Text>

                <View className="mt-3 flex-row items-center justify-between gap-2">
                  <Pressable
                    onPress={() => setTrazaAbierta(abierta ? null : alerta.alerta_id)}
                  >
                    <Text className="text-xs font-semibold text-teal-800">
                      {abierta ? "Ocultar traza Prolog" : "Ver traza Prolog"}
                    </Text>
                  </Pressable>

                  <Pressable
                    onPress={() => onMarcarFuiYo(alerta.alerta_id, !alerta.verificada_fui_yo)}
                    className="rounded-lg bg-slate-900 px-3 py-1.5"
                  >
                    <Text className="text-xs font-bold text-white">
                      {alerta.verificada_fui_yo ? "Deshacer 'Fui yo'" : "Fui yo"}
                    </Text>
                  </Pressable>
                </View>

                {abierta && (
                  <View className="mt-2 rounded-lg bg-slate-950 p-2.5">
                    {alerta.traza_prolog.map((paso, idx) => (
                      <Text key={idx} className="font-mono text-[10px] text-emerald-300">
                        ?- {paso}
                      </Text>
                    ))}
                  </View>
                )}
              </View>
            );
          })}
        </View>

        <Pressable
          onPress={() => Linking.openURL(urlReportePdfMobile(auditoria.audit_id))}
          className="mt-4 items-center rounded-xl bg-slate-900 py-3"
        >
          <Text className="text-xs font-bold text-white">Descargar Reporte PDF Bancario</Text>
        </Pressable>
      </View>
    </View>
  );
}
