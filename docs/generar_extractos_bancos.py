"""Genera 4 estados de cuenta bancarios realistas en PDF (Interbank, BCP y BBVA Peru).

Cada banco usa su propia maquetacion, tipografia, logotipo SVG, columnas reales
y resumenes financieros fieles a los extractos reales en Peru, renderizados a PDF
vectorial mediante Chrome/Edge Headless.

Archivos generados en docs/extractos_bancarios/:
  1. Interbank_Estado_Cuenta_Normal.pdf   (Normal - 0 alertas)
  2. BCP_Estado_Cuenta_Normal.pdf         (Normal - 0 alertas)
  3. BBVA_Tarjeta_Credito_Alertas.pdf     (Alertas: clonacion, madrugada USD, duplicado, hormiga)
  4. BBVA_Cuenta_Debito_Alertas.pdf       (Alertas: Z-score alto, fuera ciudad, duplicado, madrugada EUR, doble suscripcion)
"""

from __future__ import annotations

import html
import subprocess
import tempfile
from pathlib import Path

TASAS_PEN = {"PEN": 1.0, "USD": 3.75, "EUR": 4.05}

CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)


def _encontrar_navegador() -> Path:
    for ruta in CHROME_CANDIDATES:
        if ruta.is_file():
            return ruta
    raise FileNotFoundError("No se encontro Chrome ni Edge para renderizar PDF.")


def _renderizar_html_a_pdf(html_doc: str, pdf_destino: Path) -> None:
    navegador = _encontrar_navegador()
    pdf_destino.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "documento.html"
        html_path.write_text(html_doc, encoding="utf-8")
        cmd = [
            str(navegador),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_destino.resolve()}",
            html_path.resolve().as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0 or not pdf_destino.is_file():
            raise RuntimeError(f"Error al generar {pdf_destino.name}: {res.stderr}")


def _fmt_fecha_pe(fecha_iso: str) -> str:
    y, m, d = fecha_iso.split("-")
    return f"{d}/{m}/{y}"


def _pen_equiv(monto: float, moneda: str) -> float:
    return round(monto * TASAS_PEN.get(moneda, 1.0), 2)


# =============================================================================
# 1. INTERBANK — CUENTA SIMPLE SOLES (NORMAL / SIN ALERTAS)
# =============================================================================
def html_interbank_normal() -> str:
    # (nro, fecha_iso, hora, descripcion, lugar_canal, monto, moneda, es_abono)
    movs = [
        ("001841", "2026-11-01", "08:02", "ABONO DE HABERES - PLANILLA", "ICA - DIGITAL", 2650.00, "PEN", True),
        ("001912", "2026-11-01", "09:15", "COMPRA POS SUPERMERCADO METRO ICA", "ICA - POS", 122.50, "PEN", False),
        ("002034", "2026-11-02", "10:30", "PAGO SERV. ELECTROLUZ ICA", "ICA - APP", 94.20, "PEN", False),
        ("002109", "2026-11-03", "08:40", "PAGO SERV. EMAPICA AGUA POTABLE", "ICA - APP", 52.80, "PEN", False),
        ("002245", "2026-11-04", "13:10", "COMPRA POS RESTAURANTE EL CORDON", "ICA - POS", 74.00, "PEN", False),
        ("002388", "2026-11-05", "18:25", "COMPRA POS GRIFO PRIMAX PANAMERICANA", "ICA - POS", 115.00, "PEN", False),
        ("002490", "2026-11-06", "11:05", "COMPRA POS BOTICA INKAFARMA ICA", "ICA - POS", 68.90, "PEN", False),
        ("002604", "2026-11-07", "19:40", "COMPRA POS POLLERIA ROKYS ICA", "ICA - POS", 88.50, "PEN", False),
        ("002719", "2026-11-09", "09:50", "PAGO SERV. CLARO INTERNET HOGAR", "ICA - WEB", 95.00, "PEN", False),
        ("002851", "2026-11-10", "16:20", "COMPRA POS SUPERMERCADO PLAZA VEA ICA", "ICA - POS", 124.40, "PEN", False),
        ("002960", "2026-11-11", "12:15", "CARGO AUT. SPOTIFY PREMIUM", "ICA - ONLINE", 10.99, "USD", False),
        ("003088", "2026-11-12", "17:35", "COMPRA POS LIBRERIA TAI LOY ICA", "ICA - POS", 62.00, "PEN", False),
        ("003215", "2026-11-14", "20:10", "COMPRA POS CINEPLANET EL QUINDE ICA", "ICA - POS", 72.00, "PEN", False),
        ("003340", "2026-11-15", "14:05", "COMPRA POS RESTAURANTE LA OLLA ICA", "ICA - POS", 82.00, "PEN", False),
        ("003492", "2026-11-16", "09:25", "COMPRA POS GRIFO PRIMAX ICA SUR", "ICA - POS", 112.00, "PEN", False),
        ("003618", "2026-11-18", "18:50", "COMPRA POS SUPERMERCADO METRO ICA", "ICA - POS", 121.70, "PEN", False),
        ("003744", "2026-11-19", "11:40", "COMPRA POS FARMACIA MIFARMA ICA", "ICA - POS", 59.30, "PEN", False),
    ]

    saldo = 3480.00
    total_abonos = 0.0
    total_cargos = 0.0
    filas_html = [
        """<tr class="row-muted">
            <td>01/11/2026</td><td>—</td><td>SALDO ANTERIOR AL 31/10/2026</td><td>—</td><td>—</td>
            <td class="num">—</td><td class="num">—</td><td class="num">—</td><td class="num bold">3,480.00</td>
        </tr>"""
    ]

    for nro, fecha, hora, desc, loc, monto, moneda, es_abono in movs:
        eq = _pen_equiv(monto, moneda)
        if es_abono:
            saldo = round(saldo + eq, 2)
            total_abonos = round(total_abonos + eq, 2)
            c_pen, c_usd, abo = "—", "—", f"{monto:,.2f}"
            cls = "row-abono"
        else:
            saldo = round(saldo - eq, 2)
            total_cargos = round(total_cargos + eq, 2)
            c_pen = f"{monto:,.2f}" if moneda == "PEN" else "—"
            c_usd = f"US$ {monto:,.2f}" if moneda == "USD" else "—"
            abo = "—"
            cls = ""

        filas_html.append(
            f"""<tr class="{cls}">
                <td>{_fmt_fecha_pe(fecha)}</td>
                <td>{hora}</td>
                <td class="desc">{html.escape(desc)}</td>
                <td>{html.escape(loc)}</td>
                <td class="mono">{nro}</td>
                <td class="num">{c_pen}</td>
                <td class="num">{c_usd}</td>
                <td class="num green">{abo}</td>
                <td class="num">{saldo:,.2f}</td>
            </tr>"""
        )

    filas_html.append(
        f"""<tr class="row-total">
            <td>20/11/2026</td><td>—</td><td>SALDO FINAL CONTABLE DEL PERIODO</td><td>—</td><td>—</td>
            <td class="num">{total_cargos:,.2f}</td><td class="num">—</td><td class="num">{total_abonos:,.2f}</td>
            <td class="num">{saldo:,.2f}</td>
        </tr>"""
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 11mm 12mm 11mm 12mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Segoe UI", Arial, Helvetica, sans-serif;
    color: #1E293B;
    font-size: 8.2pt;
    line-height: 1.32;
    margin: 0;
    background: #FFFFFF;
  }}
  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 10px;
    border-bottom: 2.5px solid #009B3A;
    margin-bottom: 12px;
  }}
  .doc-title {{
    text-align: right;
  }}
  .doc-title h1 {{
    margin: 0;
    font-size: 14pt;
    font-weight: 700;
    color: #0039A6;
    letter-spacing: -0.2px;
  }}
  .doc-title p {{
    margin: 2px 0 0 0;
    font-size: 8pt;
    color: #475569;
  }}
  .info-grid {{
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
  }}
  .card {{
    flex: 1;
    border: 1px solid #D9E6DF;
    border-radius: 8px;
    padding: 9px 12px;
    background: #FFFFFF;
  }}
  .card-mint {{
    background: #F3FBF6;
    border-color: #BFE5CC;
  }}
  .card-label {{
    font-size: 6.7pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.45px;
    color: #009B3A;
    margin-bottom: 4px;
  }}
  .client-name {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 3px;
  }}
  .meta-line {{
    font-size: 7.6pt;
    color: #334155;
    margin: 1.5px 0;
  }}
  .kv {{
    display: flex;
    justify-content: space-between;
    font-size: 7.6pt;
    padding: 1.5px 0;
  }}
  .kv span:first-child {{ color: #475569; }}
  .kv span:last-child {{ font-weight: 600; color: #0F172A; }}
  .summary-row {{
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
  }}
  .metric {{
    flex: 1;
    border-radius: 8px;
    padding: 8px 10px;
    border: 1px solid #E2E8F0;
    background: #F8FAFC;
  }}
  .metric-primary {{
    background: #0039A6;
    border-color: #0039A6;
    color: #FFFFFF;
  }}
  .metric .m-lbl {{
    font-size: 6.6pt;
    text-transform: uppercase;
    letter-spacing: 0.35px;
    color: #64748B;
    font-weight: 600;
  }}
  .metric-primary .m-lbl {{ color: #C7DBFF; }}
  .metric .m-val {{
    font-size: 11pt;
    font-weight: 700;
    margin-top: 2px;
    font-variant-numeric: tabular-nums;
  }}
  .m-green {{ color: #009B3A; }}
  .sec-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
  }}
  .sec-head h2 {{
    margin: 0;
    font-size: 9pt;
    font-weight: 700;
    color: #0039A6;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }}
  .sec-head span {{
    font-size: 7.2pt;
    color: #64748B;
  }}
  table.movs {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.1pt;
  }}
  table.movs thead th {{
    background: #E8F6EE;
    color: #005C24;
    font-weight: 700;
    text-align: left;
    padding: 5.5px 4.5px;
    border-top: 1.2px solid #009B3A;
    border-bottom: 1.2px solid #009B3A;
    border-right: 0.4px solid #CEEBD9;
    border-left: 0.4px solid #CEEBD9;
    white-space: nowrap;
  }}
  table.movs thead th.num {{ text-align: right; }}
  table.movs tbody td {{
    padding: 4.3px 4.5px;
    border-bottom: 0.45px solid #E2E8F0;
    border-right: 0.35px solid #EEF2F6;
    border-left: 0.35px solid #EEF2F6;
    vertical-align: middle;
  }}
  table.movs tbody tr:nth-child(even) {{ background: #FAFDFB; }}
  table.movs tbody tr.row-muted {{ background: #F8FAFC; color: #475569; font-style: italic; }}
  table.movs tbody tr.row-abono {{ background: #F0FAF4; }}
  table.movs tbody tr.row-total td {{
    background: #EEF3FA;
    font-weight: 700;
    color: #0039A6;
    border-top: 1px solid #0039A6;
    border-bottom: 1.2px solid #0039A6;
  }}
  .desc {{ font-weight: 500; color: #0F172A; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .mono {{ font-family: Consolas, monospace; font-size: 6.9pt; color: #475569; }}
  .green {{ color: #008A33; font-weight: 600; }}
  .bold {{ font-weight: 700; }}
  .benefit-strip {{
    margin-top: 11px;
    padding: 7px 11px;
    border-radius: 6px;
    background: #F4F7FC;
    border-left: 3px solid #0039A6;
    font-size: 7pt;
    color: #334155;
  }}
  .footer {{
    margin-top: 10px;
    padding-top: 7px;
    border-top: 0.7px solid #CBD5E1;
    display: flex;
    justify-content: space-between;
    font-size: 6.6pt;
    color: #64748B;
  }}
</style>
</head>
<body>
  <div class="top-bar">
    <div>
      <svg width="155" height="32" viewBox="0 0 180 36" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="6" width="6" height="24" rx="2" fill="#0039A6"/>
        <rect x="9" y="12" width="6" height="18" rx="2" fill="#009B3A"/>
        <text x="22" y="27" font-family="Segoe UI, Arial, sans-serif" font-size="24" font-weight="800" fill="#009B3A" letter-spacing="-0.6">Interbank</text>
      </svg>
    </div>
    <div class="doc-title">
      <h1>Estado de Cuenta</h1>
      <p><strong>Cuenta Simple Soles</strong> &bull; Del 01/11/2026 al 20/11/2026</p>
    </div>
  </div>

  <div class="info-grid">
    <div class="card">
      <div class="card-label">Datos del Titular</div>
      <div class="client-name">CARLOS ANDRES MENDOZA QUISPE</div>
      <div class="meta-line">AV. SAN MARTIN 482 URB. SAN ISIDRO</div>
      <div class="meta-line">ICA - ICA - ICA</div>
      <div class="meta-line">Documento de Identidad: <strong>DNI ****4821</strong> &bull; C&oacute;digo Cliente: 08419204</div>
    </div>
    <div class="card card-mint">
      <div class="card-label">Informaci&oacute;n de la Cuenta</div>
      <div class="kv"><span>N&deg; de Cuenta:</span><span>898-3004819204</span></div>
      <div class="kv"><span>CCI:</span><span>003-898-013004819204-41</span></div>
      <div class="kv"><span>Tarjeta D&eacute;bito Visa:</span><span>4213 **** **** 6194</span></div>
      <div class="kv"><span>Moneda / Emisi&oacute;n:</span><span>Soles (S/) &bull; 21/11/2026</span></div>
    </div>
  </div>

  <div class="summary-row">
    <div class="metric">
      <div class="m-lbl">Saldo Inicial (31/10)</div>
      <div class="m-val">S/ 3,480.00</div>
    </div>
    <div class="metric">
      <div class="m-lbl">Total Abonos (+)</div>
      <div class="m-val m-green">S/ {total_abonos:,.2f}</div>
    </div>
    <div class="metric">
      <div class="m-lbl">Total Cargos (&minus;)</div>
      <div class="m-val">S/ {total_cargos:,.2f}</div>
    </div>
    <div class="metric metric-primary">
      <div class="m-lbl">Saldo Disponible Final</div>
      <div class="m-val">S/ {saldo:,.2f}</div>
    </div>
  </div>

  <div class="sec-head">
    <h2>Detalle de Movimientos del Periodo</h2>
    <span>Tipo de cambio referencial USD: S/ 3.75 &bull; Movimientos expresados en Soles (S/)</span>
  </div>

  <table class="movs">
    <thead>
      <tr>
        <th style="width:9.5%">Fecha Op.</th>
        <th style="width:5.5%">Hora</th>
        <th style="width:36.5%">Descripci&oacute;n del Movimiento</th>
        <th style="width:12%">Localidad / Canal</th>
        <th style="width:7%">N&deg; Op.</th>
        <th class="num" style="width:7.5%">Cargo (S/)</th>
        <th class="num" style="width:7.5%">Cargo (US$)</th>
        <th class="num" style="width:7%">Abono (S/)</th>
        <th class="num" style="width:7.5%">Saldo (S/)</th>
      </tr>
    </thead>
    <tbody>
      {"".join(filas_html)}
    </tbody>
  </table>

  <div class="benefit-strip">
    <strong>Informaci&oacute;n importante SBS:</strong> Los dep&oacute;sitos en esta cuenta se encuentran cubiertos por el Fondo de Seguro de Dep&oacute;sitos (FSD) hasta el monto m&aacute;ximo vigente. Si no reconoces alg&uacute;n consumo o deseas bloquear tu tarjeta al instante, hazlo desde tu <strong>Interbank App</strong> o llamando al <strong>(01) 311-9000</strong> (Lima) / <strong>0-801-00802</strong> (Provincias).
  </div>

  <div class="footer">
    <div>Banco Internacional del Per&uacute; S.A.A. - Interbank &bull; Av. Carlos Villar&aacute;n 140, La Victoria, Lima &bull; RUC 20100053455</div>
    <div>www.interbank.pe &bull; P&aacute;gina 1 de 1</div>
  </div>
</body>
</html>"""


# =============================================================================
# 2. BCP — BANCO DE CREDITO DEL PERU (CUENTA DE AHORROS DIGITAL - NORMAL)
# =============================================================================
def html_bcp_normal() -> str:
    # (nro, fecha_op, fecha_proc, hora, desc, oficina_canal, monto, es_abono)
    movs = [
        ("401290", "2026-11-01", "2026-11-01", "08:15", "TRANSF. HABERES EMPRESA", "BMOVIL ICA", 3200.00, True),
        ("401512", "2026-11-01", "2026-11-01", "10:12", "POS SUPERMERCADO PLAZA VEA ICA", "POS ICA", 136.80, False),
        ("402104", "2026-11-02", "2026-11-02", "09:05", "PAGO SERV. MOVISTAR FIBRA HOGAR", "BMOVIL ICA", 99.90, False),
        ("402688", "2026-11-03", "2026-11-03", "11:20", "PAGO SERV. ELECTROLUZ ICA", "BMOVIL ICA", 108.50, False),
        ("403110", "2026-11-04", "2026-11-04", "13:45", "POS MENU EJECUTIVO SAN MARTIN", "POS ICA", 54.00, False),
        ("403792", "2026-11-05", "2026-11-05", "17:10", "POS BOTICA MIFARMA ICA", "POS ICA", 74.50, False),
        ("404215", "2026-11-06", "2026-11-06", "12:00", "CARGO AUT. NETFLIX PERU", "WEB ICA", 44.90, False),
        ("404890", "2026-11-07", "2026-11-08", "15:30", "POS SODIMAC HOGAR ICA", "POS ICA", 132.00, False),
        ("405302", "2026-11-08", "2026-11-09", "19:15", "POS POLLERIA NORKYS ICA", "POS ICA", 92.00, False),
        ("406114", "2026-11-10", "2026-11-10", "08:55", "PAGO SERV. EMAPICA SERVICIO AGUA", "BMOVIL ICA", 56.40, False),
        ("406785", "2026-11-11", "2026-11-11", "16:40", "POS GRIFO PRIMAX AV SAN MARTIN", "POS ICA", 118.00, False),
        ("407240", "2026-11-12", "2026-11-12", "13:20", "POS RESTAURANTE EL PALLAR", "POS ICA", 84.00, False),
        ("407918", "2026-11-13", "2026-11-13", "18:05", "POS SUPERMERCADO METRO ICA", "POS ICA", 134.60, False),
        ("408503", "2026-11-14", "2026-11-15", "20:20", "POS CINEPLANET ICA", "POS ICA", 76.00, False),
        ("409127", "2026-11-15", "2026-11-16", "11:15", "POS TIENDA RIPLEY EL QUINDE", "POS ICA", 138.90, False),
        ("409864", "2026-11-17", "2026-11-17", "10:40", "POS CLINICA SAN PABLO ICA", "POS ICA", 120.00, False),
        ("410391", "2026-11-18", "2026-11-18", "17:50", "POS BODEGA LA ESPERANZA ICA", "POS ICA", 58.50, False),
        ("410945", "2026-11-19", "2026-11-19", "14:15", "WEB UBER VIAJE URBANO", "WEB ICA", 48.00, False),
    ]

    saldo = 4120.00
    total_abonos = 0.0
    total_cargos = 0.0
    filas_html = [
        """<tr class="saldo-row">
            <td>01/11/2026</td><td>01/11/2026</td><td>—</td><td>SALDO ANTERIOR</td><td>—</td><td>—</td>
            <td class="num">—</td><td class="num">—</td><td class="num bold">4,120.00</td>
        </tr>"""
    ]

    for nro, fop, fproc, hora, desc, canal, monto, es_abono in movs:
        if es_abono:
            saldo = round(saldo + monto, 2)
            total_abonos = round(total_abonos + monto, 2)
            cargo_s, abono_s = "—", f"{monto:,.2f}"
        else:
            saldo = round(saldo - monto, 2)
            total_cargos = round(total_cargos + monto, 2)
            cargo_s, abono_s = f"{monto:,.2f}-", "—"

        filas_html.append(
            f"""<tr>
                <td>{_fmt_fecha_pe(fop)}</td>
                <td>{_fmt_fecha_pe(fproc)}</td>
                <td>{hora}</td>
                <td class="desc">{html.escape(desc)}</td>
                <td>{html.escape(canal)}</td>
                <td class="mono">{nro}</td>
                <td class="num cargo">{cargo_s}</td>
                <td class="num abono">{abono_s}</td>
                <td class="num">{saldo:,.2f}</td>
            </tr>"""
        )

    filas_html.append(
        f"""<tr class="final-row">
            <td>20/11/2026</td><td>20/11/2026</td><td>—</td><td>SALDO FINAL CONTABLE</td><td>—</td><td>—</td>
            <td class="num">{total_cargos:,.2f}-</td><td class="num">{total_abonos:,.2f}</td><td class="num">{saldo:,.2f}</td>
        </tr>"""
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 11mm 11mm 11mm 11mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    color: #1A2433;
    font-size: 7.8pt;
    line-height: 1.28;
    margin: 0;
    background: #FFFFFF;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 2.5px solid #FF7800;
    margin-bottom: 10px;
  }}
  .header-right {{
    text-align: right;
  }}
  .header-right .title {{
    font-size: 12.5pt;
    font-weight: 800;
    color: #002A8D;
    letter-spacing: 0.4px;
  }}
  .header-right .sub {{
    font-size: 7.6pt;
    color: #4A5568;
    margin-top: 2px;
  }}
  .envelope {{
    display: flex;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 10px;
  }}
  .postal {{
    width: 47%;
    padding: 8px 10px;
    border: 0.8px solid #D2DBE8;
    background: #FAFBFD;
  }}
  .postal .name {{
    font-size: 8.6pt;
    font-weight: 700;
    color: #002A8D;
    margin-bottom: 3px;
  }}
  .postal div {{
    font-size: 7.4pt;
    color: #2D3748;
  }}
  .acct-box {{
    width: 53%;
    border: 0.8px solid #002A8D;
  }}
  .acct-box-head {{
    background: #002A8D;
    color: #FFFFFF;
    font-size: 7pt;
    font-weight: 700;
    padding: 3.5px 8px;
    letter-spacing: 0.4px;
  }}
  .acct-box-body {{
    padding: 5px 8px;
  }}
  .acct-row {{
    display: flex;
    justify-content: space-between;
    font-size: 7.3pt;
    padding: 1.5px 0;
    border-bottom: 0.35px dotted #CBD5E1;
  }}
  .acct-row:last-child {{ border-bottom: none; }}
  .acct-row span:first-child {{ color: #4A5568; font-weight: 600; }}
  .acct-row span:last-child {{ color: #0F172A; font-weight: 700; font-family: Consolas, monospace; }}

  .equation {{
    display: flex;
    border: 0.8px solid #B8C7DE;
    border-top: 2px solid #002A8D;
    margin-bottom: 11px;
    background: #F4F7FC;
  }}
  .eq-cell {{
    flex: 1;
    padding: 6px 8px;
    border-right: 0.6px solid #CBD5E1;
    text-align: center;
  }}
  .eq-cell:last-child {{
    border-right: none;
    background: #E8EFFA;
  }}
  .eq-cell .lbl {{
    font-size: 6.4pt;
    font-weight: 700;
    color: #4A5568;
    text-transform: uppercase;
  }}
  .eq-cell .val {{
    font-size: 9.2pt;
    font-weight: 700;
    color: #0F172A;
    margin-top: 2px;
    font-variant-numeric: tabular-nums;
  }}
  .eq-cell:last-child .val {{ color: #002A8D; }}

  .sec-bar {{
    background: #002A8D;
    color: #FFFFFF;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 4px 8px;
    letter-spacing: 0.4px;
    display: flex;
    justify-content: space-between;
  }}
  table.bcp {{
    width: 100%;
    border-collapse: collapse;
    font-size: 6.9pt;
  }}
  table.bcp thead th {{
    background: #EBF0F8;
    color: #002A8D;
    font-weight: 700;
    text-align: left;
    padding: 4.5px 4px;
    border-bottom: 1px solid #002A8D;
    border-right: 0.35px solid #D2DBE8;
    border-left: 0.35px solid #D2DBE8;
    white-space: nowrap;
  }}
  table.bcp thead th.num {{ text-align: right; }}
  table.bcp tbody td {{
    padding: 3.9px 4px;
    border-bottom: 0.4px solid #DFE6F0;
    border-right: 0.35px solid #EDF1F7;
    border-left: 0.35px solid #EDF1F7;
  }}
  table.bcp tbody tr:nth-child(even) {{ background: #F9FBFD; }}
  table.bcp tbody tr.saldo-row td {{ background: #F1F5FA; font-weight: 600; color: #334155; }}
  table.bcp tbody tr.final-row td {{
    background: #E8EFFA;
    font-weight: 700;
    color: #002A8D;
    border-top: 1px solid #002A8D;
    border-bottom: 1.2px solid #002A8D;
  }}
  .desc {{ font-family: Consolas, "Courier New", monospace; font-size: 6.8pt; color: #0F172A; }}
  .mono {{ font-family: Consolas, monospace; font-size: 6.8pt; color: #475569; }}
  .num {{ text-align: right; font-family: Consolas, monospace; font-size: 6.9pt; white-space: nowrap; }}
  .cargo {{ color: #1E293B; }}
  .abono {{ color: #047857; font-weight: 700; }}
  .bold {{ font-weight: 700; }}

  .bcp-note {{
    margin-top: 10px;
    padding: 7px 9px;
    border: 0.6px solid #CBD5E1;
    border-left: 3px solid #FF7800;
    background: #FFFBF7;
    font-size: 6.8pt;
    color: #334155;
  }}
  .footer {{
    margin-top: 8px;
    padding-top: 6px;
    border-top: 0.8px solid #002A8D;
    display: flex;
    justify-content: space-between;
    font-size: 6.4pt;
    color: #4A5568;
  }}
</style>
</head>
<body>
  <div class="header">
    <div>
      <svg width="138" height="34" viewBox="0 0 150 38" xmlns="http://www.w3.org/2000/svg">
        <polygon points="2,7 14,7 22,19 14,31 2,31 10,19" fill="#FF7800"/>
        <polygon points="15,12 22,12 27,19 22,26 15,26 20,19" fill="#FF7800" opacity="0.88"/>
        <text x="33" y="28" font-family="Arial Black, Arial, sans-serif" font-size="25" font-weight="900" fill="#002A8D" letter-spacing="0.5">BCP</text>
      </svg>
    </div>
    <div class="header-right">
      <div class="title">ESTADO DE CUENTA</div>
      <div class="sub">CUENTA DE AHORROS DIGITAL SOLES &bull; P&Aacute;GINA 1 DE 1</div>
    </div>
  </div>

  <div class="envelope">
    <div class="postal">
      <div class="name">SR(A). PAREDES HUAMAN VALERIA SOFIA</div>
      <div>CAL. LIMA 315 INT. 204 - CERCADO</div>
      <div>ICA - ICA - ICA</div>
      <div style="margin-top:4px;">C&Oacute;DIGO CLIENTE: <strong>00489217</strong> &bull; DOC: <strong>DNI ****7319</strong></div>
    </div>
    <div class="acct-box">
      <div class="acct-box-head">DATOS DE LA CUENTA</div>
      <div class="acct-box-body">
        <div class="acct-row"><span>N&deg; DE CUENTA:</span><span>380-94821054-0-18</span></div>
        <div class="acct-row"><span>CCI:</span><span>002-380-194821054018-92</span></div>
        <div class="acct-row"><span>TARJETA D&Eacute;BITO:</span><span>4557 **** **** 3391</span></div>
        <div class="acct-row"><span>PERIODO:</span><span>01/11/2026 AL 20/11/2026</span></div>
        <div class="acct-row"><span>MONEDA / AGENCIA:</span><span>SOLES (S/) - ICA CENTRO</span></div>
      </div>
    </div>
  </div>

  <div class="equation">
    <div class="eq-cell">
      <div class="lbl">Saldo Anterior</div>
      <div class="val">S/ 4,120.00</div>
    </div>
    <div class="eq-cell">
      <div class="lbl">(+) Total Abonos</div>
      <div class="val">S/ {total_abonos:,.2f}</div>
    </div>
    <div class="eq-cell">
      <div class="lbl">(&minus;) Total Cargos</div>
      <div class="val">S/ {total_cargos:,.2f}</div>
    </div>
    <div class="eq-cell">
      <div class="lbl">(&minus;) ITF Periodo</div>
      <div class="val">S/ 0.00</div>
    </div>
    <div class="eq-cell">
      <div class="lbl">(=) Saldo Contable</div>
      <div class="val">S/ {saldo:,.2f}</div>
    </div>
  </div>

  <div class="sec-bar">
    <span>DETALLE DE OPERACIONES DEL PERIODO</span>
    <span>LOS CARGOS SE IDENTIFICAN CON SIGNO (-)</span>
  </div>

  <table class="bcp">
    <thead>
      <tr>
        <th style="width:9.5%">Fecha Op.</th>
        <th style="width:9.5%">Fecha Proc.</th>
        <th style="width:6%">Hora</th>
        <th style="width:30%">Descripci&oacute;n</th>
        <th style="width:12%">Oficina / Canal</th>
        <th style="width:7.5%">N&deg; Op.</th>
        <th class="num" style="width:8.5%">Cargos</th>
        <th class="num" style="width:8%">Abonos</th>
        <th class="num" style="width:9%">Saldo</th>
      </tr>
    </thead>
    <tbody>
      {"".join(filas_html)}
    </tbody>
  </table>

  <div class="bcp-note">
    <strong>AVISO IMPORTANTE BCP:</strong> Revise oportunamente las operaciones de su estado de cuenta. En caso de extrav&iacute;o, robo o consumos no reconocidos comun&iacute;quese de inmediato con nuestra <strong>Banca por Tel&eacute;fono al (01) 311-9898</strong> (atenci&oacute;n 24 horas) o bloquee su tarjeta desde Banca M&oacute;vil BCP. Dep&oacute;sitos cubiertos por el Fondo de Seguro de Dep&oacute;sitos (FSD) seg&uacute;n normativa SBS vigente.
  </div>

  <div class="footer">
    <div><strong>BANCO DE CR&Eacute;DITO DEL PER&Uacute; - BCP</strong> &bull; RUC 20100047218 &bull; Calle Centenario 156, La Molina, Lima 12</div>
    <div>www.viabcp.com &bull; Emisi&oacute;n: 21/11/2026</div>
  </div>
</body>
</html>"""


# =============================================================================
# 3. BBVA #1 — TARJETA DE CREDITO VISA CLASICA (PARA DETECTAR ALERTAS)
# =============================================================================
def html_bbva_credito_alertas() -> str:
    # (fecha, hora, concepto, lugar_canal, cuotas, monto, moneda)
    movs = [
        ("2026-11-01", "08:20", "CONSUMO POS CAFE TOSTADO ICA", "ICA - POS", "01/01", 13.50, "PEN"),
        ("2026-11-02", "10:15", "PAGO SERV. ELECTROLUZ ICA", "ICA - WEB", "01/01", 102.40, "PEN"),
        ("2026-11-03", "08:35", "CONSUMO POS CAFE TOSTADO ICA", "ICA - POS", "01/01", 14.00, "PEN"),
        ("2026-11-03", "19:10", "CONSUMO POS BODEGA EXPRESS ICA", "ICA - POS", "01/01", 16.50, "PEN"),
        ("2026-11-04", "12:00", "CARGO AUT. NETFLIX.COM", "ICA - ONLINE", "01/01", 44.90, "PEN"),
        ("2026-11-05", "08:25", "CONSUMO POS CAFE TOSTADO ICA", "ICA - POS", "01/01", 12.50, "PEN"),
        # Cobro duplicado (4 minutos)
        ("2026-11-05", "18:14", "CONSUMO POS SUPERMERCADO METRO ICA", "ICA - POS", "01/01", 164.80, "PEN"),
        ("2026-11-05", "18:18", "CONSUMO POS SUPERMERCADO METRO ICA", "ICA - POS", "01/01", 164.80, "PEN"),
        ("2026-11-06", "14:20", "CONSUMO POS POLLERIA ROKYS ICA", "ICA - POS", "01/01", 78.00, "PEN"),
        ("2026-11-07", "16:40", "CONSUMO POS BODEGA EXPRESS ICA", "ICA - POS", "01/01", 18.00, "PEN"),
        ("2026-11-08", "11:00", "CARGO AUT. SPOTIFY PREMIUM", "ICA - ONLINE", "01/01", 6.99, "USD"),
        ("2026-11-09", "08:40", "CONSUMO POS CAFE TOSTADO ICA", "ICA - POS", "01/01", 15.00, "PEN"),
        ("2026-11-10", "17:15", "CONSUMO POS BOTICA INKAFARMA ICA", "ICA - POS", "01/01", 58.60, "PEN"),
        # Viaje imposible: Ica 13:20 -> Trujillo 14:10 (50 min)
        ("2026-11-11", "13:20", "CONSUMO POS GRIFO PRIMAX ICA", "ICA - POS", "01/01", 95.00, "PEN"),
        ("2026-11-11", "14:10", "CONSUMO POS MALL AVENTURA TRUJILLO", "TRUJILLO - POS", "01/01", 410.00, "PEN"),
        ("2026-11-12", "18:30", "CONSUMO POS BODEGA EXPRESS ICA", "ICA - POS", "01/01", 14.50, "PEN"),
        ("2026-11-13", "09:10", "PAGO SERV. CLARO INTERNET HOGAR", "ICA - WEB", "01/01", 92.00, "PEN"),
        ("2026-11-14", "12:30", "CARGO AUT. DISNEY PLUS", "ICA - ONLINE", "01/01", 8.99, "USD"),
        # Compra madrugada en USD (Miami)
        ("2026-11-15", "03:22", "CONSUMO WEB ELECTROGLOBAL STORE USA", "MIAMI - WEB", "01/01", 280.00, "USD"),
        ("2026-11-16", "08:30", "CONSUMO POS CAFE TOSTADO ICA", "ICA - POS", "01/01", 13.00, "PEN"),
        ("2026-11-17", "19:45", "CONSUMO POS CINEPLANET EL QUINDE ICA", "ICA - POS", "01/01", 62.00, "PEN"),
        ("2026-11-18", "20:05", "CONSUMO POS BODEGA EXPRESS ICA", "ICA - POS", "01/01", 19.00, "PEN"),
    ]

    total_pen_only = round(sum(m[5] for m in movs if m[6] == "PEN"), 2)
    total_usd_only = round(sum(m[5] for m in movs if m[6] == "USD"), 2)
    total_eq_pen = round(sum(_pen_equiv(m[5], m[6]) for m in movs), 2)
    linea_total = 6500.00
    disponible = round(linea_total - total_eq_pen, 2)
    uso_pct = min(round((total_eq_pen / linea_total) * 100, 1), 100.0)

    filas_html = []
    for idx, (fecha, hora, concepto, lugar, cuotas, monto, moneda) in enumerate(movs, 1):
        col_pen = f"{monto:,.2f}" if moneda == "PEN" else "—"
        col_usd = f"{monto:,.2f}" if moneda == "USD" else "—"
        filas_html.append(
            f"""<tr>
                <td>{_fmt_fecha_pe(fecha)}</td>
                <td>{hora}</td>
                <td class="desc">{html.escape(concepto)}</td>
                <td>{html.escape(lugar)}</td>
                <td class="center">{cuotas}</td>
                <td class="num">{col_pen}</td>
                <td class="num">{col_usd}</td>
            </tr>"""
        )

    filas_html.append(
        f"""<tr class="total-row">
            <td colspan="5">TOTAL CONSUMOS DEL CICLO DE FACTURACION (EQ. S/ {total_eq_pen:,.2f})</td>
            <td class="num">S/ {total_pen_only:,.2f}</td>
            <td class="num">US$ {total_usd_only:,.2f}</td>
        </tr>"""
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 10mm 11mm 10mm 11mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Segoe UI", Arial, Helvetica, sans-serif;
    color: #121212;
    font-size: 7.7pt;
    line-height: 1.28;
    margin: 0;
    background: #FFFFFF;
  }}
  .top-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-bottom: 8px;
    border-bottom: 2px solid #072146;
    margin-bottom: 10px;
  }}
  .doc-meta {{
    text-align: right;
  }}
  .doc-meta .main {{
    font-size: 13pt;
    font-weight: 300;
    color: #072146;
    letter-spacing: 0.6px;
  }}
  .doc-meta .sub {{
    font-size: 8.2pt;
    font-weight: 700;
    color: #1464A5;
    margin-top: 1px;
  }}
  .doc-meta .num-card {{
    font-size: 7.4pt;
    color: #4A5568;
    font-family: Consolas, monospace;
    margin-top: 2px;
  }}
  .hero {{
    display: flex;
    gap: 12px;
    margin-bottom: 10px;
  }}
  .client-panel {{
    width: 48%;
    padding: 4px 2px;
  }}
  .client-panel .tag {{
    font-size: 6.5pt;
    font-weight: 700;
    color: #1464A5;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .client-panel .cname {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #072146;
    margin: 2px 0;
  }}
  .client-panel p {{
    margin: 1.5px 0;
    font-size: 7.4pt;
    color: #334155;
  }}
  .pay-panel {{
    width: 52%;
    background: #EDF5FC;
    border: 0.8px solid #BCD7EE;
    border-left: 4px solid #072146;
    padding: 8px 11px;
  }}
  .pay-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 5px;
    border-bottom: 0.6px solid #C6DCEF;
    margin-bottom: 6px;
  }}
  .pay-top .due-lbl {{
    font-size: 6.8pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #072146;
  }}
  .pay-top .due-pill {{
    background: #072146;
    color: #2DCCCD;
    font-weight: 700;
    font-size: 7.8pt;
    padding: 2.5px 8px;
    border-radius: 3px;
  }}
  .pay-grid {{
    display: flex;
    justify-content: space-between;
    gap: 8px;
  }}
  .pay-item .lbl {{ font-size: 6.6pt; color: #475569; }}
  .pay-item .val {{ font-size: 10pt; font-weight: 700; color: #072146; margin-top: 1px; font-variant-numeric: tabular-nums; }}
  .pay-item .val-sm {{ font-size: 8.6pt; font-weight: 700; color: #1464A5; margin-top: 2px; }}

  .tri-cards {{
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
  }}
  .mini-card {{
    flex: 1;
    border: 0.7px solid #D4DFEA;
    padding: 6px 8px;
    background: #FFFFFF;
  }}
  .mini-card h3 {{
    margin: 0 0 4px 0;
    font-size: 6.8pt;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: #072146;
    border-bottom: 0.6px solid #E2E8F0;
    padding-bottom: 2.5px;
  }}
  .mini-kv {{
    display: flex;
    justify-content: space-between;
    font-size: 7pt;
    padding: 1px 0;
  }}
  .mini-kv span:first-child {{ color: #64748B; }}
  .mini-kv span:last-child {{ font-weight: 700; color: #0F172A; font-variant-numeric: tabular-nums; }}
  .bar-bg {{
    height: 4px;
    background: #E2E8F0;
    margin-top: 4px;
    border-radius: 2px;
    overflow: hidden;
  }}
  .bar-fill {{
    height: 100%;
    background: #1464A5;
    width: {uso_pct}%;
  }}

  .sec-title {{
    font-size: 8pt;
    font-weight: 700;
    color: #072146;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    margin: 4px 0 4px 0;
    display: flex;
    justify-content: space-between;
  }}
  .sec-title span:last-child {{
    font-size: 6.8pt;
    font-weight: 400;
    color: #64748B;
    text-transform: none;
  }}
  table.bbva {{
    width: 100%;
    border-collapse: collapse;
    font-size: 6.85pt;
  }}
  table.bbva thead th {{
    background: #072146;
    color: #FFFFFF;
    font-weight: 600;
    text-align: left;
    padding: 4.5px 4.5px;
    border-right: 0.35px solid #1C3B66;
    border-left: 0.35px solid #1C3B66;
    white-space: nowrap;
  }}
  table.bbva thead th.num {{ text-align: right; }}
  table.bbva thead th.center {{ text-align: center; }}
  table.bbva tbody td {{
    padding: 3.35px 4.5px;
    border-bottom: 0.4px solid #E2E8F0;
    border-right: 0.35px solid #EDF2F7;
    border-left: 0.35px solid #EDF2F7;
  }}
  table.bbva tbody tr:nth-child(even) {{ background: #F8FAFD; }}
  table.bbva tbody tr.total-row td {{
    background: #EDF5FC;
    font-weight: 700;
    color: #072146;
    border-top: 1px solid #072146;
    border-bottom: 1.2px solid #072146;
  }}
  .desc {{ font-weight: 500; color: #0F172A; }}
  .center {{ text-align: center; color: #64748B; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}

  .alert-footer {{
    margin-top: 8px;
    padding: 6px 9px;
    background: #F4F7FA;
    border-left: 3px solid #2DCCCD;
    font-size: 6.6pt;
    color: #334155;
  }}
  .footer {{
    margin-top: 7px;
    padding-top: 5px;
    border-top: 0.7px solid #CBD5E1;
    display: flex;
    justify-content: space-between;
    font-size: 6.3pt;
    color: #64748B;
  }}
</style>
</head>
<body>
  <div class="top-header">
    <div>
      <svg width="118" height="30" viewBox="0 0 132 34" xmlns="http://www.w3.org/2000/svg">
        <text x="0" y="27" font-family="Arial Black, Segoe UI, Arial, sans-serif" font-size="27" font-weight="900" fill="#072146" letter-spacing="0.3">BBV</text>
        <text x="64" y="23" font-family="Arial Black, Segoe UI, Arial, sans-serif" font-size="26" font-weight="900" fill="#072146">A</text>
        <text x="90" y="27" font-family="Segoe UI, Arial, sans-serif" font-size="9" font-weight="600" fill="#1464A5">Per&uacute;</text>
      </svg>
    </div>
    <div class="doc-meta">
      <div class="main">ESTADO DE CUENTA</div>
      <div class="sub">Tarjeta de Cr&eacute;dito Visa Cl&aacute;sica</div>
      <div class="num-card">N&deg; 4557 **** **** 9034 &bull; Contrato 0011-0284-80009034</div>
    </div>
  </div>

  <div class="hero">
    <div class="client-panel">
      <div class="tag">Titular de la Tarjeta</div>
      <div class="cname">MENDOZA QUISPE, CARLOS ANDRES</div>
      <p>URB. PUENTE BLANCO ETAPA II MZ. C LT. 14</p>
      <p>ICA - ICA - ICA &bull; DNI ****4821</p>
      <p style="margin-top:4px;">Ciclo de facturaci&oacute;n: <strong>21/10/2026 al 20/11/2026</strong> &bull; Corte: <strong>20/11/2026</strong></p>
    </div>
    <div class="pay-panel">
      <div class="pay-top">
        <span class="due-lbl">&Uacute;ltimo D&iacute;a de Pago</span>
        <span class="due-pill">05 DIC 2026</span>
      </div>
      <div class="pay-grid">
        <div class="pay-item">
          <div class="lbl">Pago Total Soles</div>
          <div class="val">S/ {total_pen_only:,.2f}</div>
        </div>
        <div class="pay-item">
          <div class="lbl">Pago Total D&oacute;lares</div>
          <div class="val">US$ {total_usd_only:,.2f}</div>
        </div>
        <div class="pay-item">
          <div class="lbl">Pago M&iacute;nimo Ref.</div>
          <div class="val-sm">S/ 245.00</div>
        </div>
      </div>
    </div>
  </div>

  <div class="tri-cards">
    <div class="mini-card">
      <h3>L&iacute;nea de Cr&eacute;dito</h3>
      <div class="mini-kv"><span>L&iacute;nea Aprobada:</span><span>S/ {linea_total:,.2f}</span></div>
      <div class="mini-kv"><span>L&iacute;nea Utilizada:</span><span>S/ {total_eq_pen:,.2f}</span></div>
      <div class="mini-kv"><span>L&iacute;nea Disponible:</span><span>S/ {disponible:,.2f}</span></div>
      <div class="bar-bg"><div class="bar-fill"></div></div>
    </div>
    <div class="mini-card">
      <h3>Tasas y Comisiones</h3>
      <div class="mini-kv"><span>TEA Compras:</span><span>49.90%</span></div>
      <div class="mini-kv"><span>TCEA M&aacute;xima Ref.:</span><span>62.14%</span></div>
      <div class="mini-kv"><span>T.C. Referencial:</span><span>S/ 3.75 / US$</span></div>
    </div>
    <div class="mini-card">
      <h3>Puntos BBVA</h3>
      <div class="mini-kv"><span>Saldo Anterior:</span><span>4,210 pts</span></div>
      <div class="mini-kv"><span>Ganados en el Mes:</span><span>+620 pts</span></div>
      <div class="mini-kv"><span>Saldo Disponible:</span><span>4,830 pts</span></div>
    </div>
  </div>

  <div class="sec-title">
    <span>Detalle de Consumos y Operaciones del Periodo</span>
    <span>Bimoneda (Soles y D&oacute;lares) &bull; 22 operaciones registradas</span>
  </div>

  <table class="bbva">
    <thead>
      <tr>
        <th style="width:10%">Fecha Op.</th>
        <th style="width:6.5%">Hora</th>
        <th style="width:39.5%">Concepto / Establecimiento</th>
        <th style="width:15%">Lugar / Canal</th>
        <th class="center" style="width:7%">Cuotas</th>
        <th class="num" style="width:11%">Soles (S/)</th>
        <th class="num" style="width:11%">D&oacute;lares (US$)</th>
      </tr>
    </thead>
    <tbody>
      {"".join(filas_html)}
    </tbody>
  </table>

  <div class="alert-footer">
    <strong>Seguridad BBVA:</strong> Si detectas consumos no reconocidos, duplicados o fuera de tu ciudad habitual, apaga tu tarjeta de inmediato desde tu <strong>App BBVA</strong> o comun&iacute;cate las 24 horas con <strong>Banca por Tel&eacute;fono (01) 595-0000</strong>. Pagar el total del mes antes del &uacute;ltimo d&iacute;a de pago evita intereses compensatorios.
  </div>

  <div class="footer">
    <div><strong>Banco BBVA Per&uacute; S.A.</strong> &bull; Av. Rep&uacute;blica de Panam&aacute; 3055, San Isidro, Lima &bull; RUC 20100130204</div>
    <div>www.bbva.pe &bull; Emisi&oacute;n: 21/11/2026 &bull; P&aacute;gina 1 de 1</div>
  </div>
</body>
</html>"""


# =============================================================================
# 4. BBVA #2 — CUENTA INDEPENDENCIA SOLES / DEBITO (PARA DETECTAR ALERTAS)
# =============================================================================
def html_bbva_debito_alertas() -> str:
    # (nro, f_op, f_val, hora, desc, lugar_canal, monto, moneda, es_abono)
    movs = [
        ("781020", "2026-11-01", "2026-11-01", "09:10", "ABONO TRANSF. INTERBANCARIA", "ICA - WEB", 1200.00, "PEN", True),
        ("781145", "2026-11-01", "2026-11-01", "12:40", "COMPRA POS SUPERMERCADO PLAZA VEA ICA", "ICA - POS", 128.40, "PEN", False),
        # Doble suscripcion Prime Video (cargo 1)
        ("781302", "2026-11-02", "2026-11-02", "09:00", "CARGO AUT. AMAZON PRIME VIDEO", "ICA - ONLINE", 7.99, "USD", False),
        ("781490", "2026-11-03", "2026-11-03", "13:15", "CONSUMO WEB RAPPI COMIDA ICA", "ICA - ONLINE", 19.50, "PEN", False),
        ("781612", "2026-11-04", "2026-11-04", "08:50", "PAGO SERV. MOVISTAR INTERNET HOGAR", "ICA - APP", 89.00, "PEN", False),
        ("781840", "2026-11-05", "2026-11-05", "18:20", "COMPRA POS GRIFO PRIMAX ICA", "ICA - POS", 92.00, "PEN", False),
        ("781995", "2026-11-06", "2026-11-06", "14:05", "CONSUMO WEB RAPPI COMIDA ICA", "ICA - ONLINE", 21.00, "PEN", False),
        ("782150", "2026-11-07", "2026-11-07", "10:30", "PAGO SERV. EMAPICA AGUA POTABLE", "ICA - APP", 45.20, "PEN", False),
        # Cobro duplicado presencial (7 minutos)
        ("782311", "2026-11-08", "2026-11-08", "11:05", "COMPRA POS BOTICA INKAFARMA ICA", "ICA - POS", 89.50, "PEN", False),
        ("782314", "2026-11-08", "2026-11-08", "11:12", "COMPRA POS BOTICA INKAFARMA ICA", "ICA - POS", 89.50, "PEN", False),
        ("782590", "2026-11-09", "2026-11-09", "19:30", "COMPRA POS POLLERIA NORKYS ICA", "ICA - POS", 74.00, "PEN", False),
        ("782742", "2026-11-10", "2026-11-10", "13:50", "CONSUMO WEB RAPPI COMIDA ICA", "ICA - ONLINE", 18.00, "PEN", False),
        # Presencial fuera de ciudad (Arequipa)
        ("782918", "2026-11-11", "2026-11-11", "15:35", "COMPRA POS TIENDA SAGA FALABELLA", "AREQUIPA - POS", 245.00, "PEN", False),
        ("783104", "2026-11-12", "2026-11-12", "09:40", "PAGO SERV. ELECTROLUZ ICA", "ICA - APP", 98.60, "PEN", False),
        # Compra madrugada en EUR (Madrid)
        ("783289", "2026-11-13", "2026-11-13", "02:47", "CONSUMO WEB GAMINGKEYS EUROPA", "MADRID - ONLINE", 75.00, "EUR", False),
        ("783490", "2026-11-14", "2026-11-14", "17:10", "COMPRA POS SUPERMERCADO METRO ICA", "ICA - POS", 112.30, "PEN", False),
        ("783615", "2026-11-15", "2026-11-15", "13:05", "CONSUMO WEB RAPPI COMIDA ICA", "ICA - ONLINE", 22.00, "PEN", False),
        # Doble suscripcion Prime Video (cargo 2)
        ("783790", "2026-11-16", "2026-11-16", "09:05", "CARGO AUT. AMAZON PRIME VIDEO", "ICA - ONLINE", 7.99, "USD", False),
        # Monto anomalo Z-Score alto (diurna S/ 1,180)
        ("783952", "2026-11-17", "2026-11-17", "16:40", "CONSUMO WEB JOYERIA ORO FINO", "ICA - ONLINE", 1180.00, "PEN", False),
        ("784120", "2026-11-18", "2026-11-18", "12:25", "COMPRA POS RESTAURANTE EL PALLAR", "ICA - POS", 66.00, "PEN", False),
        ("784305", "2026-11-19", "2026-11-19", "18:45", "CONSUMO WEB UBER VIAJE URBANO", "ICA - ONLINE", 28.50, "PEN", False),
        ("784499", "2026-11-20", "2026-11-20", "11:30", "COMPRA POS BOTICA MIFARMA ICA", "ICA - POS", 52.00, "PEN", False),
    ]

    saldo = 4850.00
    total_abonos = 0.0
    total_cargos = 0.0
    filas_html = [
        """<tr class="saldo-row">
            <td>01/11/2026</td><td>01/11/2026</td><td>—</td><td>SALDO ANTERIOR AL 31/10/2026</td><td>—</td><td>—</td>
            <td class="num">—</td><td class="num">—</td><td class="num bold">4,850.00</td>
        </tr>"""
    ]

    for nro, fop, fval, hora, desc, lugar, monto, moneda, es_abono in movs:
        eq = _pen_equiv(monto, moneda)
        if es_abono:
            saldo = round(saldo + eq, 2)
            total_abonos = round(total_abonos + eq, 2)
            cargo_str, abono_str = "—", f"S/ {monto:,.2f}"
            cls = "abono-row"
        else:
            saldo = round(saldo - eq, 2)
            total_cargos = round(total_cargos + eq, 2)
            if moneda == "PEN":
                cargo_str = f"S/ {monto:,.2f}"
            elif moneda == "USD":
                cargo_str = f"US$ {monto:,.2f}"
            else:
                cargo_str = f"EUR {monto:,.2f}"
            abono_str = "—"
            cls = ""

        filas_html.append(
            f"""<tr class="{cls}">
                <td>{_fmt_fecha_pe(fop)}</td>
                <td>{_fmt_fecha_pe(fval)}</td>
                <td>{hora}</td>
                <td class="desc">{html.escape(desc)}</td>
                <td>{html.escape(lugar)}</td>
                <td class="mono">{nro}</td>
                <td class="num">{cargo_str}</td>
                <td class="num abono">{abono_str}</td>
                <td class="num">{saldo:,.2f}</td>
            </tr>"""
        )

    filas_html.append(
        f"""<tr class="final-row">
            <td>20/11/2026</td><td>20/11/2026</td><td>—</td><td>SALDO CONTABLE FINAL AL 20/11/2026</td><td>—</td><td>—</td>
            <td class="num">S/ {total_cargos:,.2f}</td><td class="num">S/ {total_abonos:,.2f}</td><td class="num">{saldo:,.2f}</td>
        </tr>"""
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 10mm 11mm 10mm 11mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Segoe UI", Arial, Helvetica, sans-serif;
    color: #1A202C;
    font-size: 7.6pt;
    line-height: 1.25;
    margin: 0;
    background: #FFFFFF;
  }}
  .top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 7px;
    border-bottom: 2.5px solid #1464A5;
    margin-bottom: 9px;
  }}
  .top-right {{
    text-align: right;
  }}
  .top-right .t1 {{
    font-size: 12pt;
    font-weight: 700;
    color: #004481;
  }}
  .top-right .t2 {{
    font-size: 7.4pt;
    color: #4A5568;
    margin-top: 1px;
  }}
  .meta-box {{
    display: flex;
    gap: 10px;
    margin-bottom: 9px;
  }}
  .meta-left {{
    flex: 1;
    border: 0.7px solid #CBD9E8;
    background: #F7FAFD;
    padding: 7px 10px;
  }}
  .meta-left .tit {{
    font-size: 9pt;
    font-weight: 700;
    color: #004481;
  }}
  .meta-left div {{ font-size: 7.3pt; color: #334155; margin-top: 1.5px; }}
  .meta-right {{
    flex: 1.15;
    border: 0.7px solid #CBD9E8;
    padding: 7px 10px;
  }}
  .mr {{
    display: flex;
    justify-content: space-between;
    font-size: 7.2pt;
    padding: 1.2px 0;
  }}
  .mr span:first-child {{ color: #64748B; }}
  .mr span:last-child {{ font-weight: 700; color: #0F172A; font-family: Consolas, monospace; }}

  .saldo-strip {{
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
  }}
  .sb {{
    flex: 1;
    border: 0.7px solid #D1DFEC;
    border-top: 2.5px solid #1464A5;
    padding: 6px 8px;
    background: #FFFFFF;
  }}
  .sb-final {{
    border-top-color: #004481;
    background: #EDF5FC;
  }}
  .sb .l {{ font-size: 6.4pt; text-transform: uppercase; color: #64748B; font-weight: 700; }}
  .sb .v {{ font-size: 9.8pt; font-weight: 700; color: #004481; margin-top: 2px; font-variant-numeric: tabular-nums; }}

  .sec-bar {{
    font-size: 7.6pt;
    font-weight: 700;
    color: #004481;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
  }}
  .sec-bar span:last-child {{ font-size: 6.6pt; font-weight: 400; color: #64748B; text-transform: none; }}
  table.sav {{
    width: 100%;
    border-collapse: collapse;
    font-size: 6.65pt;
  }}
  table.sav thead th {{
    background: #E8F2FA;
    color: #004481;
    font-weight: 700;
    text-align: left;
    padding: 4.2px 3.8px;
    border-top: 1px solid #004481;
    border-bottom: 1px solid #004481;
    border-right: 0.35px solid #C8DCEF;
    border-left: 0.35px solid #C8DCEF;
    white-space: nowrap;
  }}
  table.sav thead th.num {{ text-align: right; }}
  table.sav tbody td {{
    padding: 3.15px 3.8px;
    border-bottom: 0.4px solid #E2E8F0;
    border-right: 0.35px solid #EDF2F7;
    border-left: 0.35px solid #EDF2F7;
  }}
  table.sav tbody tr:nth-child(even) {{ background: #F9FBFD; }}
  table.sav tbody tr.saldo-row td {{ background: #F1F5F9; font-weight: 600; color: #475569; }}
  table.sav tbody tr.abono-row td {{ background: #F0FBF6; }}
  table.sav tbody tr.final-row td {{
    background: #E8F2FA;
    font-weight: 700;
    color: #004481;
    border-top: 1px solid #004481;
    border-bottom: 1.2px solid #004481;
  }}
  .desc {{ font-weight: 500; color: #0F172A; }}
  .mono {{ font-family: Consolas, monospace; font-size: 6.5pt; color: #475569; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .abono {{ color: #047857; font-weight: 700; }}
  .bold {{ font-weight: 700; }}

  .fsd {{
    margin-top: 8px;
    padding: 5.5px 8px;
    background: #F4F8FC;
    border: 0.6px solid #D1DFEC;
    font-size: 6.4pt;
    color: #334155;
  }}
  .footer {{
    margin-top: 6px;
    padding-top: 5px;
    border-top: 0.7px solid #CBD5E1;
    display: flex;
    justify-content: space-between;
    font-size: 6.2pt;
    color: #64748B;
  }}
</style>
</head>
<body>
  <div class="top">
    <div>
      <svg width="114" height="28" viewBox="0 0 132 34" xmlns="http://www.w3.org/2000/svg">
        <text x="0" y="27" font-family="Arial Black, Segoe UI, Arial, sans-serif" font-size="27" font-weight="900" fill="#004481" letter-spacing="0.3">BBV</text>
        <text x="64" y="23" font-family="Arial Black, Segoe UI, Arial, sans-serif" font-size="26" font-weight="900" fill="#004481">A</text>
        <text x="90" y="27" font-family="Segoe UI, Arial, sans-serif" font-size="9" font-weight="600" fill="#1464A5">Per&uacute;</text>
      </svg>
    </div>
    <div class="top-right">
      <div class="t1">EXTRACTO DE CUENTA DE AHORROS</div>
      <div class="t2">Cuenta Independencia Soles &bull; Oficina 0284 - ICA &bull; Emisi&oacute;n: 21/11/2026</div>
    </div>
  </div>

  <div class="meta-box">
    <div class="meta-left">
      <div class="tit">TORRES SALAZAR, LUIS FERNANDO</div>
      <div>AV. CUTERVO 618 URB. LUREN</div>
      <div>ICA - ICA - ICA</div>
      <div>Documento: <strong>DNI ****6104</strong> &bull; Periodo: <strong>01/11/2026 al 20/11/2026</strong></div>
    </div>
    <div class="meta-right">
      <div class="mr"><span>N&deg; de Cuenta:</span><span>0011-0284-0200551924</span></div>
      <div class="mr"><span>CCI:</span><span>011-284-000200551924-47</span></div>
      <div class="mr"><span>Tarjeta D&eacute;bito Visa:</span><span>4557 **** **** 7742</span></div>
      <div class="mr"><span>Moneda / T.C. Ref.:</span><span>PEN (USD 3.75 / EUR 4.05)</span></div>
    </div>
  </div>

  <div class="saldo-strip">
    <div class="sb">
      <div class="l">Saldo Inicial (31/10)</div>
      <div class="v">S/ 4,850.00</div>
    </div>
    <div class="sb">
      <div class="l">Total Abonos (+)</div>
      <div class="v" style="color:#047857">S/ {total_abonos:,.2f}</div>
    </div>
    <div class="sb">
      <div class="l">Total Cargos Eq. (&minus;)</div>
      <div class="v">S/ {total_cargos:,.2f}</div>
    </div>
    <div class="sb sb-final">
      <div class="l">Saldo Contable Final</div>
      <div class="v">S/ {saldo:,.2f}</div>
    </div>
  </div>

  <div class="sec-bar">
    <span>Movimiento y Saldo a la Fecha</span>
    <span>Cargos en moneda extranjera debitados al tipo de cambio vigente</span>
  </div>

  <table class="sav">
    <thead>
      <tr>
        <th style="width:9%">Fecha Oper.</th>
        <th style="width:9%">Fecha Valor</th>
        <th style="width:5.5%">Hora</th>
        <th style="width:31.5%">Descripci&oacute;n / Concepto</th>
        <th style="width:13%">Canal / Ciudad</th>
        <th style="width:7%">N&deg; Oper.</th>
        <th class="num" style="width:9%">Cargo</th>
        <th class="num" style="width:8%">Abono</th>
        <th class="num" style="width:8%">Saldo</th>
      </tr>
    </thead>
    <tbody>
      {"".join(filas_html)}
    </tbody>
  </table>

  <div class="fsd">
    <strong>Fondo de Seguro de Dep&oacute;sitos (FSD):</strong> Los dep&oacute;sitos en esta cuenta cuentan con la cobertura del FSD conforme a la normativa SBS vigente. Ante cualquier operaci&oacute;n no reconocida, bloquee su tarjeta desde su App BBVA o comun&iacute;quese al <strong>(01) 595-0000</strong>.
  </div>

  <div class="footer">
    <div><strong>Banco BBVA Per&uacute; S.A.</strong> &bull; Av. Rep&uacute;blica de Panam&aacute; 3055, San Isidro, Lima &bull; RUC 20100130204</div>
    <div>www.bbva.pe &bull; P&aacute;gina 1 de 1</div>
  </div>
</body>
</html>"""


def main() -> None:
    salida = Path(__file__).resolve().parent / "extractos_bancarios"
    generadores = (
        ("Interbank_Estado_Cuenta_Normal.pdf", html_interbank_normal),
        ("BCP_Estado_Cuenta_Normal.pdf", html_bcp_normal),
        ("BBVA_Tarjeta_Credito_Alertas.pdf", html_bbva_credito_alertas),
        ("BBVA_Cuenta_Debito_Alertas.pdf", html_bbva_debito_alertas),
    )
    for nombre, fn in generadores:
        ruta = salida / nombre
        _renderizar_html_a_pdf(fn(), ruta)
        print(f"[OK] {ruta.name} ({ruta.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
