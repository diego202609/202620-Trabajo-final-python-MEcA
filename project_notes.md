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

### 3B. Limpieza y Cruce Piloto (`src/limpieza_cruce.py`) (Completada en rama `feat/cruce-indicadores`)
- Implementados `src/limpieza_cruce.py`, `data/processed/README.md` y `tests/test_limpieza_cruce.py`.
- Archivos generados en `data/processed/`:
  - `paa_limpio.csv` (`9.877` filas), `contratos_limpio.csv` (`9.290` filas), `cruce_entidad_anio.csv` (`12` filas), `cruce_entidad_anio_segmento.csv` (`302` filas) y `auditoria_calidad.json`.
- **Hallazgo clave verificado:** en MinAmbiente 2023 existen dos ítems cuasi-idénticos de `$333,535 MM` (*Fondo para la Vida y la Biodiversidad*, donde solo varió la cita de artículos de la Ley 2294 de 2023 sin borrar la fila previa). Al controlar por ese duplicado administrativo atípico, la ejecución 2023 de MinAmbiente pasa de **32,9% a 50,9% (+18,0 pp)**.
- Cuadre entre suma de `paa_detalle` y `paa_encabezado`: diferencia máxima `< 0,001 COP`.

---

## Fase 4 — Escalamiento (6 Entidades), Indicadores R5, Visualizaciones y Cartilla (Completada — 2026-11-25)
- Descarga definitiva de las **6 entidades (`2022–2025`)** completada en `data/raw/`:
  - `paa_encabezado.csv`: `24` filas | `paa_detalle.csv`: `27.160` filas | `contratos_secop2.csv`: `25.317` filas | `clasificador_unspsc.csv`: `49.022` filas.
- Implementados `src/indicadores.py`, `src/visualizacion.py`, `src/generar_cartilla.py` y `tests/test_indicadores.py`.
- Contratos CSV generados en `data/dashboard_data/` (`resumen_entidad_anio.csv`, `modalidades_entidad_anio.csv`, `concentracion_proveedores.csv`, `top_proveedores_entidad.csv`, `brechas_segmento_unspsc.csv`, `distribucion_franjas_cuantia.csv` + `README.md`).
- **Cartilla Maestra del equipo generada en doble formato:** `docs/cartilla_equipo.md` + `docs/cartilla_interactiva.html` (con las 6 gráficas Plotly interactivas, respuestas jurídicas/económicas completas a las 5 dudas del grupo y el prompt listo para el Rubro 5).
- **Verificación:** `15 passed` en `pytest` offline.

---

## Fase 5 — Uso de IA para Ir Más Allá de la Metodología (Rubro 5) (Completada — 2026-11-26)
- Archivados de forma íntegra y literal el prompt y las 4 propuestas de la IA en `docs/rubro5_uso_ia.md` y `data/dashboard_data/rubro5_registro_ia.json`.
- **Implementadas en código (`src/config.py`, `src/indicadores.py`, `src/visualizacion.py`):**
  1. **Deflactación intertemporal a precios constantes de 2025 (IPC oficial DANE):** la brecha acumulada de las 6 entidades pasa de `-$1.563,73 MM` corrientes a `-$1.657,48 MM` constantes de 2025 (`-$93,75 MM` adicionales en poder adquisitivo real), y el crecimiento ejecutado `2022 → 2025` baja de `+131,66%` nominal a `+91,73%` real (`-39,93 pp` de ilusión monetaria).
  2. **Índice de Disimilitud Estructural de Duncan ($D_{it}$) sobre segmentos UNSPSC:** promedio muestral de `23,60%`, revelando casos de compensación oculta como MinCulturas (`100,44%` de ejecución agregada aparente pero `32,07%` promedio de reasignación entre segmentos UNSPSC) y MinHacienda (`40,31%` promedio, máximo `55,88%`).
- **Descartadas críticamente con sustento técnico e institucional:**
  - *Propuesta #4 (Emparejamiento micro bipartito `1:1` PAA–Contrato):* descartada porque las bolsas globales pluripersonales (`1:M`) y licitaciones agrupadas por lotes (`M:1`) violan la cardinalidad `1:1` y la cota $|\ln E_k - \ln P_j| \le \ln(1,5)$, fabricando falsos "no ejecutados".
  - *Propuesta #3 (Entropía estacional Kullback-Leibler y $\text{RIC}^{\text{Q4}}$):* descartada porque el PAA carece de cronograma mensual de desembolsos comparable y la concentración de firmas en enero obedece a operación anual ordinaria / Ley de Garantías 2022, desviando el foco de la pregunta única (Rubro 4).
- **Verificación:** `17 passed` en `pytest` offline.

---

## Fase 6 — Visualizaciones Plotly, Streamlit y Notebook Tutorial (Completada — 2026-11-26)
- Construido `app_streamlit.py` con 6 pestañas interactivas, filtros por entidad y año, selector entre pesos constantes de 2025 (IPC DANE) y pesos corrientes, KPIs dinámicos y botones de descarga CSV.
- Construido y ejecutado de principio a fin `A_contraluz_tutorial.ipynb` (`28` celdas, `RANDOM_SEED = 42`, única celda de imports sin paquetes sin usar, las 6 secciones con introducciones de `<= 3` líneas e hilo conductor explícito, demostración empírica R6, Rubro 5 íntegro con prompt + respuesta completa + *Antes vs. Después* + evaluación crítica, y limitaciones explícitas).
- Implementada auditoría automática en `tests/test_rubrica_notebook.py`.

---

## Fase 7 — Auditoría 20/20 y Empaquetado `.zip` Final (Completada — 2026-11-26)
- Construido `empaquetar_entrega.py` generando `entrega_grupo3_acontraluz.zip` (`35` archivos limpios, `~9,44 MB` comprimido).
- Aplicados ajustes de pulido de auditoría (`docs/decisiones.md` actualizado 100% a cifras finales de 6 entidades, encabezados de Sección 6 unificados en español, `width="stretch"` en `streamlit 1.67` sin advertencias de deprecación y estilos de línea accesibles en `HHI`).
- Verificada ejecución aislada del `.zip` descomprimido en carpeta limpia (`exit code 0`) y suite completa `pytest` en verde (`23 passed`).

---

## Comandos Clave de Re-ejecución
```powershell
# Desde Trabajo Final\a-contraluz-secop con .venv activo:
python -m pytest -v
python -m src.ingesta                                  # Verifica lectura offline desde caché
python -m src.ingesta --modo piloto --actualizar-api   # Regenera piloto desde datos.gov.co
python -m src.ingesta --modo completo --actualizar-api # Escala a 6 entidades desde datos.gov.co
```
