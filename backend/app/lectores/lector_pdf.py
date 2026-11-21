"""Implementación concreta para estados de cuenta en PDF con pdfplumber (Unidad 3 - POO).

Soporta:
  - Tablas bancarias con filas delimitadas (Interbank, BCP Ahorros, BBVA y extractos estándar).
  - Extractos reales de Tarjeta de Crédito BCP VISA (y formatos similares) con cajas sin líneas
    horizontales entre filas, fechas cortas en español (ej. '20Oct'), doble columna Soles/Dólares,
    pagos con signo '-' al final y páginas informativas anexas.
"""

from __future__ import annotations

import io
import re
import unicodedata
from datetime import date, datetime
from typing import Any

import pdfplumber

from app.config import CIUDAD_HABITUAL_DEFAULT
from app.lectores.base import LectorEstadoCuenta, Movimiento

_MESES_CORTO: dict[str, int] = {
    "ene": 1,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "aug": 8,
    "set": 9,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
    "dec": 12,
}

_CIUDADES_CONOCIDAS = (
    "ica",
    "lima",
    "trujillo",
    "arequipa",
    "cusco",
    "piura",
    "chiclayo",
    "huancayo",
    "tacna",
    "chincha",
    "pisco",
    "miami",
    "madrid",
    "bogota",
    "santiago",
    "mexico",
)

_PATRON_FILA_TEXTO = re.compile(
    r"^(?P<id>TX\d+)?\s*"
    r"(?P<fecha>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\s+"
    r"(?P<hora>\d{2}:\d{2})?\s*"
    r"(?P<comercio>.+?)\s+"
    r"(?P<ciudad>[A-Za-zÁÉÍÓÚáéíóúÑñ]+)\s+"
    r"(?P<canal>presencial|online)\s+"
    r"(?P<monto>[\d.,]+)\s*"
    r"(?P<moneda>PEN|USD|EUR|S/)?\s*"
    r"(?P<tipo>compra|suscripcion|servicio)?$",
    re.IGNORECASE,
)

_PATRON_FECHA_CORTA = re.compile(r"^(\d{1,2})[-/\s]?([A-Za-z]{3})$")
_PATRON_FECHA_NUM = re.compile(r"^(\d{2})/(\d{2})(?:/(\d{2,4}))?$")
_PATRON_FECHA_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_PATRON_MONTO_BANCO = re.compile(r"^(?:S/|US\$|\$|EUR|€)?\s*[\d,]+(?:\.\d{2})-?$", re.IGNORECASE)
_PATRON_CICLO = re.compile(r"(\d{2}/\d{2}/\d{2,4})\s+(?:al\s+)?(\d{2}/\d{2}/\d{2,4})", re.IGNORECASE)
_PATRON_HORA = re.compile(r"\b(\d{1,2}:\d{2})\b")

_MARCADORES_FIN_TABLA = (
    "como calcular tu pago minimo",
    "monto total facturado",
    "sub total",
    "subtotal",
    "como esta compuesta su deuda",
    "detalle plan cuotas",
    "plan de cuotas",
    "informacion importante",
    "la comision de membresia",
)

_CARGOS_FINANCIEROS_SIN_FECHA = (
    "intereses",
    "comision por uso de canales",
    "comision por uso de cajeros",
    "seguro de desgravamen",
    "comision anual por membresia",
    "membresia",
    "portes",
)

_TIPOS_OPERACION_BANCO = {
    "pago",
    "pagoservic",
    "consumo",
    "compra",
    "compras",
    "retiro",
    "disposicion",
    "cargo",
    "abono",
    "cuota",
    "comision",
}


def _sin_tildes(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _parsear_fecha_ciclo(raw: str) -> date | None:
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _detectar_ciclo_facturacion(texto_completo: str) -> tuple[date | None, date | None]:
    """Localiza el rango de fechas del ciclo de facturación (ej. '28/09/26 25/10/26')."""
    for match in _PATRON_CICLO.finditer(texto_completo):
        f1 = _parsear_fecha_ciclo(match.group(1))
        f2 = _parsear_fecha_ciclo(match.group(2))
        if f1 and f2 and 0 <= (f2 - f1).days <= 65:
            return f1, f2
    return None, None


def _resolver_fecha_token(
    token: str,
    inicio_ciclo: date | None,
    cierre_ciclo: date | None,
) -> str | None:
    """Convierte tokens como '20Oct', '03Abr', '20/10/26' o '2026-10-20' a ISO 'YYYY-MM-DD'."""
    limpio = token.strip()
    if _PATRON_FECHA_ISO.match(limpio):
        return limpio

    m_num = _PATRON_FECHA_NUM.match(limpio)
    if m_num:
        dia, mes, anio_raw = int(m_num.group(1)), int(m_num.group(2)), m_num.group(3)
        if not (1 <= mes <= 12 and 1 <= dia <= 31):
            return None
        if anio_raw:
            anio = int(anio_raw) + (2000 if len(anio_raw) == 2 else 0)
        else:
            anio = _resolver_anio_mes(mes, inicio_ciclo, cierre_ciclo)
        return f"{anio:04d}-{mes:02d}-{dia:02d}"

    m_corta = _PATRON_FECHA_CORTA.match(_sin_tildes(limpio))
    if m_corta:
        dia = int(m_corta.group(1))
        mes = _MESES_CORTO.get(m_corta.group(2).lower())
        if mes and 1 <= dia <= 31:
            anio = _resolver_anio_mes(mes, inicio_ciclo, cierre_ciclo)
            return f"{anio:04d}-{mes:02d}-{dia:02d}"

    return None


def _resolver_anio_mes(mes: int, inicio: date | None, cierre: date | None) -> int:
    if inicio and cierre:
        if inicio.year == cierre.year:
            return cierre.year
        return inicio.year if mes >= inicio.month else cierre.year
    if cierre:
        return cierre.year
    return datetime.now().year


def _inferir_ciudad_en_descripcion(descripcion: str, ciudad_default: str) -> str:
    low = _sin_tildes(descripcion).lower()
    for ciudad in _CIUDADES_CONOCIDAS:
        if re.search(rf"\b{ciudad}\b", low):
            return ciudad.capitalize()
    return ciudad_default


def _es_pagina_guia_informativa(texto_pagina: str) -> bool:
    low = _sin_tildes(texto_pagina).lower()
    return (
        "conoce el estado de cuenta" in low
        or ("recomendaciones:" in low and "calculo del minimo a pagar" in low)
    )


class LectorPDF(LectorEstadoCuenta):
    """Lector polimórfico especializado en extraer tablas de estados de cuenta PDF."""

    formato = "pdf"

    def leer(
        self,
        contenido: bytes,
        nombre_archivo: str,
        ciudad_default: str = CIUDAD_HABITUAL_DEFAULT,
    ) -> tuple[Movimiento, ...]:
        filas_extraidas: list[dict[str, Any]] = []

        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            textos_paginas = [(p.extract_text() or "") for p in pdf.pages]
            inicio_ciclo, cierre_ciclo = _detectar_ciclo_facturacion("\n".join(textos_paginas))

            for pagina, texto_pagina in zip(pdf.pages, textos_paginas):
                if _es_pagina_guia_informativa(texto_pagina):
                    continue

                filas_pagina: list[dict[str, Any]] = []

                # 1) Intenta extracción estructurada de tablas con filas delimitadas
                tablas = pagina.extract_tables() or []
                tabla_empaquetada = False
                for tabla in tablas:
                    if self._es_tabla_celdas_multilinea(tabla):
                        tabla_empaquetada = True
                        continue
                    filas_pagina.extend(self._convertir_tabla_a_filas(tabla))

                # 2) Si las filas vienen dentro de cajas sin líneas horizontales (ej. BCP Tarjeta VISA),
                #    usa agrupación exacta por coordenadas Y/X de palabras.
                if not filas_pagina and (tabla_empaquetada or self._tiene_cabecera_bancaria_libre(texto_pagina)):
                    filas_pagina.extend(
                        self._extraer_por_coordenadas_bancarias(
                            pagina=pagina,
                            inicio_ciclo=inicio_ciclo,
                            cierre_ciclo=cierre_ciclo,
                            ciudad_default=ciudad_default,
                        )
                    )

                # 3) Fallback para tablas sin líneas verticales (estrategia de texto + líneas horizontales)
                if not filas_pagina:
                    tablas_texto = (
                        pagina.extract_tables(
                            table_settings={
                                "vertical_strategy": "text",
                                "horizontal_strategy": "lines",
                                "intersection_x_tolerance": 6,
                                "intersection_y_tolerance": 4,
                            }
                        )
                        or []
                    )
                    for tabla in tablas_texto:
                        if not self._es_tabla_celdas_multilinea(tabla):
                            filas_pagina.extend(self._convertir_tabla_a_filas(tabla))

                # 4) Último recurso: coordenadas bancarias o regex de texto plano
                if not filas_pagina:
                    filas_pagina.extend(
                        self._extraer_por_coordenadas_bancarias(
                            pagina=pagina,
                            inicio_ciclo=inicio_ciclo,
                            cierre_ciclo=cierre_ciclo,
                            ciudad_default=ciudad_default,
                        )
                    )

                if not filas_pagina:
                    filas_pagina.extend(self._extraer_desde_texto_plano(texto_pagina))

                filas_extraidas.extend(filas_pagina)

        if not filas_extraidas:
            raise ValueError(
                f"El PDF '{nombre_archivo}' no contiene tablas de movimientos legibles."
            )

        return self._construir_movimientos_desde_filas(
            filas_extraidas, ciudad_default=ciudad_default
        )

    @staticmethod
    def _es_tabla_celdas_multilinea(tabla: list[list[str | None]]) -> bool:
        """Detecta tablas donde pdfplumber agrupó múltiples transacciones en una sola celda con '\\n'."""
        if not tabla:
            return False
        for fila in tabla[1:]:
            for celda in fila:
                if not celda or "\n" not in celda:
                    continue
                lineas = [ln.strip() for ln in celda.splitlines() if ln.strip()]
                fechas = sum(
                    1
                    for ln in lineas
                    if _PATRON_FECHA_CORTA.match(_sin_tildes(ln))
                    or _PATRON_FECHA_NUM.match(ln)
                    or _PATRON_FECHA_ISO.match(ln)
                )
                montos = sum(1 for ln in lineas if _PATRON_MONTO_BANCO.match(ln))
                if fechas >= 2 or montos >= 2:
                    return True
        return False

    @staticmethod
    def _tiene_cabecera_bancaria_libre(texto_pagina: str) -> bool:
        low = _sin_tildes(texto_pagina).lower()
        return (
            ("fecha de" in low or "fecha" in low)
            and ("descripcion" in low or "concepto" in low)
            and ("soles" in low or "dolares" in low)
        )

    @staticmethod
    def _convertir_tabla_a_filas(tabla: list[list[str | None]]) -> list[dict[str, str]]:
        """Transforma una tabla de pdfplumber descartando títulos o pies publicitarios."""
        if len(tabla) < 2:
            return []

        indice_header = -1
        for idx, fila in enumerate(tabla):
            celdas = [_sin_tildes(str(c or "")).strip().lower() for c in fila]
            texto_fila = " ".join(celdas)
            tiene_fecha = "fecha" in texto_fila or "date" in texto_fila
            tiene_monto_o_desc = any(
                k in texto_fila
                for k in ("monto", "importe", "comercio", "cargo", "soles", "descripcion", "concepto")
            )
            if tiene_fecha and tiene_monto_o_desc and len([c for c in celdas if c]) >= 4:
                indice_header = idx
                break

        if indice_header == -1:
            return []

        encabezados = [
            str(col or f"col_{i}").strip() for i, col in enumerate(tabla[indice_header])
        ]
        resultado: list[dict[str, str]] = []
        for fila in tabla[indice_header + 1 :]:
            if not fila or all(not (c or "").strip() for c in fila):
                continue
            registro = {
                encabezados[i]: str(fila[i] or "").replace("\n", " ").strip()
                for i in range(min(len(encabezados), len(fila)))
            }
            resultado.append(registro)
        return resultado

    @staticmethod
    def _agrupar_palabras_en_lineas(
        palabras: list[dict[str, Any]], tolerancia_y: float = 3.5
    ) -> list[list[dict[str, Any]]]:
        ordenadas = sorted(palabras, key=lambda w: (round(float(w["top"]), 1), float(w["x0"])))
        lineas: list[list[dict[str, Any]]] = []
        for palabra in ordenadas:
            top = float(palabra["top"])
            if not lineas or abs(top - float(lineas[-1][0]["top"])) > tolerancia_y:
                lineas.append([palabra])
            else:
                lineas[-1].append(palabra)
        for linea in lineas:
            linea.sort(key=lambda w: float(w["x0"]))
        return lineas

    @classmethod
    def _extraer_por_coordenadas_bancarias(
        cls,
        *,
        pagina: Any,
        inicio_ciclo: date | None,
        cierre_ciclo: date | None,
        ciudad_default: str,
    ) -> list[dict[str, str]]:
        """Extrae movimientos alineados por fila visual (coordenada Y) y columna (coordenada X).

        Resuelve extractos reales tipo BCP Tarjeta VISA donde las columnas tienen separadores
        verticales pero las filas de movimientos no tienen líneas horizontales entre sí.
        """
        palabras = pagina.extract_words(keep_blank_chars=False, use_text_flow=False) or []
        if not palabras:
            return []

        lineas = cls._agrupar_palabras_en_lineas(palabras)

        # Localiza la banda de encabezados (puede ocupar 1 o 2 líneas apiladas, ej. 'Fecha de / proceso')
        idx_header = -1
        header_words: list[dict[str, Any]] = []
        for idx, linea in enumerate(lineas):
            combinadas = list(linea)
            if idx + 1 < len(lineas):
                diff_y = float(lineas[idx + 1][0]["top"]) - float(linea[0]["top"])
                if 0 < diff_y <= 15.0:
                    combinadas.extend(lineas[idx + 1])

            texto_norm = _sin_tildes(" ".join(w["text"] for w in combinadas)).lower()
            tiene_desc = any(k in texto_norm for k in ("descripcion", "concepto", "establecimiento"))
            tiene_moneda = "soles" in texto_norm or "dolares" in texto_norm or "cargos" in texto_norm
            tiene_fecha = "fecha" in texto_norm
            if tiene_desc and tiene_moneda and tiene_fecha:
                idx_header = idx
                header_words = combinadas
                break

        if idx_header == -1:
            return []

        y_header_bottom = max(float(w["bottom"]) for w in header_words) + 1.5

        x_soles: float | None = None
        x_dolares: float | None = None
        x_tipo: float | None = None
        for w in header_words:
            t = _sin_tildes(w["text"]).lower()
            if t == "soles" and x_soles is None:
                x_soles = float(w["x0"])
            elif t == "dolares" and x_dolares is None:
                x_dolares = float(w["x0"])
            elif t in {"tipo", "operacion"} and x_tipo is None:
                x_tipo = float(w["x0"])

        # Ajusta frontera izquierda de Soles / Dólares usando líneas verticales si existen
        lineas_verticales = sorted(
            float(ln["x0"])
            for ln in (pagina.lines or [])
            if abs(float(ln["x0"]) - float(ln["x1"])) <= 1.5
            and (float(ln["bottom"]) - float(ln["top"])) >= 40.0
        )
        if x_soles is not None:
            izquierda_soles = [x for x in lineas_verticales if x <= x_soles + 4.0]
            x_soles_min = izquierda_soles[-1] if izquierda_soles else (x_soles - 18.0)
        else:
            x_soles_min = float(pagina.width) * 0.72

        if x_dolares is not None:
            izquierda_dolares = [x for x in lineas_verticales if x <= x_dolares + 4.0]
            x_dolares_min = izquierda_dolares[-1] if izquierda_dolares else (x_dolares - 12.0)
        else:
            x_dolares_min = float(pagina.width) * 0.90

        x_tipo_min = (x_tipo - 10.0) if x_tipo is not None else None
        fecha_cierre_iso = (
            cierre_ciclo.strftime("%Y-%m-%d")
            if cierre_ciclo
            else datetime.now().strftime("%Y-%m-%d")
        )

        filas: list[dict[str, str]] = []
        for linea in lineas[idx_header + 1 :]:
            if float(linea[0]["top"]) <= y_header_bottom:
                continue

            texto_linea = " ".join(w["text"] for w in linea).strip()
            norm_linea = _sin_tildes(texto_linea).lower()

            if any(fin in norm_linea for fin in _MARCADORES_FIN_TABLA):
                break

            if (
                "saldo anterior" in norm_linea
                or "saldo inicial" in norm_linea
                or "xxxxxx" in norm_linea
                or "****" in norm_linea
            ):
                continue

            # Separa montos en Soles / Dólares según coordenada X
            monto_soles = ""
            monto_dolares = ""
            tokens_cuerpo: list[dict[str, Any]] = []
            for w in linea:
                txt = w["text"].strip()
                x0 = float(w["x0"])
                if x0 >= x_dolares_min and _PATRON_MONTO_BANCO.match(txt):
                    monto_dolares = txt
                elif x0 >= x_soles_min and _PATRON_MONTO_BANCO.match(txt):
                    monto_soles = txt
                else:
                    tokens_cuerpo.append(w)

            # Fallback si el monto quedó pegado en el extremo derecho
            if not monto_soles and not monto_dolares and tokens_cuerpo:
                ultimo = tokens_cuerpo[-1]["text"].strip()
                if _PATRON_MONTO_BANCO.match(ultimo):
                    monto_soles = ultimo
                    tokens_cuerpo = tokens_cuerpo[:-1]

            if not monto_soles and not monto_dolares:
                continue

            raw_monto = monto_soles or monto_dolares
            moneda = "USD" if (monto_dolares and not monto_soles) else "PEN"
            if "EUR" in raw_monto.upper() or "€" in raw_monto:
                moneda = "EUR"
            elif "US$" in raw_monto.upper() or "$" in raw_monto:
                moneda = "USD"

            # En tarjetas de crédito, los montos con '-' al final o inicio son pagos/abonos a la tarjeta
            es_pago_abono = raw_monto.endswith("-") or raw_monto.startswith("-")

            # Extrae fechas iniciales (ej. '20Oct 20Oct')
            fechas_en_linea: list[str] = []
            idx_cuerpo = 0
            while idx_cuerpo < len(tokens_cuerpo) and len(fechas_en_linea) < 2:
                f_iso = _resolver_fecha_token(
                    tokens_cuerpo[idx_cuerpo]["text"], inicio_ciclo, cierre_ciclo
                )
                if f_iso:
                    fechas_en_linea.append(f_iso)
                    idx_cuerpo += 1
                else:
                    break

            resto = tokens_cuerpo[idx_cuerpo:]
            if not resto:
                continue

            # Extrae 'Tipo de Operación' si cae en esa columna o coincide con catálogo bancario
            tipo_op = ""
            if resto:
                ultimo_norm = _sin_tildes(resto[-1]["text"]).lower()
                cae_en_tipo = x_tipo_min is not None and float(resto[-1]["x0"]) >= x_tipo_min
                if ultimo_norm in _TIPOS_OPERACION_BANCO or (cae_en_tipo and len(resto) > 1):
                    tipo_op = ultimo_norm
                    resto = resto[:-1]

            descripcion = " ".join(w["text"] for w in resto).strip()
            if not descripcion:
                continue

            desc_norm = _sin_tildes(descripcion).lower()

            # Descarta pagos/abonos hechos por el titular a la tarjeta
            if es_pago_abono or tipo_op in {"pago", "abono"} or any(
                p in desc_norm for p in ("pago banca movil", "pago en ventanilla", "pago tarjeta")
            ):
                continue

            # Determina fecha (si es cargo financiero sin fecha como INTERESES, usa la fecha de cierre)
            if fechas_en_linea:
                fecha_iso = fechas_en_linea[-1]
            elif any(c in desc_norm for c in _CARGOS_FINANCIEROS_SIN_FECHA):
                fecha_iso = fecha_cierre_iso
            else:
                continue

            # Extrae hora si viene en la descripción y la limpia del nombre del comercio
            m_hora = _PATRON_HORA.search(descripcion)
            if m_hora:
                hora = m_hora.group(1).zfill(5)
                descripcion_limpia = re.sub(r"\s*\(?\b\d{1,2}:\d{2}\b\)?\s*", " ", descripcion).strip()
                if descripcion_limpia:
                    descripcion = descripcion_limpia
            else:
                hora = "12:00"

            # Clasifica tipo y canal según operación real BCP/banco
            if tipo_op == "pagoservic" or any(c in desc_norm for c in _CARGOS_FINANCIEROS_SIN_FECHA):
                tipo = "servicio"
                canal = "online"
            else:
                tipo = ""
                canal = ""

            ciudad = _inferir_ciudad_en_descripcion(descripcion, ciudad_default)
            filas.append(
                {
                    "fecha": fecha_iso,
                    "hora": hora,
                    "comercio": descripcion,
                    "ciudad": ciudad,
                    "canal": canal,
                    "monto": raw_monto,
                    "moneda": moneda,
                    "tipo": tipo,
                }
            )

        return filas

    @staticmethod
    def _extraer_desde_texto_plano(texto: str) -> list[dict[str, str]]:
        filas: list[dict[str, str]] = []
        for linea in texto.splitlines():
            match = _PATRON_FILA_TEXTO.match(linea.strip())
            if match:
                filas.append({k: v or "" for k, v in match.groupdict().items()})
        return filas
