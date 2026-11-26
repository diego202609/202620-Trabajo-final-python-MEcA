# A contra(luz): Análisis y Veeduría de la Contratación Pública en Colombia

**Trabajo Final — Taller de Programación Aplicada a Python (MECA 4110 / EECO 5617, Universidad de los Andes, 2026-II)**  
**Grupo 3:**
- Diego Andrés Niño Estupiñán (`201719748`)
- Juan Sebastián Puerto Sanz (`201532975`)
- Nathalia Alexandra Acero Pérez (`202524470`)

---

## 1. Descripción del Proyecto
Tutorial autocontenido de ciencia de datos y economía en Jupyter Notebook (`A_contraluz_tutorial.ipynb`) acompañado de módulos reproducibles (`src/`), pruebas automáticas (`tests/`) y un tablero interactivo en **Streamlit (`app_streamlit.py`)**.

El proyecto contrasta la **planeación contractual (Plan Anual de Adquisiciones — PAA, `27.160` ítems)** frente a la **contratación ejecutada en SECOP II (`25.317` contratos)** e integrada al `99,8%+` con el **Clasificador de Bienes y Servicios (UNSPSC v14.1, `49.022` productos)** para una muestra concreta de **6 entidades nacionales del nivel central (2022–2025)**: `ANCP`, `MinHacienda`, `MinAmbiente`, `MinEducación`, `MinCulturas` y `DNP`. Consulta programáticamente la API pública Socrata (`datos.gov.co`) y conserva copia congelada local dentro del `.zip` para garantizar reproducibilidad total sin conexión.

---

## 2. Estructura del Repositorio

```text
a-contraluz-secop/
├── AGENTS.md                       # Reglas no negociables para agentes de IA y humanos
├── README.md                       # Guía del equipo, rutina Git y cómo ejecutar
├── project_notes.md                # Bitácora viva de decisiones, comandos y verificaciones
├── requirements.txt                # Dependencias con versiones acotadas
├── pytest.ini                      # Configuración de pruebas automáticas
├── .gitignore                      # Exclusiones (.venv, .env, caché temporal)
├── .env.example                    # Variable opcional SOCRATA_APP_TOKEN
├── .agents/
│   ├── agents/
│   │   ├── data-worker.md          # Worker (model: flash) para cálculos y tests
│   │   ├── viz-worker.md           # Worker (model: flash) para gráficas Plotly
│   │   └── rubric-auditor.md       # Auditor (solo lectura) contra rúbrica 20/20
│   └── skills/
│       ├── acontraluz-charts/SKILL.md   # Estándar visual y accesibilidad Plotly
│       └── rubrica-notebook/SKILL.md    # Checklist estricto del .ipynb y .zip
├── docs/
│   └── decisiones.md               # Pregunta final, muestra, nivel UNSPSC y limitaciones
├── data/
│   ├── README.md                   # Diccionario verificado de fuentes, grano y cautelas
│   ├── raw/                        # Datos congelados vía API (inmutables, van en el .zip)
│   ├── processed/                  # Tablas limpias y cruzadas
│   ├── dashboard_data/             # CSVs finales (contrato para Notebook y Streamlit)
│   └── pruebas/                    # Salidas aisladas de pruebas (no se mezclan)
├── src/                            # Módulos Python (# %%) con la lógica reproducible
├── tests/                          # Pruebas automáticas offline (pytest + fixtures)
├── A_contraluz_tutorial.ipynb      # Tutorial principal autocontenido (protagonista del .zip)
├── app_streamlit.py                # Tablero interactivo Streamlit (resultado del análisis)
└── empaquetar_entrega.py           # Genera entrega_grupo3_acontraluz.zip limpio
```

---

## 3. Reparto de Frentes del Equipo (Propiedad de Carpetas)

| Frente | Responsable | Carpetas / archivos bajo su propiedad | Rama |
|---|---|---|---|
| **Frente 1 — Ingesta, API SODA y Calidad** | Diego Andrés Niño Estupiñán | `src/config.py`, `src/ingesta.py`, `data/raw/`, `data/README.md`, `tests/test_ingesta.py` | `feat/ingesta-api` |
| **Frente 2 — Limpieza, Cruce UNSPSC, Indicadores y Mejora IA (Rubro 5)** | Juan Sebastián Puerto Sanz | `src/limpieza_cruce.py`, `src/indicadores.py`, `data/processed/`, `data/dashboard_data/`, `tests/test_indicadores.py` | `feat/cruce-indicadores` |
| **Frente 3 — Visualización, Streamlit, Notebook y Empaquetado `.zip`** | Nathalia Alexandra Acero Pérez | `src/visualizacion.py`, `app_streamlit.py`, `A_contraluz_tutorial.ipynb`, `README.md`, `docs/decisiones.md`, `empaquetar_entrega.py` | `feat/fase6-entregables` |

---

## 4. Cronograma de Sprint (Meta: Viernes 27 · Límite Oficial: Sábado 28, 23:59 COT)

| Día | Bloques principales | Hito de cierre ("Done") |
|---|---|---|
| **Mié 25** | **Mañana:** Repo en GitHub + Descubrimiento de APIs `datos.gov.co` (sin descarga masiva) + congelar `data/README.md` y `docs/decisiones.md`.<br>**Tarde/Noche:** Pipeline piloto funcionando en **3 entidades** + esqueleto del notebook. | Pipeline ingesta/limpieza validado en 3 entidades piloto + `pytest` verde. |
| **Jue 26** | **Mañana:** Escalamiento a **5–6 entidades (2022–2025)** en `src/config.py` + indicadores R5 en `data/dashboard_data/`.<br>**Tarde/Noche:** **Rubro 5 (Uso de IA)** implementado (*antes vs. después*) + gráficas Plotly y `app_streamlit.py`. | CSVs definitivos, mejora Rubro 5 y tablero Streamlit operativos. |
| **Vie 27** | **Mañana:** Ensamble completo de `A_contraluz_tutorial.ipynb` + `nbconvert --execute`.<br>**Tarde/Noche:** Auditoría con `rubric-auditor`, PR `fix/auditoria`, generación de `.zip` y prueba en carpeta limpia sin internet. | **META:** `.zip` validado 20/20 listo para subir. |
| **Sáb 28** | Colchón solo para ajustes menores y subida final del `.zip` a Bloque Neón. | Entrega confirmada antes de 23:59 COT. |

---

## 5. Cómo Ejecutar (Evaluador y Equipo)

### Primera vez en un computador nuevo
1. Clonar el repositorio (o descomprimir el archivo `.zip` de entrega) y abrir la carpeta en VS Code / Antigravity.
2. Crear el entorno virtual con Python 3.11 o superior:
   - **Windows (PowerShell):**
     ```powershell
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Mac / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. Instalar dependencias:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Comandos principales

| Acción | Comando |
|---|---|
| Ejecutar pruebas automáticas offline | `python -m pytest -v` |
| Ejecutar el notebook de principio a fin (*Restart & Run All*) | `python -m jupyter nbconvert --to notebook --execute --inplace A_contraluz_tutorial.ipynb` |
| Abrir el tablero interactivo en Streamlit | `streamlit run app_streamlit.py` |
| Regenerar los datos desde la API de `datos.gov.co` | `python -m src.ingesta --modo completo --actualizar-api` *(opcional; el notebook usa caché local por defecto)* |
| Generar el `.zip` limpio de entrega | `python empaquetar_entrega.py` |

*(Nota: si se cuenta con un token de aplicación de Socrata para mayor límite de consultas al regenerar desde API, puede configurarse en `.env` siguiendo `.env.example`. No es necesario para ejecutar el notebook en modo caché local).*

---

## 6. Rutina de Trabajo Colaborativo en Git (Patrón Taller 2)

### Cada vez que empieces a trabajar
1. Activa el entorno virtual (`.venv` visible al inicio de la terminal).
2. Trae los cambios más recientes de `main`:
   ```bash
   git checkout main
   git pull origin main
   ```
3. Crea o actualiza tu rama del frente:
   ```bash
   git checkout -b feat/mi-tarea
   # o si la rama ya existe:
   git checkout feat/mi-tarea
   git merge main
   ```
4. Actualiza librerías si cambió `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Al terminar un bloque de trabajo
1. Corre pruebas antes de subir:
   ```bash
   python -m pytest -v
   ```
2. Guarda y sube en tu rama:
   ```bash
   git status
   git add <archivos_de_tu_frente>
   git commit -m "Mensaje claro y corto del cambio"
   git push -u origin feat/mi-tarea
   ```
3. Abre un **Pull Request hacia `main`** y pide revisión a otro integrante.

### Reglas rápidas de convivencia
- **Siempre `git pull`** antes de empezar.
- **Nunca subir** `.env`, tokens, contraseñas ni carpetas `.venv/`.
- **Respeta la propiedad de carpetas:** no edites archivos de otro frente sin coordinar primero.
- Si aparece un conflicto de merge (`conflict`), **no forzar push** ni sobreescribir; avisar al equipo para resolverlo juntos.
