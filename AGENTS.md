# AGENTS.md — Reglas No Negociables (*A contra(luz)*)

## Propósito del proyecto
Este repositorio corresponde al **Trabajo Final del Taller de Programación Aplicada a Python (Universidad de los Andes, 2026-II — Grupo 3)**: ***A contra(luz): análisis y veeduría de la contratación pública en Colombia***.

Construimos un **tutorial autocontenido en Jupyter Notebook (`A_contraluz_tutorial.ipynb`)** empacado en un **`.zip` reproducible**, respaldado por módulos Python limpios (`src/`), pruebas automáticas (`tests/`) y un tablero interactivo en **Streamlit (`app_streamlit.py`)** como resultado del análisis económico.

**Integrantes (Grupo 3):**
- Diego Andrés Niño Estupiñán — `201719748`
- Juan Sebastián Puerto Sanz — `201532975`
- Nathalia Alexandra Acero Pérez — `202524470`

---

## Audiencia y estilo de código
- El código analítico debe ser claro y auditable para un estudiante con un semestre de Python.
- Usar código de `pandas` explícito, paso a paso, con variables intermedias descriptivas y `docstrings` en español.
- Evitar cadenas densas de métodos difíciles de depurar, trucos opacos o transformaciones sin explicar.
- Mantener **rutas 100% relativas** usando `pathlib.Path` (nunca rutas absolutas como `C:\...` o `/Users/...`).
- Si existe cualquier componente con aleatoriedad, fijar la semilla global **`RANDOM_SEED = 42`** desde `src/config.py`.

---

## Reglas No Negociables

### A. Integridad de datos y evidencia
1. **Inspeccionar antes de afirmar:** nunca inventar nombres de columnas, Dataset IDs de `datos.gov.co`, NITs de entidades, valores categóricos ni significados de variables.
2. **Leer `data/README.md` primero:** antes de analizar datos crudos, consultar `data/README.md` (fuente, qué representa una fila, cobertura, tipos y cautelas). Solo re-inspeccionar los archivos si hace falta responder una pregunta nueva aún no documentada, y registrar el hallazgo verificado en `data/README.md`.
3. **Inmutabilidad de `data/raw/`:** jamás editar manualmente los archivos descargados en `data/raw/`. Toda limpieza ocurre por código en `src/limpieza_cruce.py` y se guarda en `data/processed/`.
4. **Identificar el grano antes de agregar o graficar:** antes de calcular cualquier indicador o crear una gráfica, dejar explícito qué representa una fila, qué magnitud se suma o cuenta y si los datos son población completa (del subconjunto seleccionado) o muestra.
5. **Cero resultados huérfanos:** toda tabla, métrica, cruce, chequeo o gráfica que sustente una afirmación del proyecto debe generarse ejecutando código aceptado (`src/*.py` o el notebook), nunca mediante comandos sueltos y descartables en terminal.
6. **Aislamiento de pruebas:** cualquier corrida exploratoria o de prueba escribe únicamente en `data/pruebas/` y nunca se mezcla con `data/raw/`, `data/processed/` ni `data/dashboard_data/`.

### B. Arquitectura y reproducibilidad (patrón `coding-agents-for-data-science`)
7. **Lógica en scripts `# %%` y contratos CSV:** durante el desarrollo en equipo, la lógica de ingesta, limpieza, cruce e indicadores vive en módulos Python con celdas percent-cell (`# %%`) en `src/`. Cada etapa escribe archivos CSV limpios y documentados como contrato para la siguiente (`data/raw/` → `data/processed/` → `data/dashboard_data/`).
8. **Notebook autocontenido y reproducible sin internet:** `src/ingesta.py` consulta la API Socrata SODA de `datos.gov.co` y guarda copia local en `data/raw/`. Por defecto (`USAR_CACHE_LOCAL = True`), el notebook lee esa copia congelada incluida en el `.zip` para garantizar que *Reiniciar y ejecutar todo* corra sin errores, sin intervención manual y sin depender de red; `USAR_CACHE_LOCAL = False` permite regenerar desde la API.
9. **Streamlit sin duplicar código ni bloquear el notebook:** `app_streamlit.py` consume exclusivamente los CSVs revisados de `data/dashboard_data/` y las funciones de `src/visualizacion.py`. Nunca ejecutar un servidor Streamlit bloqueante dentro del `.ipynb`.
10. **Limpieza y código sin basura:** no dejar celdas vacías, código comentado olvidado, pruebas sueltas ni `imports` sin uso.

### C. Cumplimiento obligatorio de recomendaciones del equipo pedagógico (R1–R8 — Rubro 3)
Todo desarrollo y revisión debe evidenciar estos 8 puntos sin excepción:
- **R1 (Pregunta sobre el fenómeno):** una única pregunta analítica concisa y bien delimitada sobre el fenómeno económico/contractual (ej. desviación entre planeación en PAA y ejecución en SECOP II), no sobre "cómo construir una herramienta".
- **R2 (Cruce PAA × Contratos SECOP II):** contrastar lo planeado en el PAA con lo efectivamente contratado en SECOP II.
- **R3 (API de `datos.gov.co`):** extracción reproducible mediante la API Socrata (`requests`/SODA), sin descargas manuales entidad por entidad.
- **R4 (Muestra concreta):** muestra fija de **5 a 10 entidades del orden nacional** (iniciando con 3 piloto y escalando a 5–6 definitivas vía `src/config.py`) para el periodo **2022–2025**.
- **R5 (Indicadores definidos desde el inicio):** calcular explícitamente `% de lo planeado que se contrata`, `peso de la contratación directa` (y distribución por modalidad), `concentración por proveedor` (ej. participación Top-k e índice HHI) y distribución por categoría UNSPSC.
- **R6 (Cruce explícito con Clasificador UNSPSC):** documentar e implementar exactamente **por qué código y a qué nivel jerárquico** (segmento, familia o clase) se cruzan el PAA y los contratos con el Clasificador de Bienes y Servicios.
- **R7 (Secuencia concreta):** cada paso del tutorial explica explícitamente qué transforma o calcula.
- **R8 (Análisis económico real + Streamlit):** el tablero en Streamlit es el resultado visual de un análisis económico riguroso, no solo un contenedor de gráficos.

### D. Reglas estrictas de la Rúbrica del Trabajo Final (20/20 pts)
- **Rubro 1 (Notebook):** encabezado con nombres y códigos completos; **una única celda de imports** con solo los paquetes estrictamente usados; revisión justificada de tipos, faltantes, duplicados y atípicos; ejecución limpia *Restart & Run All*.
- **Rubro 2 (Tutorial autocontenido):** **toda sección tiene una introducción de máximo 3 líneas**; hilo conductor explícito entre secciones; todos los insumos en el `.zip` con rutas relativas.
- **Rubro 3 (Recomendaciones):** tabla de trazabilidad R1–R8 verificada.
- **Rubro 4 (Pregunta y metodología):** una única pregunta; cero componentes superfluos; interpretación ligada directamente a la pregunta; **sección explícita de limitaciones** (supuestos, sesgos, alcance, causalidad y validez externa).
- **Rubro 5 (Uso de IA más allá de la metodología):** sección dedicada que incluya: (1) prompt completo y bien formulado (contexto, metodología actual, objetivo, restricciones), (2) respuesta íntegra de la IA, (3) distinción precisa de qué va más allá de lo recomendado por los profesores, (4) **implementación real en código de al menos una mejora** mostrando su efecto en los resultados (*antes vs. después*), y (5) evaluación crítica de qué descartó el equipo y por qué.

### E. Colaboración Git, privacidad y seguridad (patrón Taller 2)
11. **Propiedad de carpetas y PRs:** cada integrante trabaja en su propia rama (`feat/...`, `fix/...`) y abre Pull Request hacia `main`. No editar carpetas de otro frente sin avisar; ejecutar `git pull` antes de comenzar y correr `pytest` antes de hacer merge.
12. **Secretos y privacidad:** nunca subir `.env`, tokens ni contraseñas al repositorio. No almacenar ni exponer datos personales sensibles innecesarios de personas naturales si aparecen en campos auxiliares de SECOP II.

---

## Uso de subagentes y skills (`.agents/`)
- **Agente Padre (modelo fuerte):** responsable de decisiones de diseño, inspección de API, definición de pregunta/muestra, interpretación económica y evaluación crítica del Rubro 5.
- **Workers (`model: flash` en `.agents/agents/`):** usar únicamente para tareas acotadas con entradas, salidas, columnas y verificación ya especificadas (`data-worker`, `viz-worker`).
- **Auditor (`rubric-auditor`):** solo lectura; audita el notebook, `src/` y el `.zip` contra la matriz de 20 puntos antes de la entrega.
- **Skills (`.agents/skills/`):** consultar `acontraluz-charts` al diseñar cualquier figura Plotly y `rubrica-notebook` al redactar o revisar `A_contraluz_tutorial.ipynb`.
