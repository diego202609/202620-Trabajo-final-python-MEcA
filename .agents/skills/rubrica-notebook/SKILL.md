---
name: rubrica-notebook
description: Reglas estrictas de estructura, redacción y verificación para construir y revisar A_contraluz_tutorial.ipynb y el archivo .zip de entrega apuntando a 20/20 puntos.
---

# Skill: Cumplimiento Estricto de Rúbrica del Notebook (`rubrica-notebook`)

Usa este skill al diseñar el esqueleto, redactar celdas o auditar `A_contraluz_tutorial.ipynb` y el empaquetado `.zip`. Cada regla corresponde directamente al **Nivel 4 (4/4 pts)** de los cinco rubros de evaluación.

---

## 1. Estructura Obligatoria de `A_contraluz_tutorial.ipynb`

1. **Celda 1 (Markdown — Encabezado e Identificación):**
   - Título del proyecto (*A contra(luz)*).
   - Nombres completos y códigos de los 3 integrantes:
     - Diego Andrés Niño Estupiñán (`201719748`)
     - Juan Sebastián Puerto Sanz (`201532975`)
     - Nathalia Alexandra Acero Pérez (`202524470`)
   - Pregunta única de investigación bien delimitada (entidades, periodo `2022–2025`, variables y alcance).
   - Tabla compacta de trazabilidad de las recomendaciones del equipo pedagógico (`R1–R8`).
2. **Celda 2 (Código — Única sección de cargue de paquetes):**
   - **Todos los `import` del notebook van aquí y solo aquí.**
   - Prohibido importar paquetes en celdas posteriores.
   - Prohibido dejar un paquete importado que no se use en el notebook.
   - Fijar explícitamente `RANDOM_SEED = 42` y verificar rutas relativas desde `Path.cwd()`.
3. **Secciones analíticas numeradas (orden lógico del tutorial):**
   - **Sección 1:** Contexto, pregunta de investigación y fuentes oficiales (`datos.gov.co` SODA API + Clasificador UNSPSC).
   - **Sección 2:** Adquisición reproducible de datos (API Socrata con caché local incluido en el `.zip`) y verificación de grano.
   - **Sección 3:** Auditoría de calidad, limpieza justificada (tipos, faltantes, duplicados, atípicos) y cruce exacto PAA ↔ SECOP II ↔ UNSPSC (**código y nivel jerárquico**).
   - **Sección 4:** Cálculo e interpretación de los indicadores centrales (`% ejecutado vs. planeado`, `peso contratación directa`, `concentración por proveedor`, `brechas por categoría UNSPSC`).
   - **Sección 5:** Uso de IA para ir más allá de la metodología (**Rubro 5 completo** — ver detalle abajo).
   - **Sección 6:** Respuesta integrada a la pregunta, **limitaciones explícitas** y guía breve de ejecución del tablero **Streamlit (`app_streamlit.py`)**.

---

## 2. Regla de Oro de Introducciones e Hilo Conductor (Rubro 2)
- **TODAS las secciones** (sin excepción) deben abrir con un párrafo introductorio de **máximo 3 líneas** (aprox. ≤ 45–55 palabras / ≤ 3 oraciones cortas, sin saltos que lo extiendan a 4+ líneas visuales).
- Cada introducción debe cumplir doble función:
  1. Retomar brevemente lo hallado en la sección anterior (**hilo conductor explícito**).
  2. Anticipar con precisión qué se calcula o demuestra en la sección actual (**R7**).

---

## 3. Reglas Obligatorias de la Sección del Rubro 5 (Uso de IA)
Para garantizar **4/4 puntos** en el Rubro 5, la Sección 5 debe contener estos **5 bloques explícitos**:
1. **Prompt completo y bien formulado:** incluye contexto del proyecto, metodología actual implementada (R1–R8), objetivo analítico y restricciones reales de los datos. *(Nunca un prompt genérico).*
2. **Respuesta completa de la IA:** mostrada íntegramente en formato legible (cita o bloque desplegable/Markdown completo sin recortes ocultos).
3. **Qué va más allá de lo recomendado por los profesores:** tabla o viñetas distinguiendo con precisión qué propuestas de la IA superan lo ya pedido en la evaluación de la propuesta (`3.75` / `4.3`).
4. **Implementación real en código y efecto en los resultados:** ejecutar al menos una mejora sugerida directamente en celdas del notebook (llamando a `src/indicadores.py`) y mostrar una comparativa cuantitativa/visual ***antes vs. después***.
5. **Evaluación crítica del equipo:** explicar explícitamente **qué sugerencias de la IA se descartaron y por qué** (por sesgos, falta de datos, no identificabilidad causal o riesgo de componentes superfluos).

---

## 4. Reglas del Empaquetado `.zip` Autocontenido
- El `.zip` (`entrega_grupo3_acontraluz.zip`) debe contener únicamente lo necesario para ejecutar el tutorial y Streamlit de forma autónoma:
  - `A_contraluz_tutorial.ipynb` (guardado con salidas ejecutadas limpiamente)
  - `app_streamlit.py`
  - `src/` (solo `.py` usados, sin `__pycache__`)
  - `data/README.md`, `data/raw/`, `data/processed/`, `data/dashboard_data/` (sin `data/pruebas/`)
  - `docs/decisiones.md`, `README.md`, `requirements.txt`
- **Excluir siempre del `.zip`:** `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ipynb_checkpoints/`, `.env`, `data/pruebas/` y archivos basura temporales.
- **Prueba obligatoria antes de entregar:** descomprimir el `.zip` en una carpeta nueva fuera del repo, activar un `.venv` limpio con `requirements.txt` y correr `nbconvert --execute` sin errores ni intervención manual.
