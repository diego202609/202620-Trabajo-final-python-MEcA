# Project Notes — Bitácora Viva (*A contra(luz)*)

Este archivo mantiene la memoria operativa del proyecto entre conversaciones y entre los 3 integrantes del Grupo 3. Todo lo registrado aquí corresponde a **hechos verificados**.

---

## Contexto General y Meta
- **Proyecto:** *A contra(luz): análisis y veeduría de la contratación pública en Colombia*.
- **Repositorio GitHub:** `https://github.com/diego202609/202620-Trabajo-final-python-MEcA.git`
- **Entregable oficial:** Archivo `.zip` autocontenido con `A_contraluz_tutorial.ipynb`, módulos `src/`, datos congelados en `data/`, `requirements.txt` y `app_streamlit.py`.
- **Ventana de sprint:** Miércoles 25 – Viernes 27 de noviembre de 2026 (sábado 28 colchón; límite oficial: sábado 28, 23:59 COT).
- **Plan completo dentro del repo:** `docs/plan.md`.

---

## Fase 1 — Reglas `.md` y Andamiaje (Completada — 2026-11-24)
- Creados 21 archivos base (`AGENTS.md`, `README.md`, `project_notes.md`, `docs/decisiones.md`, `data/README.md`, `.agents/agents/`, `.agents/skills/`, configuración Python/pytest).
- Commit inicial en `main`: `ad2b18f`, conectado y sincronizado con `origin/main`.
- Entorno `.venv` creado con Python 3.14.6 (Anaconda) e instaladas todas las dependencias (`pandas 3.1.1`, `plotly 6.9.0`, `streamlit 1.67.0`, `pytest 9.2.0`, `xlrd 2.0.2`).

---

## Fase 2 — Descubrimiento de APIs y Congelación de Alcance (Completada — 2026-11-25)
- **Endpoints Socrata verificados en vivo (`datos.gov.co`):**
  - `b6m4-qgqv`: SECOP II — PAA Encabezado (1 fila por entidad-año, última versión publicada).
  - `9sue-ezhx`: SECOP II — PAA Detalle (ítems de la última versión publicada; suma de `valor_total_esperado` cuadra al peso con `b6m4-qgqv`).
  - `jbjy-vk9h`: SECOP II — Contratos Electrónicos (100% cobertura UNSPSC en entidades seleccionadas; 31 columnas analíticas seleccionadas excluyendo datos personales sensibles).
  - Clasificador UNSPSC v14.1: `clasificador_de_bienes_y_servicios_v14_1.xls` (hoja `'Clasificador'`, `header=3`, `49.022` productos, `3.818` clases, `420` familias, `56` segmentos).
- **Muestra aprobada (`2022–2025`, orden Nacional, nivel central, `Publicado` los 4 años):**
  - **Piloto (3):** ANCP (`700037070`), MinHacienda (`700065089`), MinAmbiente (`700209018`).
  - **Escala (+3 → 6 totales):** MinEducación (`700066053`), MinCulturas (`700637010`), DNP (`700220049`).
- **Hallazgo empírico R6 (UNSPSC):** Cruce a 8 dígitos (Producto) solo empata 17,4% (PAA) y 16,1% (Contratos); cruce a **Clase (6 dígitos) / Familia (4) / Segmento (2)** alcanza **99,99%** en PAA y **99,67%** en Contratos.
- **Documentado en:** `docs/plan.md`, `docs/decisiones.md` y `data/README.md`.

---

## Fase 3 — Ingesta, Limpieza y Cruce Piloto (En curso — 2026-11-25)
### 3A. Ingesta API Piloto (Completada en rama `feat/ingesta-api`)
- Implementados `src/config.py`, `src/ingesta.py` y `tests/test_ingesta.py` + fixtures reales en `tests/fixtures/`.
- Extracción piloto ejecutada en < 30 segundos:
  - `data/raw/paa_encabezado.csv`: `12` filas (`2,7 KB`)
  - `data/raw/paa_detalle.csv`: `9.877` filas (`6,4 MB`)
  - `data/raw/contratos_secop2.csv`: `9.290` filas (`4,6 MB`)
  - `data/raw/clasificador_unspsc.csv`: `49.022` filas (`8,4 MB`)
- **Verificación:** `.\.venv\Scripts\python.exe -m pytest -v` → **5 passed in 0.95s**.
- **Hallazgos reales de calidad detectados para 3B (`src/limpieza_cruce.py`):**
  - `808` contratos con `valor_del_contrato <= 0` (`559` Acuerdos Marco de Precios de ANCP + `160` convenios/otros sin cuantía).
  - `31` contratos con código UNSPSC `"UNSPECIFIED"` (`0,33%`).
  - `626` ítems PAA con múltiples códigos UNSPSC separados por delimitador.
  - Posible doble registro atípico de `$333,5 MM` en MinAmbiente 2023 (*Fondo para la Vida y la Biodiversidad*, dos `id` distintos con igual texto y monto).
  - Diferencia significativa entre `valor_total_esperado` (`3.546 MM`) y `valor_esperado_de_presupuesto` (`2.914 MM`) por vigencias futuras.

### 3B. Limpieza y Cruce Piloto (`src/limpieza_cruce.py`) *(Siguiente paso hoy Mié 25 tarde)*
- Construir `src/limpieza_cruce.py` + pruebas offline para generar tablas limpias y cruzadas en `data/processed/` y reporte de auditoría de calidad.

---

## Fase 4 — Escalamiento (6 Entidades) e Indicadores R5 *(Pendiente — Jue 26 mañana)*
- Correr `python -m src.ingesta --modo completo --actualizar-api`, re-ejecutar `src/limpieza_cruce.py` y generar `src/indicadores.py` + CSVs en `data/dashboard_data/`.

---

## Fase 5 — Uso de IA para Ir Más Allá de la Metodología (Rubro 5) *(Pendiente — Jue 26 tarde)*
- Formular prompt estructurado con resultados reales de las 6 entidades, implementar al menos 1 mejora en código (*antes vs. después*) y redactar evaluación crítica de descartes.

---

## Fase 6 — Visualizaciones Plotly, Streamlit y Notebook Tutorial *(Pendiente — Jue 26 noche / Vie 27 mañana)*
- Construir `src/visualizacion.py`, `app_streamlit.py`, `A_contraluz_tutorial.ipynb` y `tests/test_rubrica_notebook.py`.

---

## Fase 7 — Auditoría 20/20, PR `fix/auditoria` y Empaquetado `.zip` *(Pendiente — Vie 27 tarde/noche)*
- Correr `rubric-auditor` (solo lectura), cerrar PR `fix/auditoria`, generar `entrega_grupo3_acontraluz.zip` y validar en carpeta limpia sin internet.

---

## Comandos Clave de Re-ejecución
```powershell
# Desde Trabajo Final\a-contraluz-secop con .venv activo:
python -m pytest -v
python -m src.ingesta                                  # Verifica lectura offline desde caché
python -m src.ingesta --modo piloto --actualizar-api   # Regenera piloto desde datos.gov.co
python -m src.ingesta --modo completo --actualizar-api # Escala a 6 entidades desde datos.gov.co
```
