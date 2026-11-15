"""Orquestador principal que une POO (Ingesta), Funcional, Analítica y SWI-Prolog."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from app.analitica import calcular_analitica_y_fugas
from app.db import RepositorioSQLite, calcular_nivel_riesgo
from app.funcional import aplicar_pipeline_funcional
from app.lectores import obtener_lector
from app.logica import MotorInferenciaProlog
from app.schemas import (
    AlertaFraude,
    AuditoriaResponse,
    EscudoAntifraude,
    MetadatosMotor,
    ModoControl,
    ParadigmasInfo,
    PerfilConfig,
    TransaccionProcesada,
)

_ORDEN_SEVERIDAD = {"critica": 0, "alta": 1, "media": 2, "baja": 3}


class ServicioAuditorFinGuard:
    """Coordina la ejecución multiparadigma completa en menos de 3 segundos (RNF-03)."""

    def __init__(
        self,
        repositorio: RepositorioSQLite | None = None,
        motor_prolog: MotorInferenciaProlog | None = None,
    ) -> None:
        self.repositorio = repositorio or RepositorioSQLite()
        self.motor_prolog = motor_prolog or MotorInferenciaProlog()

    def auditar_archivo(
        self,
        *,
        contenido: bytes,
        nombre_archivo: str,
        ciudad_habitual: str,
        modo: ModoControl,
        presupuesto_mensual: float,
    ) -> AuditoriaResponse:
        inicio = time.perf_counter()
        audit_id = f"aud-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        # 1. UNIDAD 3 (POO): Ingesta polimórfica PDF o CSV
        lector = obtener_lector(nombre_archivo)
        movimientos = lector.leer(
            contenido, nombre_archivo=nombre_archivo, ciudad_default=ciudad_habitual
        )

        # 2. UNIDAD 1 (Funcional): Pipeline inmutable, conversión de divisas, lambdas y orden superior
        transacciones_clasificadas = aplicar_pipeline_funcional(movimientos, modo=modo)

        # 3. UNIDAD 3 (Ciencia de Datos): Pandas + NumPy (Z-Score y Radar de Fugas)
        resumen_gastos, radar_fugas, z_scores = calcular_analitica_y_fugas(
            transacciones_clasificadas,
            presupuesto_mensual=presupuesto_mensual,
            modo=modo,
        )

        # 4. UNIDAD 2 (Lógica): Motor SWI-Prolog (unificación, resolución y backtracking)
        inferencias = self.motor_prolog.inferir_alertas(
            transacciones_clasificadas,
            z_scores=z_scores,
            ciudad_habitual=ciudad_habitual,
            modo=modo,
        )

        mapa_tx = {tx.id: tx for tx in transacciones_clasificadas}
        alertas: list[AlertaFraude] = []
        for inf in inferencias:
            tx = mapa_tx.get(inf.transaccion_id)
            if tx is None:
                continue
            regla_slug = inf.regla_activada.split("/")[0]
            alertas.append(
                AlertaFraude(
                    alerta_id=f"{audit_id}-{tx.id}-{regla_slug}",
                    transaccion_id=tx.id,
                    fecha=tx.fecha,
                    hora=tx.hora,
                    comercio=tx.comercio,
                    ciudad=tx.ciudad,
                    canal=tx.canal,  # type: ignore[arg-type]
                    monto_pen=tx.monto_pen,
                    severidad=inf.severidad,  # type: ignore[arg-type]
                    regla_activada=inf.regla_activada,
                    titulo=inf.titulo,
                    explicacion=inf.explicacion,
                    traza_prolog=list(inf.traza_prolog),
                    z_score=z_scores.get(tx.id),
                    verificada_fui_yo=False,
                )
            )

        alertas.sort(key=lambda a: (_ORDEN_SEVERIDAD.get(a.severidad, 9), -a.monto_pen))
        ids_sospechosas = {a.transaccion_id for a in alertas}

        transacciones_salida = [
            TransaccionProcesada(
                id=tx.id,
                fecha=tx.fecha,
                hora=tx.hora,
                comercio=tx.comercio,
                ciudad=tx.ciudad,
                canal=tx.canal,  # type: ignore[arg-type]
                monto_original=tx.monto_original,
                moneda_original=tx.moneda_original,
                monto_pen=tx.monto_pen,
                tipo=tx.tipo,
                categoria=tx.categoria,
                etiqueta_modo=tx.etiqueta_modo,
                z_score=z_scores.get(tx.id, 0.0),
                es_sospechosa=tx.id in ids_sospechosas,
            )
            for tx in transacciones_clasificadas
        ]

        duracion_ms = round((time.perf_counter() - inicio) * 1000.0, 2)
        escudo = EscudoAntifraude(
            nivel_riesgo_general=calcular_nivel_riesgo(alertas),  # type: ignore[arg-type]
            total_alertas=len(alertas),
            alertas_activas=len(alertas),
            alertas=alertas,
        )

        respuesta = AuditoriaResponse(
            audit_id=audit_id,
            archivo=nombre_archivo,
            formato=lector.formato,  # type: ignore[arg-type]
            fecha_auditoria=datetime.now(timezone.utc).isoformat(),
            perfil=PerfilConfig(
                ciudad_habitual=ciudad_habitual,
                modo=modo,
                presupuesto_mensual=presupuesto_mensual,
            ),
            resumen_gastos=resumen_gastos,
            radar_fugas=radar_fugas,
            escudo_antifraude=escudo,
            transacciones=transacciones_salida,
            metadatos_motor=MetadatosMotor(
                paradigmas=ParadigmasInfo(
                    funcional="Pipeline inmutable Python (frozen dataclasses, lambdas, map/filter/reduce, orden superior)",
                    logico="SWI-Prolog (hechos transaccion/7, unificación, backtracking y traza explicable)",
                    multiparadigma_datos="POO polimórfica (LectorPDF/LectorCSV + Movimiento) + Pandas & NumPy (Z-Score)",
                ),
                tiempo_procesamiento_ms=duracion_ms,
                motor_prolog_activo=self.motor_prolog.motor_activo,
            ),
        )
        self.repositorio.guardar_auditoria(respuesta)
        return respuesta
