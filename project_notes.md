# Project Notes — Bitácora Viva (*A contra(luz)*)

Este archivo mantiene la memoria operativa del proyecto entre conversaciones y entre los 3 integrantes del Grupo 3. Actualizar al cierre de cada fase con **hechos verificados** (nunca supuestos).

---

## Contexto General y Meta
- **Proyecto:** *A contra(luz): análisis y veeduría de la contratación pública en Colombia*.
- **Entregable oficial:** Archivo `.zip` autocontenido con `A_contraluz_tutorial.ipynb`, módulos `src/`, datos congelados en `data/`, `requirements.txt` y `app_streamlit.py`.
- **Ventana de sprint:** Miércoles 25 – Viernes 27 de noviembre de 2026 (sábado 28 colchón; límite oficial en Bloque Neón: sábado 28, 23:59 COT).
- **Objetivo de evaluación:** 20/20 puntos (5,0) cumpliendo los 5 rubros de la rúbrica y las 8 recomendaciones (`R1–R8`) de la evaluación de la propuesta (`3.75` → `4.3`).

---

## Fase 1 — Reglas `.md` y Andamiaje (Completada)
- **Fecha:** 2026-11-24 (preparación lista para arrancar miércoles 25).
- **Archivos creados:**
  - Gobernanza y documentación: `AGENTS.md`, `README.md`, `project_notes.md`, `docs/decisiones.md`, `data/README.md`.
  - Subagentes y skills: `.agents/agents/{data-worker.md, viz-worker.md, rubric-auditor.md}`, `.agents/skills/{acontraluz-charts/SKILL.md, rubrica-notebook/SKILL.md}`.
  - Configuración técnica: `.gitignore`, `.env.example`, `requirements.txt`, `pytest.ini` y estructura de carpetas `data/`, `src/`, `tests/`.
- **Estado Git:** Repositorio inicializado localmente, listo para vincular con el remoto en GitHub (`git remote add origin <URL>`).

---

## Fase 2 — Descubrimiento de APIs `datos.gov.co` y Congelación de Alcance *(Pendiente — Mié 25 mañana)*
- **Objetivo:** Inspeccionar metadata y consultas agregadas SoQL de PAA, Contratos SECOP II y Clasificador UNSPSC **sin descarga masiva**.
- **Por registrar al cerrar Fase 2:**
  - Dataset IDs verificados en `datos.gov.co` y URL del Clasificador UNSPSC.
  - Esquema real de columnas y grano (qué representa una fila) en `data/README.md`.
  - Diagnóstico de entidades candidatas bajo los 5 filtros "sin complicaciones".
  - 3 entidades piloto + pool de 5–6 entidades definitivas (NITs verificados).
  - Regla exacta de cruce UNSPSC (código y nivel: segmento/familia/clase).
  - Pregunta única congelada en `docs/decisiones.md`.

---

## Fase 3 — Ingesta, Limpieza y Cruce Piloto (3 Entidades) *(Pendiente — Mié 25 tarde/noche)*
- **Por registrar:** comandos de ejecución, conteo de filas por entidad/año, resultados de auditoría de tipos/faltantes/duplicados/atípicos y estado de `pytest`.

---

## Fase 4 — Escalamiento (5–6 Entidades) e Indicadores R5 *(Pendiente — Jue 26 mañana)*
- **Por registrar:** NITs añadidos en `src/config.py`, inventario de CSVs generados en `data/dashboard_data/` con su proveniencia y hallazgos clave.

---

## Fase 5 — Uso de IA para Ir Más Allá de la Metodología (Rubro 5) *(Pendiente — Jue 26 tarde)*
- **Por registrar:** resumen del prompt estructurado, sugerencias de la IA que van más allá de lo recomendado por los profesores, mejora(s) implementada(s) en código, efecto cuantitativo *antes vs. después* y sugerencias descartadas con su justificación.

---

## Fase 6 — Visualizaciones Plotly, Streamlit y Notebook Tutorial *(Pendiente — Jue 26 noche / Vie 27 mañana)*
- **Por registrar:** lista de figuras en `src/visualizacion.py`, validación de `app_streamlit.py`, y corrida limpia de `nbconvert --execute` sobre `A_contraluz_tutorial.ipynb`.

---

## Fase 7 — Auditoría 20/20, PR `fix/auditoria` y Empaquetado `.zip` *(Pendiente — Vie 27 tarde/noche)*
- **Por registrar:** hallazgos del agente `rubric-auditor`, correcciones aplicadas, tamaño final de `entrega_grupo3_acontraluz.zip` y verificación en carpeta limpia sin internet.

---

## Problemas Abiertos / Riesgos a Monitorear
1. Verificar el miércoles 25 a primera hora qué dataset exacto de PAA de SECOP II está activo y actualizado en `datos.gov.co` (y si conserva versiones/actualizaciones o última versión por vigencia).
2. Validar cómo vienen formateados los códigos UNSPSC en PAA vs. Contratos SECOP II (ej. prefijos `V1.`, múltiples códigos separados por `;` o `,`, o longitud de 8 dígitos).
3. Vigilar el tamaño final de los CSVs en `data/raw/` para que el `.zip` de entrega sea ágil de subir y ejecutar.
