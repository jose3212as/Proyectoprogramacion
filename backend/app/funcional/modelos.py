"""Modelos inmutables (frozen dataclasses) para garantizar trazabilidad de auditoría (RNF-02)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TransaccionInmutable:
    """Registro financiero original inmutable."""

    id: str
    fecha: str
    hora: str
    comercio: str
    ciudad: str
    canal: str
    monto_original: float
    moneda_original: str
    tipo: str


@dataclass(frozen=True, slots=True)
class TransaccionNormalizada:
    """Transacción inmutable enriquecida con monto convertido a soles (PEN)."""

    id: str
    fecha: str
    hora: str
    comercio: str
    ciudad: str
    canal: str
    monto_original: float
    moneda_original: str
    monto_pen: float
    tipo: str


@dataclass(frozen=True, slots=True)
class TransaccionClasificada:
    """Transacción final del pipeline funcional con categoría y etiqueta según modo."""

    id: str
    fecha: str
    hora: str
    comercio: str
    ciudad: str
    canal: str
    monto_original: float
    moneda_original: str
    monto_pen: float
    tipo: str
    categoria: str
    etiqueta_modo: str
