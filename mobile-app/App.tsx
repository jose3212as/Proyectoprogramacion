import "./global.css";
import React, { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import * as DocumentPicker from "expo-document-picker";
import { DiagnosisCards } from "./src/components/DiagnosisCards";
import { auditarArchivoMobile, marcarFuiYoMobile } from "./src/services/api";
import { AuditoriaResponse, ModoControl } from "./src/types/finguard";

export default function App() {
  const [ciudad, setCiudad] = useState("Ica");
  const [modo, setModo] = useState<ModoControl>("normal");
  const [presupuesto, setPresupuesto] = useState("2500");
  const [archivoSeleccionado, setArchivoSeleccionado] = useState<{
    uri: string;
    nombre: string;
    mimeType?: string;
  } | null>(null);
  const [auditoria, setAuditoria] = useState<AuditoriaResponse | null>(null);
  const [cargando, setCargando] = useState(false);
  const [mensajeError, setMensajeError] = useState<string | null>(null);

  const seleccionarArchivo = async () => {
    const res = await DocumentPicker.getDocumentAsync({
      type: ["text/csv", "application/pdf", "text/comma-separated-values"],
      copyToCacheDirectory: true,
    });
    if (res.canceled || res.assets.length === 0) return;
    const asset = res.assets[0];
    setArchivoSeleccionado({
      uri: asset.uri,
      nombre: asset.name,
      mimeType: asset.mimeType,
    });
    setMensajeError(null);
  };

  const ejecutarAuditoriaArchivo = async () => {
    if (!archivoSeleccionado) return;
    setCargando(true);
    setMensajeError(null);
    try {
      const resp = await auditarArchivoMobile({
        ...archivoSeleccionado,
        ciudadHabitual: ciudad.trim() || "Ica",
        modo,
        presupuestoMensual: Math.max(Number(presupuesto) || 2500, 100),
      });
      setAuditoria(resp);
    } catch (err) {
      setMensajeError(
        err instanceof Error ? err.message : "No se pudo conectar con la API de FinGuard."
      );
    } finally {
      setCargando(false);
    }
  };

  const manejarFuiYo = async (alertaId: string, verificada: boolean) => {
    if (!auditoria) return;

    const res = await marcarFuiYoMobile(alertaId, verificada);
    setAuditoria((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        escudo_antifraude: {
          ...prev.escudo_antifraude,
          alertas_activas: res.alertas_activas,
          nivel_riesgo_general: res.nivel_riesgo_general,
          alertas: prev.escudo_antifraude.alertas.map((a) =>
            a.alerta_id === alertaId ? { ...a, verificada_fui_yo: res.verificada_fui_yo } : a
          ),
        },
      };
    });
  };

  return (
    <SafeAreaView className="flex-1 bg-slate-50">
      <StatusBar style="dark" />
      <ScrollView className="flex-1 px-4 pt-4">
        <View className="mb-4 rounded-2xl bg-slate-900 p-4">
          <Text className="text-xl font-extrabold text-white">FinGuard</Text>
          <Text className="mt-1 text-xs text-slate-300">
            Revisión privada de estados de cuenta PDF/CSV y escudo antifraude
          </Text>
        </View>

        <View className="mb-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <Text className="text-sm font-bold text-slate-900">Configuración de Auditoría</Text>

          <Text className="mt-3 text-xs font-semibold text-slate-600">Ciudad Habitual</Text>
          <TextInput
            value={ciudad}
            onChangeText={setCiudad}
            placeholder="Ej. Ica"
            className="mt-1 rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-900"
          />

          <Text className="mt-3 text-xs font-semibold text-slate-600">
            Presupuesto Mensual (S/)
          </Text>
          <TextInput
            value={presupuesto}
            onChangeText={setPresupuesto}
            keyboardType="numeric"
            className="mt-1 rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-900"
          />

          <Text className="mt-3 text-xs font-semibold text-slate-600">Modo de Control</Text>
          <View className="mt-1.5 flex-row gap-2">
            <Pressable
              onPress={() => setModo("normal")}
              className={`flex-1 rounded-xl border py-2.5 items-center ${
                modo === "normal"
                  ? "border-slate-900 bg-slate-900"
                  : "border-slate-200 bg-slate-50"
              }`}
            >
              <Text
                className={`text-xs font-bold ${
                  modo === "normal" ? "text-white" : "text-slate-700"
                }`}
              >
                Normal
              </Text>
            </Pressable>
            <Pressable
              onPress={() => setModo("ahorro_estricto")}
              className={`flex-1 rounded-xl border py-2.5 items-center ${
                modo === "ahorro_estricto"
                  ? "border-teal-700 bg-teal-700"
                  : "border-slate-200 bg-slate-50"
              }`}
            >
              <Text
                className={`text-xs font-bold ${
                  modo === "ahorro_estricto" ? "text-white" : "text-slate-700"
                }`}
              >
                Ahorro Estricto
              </Text>
            </Pressable>
          </View>

          <Pressable
            onPress={seleccionarArchivo}
            className="mt-4 items-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 py-3.5"
          >
            <Text className="text-xs font-bold text-slate-700">
              {archivoSeleccionado
                ? `Archivo: ${archivoSeleccionado.nombre}`
                : "Seleccionar Estado de Cuenta (.CSV o .PDF)"}
            </Text>
          </Pressable>

          <Pressable
            onPress={ejecutarAuditoriaArchivo}
            disabled={!archivoSeleccionado || cargando}
            className={`mt-3 items-center rounded-xl py-3 ${
              !archivoSeleccionado || cargando ? "bg-slate-300" : "bg-teal-600"
            }`}
          >
            <Text className="text-sm font-bold text-white">Auditar Cuenta</Text>
          </Pressable>
        </View>

        {cargando && <ActivityIndicator size="large" color="#0d9488" className="my-4" />}

        {mensajeError && (
          <View className="mb-4 rounded-xl border border-rose-200 bg-rose-50 p-3">
            <Text className="text-xs font-medium text-rose-800">{mensajeError}</Text>
          </View>
        )}

        {auditoria && <DiagnosisCards auditoria={auditoria} onMarcarFuiYo={manejarFuiYo} />}
      </ScrollView>
    </SafeAreaView>
  );
}
