"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  auditarCuentaArchivo,
  auditarDemoBackend,
  marcarAlertaFuiYo,
  obtenerAuditoriaPorId,
  obtenerHistorial,
  verificarSaludBackend,
} from "@/lib/api";
import { MOCK_AUDITORIA_DEMO } from "@/lib/mockData";
import { AuditoriaResponse, HistorialItem, ModoControl } from "@/types/finguard";

interface AuditContextValue {
  backendOnline: boolean;
  motorProlog: string;
  auditoria: AuditoriaResponse | null;
  historial: HistorialItem[];
  cargando: boolean;
  actualizandoAlertaId: string | null;
  error: string | null;
  limpiarError: () => void;
  refrescarEstado: () => Promise<void>;
  auditarArchivo: (params: {
    archivo: File;
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => Promise<boolean>;
  auditarDemo: (params: {
    formato: "csv" | "pdf";
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => Promise<boolean>;
  cargarDesdeHistorial: (auditId: string) => Promise<boolean>;
  toggleFuiYo: (alertaId: string, verificada: boolean) => Promise<void>;
}

const AuditContext = createContext<AuditContextValue | null>(null);
const STORAGE_KEY = "finguard_active_audit_v1";

export function AuditProvider({ children }: { children: React.ReactNode }) {
  const [backendOnline, setBackendOnline] = useState(false);
  const [motorProlog, setMotorProlog] = useState("verificando");
  const [auditoria, setAuditoria] = useState<AuditoriaResponse | null>(null);
  const [historial, setHistorial] = useState<HistorialItem[]>([]);
  const [cargando, setCargando] = useState(false);
  const [actualizandoAlertaId, setActualizandoAlertaId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const persistirLocal = useCallback((data: AuditoriaResponse | null) => {
    setAuditoria(data);
    try {
      if (data) {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } else {
        sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // Ignora restricciones de almacenamiento privado
    }
  }, []);

  const refrescarEstado = useCallback(async () => {
    const salud = await verificarSaludBackend();
    setBackendOnline(salud.online);
    setMotorProlog(salud.motorProlog ?? "offline");
    if (salud.online) {
      try {
        const items = await obtenerHistorial();
        setHistorial(items);
      } catch {
        // Historial opcional
      }
    }
  }, []);

  useEffect(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        setAuditoria(JSON.parse(saved) as AuditoriaResponse);
      }
    } catch {
      // Ignora JSON inválido
    }
    refrescarEstado();
  }, [refrescarEstado]);

  const auditarArchivo = useCallback(
    async (params: {
      archivo: File;
      ciudadHabitual: string;
      modo: ModoControl;
      presupuestoMensual: number;
    }): Promise<boolean> => {
      setCargando(true);
      setError(null);
      try {
        const res = await auditarCuentaArchivo(params);
        persistirLocal(res);
        await refrescarEstado();
        return true;
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudo conectar con el servidor FastAPI en http://127.0.0.1:8000."
        );
        return false;
      } finally {
        setCargando(false);
      }
    },
    [persistirLocal, refrescarEstado]
  );

  const auditarDemo = useCallback(
    async (params: {
      formato: "csv" | "pdf";
      ciudadHabitual: string;
      modo: ModoControl;
      presupuestoMensual: number;
    }): Promise<boolean> => {
      setCargando(true);
      setError(null);
      try {
        const res = await auditarDemoBackend(params);
        persistirLocal(res);
        await refrescarEstado();
        return true;
      } catch {
        persistirLocal({
          ...MOCK_AUDITORIA_DEMO,
          perfil: {
            ciudad_habitual: params.ciudadHabitual,
            modo: params.modo,
            presupuesto_mensual: params.presupuestoMensual,
          },
        });
        return true;
      } finally {
        setCargando(false);
      }
    },
    [persistirLocal, refrescarEstado]
  );

  const cargarDesdeHistorial = useCallback(
    async (auditId: string): Promise<boolean> => {
      setCargando(true);
      setError(null);
      try {
        const data = await obtenerAuditoriaPorId(auditId);
        persistirLocal(data);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo recuperar la auditoría.");
        return false;
      } finally {
        setCargando(false);
      }
    },
    [persistirLocal]
  );

  const toggleFuiYo = useCallback(
    async (alertaId: string, verificada: boolean) => {
      if (!auditoria) return;
      setActualizandoAlertaId(alertaId);
      setError(null);
      try {
        if (auditoria.audit_id === "demo-offline-001") {
          const alertas = auditoria.escudo_antifraude.alertas.map((a) =>
            a.alerta_id === alertaId ? { ...a, verificada_fui_yo: verificada } : a
          );
          const activas = alertas.filter((a) => !a.verificada_fui_yo).length;
          persistirLocal({
            ...auditoria,
            escudo_antifraude: {
              ...auditoria.escudo_antifraude,
              alertas_activas: activas,
              nivel_riesgo_general: activas === 0 ? "bajo" : "critico",
              alertas,
            },
          });
          return;
        }

        const resp = await marcarAlertaFuiYo(alertaId, verificada);
        const alertas = auditoria.escudo_antifraude.alertas.map((a) =>
          a.alerta_id === alertaId ? { ...a, verificada_fui_yo: resp.verificada_fui_yo } : a
        );
        const idsActivos = new Set(
          alertas.filter((a) => !a.verificada_fui_yo).map((a) => a.transaccion_id)
        );
        persistirLocal({
          ...auditoria,
          escudo_antifraude: {
            ...auditoria.escudo_antifraude,
            alertas_activas: resp.alertas_activas,
            nivel_riesgo_general: resp.nivel_riesgo_general,
            alertas,
          },
          transacciones: auditoria.transacciones.map((tx) => ({
            ...tx,
            es_sospechosa: idsActivos.has(tx.id),
          })),
        });
        await refrescarEstado();
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo actualizar la alerta.");
      } finally {
        setActualizandoAlertaId(null);
      }
    },
    [auditoria, persistirLocal, refrescarEstado]
  );

  return (
    <AuditContext.Provider
      value={{
        backendOnline,
        motorProlog,
        auditoria,
        historial,
        cargando,
        actualizandoAlertaId,
        error,
        limpiarError: () => setError(null),
        refrescarEstado,
        auditarArchivo,
        auditarDemo,
        cargarDesdeHistorial,
        toggleFuiYo,
      }}
    >
      {children}
    </AuditContext.Provider>
  );
}

export function useAudit() {
  const ctx = useContext(AuditContext);
  if (!ctx) {
    throw new Error("useAudit debe usarse dentro de AuditProvider");
  }
  return ctx;
}
