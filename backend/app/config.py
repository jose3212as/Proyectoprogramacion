"""Configuración centralizada del servidor FinGuard."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from types import MappingProxyType

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent
DOCS_DIR = ROOT_DIR / "docs"
DB_PATH = BACKEND_DIR / "finguard.db"
PROLOG_RULES_PATH = APP_DIR / "logica" / "reglas_fraude.pl"
DEMO_CSV_PATH = DOCS_DIR / "estado_cuenta_demo.csv"
DEMO_PDF_PATH = DOCS_DIR / "estado_cuenta_demo.pdf"

TASAS_CAMBIO_PEN: MappingProxyType[str, float] = MappingProxyType(
    {
        "PEN": 1.0,
        "S/": 1.0,
        "USD": 3.75,
        "EUR": 4.05,
    }
)

PRESUPUESTO_MENSUAL_DEFAULT = 2500.0
CIUDAD_HABITUAL_DEFAULT = "Ica"
MODO_DEFAULT = "normal"


def resolver_ruta_swipl() -> str | None:
    """Localiza el ejecutable de SWI-Prolog en PATH o rutas estándar de Windows."""
    en_path = shutil.which("swipl")
    if en_path:
        return en_path

    candidatos = [
        Path(r"C:\Program Files\swipl\bin\swipl.exe"),
        Path(r"C:\Program Files (x86)\swipl\bin\swipl.exe"),
        Path(os.environ.get("SWI_HOME_DIR", "")) / "bin" / "swipl.exe",
    ]
    for ruta in candidatos:
        if ruta.is_file():
            return str(ruta)
    return None
