# Plan Maestro de Equipo — Trabajo Final de Python (*A contra(luz)*)

**Equipo (Grupo 3):** Diego Andrés Niño Estupiñán (`201719748`), Juan Sebastián Puerto Sanz (`201532975`), Nathalia Alexandra Acero Pérez (`202524470`).  
**Ventana de ejecución:** **Sprint de 3 días — Miércoles 25 a Viernes 27 de noviembre de 2026** *(sábado 28 reservado como colchón de seguridad antes del límite oficial 23:59 COT en Bloque Neón)*.  
**Estrategia elegida:** **Camino seguro (20/20 pts = 5,0)** — cumplir al 100% los 5 rubros de la rúbrica final y **todas** las recomendaciones registradas en la evaluación de la propuesta (`3.75` → `4.3`).

---

## 1. Decisiones Confirmadas

| Dimensión | Decisión acordada |
|---|---|
| **Meta y entrega** | **Arranque:** miércoles 25 de nov. · **Meta de cierre:** viernes 27 de nov. · **Plazo oficial:** sábado 28 de nov. (`23:59 COT`). Entregable: **`.zip` autocontenido** con `A_contraluz_tutorial.ipynb`, módulos `src/`, datos cacheados, `requirements.txt` y `app_streamlit.py`. |
| **Repositorio** | Repositorio nuevo en GitHub (`202620-Trabajo-final-python-MEcA`) con flujo de ramas + Pull Requests hacia `main`. |
| **Muestra de entidades** | **Enfoque incremental aprobado:** iniciar con **3 entidades piloto** (`Colombia Compra Eficiente`, `MinHacienda`, `MinAmbiente`) y escalar a **6 entidades** sumando `MinEducación`, `MinCulturas` y `DNP` (todas del orden nacional, nivel central, `Publicado` en `2022–2025`, `100%` UNSPSC en contratos). |
| **Agentes y equipo** | Trabajo colaborativo con GitHub + Antigravity (**agente padre** por integrante, **workers `model: flash`** para tareas acotadas y **checker `rubric-auditor`** de solo lectura al cierre). |

---

## 2. Matriz de Cumplimiento (Rúbrica 20 pts + Recomendaciones R1–R8)

| Rubro (4 pts c/u) | Exigencia Nivel 4 (4/4 pts) | Mecanismo de garantía |
|---|---|---|
| **1. Cuaderno de Jupyter** | Orden lógico, buena ortografía, encabezado con nombres y códigos; **una sola sección de imports** (solo los usados); **cero código basura**; `Restart & Run All` sin errores ni intervención manual; semilla fija (`42`); revisión justificada de tipos, faltantes, duplicados y atípicos. | Lógica pesada en `src/*.py`; notebook con única celda de imports, auditoría explícita de calidad de datos y prueba automática con `nbconvert --execute`. |
| **2. Tutorial autocontenido, hilo conductor e introducciones** | **Cada sección tiene introducción de máximo 3 líneas**; hilo conductor explícito; todos los insumos en el `.zip` con **rutas relativas**; ejecutable sin contexto ni internet. | Modo `USAR_CACHE_LOCAL = True` leyendo `data/raw/` incluido en el `.zip`; test automático (`test_rubrica_notebook.py`) valida introducciones ≤ 3 líneas y cero rutas absolutas. |
| **3. Recomendaciones del equipo pedagógico** | Evidenciar **R1–R8**: **R1** Pregunta sobre el fenómeno; **R2** Cruce PAA × Contratos SECOP II; **R3** API `datos.gov.co` (`requests`/SODA); **R4** Muestra concreta (5–10 entidades nacionales, 2022–2025); **R5** Indicadores definidos desde el inicio (`% ejecutado`, contratación directa, concentración por proveedor); **R6** Método exacto de cruce UNSPSC (**código y nivel**); **R7** Secuencia indicando qué se calcula en cada paso; **R8** Análisis económico sustantivo con Streamlit como resultado. | Checklist obligatorio `R1–R8` en `AGENTS.md`, tabla de trazabilidad en el notebook y auditoría de `rubric-auditor`. |
| **4. Pregunta y metodología** | **Una única pregunta** concisa y bien delimitada; metodología directa sin componentes superfluos; resultados interpretados en función de la pregunta; **limitaciones explícitas**. | Pregunta única congelada en `docs/decisiones.md`; cero gráficos superfluos; sección dedicada de limitaciones (vigencias futuras, rezagos de reporte, alcance descriptivo no causal, validez externa). |
| **5. Uso de IA para ir más allá de la metodología** | Sección dedicada con: (a) **prompt bien formulado**, (b) **respuesta completa de la IA**, (c) qué sugerencias **van más allá** de lo recomendado, (d) **implementación real en código de al menos una mejora** mostrando su efecto *antes vs. después*, (e) **evaluación crítica** de descartes. | Fase propia (Jueves 26 tarde) una vez la metodología base R1–R8 tiene cifras reales. |

---

## 3. Arquitectura Técnica

```text
API Socrata datos.gov.co (b6m4-qgqv, 9sue-ezhx, jbjy-vk9h) + Clasificador UNSPSC (CCE)
   │
   ▼  src/ingesta.py (# %%) [API SODA + caché local]
data/raw/ (CSVs congelados + README.md)
   │
   ▼  src/limpieza_cruce.py (# %%) [Auditoría + normalización + cruce UNSPSC]
data/processed/ (Tablas limpias e integradas)
   │
   ▼  src/indicadores.py (# %%) [Indicadores R5 + Mejora IA Rubro 5]
data/dashboard_data/ (CSVs finales machine-readable + README.md)
   │
   ▼  src/visualizacion.py [Funciones Plotly accesibles]
   ├──► A_contraluz_tutorial.ipynb (Entregable principal .zip)
   └──► app_streamlit.py           (Tablero interactivo .zip)
```

---

## 4. Distribución de Frentes y Uso de Multiagentes

| Frente | Dueño exclusivo de archivos | Responsabilidad principal | Uso recomendado de agentes |
|---|---|---|---|
| **Frente 1 — Ingesta, API SODA y Calidad** | `src/config.py`, `src/ingesta.py`, `data/raw/`, `data/README.md`, `tests/test_ingesta.py` | Endpoints `datos.gov.co`, descarga paginada/cacheada, Clasificador UNSPSC, auditoría de calidad y fixtures. | Padre diseña contrato; `data-worker` (`flash`) construye tests offline. |
| **Frente 2 — Limpieza, Cruce UNSPSC, Indicadores y Rubro 5** | `src/limpieza_cruce.py`, `src/indicadores.py`, `data/processed/`, `data/dashboard_data/`, `tests/test_indicadores.py` | Limpieza documentada, cruce UNSPSC (código + nivel), indicadores R5, prompt/implementación/crítica del Rubro 5. | Padre define fórmulas y crítica; `data-worker` (`flash`) calcula familias de indicadores y CSVs. |
| **Frente 3 — Visualización, Streamlit, Notebook y `.zip`** | `src/visualizacion.py`, `app_streamlit.py`, `A_contraluz_tutorial.ipynb`, `README.md`, `docs/decisiones.md`, `empaquetar_entrega.py` | Gráficas Plotly accesibles, app Streamlit, ensamble del notebook tutorial y empaquetado `.zip`. | Padre arma narrativa; `viz-worker` (`flash`) genera figuras; `rubric-auditor` (solo lectura) audita 20/20. |

---

## 5. Cronograma de Sprint — 3 Días (Mié 25 – Vie 27) + Sáb 28 Colchón

| Día / Bloque | Fases y actividades | Hito de cierre ("Done") |
|---|---|---|
| **Mié 25 — Mañana**<br>*(Fases 1 + 2)* | Repo en GitHub + Descubrimiento de APIs `datos.gov.co` (sin descarga masiva) + selección de 3 entidades piloto y pool de 6 + congelar pregunta. | `data/README.md` y `docs/decisiones.md` verificados y aprobados. |
| **Mié 25 — Tarde/Noche**<br>*(Fase 3 — Piloto 3 entidades)* | Implementar `src/config.py`, `src/ingesta.py` y `src/limpieza_cruce.py` en las **3 entidades piloto** + Clasificador UNSPSC + fixtures y `pytest`. | Pipeline ingesta + limpieza + cruce corriendo en 3 entidades piloto y `pytest` verde. |
| **Jue 26 — Mañana**<br>*(Fase 4 — Escalamiento 6 entidades + Indicadores R5)* | Cambiar `MODO_MUESTRA` a las **6 entidades** en `src/config.py`, congelar `data/raw/` definitivo, calcular todos los indicadores R5 en `data/dashboard_data/`. | CSVs definitivos de **6 entidades (2022–2025)** validados + `pytest` verde. |
| **Jue 26 — Tarde/Noche**<br>*(Fase 5 Rubro 5 IA + Fase 6A Gráficas y Streamlit)* | Ejecutar Rubro 5 (prompt, respuesta completa, mejora real en código *antes vs. después*, evaluación crítica); construir `src/visualizacion.py` y `app_streamlit.py`. | Mejora Rubro 5 implementada + gráficas Plotly y Streamlit operativos. |
| **Vie 27 — Mañana**<br>*(Fase 6B — Notebook Tutorial)* | Ensamblar `A_contraluz_tutorial.ipynb` completo y `tests/test_rubrica_notebook.py`; correr `nbconvert --execute`. | Notebook ejecutando de principio a fin sin errores y pasando tests de rúbrica. |
| **Vie 27 — Tarde/Noche**<br>*(Fase 7 — Auditoría 20/20 y `.zip`)* | Correr `rubric-auditor` (solo lectura), cerrar PR `fix/auditoria`, generar `entrega_grupo3_acontraluz.zip` y probar en carpeta limpia sin internet. | **META CUMPLIDA:** `.zip` validado 20/20 desde el viernes en la noche. |
| **Sáb 28 — Colchón y Subida** | Solo ajustes menores de última lectura y subida final a Bloque Neón antes de 23:59 COT. | Entrega confirmada en Bloque Neón. |

---

## 6. Verificación Obligatoria antes de Entregar
1. `python -m pytest -v` (pruebas offline con fixtures reales + verificación programática del notebook).
2. `python -m jupyter nbconvert --to notebook --execute --inplace A_contraluz_tutorial.ipynb` (*Restart & Run All*).
3. `streamlit run app_streamlit.py` sin errores.
4. Prueba manual en carpeta limpia descomprimiendo `entrega_grupo3_acontraluz.zip` y creando un `.venv` nuevo desde `requirements.txt`.
