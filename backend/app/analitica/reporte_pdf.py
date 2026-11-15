"""Generador de reporte ejecutivo de auditoría en PDF para reclamos bancarios (RF-10)."""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas import AuditoriaResponse


def generar_reporte_auditoria_pdf(auditoria: AuditoriaResponse) -> bytes:
    """Construye un reporte PDF descargable con el diagnóstico completo de FinGuard."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "FGTitle",
        parent=estilos["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    subtitulo = ParagraphStyle(
        "FGSub",
        parent=estilos["Normal"],
        fontSize=9.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )
    seccion = ParagraphStyle(
        "FGSec",
        parent=estilos["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#0F766E"),
        spaceBefore=10,
        spaceAfter=6,
    )
    cuerpo = ParagraphStyle(
        "FGBody",
        parent=estilos["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
    )

    elementos = [
        Paragraph("FinGuard — Reporte Ejecutivo de Auditoría Financiera", titulo),
        Paragraph(
            f"ID Auditoría: {auditoria.audit_id} | Archivo: {auditoria.archivo} | "
            f"Ciudad habitual: {auditoria.perfil.ciudad_habitual} | Modo: {auditoria.perfil.modo}",
            subtitulo,
        ),
        Paragraph("1. Resumen Estadístico de Gastos", seccion),
        Paragraph(
            f"Gasto Total: <b>S/ {auditoria.resumen_gastos.gasto_total:,.2f}</b> | "
            f"Promedio Diario: <b>S/ {auditoria.resumen_gastos.promedio_diario:,.2f}</b> | "
            f"Consumo de Presupuesto: <b>{auditoria.resumen_gastos.presupuesto_consumido_pct:.1f}%</b> "
            f"(estado: {auditoria.resumen_gastos.estado_presupuesto}) | "
            f"Movimientos: <b>{auditoria.resumen_gastos.cantidad_movimientos}</b>",
            cuerpo,
        ),
        Spacer(1, 4 * mm),
    ]

    filas_cat = [["Categoría", "Movimientos", "Total (S/)", "% del Total"]]
    for cat in auditoria.resumen_gastos.por_categoria:
        filas_cat.append(
            [cat.categoria, str(cat.cantidad), f"S/ {cat.total:,.2f}", f"{cat.porcentaje:.1f}%"]
        )

    tabla_cat = Table(filas_cat, colWidths=[60 * mm, 35 * mm, 45 * mm, 35 * mm])
    tabla_cat.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    elementos.append(tabla_cat)

    elementos.append(Paragraph("2. Radar de Fugas de Dinero", seccion))
    elementos.append(
        Paragraph(
            f"Impacto estimado de fugas detectadas: <b>S/ {auditoria.radar_fugas.total_fugas_estimado:,.2f}</b>",
            cuerpo,
        )
    )
    for hormiga in auditoria.radar_fugas.gastos_hormiga:
        elementos.append(Paragraph(f"• Gasto hormiga: {hormiga.explicacion}", cuerpo))
    for dup in auditoria.radar_fugas.cobros_duplicados:
        elementos.append(Paragraph(f"• Cobro duplicado: {dup.explicacion}", cuerpo))
    for sub in auditoria.radar_fugas.suscripciones_recurrentes:
        elementos.append(Paragraph(f"• Suscripción: {sub.explicacion}", cuerpo))

    elementos.append(Paragraph("3. Escudo Antifraude (Inferencia Lógica SWI-Prolog)", seccion))
    elementos.append(
        Paragraph(
            f"Nivel de riesgo general: <b>{auditoria.escudo_antifraude.nivel_riesgo_general.upper()}</b> "
            f"({auditoria.escudo_antifraude.alertas_activas} alertas activas de {auditoria.escudo_antifraude.total_alertas})",
            cuerpo,
        )
    )
    Spacer(1, 3 * mm)

    if auditoria.escudo_antifraude.alertas:
        filas_alertas = [["Tx", "Fecha/Hora", "Regla Prolog", "Monto", "Estado", "Explicación"]]
        for al in auditoria.escudo_antifraude.alertas:
            estado = "Verificada (Fui yo)" if al.verificada_fui_yo else f"ACTIVA ({al.severidad})"
            filas_alertas.append(
                [
                    al.transaccion_id,
                    f"{al.fecha}\n{al.hora}",
                    al.regla_activada,
                    f"S/ {al.monto_pen:,.2f}",
                    estado,
                    Paragraph(al.explicacion, ParagraphStyle("Cell", fontSize=7.5, leading=10)),
                ]
            )
        tabla_al = Table(
            filas_alertas,
            colWidths=[16 * mm, 24 * mm, 33 * mm, 22 * mm, 28 * mm, 55 * mm],
            repeatRows=1,
        )
        tabla_al.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#991B1B")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#FECACA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elementos.append(tabla_al)
    else:
        elementos.append(Paragraph("No se detectaron alertas de fraude en este extracto.", cuerpo))

    doc.build(elementos)
    return buffer.getvalue()
