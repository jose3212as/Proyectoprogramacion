"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  auditarCuentaArchivo,
  cerrarSesionUsuario,
  eliminarAuditoriaHistorial,
  guardarRevisionEnCuenta,
  iniciarSesionUsuario,
  marcarAlertaFuiYo,
  obtenerAuditoriaPorId,
  obtenerHistorial,
  obtenerUsuarioActual,
  registrarUsuario,
  verificarSaludBackend,
} from "@/lib/api";
import { AuditoriaResponse, HistorialItem, ModoControl, UsuarioInfo } from "@/types/finguard";

interface AuditContextValue {
  backendOnline: boolean;
  usuario: UsuarioInfo | null;
  token: string | null;
  auditoria: AuditoriaResponse | null;
  historial: HistorialItem[];
  cargando: boolean;
  actualizandoAlertaId: string | null;
  eliminandoAuditId: string | null;
  error: string | null;
  aviso: string | null;
  limpiarError: () => void;
  limpiarAviso: () => void;
  refrescarEstado: (tokenOverride?: string | null) => Promise<void>;
  registrarCuenta: (params: {
    nombre: string;
    correo: string;
    password: string;
    ciudadHabitual: string;
    presupuestoMensual: number;
  }) => Promise<boolean>;
  iniciarSesion: (params: { correo: string; password: string }) => Promise<boolean>;
  cerrarSesion: () => Promise<void>;
  guardarRevisionActual: () => Promise<boolean>;
  auditarArchivo: (params: {
    archivo: File;
    ciudadHabitual: string;
    modo: ModoControl;
    presupuestoMensual: number;
  }) => Promise<boolean>;
  cargarDesdeHistorial: (auditId: string) => Promise<boolean>;
  eliminarDelHistorial: (auditId: string) => Promise<boolean>;
  toggleFuiYo: (alertaId: string, verificada: boolean) => Promise<void>;
}

const AuditContext = createContext<AuditContextValue | null>(null);
const STORAGE_AUDIT_KEY = "finguard_active_audit_v1";
const STORAGE_TOKEN_KEY = "finguard_auth_token_v1";

export function AuditProvider({ children }: { children: React.ReactNode }) {
  const [backendOnline, setBackendOnline] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [usuario, setUsuario] = useState<UsuarioInfo | null>(null);
  const [auditoria, setAuditoria] = useState<AuditoriaResponse | null>(null);
  const [historial, setHistorial] = useState<HistorialItem[]>([]);
  const [cargando, setCargando] = useState(false);
  const [actualizandoAlertaId, setActualizandoAlertaId] = useState<string | null>(null);
  const [eliminandoAuditId, setEliminandoAuditId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);

  const persistirAuditoria = useCallback((data: AuditoriaResponse | null) => {
    setAuditoria(data);
    try {
      if (data) {
        sessionStorage.setItem(STORAGE_AUDIT_KEY, JSON.stringify(data));
      } else {
        sessionStorage.removeItem(STORAGE_AUDIT_KEY);
      }
    } catch {
      // Ignora almacenamiento restringido
    }
  }, []);

  const persistirToken = useCallback((nuevoToken: string | null) => {
    setToken(nuevoToken);
    try {
      if (nuevoToken) {
        localStorage.setItem(STORAGE_TOKEN_KEY, nuevoToken);
      } else {
        localStorage.removeItem(STORAGE_TOKEN_KEY);
      }
    } catch {
      // Ignora almacenamiento restringido
    }
  }, []);

  const refrescarEstado = useCallback(
    async (tokenOverride?: string | null) => {
      const activo = tokenOverride !== undefined ? tokenOverride : token;
      const salud = await verificarSaludBackend();
      setBackendOnline(salud.online);
      if (!salud.online) return;

      if (activo) {
        try {
          const perfil = await obtenerUsuarioActual(activo);
          setUsuario(perfil);
          const items = await obtenerHistorial(activo);
          setHistorial(items);
          return;
        } catch {
          persistirToken(null);
          setUsuario(null);
          setHistorial([]);
        }
      } else {
        setUsuario(null);
        setHistorial([]);
      }
    },
    [persistirToken, token]
  );

  useEffect(() => {
    let tokenGuardado: string | null = null;
    try {
      const savedAudit = sessionStorage.getItem(STORAGE_AUDIT_KEY);
      if (savedAudit) {
        setAuditoria(JSON.parse(savedAudit) as AuditoriaResponse);
      }
      tokenGuardado = localStorage.getItem(STORAGE_TOKEN_KEY);
      if (tokenGuardado) {
        setToken(tokenGuardado);
      }
    } catch {
      // Ignora errores de almacenamiento
    }
    refrescarEstado(tokenGuardado);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const registrarCuenta = useCallback(
    async (params: {
      nombre: string;
      correo: string;
      password: string;
      ciudadHabitual: string;
      presupuestoMensual: number;
    }): Promise<boolean> => {
      setCargando(true);
      setError(null);
      setAviso(null);
      try {
        const res = await registrarUsuario(params);
        persistirToken(res.token);
        setUsuario(res.usuario);
        if (auditoria) {
          await guardarRevisionEnCuenta(auditoria.audit_id, res.token).catch(() => undefined);
        }
        await refrescarEstado(res.token);
        setAviso("Tu cuenta quedó lista y tus revisiones se guardarán aquí.");
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "No pudimos crear tu cuenta.");
        return false;
      } finally {
        setCargando(false);
      }
    },
    [auditoria, persistirToken, refrescarEstado]
  );

  const iniciarSesion = useCallback(
    async (params: { correo: string; password: string }): Promise<boolean> => {
      setCargando(true);
      setError(null);
      setAviso(null);
      try {
        const res = await iniciarSesionUsuario(params);
        persistirToken(res.token);
        setUsuario(res.usuario);
        if (auditoria) {
          await guardarRevisionEnCuenta(auditoria.audit_id, res.token).catch(() => undefined);
        }
        await refrescarEstado(res.token);
        setAviso(`¡Hola de nuevo, ${res.usuario.nombre}!`);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Correo o contraseña incorrectos.");
        return false;
      } finally {
        setCargando(false);
      }
    },
    [auditoria, persistirToken, refrescarEstado]
  );

  const cerrarSesion = useCallback(async () => {
    if (token) {
      await cerrarSesionUsuario(token);
    }
    persistirToken(null);
    setUsuario(null);
    setHistorial([]);
    setAviso("Cerraste tu sesión correctamente.");
  }, [persistirToken, token]);

  const guardarRevisionActual = useCallback(async (): Promise<boolean> => {
    if (!auditoria || !token) return false;
    setCargando(true);
    setError(null);
    try {
      await guardarRevisionEnCuenta(auditoria.audit_id, token);
      await refrescarEstado(token);
      setAviso("Revisión guardada en tu historial.");
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar en tu cuenta.");
      return false;
    } finally {
      setCargando(false);
    }
  }, [auditoria, refrescarEstado, token]);

  const auditarArchivo = useCallback(
    async (params: {
      archivo: File;
      ciudadHabitual: string;
      modo: ModoControl;
      presupuestoMensual: number;
    }): Promise<boolean> => {
      setCargando(true);
      setError(null);
      setAviso(null);
      try {
        const res = await auditarCuentaArchivo({ ...params, token });
        persistirAuditoria(res);
        await refrescarEstado(token);
        return true;
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No pudimos leer el archivo. Verifica que sea un CSV o PDF válido."
        );
        return false;
      } finally {
        setCargando(false);
      }
    },
    [persistirAuditoria, refrescarEstado, token]
  );

  const cargarDesdeHistorial = useCallback(
    async (auditId: string): Promise<boolean> => {
      setCargando(true);
      setError(null);
      try {
        const data = await obtenerAuditoriaPorId(auditId);
        persistirAuditoria(data);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "No pudimos abrir esa revisión.");
        return false;
      } finally {
        setCargando(false);
      }
    },
    [persistirAuditoria]
  );

  const eliminarDelHistorial = useCallback(
    async (auditId: string): Promise<boolean> => {
      if (!token) return false;
      setEliminandoAuditId(auditId);
      setError(null);
      setAviso(null);
      try {
        await eliminarAuditoriaHistorial(auditId, token);
        setHistorial((prev) => prev.filter((item) => item.audit_id !== auditId));
        if (auditoria?.audit_id === auditId) {
          persistirAuditoria(null);
        }
        setAviso("Revisión eliminada de tu historial.");
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "No pudimos eliminar esa revisión.");
        return false;
      } finally {
        setEliminandoAuditId(null);
      }
    },
    [auditoria, persistirAuditoria, token]
  );

  const toggleFuiYo = useCallback(
    async (alertaId: string, verificada: boolean) => {
      if (!auditoria) return;
      setActualizandoAlertaId(alertaId);
      setError(null);
      try {
        const resp = await marcarAlertaFuiYo(alertaId, verificada);
        const alertas = auditoria.escudo_antifraude.alertas.map((a) =>
          a.alerta_id === alertaId ? { ...a, verificada_fui_yo: resp.verificada_fui_yo } : a
        );
        const idsActivos = new Set(
          alertas.filter((a) => !a.verificada_fui_yo).map((a) => a.transaccion_id)
        );
        persistirAuditoria({
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
        await refrescarEstado(token);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No pudimos actualizar este aviso.");
      } finally {
        setActualizandoAlertaId(null);
      }
    },
    [auditoria, persistirAuditoria, refrescarEstado, token]
  );

  return (
    <AuditContext.Provider
      value={{
        backendOnline,
        usuario,
        token,
        auditoria,
        historial,
        cargando,
        actualizandoAlertaId,
        eliminandoAuditId,
        error,
        aviso,
        limpiarError: () => setError(null),
        limpiarAviso: () => setAviso(null),
        refrescarEstado,
        registrarCuenta,
        iniciarSesion,
        cerrarSesion,
        guardarRevisionActual,
        auditarArchivo,
        cargarDesdeHistorial,
        eliminarDelHistorial,
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
