"""Pruebas unitarias para la capa POO de lectores CSV y PDF (Unidad 3)."""

from __future__ import annotations

import pytest

from app.config import DEMO_CSV_PATH, DEMO_PDF_PATH
from app.lectores import (
    CompraOnline,
    CompraPresencial,
    LectorCSV,
    LectorPDF,
    ServicioBasico,
    Suscripcion,
    obtener_lector,
)


def test_fabrica_polimorfica_lectores() -> None:
    assert isinstance(obtener_lector("extracto.csv"), LectorCSV)
    assert isinstance(obtener_lector("EXTRACT.PDF"), LectorPDF)
    with pytest.raises(ValueError, match="no soportado"):
        obtener_lector("extracto.xlsx")


def test_lector_csv_demo_y_jerarquia_movimientos() -> None:
    lector = LectorCSV()
    movimientos = lector.leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    assert len(movimientos) == 24
    assert isinstance(movimientos[0], CompraPresencial)
    assert isinstance(movimientos[3], Suscripcion)
    assert isinstance(movimientos[10], CompraOnline)
    assert isinstance(movimientos[11], ServicioBasico)


def test_lector_pdf_extrae_misma_cantidad_que_csv() -> None:
    lector_csv = LectorCSV()
    lector_pdf = LectorPDF()
    movs_csv = lector_csv.leer(DEMO_CSV_PATH.read_bytes(), "estado_cuenta_demo.csv")
    movs_pdf = lector_pdf.leer(DEMO_PDF_PATH.read_bytes(), "estado_cuenta_demo.pdf")

    assert len(movs_pdf) == len(movs_csv)
    assert movs_pdf[0].comercio == movs_csv[0].comercio
    assert movs_pdf[19].monto == movs_csv[19].monto


def test_lector_pdf_bcp_tarjeta_visa_real_multilinea() -> None:
    """Valida formato real BCP Tarjeta VISA: caja sin líneas horizontales, fechas '20Oct',
    pagos con '-' descartados, columnas Soles/Dólares por X, intereses en pág. 2 y guía en pág. 3."""
    import io

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # --- Página 1: formato real BCP Tarjeta VISA ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, h - 55, "Estado de Cuenta Tarjeta VISA")
    c.setFont("Helvetica", 8)
    c.drawString(360, h - 65, "Ciclo de Facturacion  Del  Al")
    c.drawString(360, h - 80, "4349-25XX-XXXX-2832   28/09/26   25/10/26")

    # Barra naranja de encabezados + caja de movimientos sin líneas horizontales internas
    y_hdr = h - 220
    c.setFillColor(colors.HexColor("#E85D04"))
    c.rect(40, y_hdr - 22, 515, 22, stroke=1, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(43, y_hdr - 10, "Fecha de")
    c.drawString(43, y_hdr - 19, "proceso")
    c.drawString(86, y_hdr - 10, "Fecha de")
    c.drawString(86, y_hdr - 19, "consumo")
    c.drawString(230, y_hdr - 14, "Descripcion")
    c.drawString(395, y_hdr - 10, "Tipo de")
    c.drawString(395, y_hdr - 19, "Operacion")
    c.drawString(452, y_hdr - 14, "Soles")
    c.drawString(508, y_hdr - 14, "Dolares")

    # Caja principal con separadores verticales únicamente
    y_box_bottom = 180
    c.setStrokeColor(colors.black)
    c.rect(40, y_box_bottom, 515, (y_hdr - 22) - y_box_bottom, stroke=1, fill=0)
    for vx in (82, 125, 445, 500):
        c.line(vx, y_hdr, vx, y_box_bottom)

    c.setFillColor(colors.black)
    c.setFont("Courier", 8)
    filas_p1 = [
        ("", "", "SALDO ANTERIOR", "", "3,026.57", ""),
        ("", "", "JOSE CORONADO   434925XXXXXX2832", "", "", ""),
        ("20Oct", "20Oct", "PAGO BANCA MOVIL", "PAGO", "200.00-", ""),
        ("20Oct", "20Oct", "PAGO000428910478", "PAGOSERVIC", "500.00", ""),
        ("20Oct", "20Oct", "PAGO000428911458", "PAGOSERVIC", "500.00", ""),
        ("20Oct", "20Oct", "PAGO000428914556", "PAGOSERVIC", "500.00", ""),
        ("20Oct", "20Oct", "PAGO000428903637", "PAGOSERVIC", "500.00", ""),
        ("20Oct", "20Oct", "TARJ000075187638", "PAGOSERVIC", "861.40", ""),
        ("20Oct", "20Oct", "PAGO BANCA MOVIL", "PAGO", "1,500.00-", ""),
        ("20Oct", "20Oct", "PAGO BANCA MOVIL", "PAGO", "464.60-", ""),
        ("20Oct", "20Oct", "TARJ000075187638", "PAGOSERVIC", "5.00", ""),
        ("20Oct", "20Oct", "PAGO BANCA MOVIL", "PAGO", "861.97-", ""),
        ("21Oct", "21Oct", "PAGO000429291543", "PAGOSERVIC", "254.50", ""),
        ("22Oct", "22Oct", "NETFLIX.COM", "CONSUMO", "", "12.99"),
    ]
    y = y_hdr - 36
    for f1, f2, desc, tipo, sol, dol in filas_p1:
        if f1:
            c.drawString(44, y, f1)
        if f2:
            c.drawString(86, y, f2)
        c.drawString(130, y, desc)
        if tipo:
            c.drawString(392, y, tipo)
        if sol:
            c.drawRightString(496, y, sol)
        if dol:
            c.drawRightString(550, y, dol)
        y -= 13

    c.setFont("Helvetica-Bold", 8)
    c.drawString(40, 150, "¿Como calcular tu pago minimo?")
    c.drawString(120, 132, "86.69   118.55   0.00   205.24")
    c.showPage()

    # --- Página 2: intereses + sub total + deuda ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, h - 55, "Estado de Cuenta Tarjeta VISA")
    c.setFillColor(colors.HexColor("#E85D04"))
    c.rect(40, y_hdr - 22, 515, 22, stroke=1, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(43, y_hdr - 10, "Fecha de")
    c.drawString(43, y_hdr - 19, "proceso")
    c.drawString(86, y_hdr - 10, "Fecha de")
    c.drawString(86, y_hdr - 19, "consumo")
    c.drawString(230, y_hdr - 14, "Descripcion")
    c.drawString(395, y_hdr - 10, "Tipo de")
    c.drawString(395, y_hdr - 19, "Operacion")
    c.drawString(452, y_hdr - 14, "Soles")
    c.drawString(508, y_hdr - 14, "Dolares")
    c.setStrokeColor(colors.black)
    c.rect(40, y_box_bottom, 515, (y_hdr - 22) - y_box_bottom, stroke=1, fill=0)
    for vx in (82, 125, 445, 500):
        c.line(vx, y_hdr, vx, y_box_bottom)

    c.setFillColor(colors.black)
    c.setFont("Courier", 8)
    c.drawString(130, y_hdr - 36, "INTERESES")
    c.drawRightString(496, y_hdr - 36, "118.55")
    c.drawString(130, y_hdr - 52, "SUB TOTAL")
    c.drawRightString(496, y_hdr - 52, "3,239.45")
    c.drawString(130, y_hdr - 76, "MONTO TOTAL FACTURADO")
    c.drawRightString(496, y_hdr - 76, "3,239.45")
    c.drawString(130, y_hdr - 105, "¿COMO ESTA COMPUESTA SU DEUDA?")
    c.drawString(130, y_hdr - 120, "Compras   3,239.45   95.89 %")
    c.showPage()

    # --- Página 3: guía informativa (debe ser ignorada) ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, h - 55, "Conoce el estado de cuenta de tu Tarjeta de Credito")
    c.setFont("Courier", 8)
    c.drawString(40, h - 90, "03Abr 31Mar PAGO EN VENTANILLA 220.00-")
    c.drawString(40, h - 105, "15Abr 12Abr E/S STOP 50.00")
    c.showPage()
    c.save()

    lector = LectorPDF()
    movs = lector.leer(buf.getvalue(), "bcp_visa_real.pdf", ciudad_default="Ica")

    # 7 PAGOSERVIC + 1 NETFLIX USD + 1 INTERESES = 9 cargos reales (0 pagos '-' ni filas guía)
    assert len(movs) == 9
    total_pen = round(sum(m.monto for m in movs if m.moneda == "PEN"), 2)
    assert total_pen == 3239.45
    assert movs[0].fecha == "2026-10-20"
    assert movs[0].comercio == "PAGO000428910478"
    assert isinstance(movs[0], ServicioBasico)
    usd_movs = [m for m in movs if m.moneda == "USD"]
    assert len(usd_movs) == 1
    assert usd_movs[0].monto == 12.99
    assert isinstance(usd_movs[0], Suscripcion)
    assert movs[-1].fecha == "2026-10-25"
    assert movs[-1].monto == 118.55
