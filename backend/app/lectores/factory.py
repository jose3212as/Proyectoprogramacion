"""Fábrica polimórfica de lectores según la extensión del archivo."""

from __future__ import annotations

from pathlib import Path

from app.lectores.base import LectorEstadoCuenta
from app.lectores.lector_csv import LectorCSV
from app.lectores.lector_pdf import LectorPDF

_REGISTRO_LECTORES: dict[str, type[LectorEstadoCuenta]] = {
    ".csv": LectorCSV,
    ".pdf": LectorPDF,
}


def obtener_lector(nombre_archivo: str) -> LectorEstadoCuenta:
    """Retorna la instancia concreta de LectorEstadoCuenta según la extensión."""
    extension = Path(nombre_archivo).suffix.lower()
    clase_lector = _REGISTRO_LECTORES.get(extension)
    if clase_lector is None:
        soportados = ", ".join(sorted(_REGISTRO_LECTORES))
        raise ValueError(
            f"Formato '{extension or 'sin extensión'}' no soportado. Usa: {soportados}."
        )
    return clase_lector()
