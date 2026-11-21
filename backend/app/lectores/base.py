"""Clases base abstractas y jerarquía de movimientos financieros (Unidad 3 - POO)."""

from __future__ import annotations

import re
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from app.config import CIUDAD_HABITUAL_DEFAULT


@dataclass(slots=True)
class Movimiento:
    """Clase base que representa un movimiento financiero extraído del extracto."""

    id: str
    fecha: str
    hora: str
    comercio: str
    ciudad: str
    canal: str
    monto: float
    moneda: str
    tipo: str

    def es_digital(self) -> bool:
        """Indica si la operación se ejecutó por canal digital."""
        return self.canal == "online"

    def describir_riesgo_canal(self) -> str:
        """Polimorfismo base sobre el nivel de exposición del canal."""
        return "Canal estándar"


class CompraPresencial(Movimiento):
    """Movimiento físico realizado con tarjeta presente o POS."""

    def describir_riesgo_canal(self) -> str:
        return "POS físico (requiere coherencia geográfica presencial)"


class CompraOnline(Movimiento):
    """Movimiento no presencial realizado en comercio electrónico."""

    def describir_riesgo_canal(self) -> str:
        return "Comercio electrónico (card-not-present)"


class Suscripcion(Movimiento):
    """Cargo periódico asociado a servicios por suscripción."""

    def describir_riesgo_canal(self) -> str:
        return "Cargo recurrente automatizado"


class ServicioBasico(Movimiento):
    """Pago de servicios públicos o recibos recurrentes del hogar."""

    def describir_riesgo_canal(self) -> str:
        return "Pago de servicio domiciliario"


_CLASES_MOVIMIENTO: dict[tuple[str, str], type[Movimiento]] = {
    ("suscripcion", "online"): Suscripcion,
    ("suscripcion", "presencial"): Suscripcion,
    ("servicio", "online"): ServicioBasico,
    ("servicio", "presencial"): ServicioBasico,
    ("compra", "online"): CompraOnline,
    ("compra", "presencial"): CompraPresencial,
}


def crear_movimiento(
    *,
    id: str,
    fecha: str,
    hora: str,
    comercio: str,
    ciudad: str,
    canal: str,
    monto: float,
    moneda: str,
    tipo: str,
) -> Movimiento:
    """Fábrica polimórfica que instancia la subclase adecuada de Movimiento."""
    clase = _CLASES_MOVIMIENTO.get((tipo, canal), Movimiento)
    return clase(
        id=id,
        fecha=fecha,
        hora=hora,
        comercio=comercio,
        ciudad=ciudad,
        canal=canal,
        monto=monto,
        moneda=moneda,
        tipo=tipo,
    )


_ALIAS_COLUMNAS: dict[str, tuple[str, ...]] = {
    "id": ("id", "tx_id", "codigo", "operacion", "nro", "num", "n_op", "no_op", "nro_op", "n_oper", "ref"),
    "fecha": (
        "fecha",
        "date",
        "fecha_operacion",
        "fecha_movimiento",
        "fec",
        "fecha_op",
        "fecha_oper",
        "fecha_consumo",
    ),
    "hora": ("hora", "time", "hora_operacion"),
    "comercio": (
        "comercio",
        "descripcion",
        "descripcion_del_movimiento",
        "descripcion_de_la_operacion",
        "descripcion_concepto",
        "concepto_descripcion",
        "concepto_establecimiento",
        "establecimiento",
        "concepto",
        "merchant",
        "detalle",
        "glosa",
    ),
    "ciudad": ("ciudad", "city", "ubicacion", "lugar", "localidad"),
    "canal": ("canal", "channel", "modalidad", "tipo_canal"),
    "lugar_canal": (
        "lugar_canal",
        "canal_ciudad",
        "canal_lugar",
        "oficina_canal",
        "localidad_canal",
        "ciudad_canal",
    ),
    "monto": ("monto", "importe", "amount", "cargo", "cargos", "valor", "total"),
    "monto_pen": ("soles", "soles_s", "cargo_s", "cargos_s", "importe_s", "monto_s"),
    "monto_usd": ("dolares", "dolares_us", "cargo_us", "cargos_us", "importe_us", "monto_us"),
    "moneda": ("moneda", "currency", "divisa"),
    "tipo": ("tipo", "type", "clase"),
}

_FORMATOS_FECHA = ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%Y/%m/%d")
_FILAS_NO_GASTO = (
    "saldo anterior",
    "saldo inicial",
    "saldo final",
    "saldo contable",
    "sub total",
    "subtotal",
    "total cargos",
    "total abonos",
    "total consumos",
    "monto total",
    "abono de haberes",
    "abono haberes",
    "abono transf",
    "transf. haberes",
    "pago recibido",
    "pago banca movil",
    "pago en ventanilla",
    "pago tarjeta",
    "impuesto itf",
)
_PREFIJOS_GLOSA = (
    "compra pos ",
    "consumo pos ",
    "consumo web ",
    "compra web ",
    "pago serv. ",
    "pago serv ",
    "cargo aut. ",
    "cargo aut ",
    "pos ",
    "web ",
)


def _sin_tildes(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _normalizar_clave_columna(nombre: str) -> str:
    sin_tildes = _sin_tildes(nombre).lower()
    limpio = re.sub(r"[^a-z0-9]+", "_", sin_tildes).strip("_")
    for canonico, aliases in _ALIAS_COLUMNAS.items():
        if limpio in aliases:
            return canonico
    return limpio


def _extraer_ciudad_y_canal(raw_combinado: str, ciudad_default: str) -> tuple[str, str]:
    texto = raw_combinado.strip()
    if not texto:
        return ciudad_default, ""

    low = _sin_tildes(texto).lower()
    canal = ""
    if any(k in low for k in ("online", "web", "digital", "bmovil", "app", "internet", "e-comm")):
        canal = "online"
    elif any(k in low for k in ("presencial", "pos", "tienda", "fisico", "cajero", "agencia")):
        canal = "presencial"

    limpio = re.sub(
        r"\b(presencial|online|web|digital|bmovil|app|internet|e-comm|pos|tienda|fisico|cajero|agencia)\b",
        "",
        texto,
        flags=re.IGNORECASE,
    )
    limpio = re.sub(r"[-/|•]+", " ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    ciudad = limpio.title() if limpio else ciudad_default
    return ciudad, canal


def _limpiar_comercio_glosa(raw_comercio: str) -> str:
    texto = re.sub(r"\s+", " ", raw_comercio).strip()
    low = _sin_tildes(texto).lower()
    for prefijo in _PREFIJOS_GLOSA:
        if low.startswith(prefijo):
            texto = texto[len(prefijo) :].strip()
            break
    if texto.isupper() and len(texto) > 4:
        texto = " ".join(
            p
            if (p in {"USA", "BCP", "BBVA", "S.A.", "PE"} or any(ch.isdigit() for ch in p))
            else p.capitalize()
            for p in texto.split()
        )
    return texto


def _normalizar_fecha_y_hora(raw_fecha: str, raw_hora: str) -> tuple[str, str]:
    texto_fecha = raw_fecha.strip()
    texto_hora = raw_hora.strip()

    if " " in texto_fecha and not texto_hora:
        partes = texto_fecha.split()
        texto_fecha = partes[0]
        if len(partes) > 1:
            texto_hora = partes[1]

    fecha_iso = texto_fecha
    for fmt in _FORMATOS_FECHA:
        try:
            fecha_iso = datetime.strptime(texto_fecha, fmt).strftime("%Y-%m-%d")
            break
        except ValueError:
            continue

    match_hora = re.search(r"(\d{1,2}:\d{2})", texto_hora)
    hora_norm = match_hora.group(1).zfill(5) if match_hora else "12:00"
    return fecha_iso, hora_norm


def _parsear_monto_y_moneda(raw_monto: Any, raw_moneda: str) -> tuple[float, str]:
    texto = str(raw_monto).strip()
    moneda = raw_moneda.strip().upper() if raw_moneda else ""

    if not moneda:
        if "USD" in texto.upper() or "$" in texto:
            moneda = "USD"
        elif "EUR" in texto.upper() or "€" in texto:
            moneda = "EUR"
        else:
            moneda = "PEN"
    elif moneda in {"S/", "SOL", "SOLES"}:
        moneda = "PEN"

    limpio = re.sub(r"[^\d.,-]", "", texto).strip("-")
    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        partes = limpio.split(",")
        if len(partes[-1]) == 2:
            limpio = limpio.replace(",", ".")
        else:
            limpio = limpio.replace(",", "")

    monto = abs(float(limpio))
    return round(monto, 2), moneda


def _inferir_canal(raw_canal: str, comercio: str) -> str:
    canal = _sin_tildes(raw_canal).strip().lower()
    if canal in {"online", "web", "internet", "digital", "app", "bmovil"}:
        return "online"
    if canal in {"presencial", "fisico", "pos", "tienda"}:
        return "presencial"

    comercio_low = _sin_tildes(comercio).lower()
    pistas_online = ("netflix", "spotify", "amazon", "uber", "rappi", ".com", "online", "electro", "agua")
    return "online" if any(p in comercio_low for p in pistas_online) else "presencial"


def _inferir_tipo(raw_tipo: str, comercio: str) -> str:
    tipo = _sin_tildes(raw_tipo).strip().lower()
    if tipo in {"compra", "suscripcion", "servicio"}:
        return tipo

    comercio_low = _sin_tildes(comercio).lower()
    if any(k in comercio_low for k in ("netflix", "spotify", "prime", "disney", "hbo", "icloud", "cargo aut")):
        return "suscripcion"
    if any(
        k in comercio_low
        for k in ("luz", "agua", "emapica", "electroluz", "internet", "sedapal", "movistar", "claro", "pago serv")
    ):
        return "servicio"
    return "compra"


class LectorEstadoCuenta(ABC):
    """Clase base abstracta para lectores polimórficos de extractos bancarios."""

    formato: str = "desconocido"

    @abstractmethod
    def leer(
        self,
        contenido: bytes,
        nombre_archivo: str,
        ciudad_default: str = CIUDAD_HABITUAL_DEFAULT,
    ) -> tuple[Movimiento, ...]:
        """Lee un archivo binario y devuelve una tupla inmutable de Movimiento."""

    def _construir_movimientos_desde_filas(
        self,
        filas: Iterable[dict[str, Any]],
        ciudad_default: str = CIUDAD_HABITUAL_DEFAULT,
    ) -> tuple[Movimiento, ...]:
        """Normaliza diccionarios heterogéneos a instancias polimórficas Movimiento."""
        movimientos: list[Movimiento] = []
        contador = 1

        for fila in filas:
            normalizada = {
                _normalizar_clave_columna(str(k)): ("" if v is None else str(v).strip())
                for k, v in fila.items()
                if k is not None
            }

            raw_fecha = normalizada.get("fecha", "")
            raw_comercio = normalizada.get("comercio", "")
            raw_monto = normalizada.get("monto", "")
            raw_moneda = normalizada.get("moneda", "")

            if not raw_monto or raw_monto in {"-", "—", "0.00", "0"}:
                raw_pen = normalizada.get("monto_pen", "")
                raw_usd = normalizada.get("monto_usd", "")
                if raw_pen and raw_pen not in {"-", "—"}:
                    raw_monto = raw_pen
                    if not raw_moneda and not any(t in raw_pen.upper() for t in ("USD", "US$", "$", "EUR", "€")):
                        raw_moneda = "PEN"
                elif raw_usd and raw_usd not in {"-", "—"}:
                    raw_monto = raw_usd
                    if not raw_moneda and not any(t in raw_usd.upper() for t in ("EUR", "€", "PEN", "S/")):
                        raw_moneda = "USD"

            if not raw_fecha or not raw_comercio or not raw_monto or raw_monto in {"-", "—"}:
                continue

            comercio_low = _sin_tildes(raw_comercio).lower()
            # Descarta filas de encabezado repetido, saldos, totales o abonos dentro de tablas PDF.
            if (
                _sin_tildes(raw_fecha).lower() in {"fecha", "date", "fecha op.", "fecha oper."}
                or "total" in comercio_low
                or any(p in comercio_low for p in _FILAS_NO_GASTO)
            ):
                continue

            try:
                monto, moneda = _parsear_monto_y_moneda(raw_monto, raw_moneda)
            except ValueError:
                continue

            if monto <= 0:
                continue

            fecha, hora = _normalizar_fecha_y_hora(raw_fecha, normalizada.get("hora", ""))
            tx_id = normalizada.get("id") or f"TX{contador:03d}"

            raw_ciudad = normalizada.get("ciudad", "")
            raw_canal = normalizada.get("canal", "")
            raw_combinado = normalizada.get("lugar_canal", "")
            if raw_combinado and (not raw_ciudad or not raw_canal):
                ciudad_ext, canal_ext = _extraer_ciudad_y_canal(raw_combinado, ciudad_default)
                if not raw_ciudad:
                    raw_ciudad = ciudad_ext
                if not raw_canal:
                    raw_canal = canal_ext

            ciudad = raw_ciudad or ciudad_default
            canal = _inferir_canal(raw_canal, raw_comercio)
            tipo = _inferir_tipo(normalizada.get("tipo", ""), raw_comercio)
            comercio_limpio = _limpiar_comercio_glosa(raw_comercio)

            movimientos.append(
                crear_movimiento(
                    id=tx_id,
                    fecha=fecha,
                    hora=hora,
                    comercio=comercio_limpio,
                    ciudad=ciudad,
                    canal=canal,
                    monto=monto,
                    moneda=moneda,
                    tipo=tipo,
                )
            )
            contador += 1

        if not movimientos:
            raise ValueError(
                "No se encontraron transacciones válidas en el archivo. "
                "Verifica que contenga columnas de fecha, comercio y monto."
            )
        return tuple(movimientos)
