"""Módulo de ingesta polimórfica de estados de cuenta (Unidad 3 - POO)."""

from app.lectores.base import (
    CompraOnline,
    CompraPresencial,
    LectorEstadoCuenta,
    Movimiento,
    ServicioBasico,
    Suscripcion,
    crear_movimiento,
)
from app.lectores.factory import obtener_lector
from app.lectores.lector_csv import LectorCSV
from app.lectores.lector_pdf import LectorPDF

__all__ = [
    "Movimiento",
    "CompraPresencial",
    "CompraOnline",
    "Suscripcion",
    "ServicioBasico",
    "LectorEstadoCuenta",
    "LectorCSV",
    "LectorPDF",
    "crear_movimiento",
    "obtener_lector",
]
