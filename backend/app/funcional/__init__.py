"""Pipeline de programación funcional inmutable (Unidad 1)."""

from app.funcional.modelos import TransaccionClasificada, TransaccionInmutable, TransaccionNormalizada
from app.funcional.pipeline import (
    aplicar_pipeline_funcional,
    calcular_total_funcional,
    categorizar_lote,
    categorizar_transaccion,
    convertir_a_pen,
    crear_filtro_modo,
    normalizar_moneda_lote,
)

__all__ = [
    "TransaccionInmutable",
    "TransaccionNormalizada",
    "TransaccionClasificada",
    "convertir_a_pen",
    "normalizar_moneda_lote",
    "categorizar_transaccion",
    "categorizar_lote",
    "crear_filtro_modo",
    "calcular_total_funcional",
    "aplicar_pipeline_funcional",
]
