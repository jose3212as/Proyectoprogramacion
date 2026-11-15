"""Módulo de analítica estadística con Pandas y NumPy y generación de reportes PDF (Unidad 3)."""

from app.analitica.estadisticas import calcular_analitica_y_fugas
from app.analitica.reporte_pdf import generar_reporte_auditoria_pdf

__all__ = ["calcular_analitica_y_fugas", "generar_reporte_auditoria_pdf"]
