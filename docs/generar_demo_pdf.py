"""Genera el archivo docs/estado_cuenta_demo.pdf a partir de docs/estado_cuenta_demo.csv."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generar_pdf_demo(csv_path: Path, pdf_path: Path) -> None:
    with csv_path.open("r", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )
    estilos = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "TituloBanco",
        parent=estilos["Heading1"],
        fontSize=15,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "SubBanco",
        parent=estilos["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        spaceAfter=8,
    )
    aviso_style = ParagraphStyle(
        "AvisoPromo",
        parent=estilos["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#64748B"),
        spaceBefore=10,
    )

    elementos = [
        Paragraph("BANCO NACIONAL DEL PERÚ — ESTADO DE CUENTA MENSUAL", titulo_style),
        Paragraph(
            "Titular: Carlos Mendoza Quispe | Cuenta Débito: **** 4821 | Ciudad Base: Ica | Periodo: Octubre 2026",
            sub_style,
        ),
        Paragraph(
            "AVISO INFORMATIVO: Aprovecha 20% de descuento en restaurantes pagando con tu tarjeta digital. "
            "Este texto publicitario debe ser ignorado por el lector PDF.",
            aviso_style,
        ),
        Spacer(1, 6 * mm),
    ]

    encabezados = ["ID", "Fecha", "Hora", "Comercio", "Ciudad", "Canal", "Monto", "Moneda", "Tipo"]
    datos_tabla = [encabezados]
    for fila in filas:
        datos_tabla.append(
            [
                fila["id"],
                fila["fecha"],
                fila["hora"],
                fila["comercio"],
                fila["ciudad"],
                fila["canal"],
                fila["monto"],
                fila["moneda"],
                fila["tipo"],
            ]
        )

    anchos = [14 * mm, 20 * mm, 12 * mm, 44 * mm, 21 * mm, 20 * mm, 16 * mm, 15 * mm, 20 * mm]
    tabla = Table(datos_tabla, colWidths=anchos, repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("ALIGN", (6, 1), (6, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(tabla)
    elementos.append(
        Paragraph(
            "Nota legal: Si desconoce alguna operación mostrada en este documento, comuníquese con su entidad bancaria.",
            aviso_style,
        )
    )

    doc.build(elementos)


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parent
    generar_pdf_demo(raiz / "estado_cuenta_demo.csv", raiz / "estado_cuenta_demo.pdf")
    print("PDF generado correctamente en:", raiz / "estado_cuenta_demo.pdf")
