"""Análisis estadístico con Pandas y NumPy + detección de fugas de dinero (Unidad 3)."""

from __future__ import annotations

from datetime import datetime
from typing import Tuple

import numpy as np
import pandas as pd

from app.funcional.modelos import TransaccionClasificada
from app.schemas import (
    CategoriaResumen,
    CobroDuplicado,
    GastoDiario,
    GastoHormiga,
    ModoControl,
    RadarFugas,
    ResumenGastos,
    SuscripcionRecurrente,
)


def _hora_a_minutos(fecha: str, hora: str) -> int:
    """Convierte fecha + hora en minutos Unix aproximados para medir intervalos."""
    try:
        dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        return int(dt.timestamp() // 60)
    except ValueError:
        return 0


def _calcular_z_scores(montos: np.ndarray, ids: list[str]) -> tuple[float, float, dict[str, float]]:
    """Calcula media, desviación estándar y Z-Score por transacción usando NumPy."""
    if len(montos) == 0:
        return 0.0, 0.0, {}

    media = float(np.mean(montos))
    desviacion = float(np.std(montos, ddof=0))
    if desviacion <= 1e-9:
        return round(media, 2), 0.0, {tx_id: 0.0 for tx_id in ids}

    z_arr = (montos - media) / desviacion
    z_scores = {tx_id: round(float(z), 2) for tx_id, z in zip(ids, z_arr)}
    return round(media, 2), round(desviacion, 2), z_scores


def _detectar_gastos_hormiga(df: pd.DataFrame, modo: ModoControl) -> list[GastoHormiga]:
    """Detecta compras pequeñas frecuentes acumuladas en un mismo comercio."""
    monto_max = 30.0 if modo == "ahorro_estricto" else 25.0
    min_frecuencia = 2 if modo == "ahorro_estricto" else 3

    pequenas = df[(df["monto_pen"] <= monto_max) & (df["tipo"] == "compra")]
    if pequenas.empty:
        return []

    agrupado = (
        pequenas.groupby(["comercio", "categoria"], as_index=False)
        .agg(
            cantidad=("id", "count"),
            monto_promedio=("monto_pen", "mean"),
            total_acumulado=("monto_pen", "sum"),
        )
        .sort_values("total_acumulado", ascending=False)
    )

    hormigas: list[GastoHormiga] = []
    for _, fila in agrupado.iterrows():
        cantidad = int(fila["cantidad"])
        if cantidad < min_frecuencia:
            continue
        total = round(float(fila["total_acumulado"]), 2)
        prom = round(float(fila["monto_promedio"]), 2)
        comercio = str(fila["comercio"])
        hormigas.append(
            GastoHormiga(
                comercio=comercio,
                categoria=str(fila["categoria"]),
                cantidad=cantidad,
                monto_promedio=prom,
                total_acumulado=total,
                explicacion=(
                    f"Se detectaron {cantidad} compras pequeñas frecuentes en {comercio} "
                    f"(promedio S/ {prom:.2f}) acumulando S/ {total:.2f}."
                ),
            )
        )
    return hormigas


def _detectar_cobros_duplicados(df: pd.DataFrame) -> list[CobroDuplicado]:
    """Identifica cargos idénticos en el mismo comercio con corta diferencia de tiempo."""
    duplicados: list[CobroDuplicado] = []
    vistos: set[tuple[str, str]] = set()

    for (comercio, fecha), grupo in df.groupby(["comercio", "fecha"]):
        if len(grupo) < 2:
            continue
        registros = grupo.sort_values("minutos").to_dict("records")
        for i in range(len(registros)):
            for j in range(i + 1, len(registros)):
                r1, r2 = registros[i], registros[j]
                if abs(float(r1["monto_pen"]) - float(r2["monto_pen"])) >= 0.01:
                    continue
                diff_min = abs(int(r2["minutos"]) - int(r1["minutos"]))
                if diff_min <= 30 or r1["tipo"] == "suscripcion":
                    par = tuple(sorted((str(r1["id"]), str(r2["id"]))))
                    if par in vistos:
                        continue
                    vistos.add(par)
                    monto = round(float(r1["monto_pen"]), 2)
                    detalle_tiempo = (
                        f"con {diff_min} minutos de diferencia"
                        if diff_min <= 30
                        else "repetido dentro del mismo periodo"
                    )
                    duplicados.append(
                        CobroDuplicado(
                            ids_transacciones=[str(r1["id"]), str(r2["id"])],
                            comercio=str(comercio),
                            monto=monto,
                            fecha=str(fecha),
                            diferencia_minutos=diff_min,
                            explicacion=(
                                f"Posible cobro duplicado de S/ {monto:.2f} en {comercio} "
                                f"({r1['id']} y {r2['id']}, {detalle_tiempo})."
                            ),
                        )
                    )

    # También detecta suscripciones cobradas más de una vez en el mismo mes en fechas distintas.
    suscripciones = df[df["tipo"] == "suscripcion"]
    for comercio, grupo in suscripciones.groupby("comercio"):
        if len(grupo) < 2:
            continue
        registros = grupo.sort_values("minutos").to_dict("records")
        for i in range(len(registros) - 1):
            r1, r2 = registros[i], registros[i + 1]
            if abs(float(r1["monto_pen"]) - float(r2["monto_pen"])) >= 0.01:
                continue
            par = tuple(sorted((str(r1["id"]), str(r2["id"]))))
            if par in vistos:
                continue
            vistos.add(par)
            diff_min = abs(int(r2["minutos"]) - int(r1["minutos"]))
            monto = round(float(r1["monto_pen"]), 2)
            duplicados.append(
                CobroDuplicado(
                    ids_transacciones=[str(r1["id"]), str(r2["id"])],
                    comercio=str(comercio),
                    monto=monto,
                    fecha=f"{r1['fecha']} / {r2['fecha']}",
                    diferencia_minutos=diff_min,
                    explicacion=(
                        f"Doble cargo de suscripción por S/ {monto:.2f} en {comercio} "
                        f"({r1['id']} el {r1['fecha']} y {r2['id']} el {r2['fecha']})."
                    ),
                )
            )
    return duplicados


def _detectar_suscripciones_recurrentes(df: pd.DataFrame) -> list[SuscripcionRecurrente]:
    """Agrupa servicios de suscripción y estima su impacto mensual."""
    subs = df[df["categoria"] == "Suscripciones"]
    if subs.empty:
        return []

    resultado: list[SuscripcionRecurrente] = []
    for comercio, grupo in subs.groupby("comercio"):
        ids = [str(x) for x in grupo["id"].tolist()]
        monto_unit = round(float(grupo["monto_pen"].mean()), 2)
        total = round(float(grupo["monto_pen"].sum()), 2)
        freq = (
            f"{len(ids)} cargos en el periodo"
            if len(ids) > 1
            else "Cargo mensual recurrente"
        )
        resultado.append(
            SuscripcionRecurrente(
                comercio=str(comercio),
                monto_mensual=monto_unit,
                frecuencia_detectada=freq,
                transacciones=ids,
                explicacion=(
                    f"Suscripción activa en {comercio}: S/ {monto_unit:.2f} por ciclo "
                    f"(acumulado en extracto: S/ {total:.2f})."
                ),
            )
        )
    return sorted(resultado, key=lambda s: s.monto_mensual, reverse=True)


def calcular_analitica_y_fugas(
    transacciones: Tuple[TransaccionClasificada, ...],
    presupuesto_mensual: float,
    modo: ModoControl,
) -> tuple[ResumenGastos, RadarFugas, dict[str, float]]:
    """Calcula métricas estadísticas (Pandas/NumPy), Z-Scores y fugas de dinero."""
    filas = [
        {
            "id": tx.id,
            "fecha": tx.fecha,
            "hora": tx.hora,
            "comercio": tx.comercio,
            "ciudad": tx.ciudad,
            "canal": tx.canal,
            "monto_pen": tx.monto_pen,
            "tipo": tx.tipo,
            "categoria": tx.categoria,
            "minutos": _hora_a_minutos(tx.fecha, tx.hora),
        }
        for tx in transacciones
    ]
    df = pd.DataFrame(filas)

    montos_np = df["monto_pen"].to_numpy(dtype=float)
    ids_lista = df["id"].astype(str).tolist()
    media_tx, desviacion_tx, z_scores = _calcular_z_scores(montos_np, ids_lista)

    gasto_total = round(float(np.sum(montos_np)), 2)
    dias_unicos = max(int(df["fecha"].nunique()), 1)
    promedio_diario = round(gasto_total / dias_unicos, 2)
    presupuesto_seguro = max(presupuesto_mensual, 1.0)
    pct_presupuesto = round((gasto_total / presupuesto_seguro) * 100.0, 2)

    if pct_presupuesto >= 100.0:
        estado_presupuesto = "excedido"
    elif pct_presupuesto >= 75.0:
        estado_presupuesto = "precaucion"
    else:
        estado_presupuesto = "saludable"

    cat_df = (
        df.groupby("categoria", as_index=False)
        .agg(total=("monto_pen", "sum"), cantidad=("id", "count"))
        .sort_values("total", ascending=False)
    )
    por_categoria = [
        CategoriaResumen(
            categoria=str(r["categoria"]),
            total=round(float(r["total"]), 2),
            porcentaje=round((float(r["total"]) / gasto_total) * 100.0, 2) if gasto_total else 0.0,
            cantidad=int(r["cantidad"]),
        )
        for _, r in cat_df.iterrows()
    ]

    diario_df = (
        df.groupby("fecha", as_index=False)
        .agg(total=("monto_pen", "sum"))
        .sort_values("fecha")
    )
    gasto_diario = [
        GastoDiario(fecha=str(r["fecha"]), total=round(float(r["total"]), 2))
        for _, r in diario_df.iterrows()
    ]

    resumen = ResumenGastos(
        gasto_total=gasto_total,
        promedio_diario=promedio_diario,
        cantidad_movimientos=len(df),
        presupuesto_consumido_pct=pct_presupuesto,
        estado_presupuesto=estado_presupuesto,
        media_transaccion=media_tx,
        desviacion_estandar=desviacion_tx,
        por_categoria=por_categoria,
        gasto_diario=gasto_diario,
    )

    hormigas = _detectar_gastos_hormiga(df, modo)
    duplicados = _detectar_cobros_duplicados(df)
    suscripciones = _detectar_suscripciones_recurrentes(df)

    total_fugas = round(
        sum(h.total_acumulado for h in hormigas)
        + sum(d.monto for d in duplicados)
        + sum(s.monto_mensual for s in suscripciones),
        2,
    )
    radar = RadarFugas(
        total_fugas_estimado=total_fugas,
        gastos_hormiga=hormigas,
        cobros_duplicados=duplicados,
        suscripciones_recurrentes=suscripciones,
    )

    return resumen, radar, z_scores
