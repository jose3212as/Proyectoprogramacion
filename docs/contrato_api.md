# Contrato de API REST — FinGuard

Este documento formaliza los endpoints del backend en **FastAPI** y la estructura del contrato JSON compartida entre **Backend**, **Frontend Web (Next.js)** y **App Móvil (React Native / Expo)**.

## Endpoints Disponibles

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/health` | Estado del servicio y disponibilidad del motor SWI-Prolog |
| `POST` | `/api/auditar-cuenta` | Recibe un estado de cuenta `.csv` o `.pdf`, perfil (`ciudad_habitual`, `modo`, `presupuesto_mensual`) y retorna el diagnóstico completo |
| `GET` | `/api/demo` | Ejecuta una auditoría inmediata sobre el dataset oficial `docs/estado_cuenta_demo.csv` |
| `GET` | `/api/historial` | Lista las auditorías previas almacenadas en SQLite |
| `GET` | `/api/auditorias/{audit_id}` | Recupera el diagnóstico completo de una auditoría previa |
| `POST` | `/api/alertas/{alerta_id}/marcar-fui-yo` | Marca o revierte una alerta como verificada por el usuario (`Fui yo` — RF-09) |
| `GET` | `/api/auditorias/{audit_id}/reporte-pdf` | Descarga un reporte ejecutivo en PDF listo para reclamo bancario (RF-10) |

## Parámetros de `POST /api/auditar-cuenta` (`multipart/form-data`)

- `archivo`: Archivo `.csv` o `.pdf` con el estado de cuenta bancario.
- `ciudad_habitual`: Ciudad habitual de residencia (ej. `"Ica"`). Por defecto `"Ica"`.
- `modo`: `"normal"` o `"ahorro_estricto"`. Por defecto `"normal"`.
- `presupuesto_mensual`: Monto límite mensual en soles (`PEN`). Por defecto `2500.0`.

## Modos de Evaluación

- **`normal`**: Prioriza alertas de seguridad críticas, duplicados, compras nocturnas atípicas, viajes imposibles y montos estadísticamente anómalos ($Z \ge 2.0$).
- **`ahorro_estricto`**: Aplica filtros dinámicos de orden superior con umbrales más exigentes sobre gastos hormiga ($\ge 2$ compras pequeñas), desviaciones moderadas ($Z \ge 1.5$) y suscripciones múltiples.

## Referencia de Ejemplo

Ver el esquema de ejemplo completo en [`contrato_api.json`](./contrato_api.json).
