"""Funciones puras, lambdas (map/filter/reduce) y funciones de orden superior (Unidad 1)."""

from __future__ import annotations

from functools import reduce
from types import MappingProxyType
from typing import Callable, Iterable, Tuple

from app.config import TASAS_CAMBIO_PEN
from app.funcional.modelos import (
    TransaccionClasificada,
    TransaccionInmutable,
    TransaccionNormalizada,
)
from app.lectores.base import Movimiento

_REGLAS_CATEGORIA: MappingProxyType[str, tuple[str, ...]] = MappingProxyType(
    {
        "Suscripciones": ("netflix", "spotify", "prime", "disney", "hbo", "youtube", "icloud"),
        "Servicios": ("electroluz", "emapica", "sedapal", "luz", "agua", "internet", "claro", "movistar"),
        "Transporte": ("colectivo", "uber", "cabify", "grifo", "primax", "peaje", "taxi", "bus"),
        "Salud": ("botica", "inkafarma", "mifarma", "clinica", "farmacia", "salud"),
        "Comida": ("cafe", "menu", "polleria", "supermercado", "metro", "bodega", "restaurante", "rappi"),
        "Entretenimiento": ("cineplanet", "cine", "teatro", "ticket", "steam"),
    }
)


def a_transacciones_inmutables(movimientos: Iterable[Movimiento]) -> Tuple[TransaccionInmutable, ...]:
    """Convierte objetos Movimiento en una tupla de registros estrictamente inmutables."""
    return tuple(
        map(
            lambda m: TransaccionInmutable(
                id=m.id,
                fecha=m.fecha,
                hora=m.hora,
                comercio=m.comercio,
                ciudad=m.ciudad,
                canal=m.canal,
                monto_original=m.monto,
                moneda_original=m.moneda,
                tipo=m.tipo,
            ),
            movimientos,
        )
    )


def convertir_a_pen(
    monto: float,
    moneda: str,
    tasas: MappingProxyType[str, float] = TASAS_CAMBIO_PEN,
) -> float:
    """Función pura: convierte un monto de divisa origen a PEN sin efectos secundarios."""
    tasa = tasas.get(moneda.upper(), 1.0)
    return round(monto * tasa, 2)


def normalizar_moneda_lote(
    transacciones: Tuple[TransaccionInmutable, ...],
    tasas: MappingProxyType[str, float] = TASAS_CAMBIO_PEN,
) -> Tuple[TransaccionNormalizada, ...]:
    """Aplica map con expresión lambda para convertir divisas manteniendo inmutabilidad."""
    return tuple(
        map(
            lambda tx: TransaccionNormalizada(
                id=tx.id,
                fecha=tx.fecha,
                hora=tx.hora,
                comercio=tx.comercio,
                ciudad=tx.ciudad,
                canal=tx.canal,
                monto_original=tx.monto_original,
                moneda_original=tx.moneda_original,
                monto_pen=convertir_a_pen(tx.monto_original, tx.moneda_original, tasas),
                tipo=tx.tipo,
            ),
            transacciones,
        )
    )


def categorizar_transaccion(tx: TransaccionNormalizada) -> str:
    """Función pura: deduce la categoría financiera a partir del comercio y tipo."""
    if tx.tipo == "suscripcion":
        return "Suscripciones"
    if tx.tipo == "servicio":
        return "Servicios"

    comercio_low = tx.comercio.lower()
    coincidencias = tuple(
        filter(
            lambda par: any(palabra in comercio_low for palabra in par[1]),
            _REGLAS_CATEGORIA.items(),
        )
    )
    return coincidencias[0][0] if coincidencias else "Compras"


def crear_filtro_modo(
    modo: str,
) -> Callable[[TransaccionNormalizada, str], str]:
    """Función de orden superior: retorna un clasificador de etiqueta según el modo elegido."""

    def clasificar_normal(tx: TransaccionNormalizada, categoria: str) -> str:
        hora_int = int(tx.hora.split(":")[0]) if ":" in tx.hora else 12
        if tx.canal == "online" and (0 <= hora_int <= 5) and tx.monto_pen >= 200.0:
            return "atencion_seguridad"
        if tx.monto_pen <= 25.0 and categoria == "Comida":
            return "gasto_hormiga"
        return "regular"

    def clasificar_ahorro_estricto(tx: TransaccionNormalizada, categoria: str) -> str:
        if categoria == "Suscripciones":
            return "suscripcion_revisar"
        if tx.monto_pen <= 30.0 and categoria in {"Comida", "Entretenimiento"}:
            return "gasto_hormiga"
        if tx.monto_pen >= 100.0 and categoria in {"Compras", "Entretenimiento"}:
            return "recorte_sugerido"
        return "regular"

    return clasificar_ahorro_estricto if modo == "ahorro_estricto" else clasificar_normal


def categorizar_lote(
    transacciones: Tuple[TransaccionNormalizada, ...],
    etiquetador: Callable[[TransaccionNormalizada, str], str],
) -> Tuple[TransaccionClasificada, ...]:
    """Clasifica todas las transacciones usando map + lambda y la función etiquetadora."""

    def transformar(tx: TransaccionNormalizada) -> TransaccionClasificada:
        categoria = categorizar_transaccion(tx)
        return TransaccionClasificada(
            id=tx.id,
            fecha=tx.fecha,
            hora=tx.hora,
            comercio=tx.comercio,
            ciudad=tx.ciudad,
            canal=tx.canal,
            monto_original=tx.monto_original,
            moneda_original=tx.moneda_original,
            monto_pen=tx.monto_pen,
            tipo=tx.tipo,
            categoria=categoria,
            etiqueta_modo=etiquetador(tx, categoria),
        )

    return tuple(map(lambda tx: transformar(tx), transacciones))


def calcular_total_funcional(transacciones: Tuple[TransaccionClasificada, ...]) -> float:
    """Calcula el gasto total acumulado usando functools.reduce sobre una tupla inmutable."""
    return round(reduce(lambda acc, tx: acc + tx.monto_pen, transacciones, 0.0), 2)


def filtrar_por_etiqueta(
    transacciones: Tuple[TransaccionClasificada, ...],
    etiqueta: str,
) -> Tuple[TransaccionClasificada, ...]:
    """Retorna un subconjunto inmutable mediante filter y lambda."""
    return tuple(filter(lambda tx: tx.etiqueta_modo == etiqueta, transacciones))


def aplicar_pipeline_funcional(
    movimientos: Iterable[Movimiento],
    modo: str = "normal",
    tasas: MappingProxyType[str, float] = TASAS_CAMBIO_PEN,
) -> Tuple[TransaccionClasificada, ...]:
    """Ejecuta el pipeline funcional completo manteniendo inmutabilidad en cada etapa."""
    inmutables = a_transacciones_inmutables(movimientos)
    normalizadas = normalizar_moneda_lote(inmutables, tasas=tasas)
    etiquetador = crear_filtro_modo(modo)
    return categorizar_lote(normalizadas, etiquetador)
