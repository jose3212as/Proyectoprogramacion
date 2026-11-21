"""Genera 2 estados de cuenta BCP Tarjeta VISA fieles al formato real oficial (2 paginas).

Imita exactamente el diseño del Estado de Cuenta Tarjeta VISA del BCP:
  - Matriz de puntos naranja/gris superior izquierda y logotipo >BCP> superior derecha
  - Bloque superior: titular, direccion, numero de tarjeta, ciclo de facturacion y fecha limite
  - Secciones: Linea de credito, Cuenta de cargo, Pagos y recuadro de penalidad
  - Tabla de movimientos con cabecera naranja BCP y caja abierta con divisores verticales (sin lineas horizontales entre filas) en tipografia Courier
  - Pie de pagina 1: ¿Como calcular tu pago minimo?, Plan de cuotas 6 meses, Programa de fidelidad y nota legal
  - Pagina 2: Intereses, Comisiones, SUB TOTAL, MONTO TOTAL FACTURADO y ¿COMO ESTA COMPUESTA SU DEUDA? (*)

Salida en docs/extractos_bancarios/:
  1. BCP_Visa_Real_Normal.pdf
  2. BCP_Visa_Real_Sospechoso_Estafa.pdf
"""

from __future__ import annotations

import html
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)

TASA_USD = 3.75


@dataclass(frozen=True)
class FilaBcpVisa:
    f_proc: str
    f_cons: str
    descripcion: str
    tipo_op: str
    soles: str = ""
    dolares: str = ""


@dataclass(frozen=True)
class BcpVisaConfig:
    archivo: str
    titular: str
    titular_corto: str
    direccion: str
    ciudad_linea: str
    codigo_postal: str
    codigo_cliente: str
    tarjeta_mask: str
    tarjeta_compacta: str
    ciclo_del: str
    ciclo_al: str
    fecha_limite: str
    linea_credito: float
    saldo_anterior_s: float
    intereses_s: float
    deuda_revolvente_min: float
    meses_pago_minimo: int
    filas: tuple[FilaBcpVisa, ...]


def _encontrar_navegador() -> Path:
    for ruta in CHROME_CANDIDATES:
        if ruta.is_file():
            return ruta
    raise FileNotFoundError("No se encontro Chrome ni Edge para generar PDF.")


def _renderizar_pdf(html_doc: str, destino: Path) -> None:
    navegador = _encontrar_navegador()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "bcp_visa.html"
        html_path.write_text(html_doc, encoding="utf-8")
        cmd = [
            str(navegador),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={destino.resolve()}",
            html_path.resolve().as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0 or not destino.is_file():
            raise RuntimeError(f"Error al generar {destino.name}: {res.stderr}")


def _svg_puntos_bcp() -> str:
    """Genera el patron decorativo de puntos naranja/gris de la esquina superior izquierda del BCP."""
    circulos = []
    # Patron diagonal escalonado similar al PDF oficial del BCP
    for row in range(4):
        for col in range(11):
            if row == 3 and col > 8:
                continue
            cx = 6 + col * 11 + (row % 2) * 5.5
            cy = 5 + row * 8.5
            es_naranja = (col + row) % 3 != 1
            color = "#E85D04" if es_naranja else "#9CA3AF"
            op = max(0.18, 0.92 - col * 0.072 - row * 0.08)
            circulos.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.1" fill="{color}" opacity="{op:.2f}"/>')
    return f'<svg width="135" height="36" viewBox="0 0 135 36" xmlns="http://www.w3.org/2000/svg">{"".join(circulos)}</svg>'


def _svg_logo_bcp() -> str:
    """Logotipo oficial >BCP> (chevron naranja izquierdo, BCP azul marino cursiva, chevron naranja derecho)."""
    return """<svg width="108" height="30" viewBox="0 0 116 36" xmlns="http://www.w3.org/2000/svg">
      <path d="M2,8 L12,8 L20,18 L12,28 L2,28 L10,18 Z" fill="#F26522"/>
      <text x="22" y="27" font-family="Arial Black, Arial, sans-serif" font-size="25" font-weight="900" font-style="italic" fill="#002A8D" letter-spacing="0.2">BCP</text>
      <path d="M90,8 L100,8 L108,18 L100,28 L90,28 L98,18 Z" fill="#F26522"/>
    </svg>"""


def _parse_num_bcp(txt: str) -> float:
    limpio = txt.strip().replace(",", "")
    if not limpio:
        return 0.0
    neg = limpio.endswith("-")
    val = float(limpio.rstrip("-"))
    return -val if neg else val


def construir_html_bcp_visa(cfg: BcpVisaConfig) -> str:
    # Totales exactos reconciliados
    delta_soles = sum(_parse_num_bcp(f.soles) for f in cfg.filas)
    subtotal_s = round(cfg.saldo_anterior_s + delta_soles + cfg.intereses_s, 2)
    subtotal_usd = round(sum(_parse_num_bcp(f.dolares) for f in cfg.filas), 2)
    utilizada_eq_s = round(subtotal_s + subtotal_usd * TASA_USD, 2)
    disponible_s = round(max(cfg.linea_credito - utilizada_eq_s, 0.0), 2)
    pago_min_s = round(cfg.deuda_revolvente_min + cfg.intereses_s, 2)
    pago_min_usd = round(subtotal_usd * 0.12, 2) if subtotal_usd > 0 else 0.0

    # Genera las lineas dentro de la caja abierta (posiciones de columna exactas mediante filas flex/grid o tabla sin bordes horizontales)
    # Usamos tabla HTML con bordes verticales en cada celda y SIN border-bottom en tbody td, identico al PDF real del BCP!
    filas_p1_html = [
        f"""<tr>
            <td class="c-f1"></td>
            <td class="c-f2"></td>
            <td class="c-desc">SALDO ANTERIOR</td>
            <td class="c-tipo"></td>
            <td class="c-sol">{cfg.saldo_anterior_s:,.2f}</td>
            <td class="c-dol"></td>
        </tr>""",
        f"""<tr>
            <td class="c-f1"></td>
            <td class="c-f2"></td>
            <td class="c-desc" style="padding-top:6px;">{html.escape(cfg.titular_corto)}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{html.escape(cfg.tarjeta_compacta)}</td>
            <td class="c-tipo"></td>
            <td class="c-sol"></td>
            <td class="c-dol"></td>
        </tr>""",
    ]

    for f in cfg.filas:
        filas_p1_html.append(
            f"""<tr>
                <td class="c-f1">{html.escape(f.f_proc)}</td>
                <td class="c-f2">{html.escape(f.f_cons)}</td>
                <td class="c-desc">{html.escape(f.descripcion)}</td>
                <td class="c-tipo">{html.escape(f.tipo_op)}</td>
                <td class="c-sol">{html.escape(f.soles)}</td>
                <td class="c-dol">{html.escape(f.dolares)}</td>
            </tr>"""
        )

    # Relleno vacio para mantener la altura clasica de la caja abierta del BCP hasta la parte inferior de la Pagina 1
    filas_relleno = max(0, 22 - len(cfg.filas))
    for _ in range(filas_relleno):
        filas_p1_html.append(
            """<tr class="filler">
                <td class="c-f1">&nbsp;</td><td class="c-f2">&nbsp;</td><td class="c-desc">&nbsp;</td>
                <td class="c-tipo">&nbsp;</td><td class="c-sol">&nbsp;</td><td class="c-dol">&nbsp;</td>
            </tr>"""
        )

    intereses_str = f"{cfg.intereses_s:,.2f}" if cfg.intereses_s > 0 else ""
    sub_usd_str = f"{subtotal_usd:,.2f}" if subtotal_usd > 0 else ""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 7mm 10mm 8mm 10mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    color: #111827;
    font-size: 7.5pt;
    line-height: 1.22;
    margin: 0;
    background: #FFFFFF;
  }}
  .page {{
    position: relative;
    width: 100%;
  }}
  .page-break {{
    page-break-after: always;
  }}
  .top-decor {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2px;
  }}
  .hdr-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 6px;
  }}
  .hdr-left {{
    width: 54%;
  }}
  .hdr-title {{
    font-size: 13pt;
    font-weight: 700;
    color: #002A8D;
    margin: 0 0 4px 0;
  }}
  .hdr-client {{
    font-size: 7.6pt;
    line-height: 1.5;
    color: #111827;
  }}
  .hdr-right {{
    width: 44%;
    font-size: 7pt;
  }}
  .pag-num {{
    text-align: right;
    font-size: 7.2pt;
    margin-bottom: 3px;
  }}
  .card-cycle-row {{
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }}
  .box-card {{
    flex: 1.25;
  }}
  .box-cycle {{
    flex: 1;
  }}
  .bcp-lbl {{
    font-size: 7pt;
    font-weight: 700;
    color: #002A8D;
    margin-bottom: 2px;
  }}
  .bcp-sub-lbl {{
    font-size: 6pt;
    color: #002A8D;
  }}
  .u-box {{
    border-left: 0.75px solid #111;
    border-right: 0.75px solid #111;
    border-bottom: 0.75px solid #111;
    padding: 3px 6px 2px 6px;
    font-size: 7.6pt;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: space-between;
  }}
  .due-wrap {{
    display: flex;
    justify-content: flex-end;
    margin-top: 5px;
  }}
  .due-box {{
    width: 46%;
  }}
  .due-val {{
    border-left: 0.75px solid #111;
    border-right: 0.75px solid #111;
    border-bottom: 0.75px solid #111;
    text-align: center;
    font-size: 9pt;
    font-weight: 700;
    padding: 2px 4px;
  }}

  .divider {{
    border-top: 0.75px solid #111;
    margin: 5px 0 4px 0;
  }}
  .credit-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 6px;
  }}
  .credit-left {{
    width: 60%;
  }}
  .credit-right {{
    width: 34%;
  }}
  .sec-navy {{
    font-size: 8.2pt;
    font-weight: 700;
    color: #002A8D;
    margin-bottom: 3px;
  }}
  .sec-navy small {{
    font-size: 6.2pt;
    font-weight: 600;
  }}
  .eq-labels {{
    display: flex;
    font-size: 6.4pt;
    color: #002A8D;
    margin-bottom: 2px;
  }}
  .eq-labels span {{ flex: 1; }}
  .eq-vals {{
    display: flex;
    border-bottom: 0.75px solid #111;
    border-right: 0.75px solid #111;
  }}
  .eq-vals div {{
    flex: 1;
    border-left: 0.75px solid #111;
    text-align: right;
    padding: 2px 6px;
    font-size: 7.8pt;
    font-weight: 700;
  }}
  .cargo-lines {{
    font-size: 6.6pt;
    color: #111;
    line-height: 1.55;
    margin-top: 3px;
  }}

  .pagos-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
  }}
  .pagos-left {{
    width: 38%;
  }}
  .pagos-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px 10px;
  }}
  .p-cell .p-lbl {{
    font-size: 6.4pt;
    font-weight: 700;
    color: #002A8D;
    margin-bottom: 1px;
  }}
  .p-cell .p-val {{
    border-left: 0.75px solid #111;
    border-right: 0.75px solid #111;
    border-bottom: 0.75px solid #111;
    text-align: right;
    padding: 2px 5px;
    font-size: 7.7pt;
    font-weight: 600;
  }}
  .penalty-box {{
    width: 55%;
    border: 0.75px solid #111;
    padding: 5px 8px;
    font-size: 6.8pt;
    line-height: 1.35;
    margin-top: 8px;
  }}

  /* TABLA PRINCIPAL NARANJA BCP (caja abierta sin lineas horizontales entre filas) */
  table.bcp-main {{
    width: 100%;
    border-collapse: collapse;
    border: 0.85px solid #111;
  }}
  table.bcp-main thead th {{
    background: #EA580C;
    color: #FFFFFF;
    font-family: Arial, sans-serif;
    font-size: 7pt;
    font-weight: 700;
    padding: 4px 4px;
    border-right: 0.75px solid #111;
    border-bottom: 0.85px solid #111;
    text-align: left;
    vertical-align: middle;
  }}
  table.bcp-main thead th.c-desc {{ text-align: center; }}
  table.bcp-main thead th:last-child {{ border-right: none; }}
  table.bcp-main tbody td {{
    font-family: "Courier New", Courier, monospace;
    font-size: 8pt;
    padding: 1.4px 4px;
    border-right: 0.75px solid #111;
    border-bottom: none;
    vertical-align: top;
    white-space: nowrap;
  }}
  table.bcp-main tbody td:last-child {{ border-right: none; }}
  table.bcp-main tbody tr.filler td {{ padding: 2px 4px; }}
  .c-f1 {{ width: 7.8%; }}
  .c-f2 {{ width: 8.2%; }}
  .c-desc {{ width: 51%; }}
  .c-tipo {{ width: 12.5%; }}
  .c-sol {{ width: 11.2%; text-align: right; }}
  .c-dol {{ width: 9.3%; text-align: right; }}

  /* Bloque inferior Pagina 1 */
  .min-calc {{
    margin-top: 5px;
  }}
  .min-grid-hdr {{
    display: flex;
    margin-left: 56px;
    font-size: 5.9pt;
    color: #111;
    text-align: center;
    align-items: flex-end;
    margin-bottom: 2px;
  }}
  .min-grid-hdr div {{ flex: 1; padding: 0 2px; }}
  .min-row {{
    display: flex;
    align-items: flex-end;
    margin-bottom: 4px;
  }}
  .min-row .mlbl {{
    width: 56px;
    font-size: 6.4pt;
    color: #002A8D;
  }}
  .min-row .mvals {{
    flex: 1;
    display: flex;
    gap: 6px;
  }}
  .min-row .mvals div {{
    flex: 1;
    border-left: 0.75px solid #111;
    border-right: 0.75px solid #111;
    border-bottom: 0.75px solid #111;
    text-align: right;
    padding: 1.5px 4px;
    font-size: 7.2pt;
  }}
  .blue-warn {{
    color: #002A8D;
    font-size: 7.1pt;
    margin: 4px 0;
  }}
  .plan-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
  }}
  .plan-left {{
    width: 60%;
  }}
  .plan-right {{
    width: 36%;
  }}
  .plan-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 6.8pt;
    margin-top: 2px;
  }}
  .plan-table th {{
    font-weight: 400;
    color: #111;
    font-size: 6.3pt;
    text-align: center;
    padding: 1px 2px;
  }}
  .plan-table td.plbl {{
    color: #002A8D;
    font-size: 6.3pt;
    border: none;
    width: 52px;
  }}
  .plan-table td.pval {{
    border-left: 0.75px solid #111;
    border-right: 0.75px solid #111;
    border-bottom: 0.75px solid #111;
    text-align: right;
    padding: 1.5px 4px;
  }}
  .legal-box {{
    border: 0.75px solid #111;
    padding: 6px 8px;
    font-size: 6.5pt;
    line-height: 1.4;
    margin-top: 5px;
  }}

  /* Pagina 2 */
  .p2-sep {{
    border-top: 0.75px solid #111;
  }}
  .p2-debt-block {{
    font-family: "Courier New", Courier, monospace;
    font-size: 7.8pt;
    line-height: 1.42;
    white-space: pre;
    padding: 8px 6px 0 6px;
  }}
</style>
</head>
<body>
  <!-- ======================== PAGINA 1 ======================== -->
  <div class="page page-break">
    <div class="top-decor">
      <div>{_svg_puntos_bcp()}</div>
      <div>{_svg_logo_bcp()}</div>
    </div>

    <div class="hdr-row">
      <div class="hdr-left">
        <div class="hdr-title">Estado de Cuenta Tarjeta VISA</div>
        <div class="hdr-client">
          <div>{html.escape(cfg.titular)}</div>
          <div>{html.escape(cfg.direccion)}</div>
          <div>{html.escape(cfg.ciudad_linea)}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{html.escape(cfg.codigo_postal)}</div>
          <div style="margin-top:4px;">{html.escape(cfg.codigo_cliente)}</div>
        </div>
      </div>
      <div class="hdr-right">
        <div class="pag-num">Pag 1 &nbsp;de 2</div>
        <div class="card-cycle-row">
          <div class="box-card">
            <div class="bcp-lbl">N&uacute;mero de tarjeta</div>
            <div class="u-box"><span>{html.escape(cfg.tarjeta_mask)}</span></div>
          </div>
          <div class="box-cycle">
            <div class="bcp-lbl">Ciclo de Facturaci&oacute;n<br/><span class="bcp-sub-lbl">Del &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Al (d&iacute;a de cierre)</span></div>
            <div class="u-box"><span>{cfg.ciclo_del}</span><span>{cfg.ciclo_al}</span></div>
          </div>
        </div>
        <div class="due-wrap">
          <div class="due-box">
            <div class="bcp-lbl">Fecha l&iacute;mite de pago</div>
            <div class="due-val">{cfg.fecha_limite}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="divider"></div>

    <div class="credit-row">
      <div class="credit-left">
        <div class="sec-navy">L&iacute;nea de cr&eacute;dito</div>
        <div class="eq-labels">
          <span>L&iacute;nea de cr&eacute;dito S/ &nbsp;&nbsp;&minus;</span>
          <span>L&iacute;nea utilizada S/ &nbsp;&nbsp;=</span>
          <span>Cr&eacute;dito disponible S/</span>
        </div>
        <div class="eq-vals">
          <div>{cfg.linea_credito:,.0f}</div>
          <div>{utilizada_eq_s:,.2f}</div>
          <div>{disponible_s:,.2f}</div>
        </div>
      </div>
      <div class="credit-right">
        <div class="sec-navy">Cuenta de cargo <small>(si escogiste esta opci&oacute;n)</small></div>
        <div class="cargo-lines">
          <div>En soles</div>
          <div>En d&oacute;lares</div>
        </div>
      </div>
    </div>

    <div class="pagos-row">
      <div class="pagos-left">
        <div class="sec-navy">Pagos</div>
        <div class="pagos-grid">
          <div class="p-cell">
            <div class="p-lbl">Pago m&iacute;nimo S/</div>
            <div class="p-val">{pago_min_s:,.2f}</div>
          </div>
          <div class="p-cell">
            <div class="p-lbl">Pago total S/</div>
            <div class="p-val">{subtotal_s:,.2f}</div>
          </div>
          <div class="p-cell">
            <div class="p-lbl">Pago m&iacute;nimo US$</div>
            <div class="p-val">{pago_min_usd:,.2f}</div>
          </div>
          <div class="p-cell">
            <div class="p-lbl">Pago total US$</div>
            <div class="p-val">{subtotal_usd:,.2f}</div>
          </div>
        </div>
      </div>
      <div class="penalty-box">
        En caso pague pasada la fecha m&aacute;xima de pago se le cobrar&aacute; una comisi&oacute;n de penalidad por pago atrasado de 0.0% del pago m&iacute;nimo (en soles min S/0 y max S/0 ; en d&oacute;lares min $0 y max $0 )
      </div>
    </div>

    <table class="bcp-main">
      <thead>
        <tr>
          <th class="c-f1">Fecha de<br/>proceso</th>
          <th class="c-f2">Fecha de<br/>consumo</th>
          <th class="c-desc">Descripci&oacute;n</th>
          <th class="c-tipo">Tipo de<br/>Operaci&oacute;n</th>
          <th class="c-sol" style="text-align:left;">Soles</th>
          <th class="c-dol" style="text-align:left;">D&oacute;lares</th>
        </tr>
      </thead>
      <tbody>
        {"".join(filas_p1_html)}
      </tbody>
    </table>

    <div class="min-calc">
      <div class="sec-navy" style="margin-bottom:1px;">&iquest;C&oacute;mo calcular tu pago m&iacute;nimo?</div>
      <div class="min-grid-hdr">
        <div>Deuda no financiada en cuotas (revolvente)</div>
        <div>Inter&eacute;s de la deuda no financiada en cuotas (inter&eacute;s deuda revolvente)</div>
        <div>Cuota del mes</div>
        <div>Comisiones, gastos y penalidades</div>
        <div>Sobregiro</div>
        <div>TOTAL</div>
      </div>
      <div class="min-row">
        <div class="mlbl">En soles</div>
        <div class="mvals">
          <div>{cfg.deuda_revolvente_min:,.2f}</div>
          <div>{cfg.intereses_s:,.2f}</div>
          <div>0.00</div>
          <div>0.00</div>
          <div>0.00</div>
          <div>{pago_min_s:,.2f}</div>
        </div>
      </div>
      <div class="min-row">
        <div class="mlbl">En d&oacute;lares</div>
        <div class="mvals">
          <div>{pago_min_usd:,.2f}</div>
          <div>0.00</div>
          <div>0.00</div>
          <div>0.00</div>
          <div>0.00</div>
          <div>{pago_min_usd:,.2f}</div>
        </div>
      </div>
      <div class="blue-warn">Si el cliente s&oacute;lo realiza el pago m&iacute;nimo, efectuar&aacute; un pago mayor por concepto de intereses, comisiones y gastos.</div>
    </div>

    <div class="plan-row">
      <div class="plan-left">
        <div class="sec-navy" style="font-size:7.2pt;margin-bottom:0;">Plan de cuotas de los pr&oacute;ximos 6 meses <small>(hasta lo consumido en el d&iacute;a de cierre)</small></div>
        <table class="plan-table">
          <thead>
            <tr><th></th><th>Nov-26</th><th>Dic-26</th><th>Ene-27</th><th>Feb-27</th><th>Mar-27</th><th>Abr-27</th></tr>
          </thead>
          <tbody>
            <tr><td class="plbl">En soles</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td></tr>
            <tr><td class="plbl">En d&oacute;lares</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td><td class="pval">0.00</td></tr>
          </tbody>
        </table>
      </div>
      <div class="plan-right">
        <div class="sec-navy" style="font-size:7.2pt;">Programa de fidelidad</div>
      </div>
    </div>

    <div class="legal-box">
      <div>LA COMISION DE MEMBRESIA ANUAL ES DE S/ 0.00</div>
      <div>(*) TEA Tasa Efectiva Anual. Las comisiones pendientes de pago no est&aacute;n incluidas.</div>
      <div>(**) La tasa que corresponde a cada una de las transacciones en cuotas se indica en el detalle de plan de cuotas.</div>
      <div>Para conocer la deuda total actualizada comun&iacute;quese a Banca por Tel&eacute;fono V&iacute;aBCP 3119898.</div>
    </div>
  </div>

  <!-- ======================== PAGINA 2 ======================== -->
  <div class="page">
    <div class="top-decor">
      <div>{_svg_puntos_bcp()}</div>
      <div>{_svg_logo_bcp()}</div>
    </div>

    <div class="hdr-row" style="margin-bottom:14px;">
      <div class="hdr-left">
        <div class="hdr-title">Estado de Cuenta Tarjeta VISA</div>
        <div class="hdr-client">
          <div>{html.escape(cfg.titular)}</div>
          <div>{html.escape(cfg.direccion)}</div>
          <div>{html.escape(cfg.ciudad_linea)}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{html.escape(cfg.codigo_postal)}</div>
          <div style="margin-top:4px;">{html.escape(cfg.codigo_cliente.split()[0])}</div>
        </div>
      </div>
      <div class="hdr-right">
        <div class="pag-num">Pag 2 &nbsp;de 2</div>
        <div class="card-cycle-row">
          <div class="box-card">
            <div class="bcp-lbl">N&uacute;mero de tarjeta</div>
            <div class="u-box"><span>{html.escape(cfg.tarjeta_mask)}</span></div>
          </div>
          <div class="box-cycle">
            <div class="bcp-lbl">Ciclo de Facturaci&oacute;n<br/><span class="bcp-sub-lbl">Del &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Al (d&iacute;a de cierre)</span></div>
            <div class="u-box"><span>{cfg.ciclo_del}</span><span>{cfg.ciclo_al}</span></div>
          </div>
        </div>
        <div class="due-wrap">
          <div class="due-box">
            <div class="bcp-lbl">Fecha l&iacute;mite de pago</div>
            <div class="due-val">{cfg.fecha_limite}</div>
          </div>
        </div>
      </div>
    </div>

    <table class="bcp-main">
      <thead>
        <tr>
          <th class="c-f1">Fecha de<br/>proceso</th>
          <th class="c-f2">Fecha de<br/>consumo</th>
          <th class="c-desc">Descripci&oacute;n</th>
          <th class="c-tipo">Tipo de<br/>Operaci&oacute;n</th>
          <th class="c-sol" style="text-align:left;">Soles</th>
          <th class="c-dol" style="text-align:left;">D&oacute;lares</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="c-f1"></td><td class="c-f2"></td>
          <td class="c-desc" style="padding-top:6px;">INTERESES</td>
          <td class="c-tipo"></td>
          <td class="c-sol" style="padding-top:6px;">{intereses_str}</td>
          <td class="c-dol"></td>
        </tr>
        <tr>
          <td class="c-f1"></td><td class="c-f2"></td>
          <td class="c-desc">COMISION POR USO DE CANALES</td>
          <td class="c-tipo"></td><td class="c-sol"></td><td class="c-dol"></td>
        </tr>
        <tr>
          <td class="c-f1"></td><td class="c-f2"></td>
          <td class="c-desc">SUB TOTAL</td>
          <td class="c-tipo"></td>
          <td class="c-sol">{subtotal_s:,.2f}</td>
          <td class="c-dol">{sub_usd_str}</td>
        </tr>
        <tr><td class="c-f1">&nbsp;</td><td class="c-f2"></td><td class="c-desc"></td><td class="c-tipo"></td><td class="c-sol"></td><td class="c-dol"></td></tr>
        <tr>
          <td class="c-f1"></td><td class="c-f2"></td>
          <td class="c-desc">ENVIO FISICO DE ESTADO DE CUENTA</td>
          <td class="c-tipo"></td><td class="c-sol"></td><td class="c-dol"></td>
        </tr>
        <tr>
          <td class="c-f1"></td><td class="c-f2"></td>
          <td class="c-desc">GASTO MENSUAL POR SEGURO DE DESGRAVAMEN</td>
          <td class="c-tipo"></td><td class="c-sol"></td><td class="c-dol"></td>
        </tr>
        <tr><td class="c-f1">&nbsp;</td><td class="c-f2"></td><td class="c-desc"></td><td class="c-tipo"></td><td class="c-sol"></td><td class="c-dol"></td></tr>
        <tr>
          <td class="c-f1"></td><td class="c-f2"></td>
          <td class="c-desc" style="padding-bottom:10px;">COMISION ANUAL POR MEMBRESIA</td>
          <td class="c-tipo"></td><td class="c-sol"></td><td class="c-dol"></td>
        </tr>
        <tr>
          <td class="c-f1 p2-sep"></td><td class="c-f2 p2-sep"></td>
          <td class="c-desc p2-sep" style="padding:3px 4px;">MONTO TOTAL FACTURADO</td>
          <td class="c-tipo p2-sep"></td>
          <td class="c-sol p2-sep" style="padding:3px 4px;">{subtotal_s:,.2f}</td>
          <td class="c-dol p2-sep" style="padding:3px 4px;">{sub_usd_str}</td>
        </tr>
        <tr>
          <td class="c-f1 p2-sep"></td><td class="c-f2 p2-sep"></td>
          <td class="c-desc p2-sep" colspan="4" style="white-space:normal;padding:10px 6px 190px 6px;">
            <div class="p2-debt-block">¿COMO ESTA COMPUESTA SU DEUDA? (*)

Descripcion          Saldo S/     TEA S/      Saldo US$   TEA US$

Compras            {subtotal_s:10,.2f}   95.89 %    {subtotal_usd:8,.2f}   76.90 %
Disposicion Efectivo     0.00  107.00 %        0.00   85.90 %
Compras Cuotas           0.00    (**)          0.00    (**)
Saldo Total        {subtotal_s:10,.2f}              {subtotal_usd:8,.2f}

INFORMACION IMPORTANTE:
Si solo realiza el pago mínimo de su deuda en soles y no realiza más
operaciones, esta se cancelará en {cfg.meses_pago_minimo} meses.</div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</body>
</html>"""


CONFIG_NORMAL = BcpVisaConfig(
    archivo="BCP_Visa_Real_Normal.pdf",
    titular="CARLOS ANDRES MENDOZA QUISPE",
    titular_corto="CARLOS MENDOZA",
    direccion="AV. CASTROVIRREYNA N.464",
    ciudad_linea="ICA ICA-ICA",
    codigo_postal="380",
    codigo_cliente="159,222    (*MJ9JX)",
    tarjeta_mask="4349-25XX-XXXX-2832",
    tarjeta_compacta="434925XXXXXX2832",
    ciclo_del="28/09/26",
    ciclo_al="25/10/26",
    fecha_limite="23/11/26",
    linea_credito=5720.00,
    saldo_anterior_s=1240.50,
    intereses_s=0.00,
    deuda_revolvente_min=95.50,
    meses_pago_minimo=24,
    filas=(
        FilaBcpVisa("01Oct", "01Oct", "PAGO BANCA MOVIL", "PAGO", "1,240.50-"),
        FilaBcpVisa("02Oct", "02Oct", "SUPERMERCADO METRO ICA", "CONSUMO", "118.80"),
        FilaBcpVisa("03Oct", "03Oct", "PAGO000428102340 ELECTROLUZ", "PAGOSERVIC", "96.40"),
        FilaBcpVisa("05Oct", "05Oct", "BOTICA INKAFARMA ICA", "CONSUMO", "68.50"),
        FilaBcpVisa("06Oct", "06Oct", "GRIFO PRIMAX PANAMERICANA", "CONSUMO", "112.00"),
        FilaBcpVisa("08Oct", "08Oct", "RESTAURANTE EL CORDON ICA", "CONSUMO", "82.00"),
        FilaBcpVisa("10Oct", "10Oct", "PAGO000428219081 CLARO HOGAR", "PAGOSERVIC", "95.00"),
        FilaBcpVisa("11Oct", "11Oct", "NETFLIX.COM", "CONSUMO", "44.90"),
        FilaBcpVisa("13Oct", "13Oct", "SUPERMERCADO PLAZA VEA ICA", "CONSUMO", "119.40"),
        FilaBcpVisa("15Oct", "15Oct", "POLLERIA ROKYS ICA", "CONSUMO", "89.00"),
        FilaBcpVisa("16Oct", "16Oct", "PAGO000428390112 EMAPICA", "PAGOSERVIC", "62.20"),
        FilaBcpVisa("18Oct", "18Oct", "CINEPLANET EL QUINDE ICA", "CONSUMO", "74.00"),
        FilaBcpVisa("19Oct", "19Oct", "FARMACIA MIFARMA ICA", "CONSUMO", "65.80"),
        FilaBcpVisa("21Oct", "21Oct", "TIENDA RIPLEY ICA", "CONSUMO", "120.00"),
        FilaBcpVisa("22Oct", "22Oct", "GRIFO PRIMAX ICA SUR", "CONSUMO", "108.00"),
        FilaBcpVisa("24Oct", "24Oct", "RESTAURANTE EL PALLAR ICA", "CONSUMO", "80.50"),
    ),
)

CONFIG_ESTAFA = BcpVisaConfig(
    archivo="BCP_Visa_Real_Sospechoso_Estafa.pdf",
    titular="JOSE ELMER CORONADO",
    titular_corto="JOSE CORONADO",
    direccion="AV. CASTROVIRREYNA N.464",
    ciudad_linea="ICA ICA-ICA",
    codigo_postal="380",
    codigo_cliente="159,222    (*MJ9JX)",
    tarjeta_mask="4349-25XX-XXXX-2832",
    tarjeta_compacta="434925XXXXXX2832",
    ciclo_del="28/09/26",
    ciclo_al="25/10/26",
    fecha_limite="23/11/26",
    linea_credito=5720.00,
    saldo_anterior_s=2150.00,
    intereses_s=94.60,
    deuda_revolvente_min=148.20,
    meses_pago_minimo=73,
    filas=(
        # Pago parcial/total del saldo anterior (se descarta como gasto)
        FilaBcpVisa("01Oct", "01Oct", "PAGO BANCA MOVIL", "PAGO", "2,150.00-"),
        # Gastos hormiga en Cafe Tostado Ica (x4)
        FilaBcpVisa("02Oct", "02Oct", "CAFE TOSTADO ICA 08:25", "CONSUMO", "14.50"),
        # Doble suscripcion Netflix en el mismo mes (cargo 1)
        FilaBcpVisa("03Oct", "03Oct", "NETFLIX.COM", "CONSUMO", "44.90"),
        FilaBcpVisa("04Oct", "04Oct", "PAGO000428910478 ELECTROLUZ", "PAGOSERVIC", "98.40"),
        FilaBcpVisa("05Oct", "05Oct", "CAFE TOSTADO ICA 08:30", "CONSUMO", "13.00"),
        # Cobro duplicado en Supermercado Metro Ica (4 minutos de diferencia)
        FilaBcpVisa("08Oct", "08Oct", "SUPERMERCADO METRO ICA 18:12", "CONSUMO", "168.50"),
        FilaBcpVisa("08Oct", "08Oct", "SUPERMERCADO METRO ICA 18:16", "CONSUMO", "168.50"),
        FilaBcpVisa("09Oct", "09Oct", "CAFE TOSTADO ICA 08:40", "CONSUMO", "15.00"),
        FilaBcpVisa("10Oct", "10Oct", "SPOTIFY PREMIUM", "CONSUMO", "", "6.99"),
        # Viaje imposible (clonacion fisica): Ica 14:05 -> Trujillo 14:50 (45 min)
        FilaBcpVisa("12Oct", "12Oct", "GRIFO PRIMAX ICA 14:05", "CONSUMO", "95.00"),
        FilaBcpVisa("12Oct", "12Oct", "MALL AVENTURA TRUJILLO 14:50", "CONSUMO", "420.00"),
        FilaBcpVisa("14Oct", "14Oct", "BOTICA INKAFARMA ICA 11:20", "CONSUMO", "64.20"),
        FilaBcpVisa("15Oct", "15Oct", "CAFE TOSTADO ICA 08:15", "CONSUMO", "12.50"),
        # Compra online de madrugada en dolares (Miami, 03:18 AM, US$ 295 = S/ 1,106.25)
        FilaBcpVisa("16Oct", "16Oct", "TECHSTORE.COM MIAMI 03:18", "CONSUMO", "", "295.00"),
        # Compra presencial fuera de ciudad habitual (Arequipa)
        FilaBcpVisa("17Oct", "17Oct", "SAGA FALABELLA AREQUIPA 16:30", "CONSUMO", "265.00"),
        # Doble suscripcion Netflix en el mismo mes (cargo 2)
        FilaBcpVisa("18Oct", "18Oct", "NETFLIX.COM", "CONSUMO", "44.90"),
        FilaBcpVisa("19Oct", "19Oct", "PAGO000428914556 CLARO HOGAR", "PAGOSERVIC", "92.00"),
        # Monto estadisticamente anomalo (Z-Score alto, compra diurna S/ 1,450)
        FilaBcpVisa("20Oct", "20Oct", "JOYERIA ORO FINO ONLINE 15:20", "CONSUMO", "1,450.00"),
        FilaBcpVisa("21Oct", "21Oct", "POLLERIA ROKYS ICA 19:40", "CONSUMO", "86.00"),
        FilaBcpVisa("22Oct", "22Oct", "CAFE TOSTADO ICA 08:35", "CONSUMO", "14.00"),
        FilaBcpVisa("23Oct", "23Oct", "CINEPLANET EL QUINDE ICA 20:10", "CONSUMO", "68.00"),
    ),
)


def main() -> None:
    salida = Path(__file__).resolve().parent / "extractos_bancarios"
    for cfg in (CONFIG_NORMAL, CONFIG_ESTAFA):
        ruta = salida / cfg.archivo
        _renderizar_pdf(construir_html_bcp_visa(cfg), ruta)
        print(f"[OK] {ruta.name} ({ruta.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
