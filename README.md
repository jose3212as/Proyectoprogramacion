# FinGuard — Asistente Inteligente de Finanzas Personales y Escudo Antifraude

**FinGuard** es una plataforma multiplataforma (Web y Móvil) para la auditoría privada de estados de cuenta bancarios en formato **PDF** y **CSV**, control de **gastos hormiga** e inferencia explicable de **anomalías y fraudes financieros** mediante un motor híbrido que integra los tres paradigmas del curso de **Lenguajes de Programación**.

> **Privacidad por diseño:** FinGuard nunca solicita contraseñas ni credenciales bancarias reales. Todo el análisis se realiza localmente sobre el extracto cargado por el usuario.

---

## Arquitectura del Monorepo

```text
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md     # Plantilla PR para GitHub Flow
├── .gitignore
├── README.md
├── docs/
│   ├── arquitectura.md              # Diagrama de flujo híbrido y asignación de módulos
│   ├── contrato_api.json            # Contrato JSON oficial compartido por Web y Móvil
│   ├── contrato_api.md              # Documentación de endpoints REST
│   ├── estado_cuenta_demo.csv       # Dataset simulado (gastos hormiga, duplicados, clonación y compra nocturna)
│   ├── estado_cuenta_demo.pdf       # Extracto bancario en PDF generado para pruebas con pdfplumber
│   └── generar_demo_pdf.py          # Script reproducible del extracto PDF demo
├── backend/                         # API REST (Python + FastAPI + Pandas/NumPy + SWI-Prolog)
│   ├── app/
│   │   ├── lectores/                # [Unidad 3 - POO] LectorEstadoCuenta, LectorPDF, LectorCSV, Movimiento
│   │   ├── funcional/               # [Unidad 1] Modelos frozen, funciones puras, lambdas, map/filter/reduce, orden superior
│   │   ├── logica/                  # [Unidad 2] reglas_fraude.pl (SWI-Prolog) y puente PySwip
│   │   ├── analitica/               # [Unidad 3 - Datos] Pandas, NumPy (Z-Score), Radar de Fugas y reporte PDF
│   │   ├── services/                # Orquestación del motor híbrido
│   │   ├── db.py                    # Persistencia SQLite (historial y estado 'Fui yo')
│   │   └── main.py                  # Endpoints FastAPI (Swagger en /docs)
│   ├── tests/                       # Suite pytest (unidad, integración Prolog y rendimiento < 3s)
│   └── requirements.txt
├── frontend-web/                    # Aplicación Web (Next.js + TypeScript + Tailwind CSS + Recharts)
└── mobile-app/                      # Aplicación Móvil (React Native + Expo + TypeScript + NativeWind)
```

---

## Paradigmas Aplicados por Unidad

| Unidad | Módulo | Técnicas Implementadas |
| --- | --- | --- |
| **Unidad 1: Programación Funcional** | `backend/app/funcional/` | Modelos inmutables (`@dataclass(frozen=True)`), funciones puras de conversión de divisas (`USD`/`EUR` → `PEN`), `map`/`filter`/`reduce` con `lambda`, y función de orden superior `crear_filtro_modo(modo)` (`normal` vs `ahorro_estricto`). |
| **Unidad 2: Programación Lógica** | `backend/app/logica/` | Base de conocimiento dinámica `transaccion/7`, unificación, resolución y backtracking en `reglas_fraude.pl` (viaje imposible entre ciudades, compra nocturna atípica, cobro duplicado, monto anómalo Z-Score, operación fuera de ciudad) con traza explicable en español. |
| **Unidad 3: Multiparadigma y Datos** | `backend/app/lectores/` y `backend/app/analitica/` | POO con clase abstracta `LectorEstadoCuenta` (`LectorPDF` con `pdfplumber` y `LectorCSV`), jerarquía polimórfica `Movimiento`, análisis estadístico con **Pandas** y **NumPy** (media, desviación estándar y Z-Score) y exportación de reporte PDF (`reportlab`). |

---

## Requisitos Previos

- **Python 3.11+** (probado en Python 3.14)
- **SWI-Prolog** (instalado en `PATH` o en `C:\Program Files\swipl\bin\swipl.exe`)
- **Node.js 20 LTS+** y `npm`

---

## Instalación y Ejecución Local

### 1. Backend (`FastAPI` + `SWI-Prolog`)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Documentación interactiva Swagger UI: `http://127.0.0.1:8000/docs`
- Verificación de salud: `http://127.0.0.1:8000/health`

#### Ejecutar pruebas del Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

### 2. Frontend Web (`Next.js`)

```powershell
cd frontend-web
npm install
npm run dev
```

Abre `http://localhost:3000` en el navegador. Si quieres apuntar a otra URL de API, copia `.env.example` a `.env.local` y ajusta `NEXT_PUBLIC_API_URL`.

### 3. Aplicación Móvil (`React Native` + `Expo`)

```powershell
cd mobile-app
npm install
npx expo start
```

Escanea el código QR con **Expo Go** en Android/iOS. Si pruebas en un teléfono físico, copia `.env.example` a `.env` y coloca la IP LAN de tu PC en `EXPO_PUBLIC_API_URL` (ejemplo: `http://192.168.1.45:8000`).

---

## Distribución del Equipo (3 Integrantes)

| Integrante | Rol | Carpetas Asignadas |
| --- | --- | --- |
| **Integrante 1** | Backend, POO y Ciencia de Datos | `backend/app/lectores/`, `backend/app/analitica/`, `backend/app/main.py` |
| **Integrante 2** | Paradigmas Funcional y Lógico | `backend/app/funcional/`, `backend/app/logica/`, `docs/` |
| **Integrante 3** | UI/UX, Web y App Móvil | `frontend-web/`, `mobile-app/` |

---

## Reglas de Colaboración en Git (GitHub Flow)

1. La rama `main` contiene únicamente versiones estables y probadas.
2. Cada integrante trabaja en ramas descriptivas desde `main`:
   ```bash
   git checkout -b feat/reglas-prolog
   ```
3. Al finalizar una funcionalidad, se abre un **Pull Request** hacia `main` usando `.github/PULL_REQUEST_TEMPLATE.md` para revisión cruzada del equipo.
