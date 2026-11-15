# Arquitectura Técnica — FinGuard

FinGuard implementa una arquitectura Cliente–Servidor desacoplada donde un único núcleo híbrido en **Python + SWI-Prolog** integra los tres paradigmas del curso de **Lenguajes de Programación** y atiende mediante API REST tanto a la aplicación Web como a la aplicación Móvil.

## Flujo Híbrido de Procesamiento

```
[Archivo CSV / PDF]
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│ UNIDAD 3 (POO): backend/app/lectores/                    │
│  • LectorEstadoCuenta (ABC)                              │
│    ├── LectorCSV                                         │
│    └── LectorPDF (pdfplumber)                            │
│  • Jerarquía Movimiento (Presencial, Online, Suscrip.)   │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│ UNIDAD 1 (Funcional): backend/app/funcional/             │
│  • Modelos inmutables (dataclass frozen=True)            │
│  • Funciones puras de conversión de divisas (USD/EUR)    │
│  • Lambdas + map/filter/reduce para categorización       │
│  • Orden superior: crear_filtro_modo(modo)               │
└──────────────────────────────────────────────────────────┘
        │
        ├───────────────────────────────┐
        ▼                               ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│ UNIDAD 3 (Ciencia Datos): │   │ UNIDAD 2 (Lógica):       │
│ backend/app/analitica/    │   │ backend/app/logica/      │
│  • Pandas: agrupaciones   │   │  • Hechos transaccion/7  │
│  • NumPy: media y Z-Score │   │  • reglas_fraude.pl      │
│  • Gastos hormiga y fugas │   │  • Unificación y traza   │
└───────────────────────────┘   └──────────────────────────┘
        │                               │
        └───────────────┬───────────────┘
                        ▼
        [Diagnóstico Unificado + SQLite + PDF]
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
 [Frontend Web: Next.js]      [App Móvil: Expo RN]
```

## Mapeo por Integrante (Monorepo)

- **Integrante 1 (Backend, POO y Ciencia de Datos)**: `backend/app/lectores/`, `backend/app/analitica/`, `backend/app/main.py`
- **Integrante 2 (Paradigmas Funcional y Lógico)**: `backend/app/funcional/`, `backend/app/logica/`, `docs/estado_cuenta_demo.*`
- **Integrante 3 (UI/UX, Web y App Móvil)**: `frontend-web/`, `mobile-app/`
