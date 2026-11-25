# Arquitectura y Decisiones Metodológicas — *A contra(luz)*

> **Regla de integridad:** Este documento se completa con **hechos verificados** a partir de la Fase 2 (inspección real de la API de `datos.gov.co` y del Clasificador UNSPSC). Las secciones marcadas `[PENDIENTE FASE X]` no deben rellenarse con supuestos.

---

## 1. Pregunta Única de Investigación (R1 y Rubro 4)
- **Estado:** `[PENDIENTE FASE 2 — congelar el miércoles 25 al mediodía tras verificar cobertura 2022–2025]`
- **Borrador base de trabajo (alineado con recomendación del equipo pedagógico):**
  > *¿Qué tanto se desvía el valor y la composición de la contratación ejecutada en SECOP II frente a lo planeado en el Plan Anual de Adquisiciones (PAA) entre 2022 y 2025 en [5–6 entidades nacionales concretas], y en qué entidades, modalidades de contratación o segmentos UNSPSC se concentra dicha desviación?*
- **Delimitación explícita:**
  - **Población / Muestra:** `[PENDIENTE FASE 2: 5–6 entidades del orden nacional con NIT verificado]`
  - **Periodo:** `2022–2025` *(confirmar si 2025 es año completo o parcial al momento de corte en `datos.gov.co` y documentar su tratamiento).*
  - **Variables y alcance:** Planeación (PAA), ejecución contractual (Contratos Electrónicos SECOP II) y clasificación de bienes/servicios (UNSPSC).

---

## 2. Selección de Entidades "Sin Complicaciones" (R4)

### Criterios objetivos de filtrado (Fase 2)
1. **Nivel central del orden nacional sin red regional masiva** (excluir entidades desconcentradas con decenas de seccionales o volúmenes extremos como ICBF, SENA, Policía, Ejército, INVÍAS).
2. **Estabilidad institucional durante 2022–2025** (sin creación reciente, fusión ni liquidación en el periodo).
3. **Clave unívoca de cruce (1 NIT = 1 entidad)** entre PAA y Contratos SECOP II.
4. **Volumen manejable ("punto dulce"):** aprox. `300 – 4.000` contratos por entidad en 2022–2025 (riqueza estadística + `.zip` liviano).
5. **Cobertura en los 4 años (2022–2025)** y alta completitud de códigos UNSPSC.

### Muestra seleccionada *(llenar en Fase 2 / actualizar en Fase 4)*

| Etapa | Entidad | NIT verificado | Sector / Perfil | Filas PAA (2022–2025) | Filas Contratos SECOP II (2022–2025) | Observaciones |
|---|---|---|---|---:|---:|---|
| Piloto 1 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | — | — | — |
| Piloto 2 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | — | — | — |
| Piloto 3 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | — | — | — |
| Escala 4 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | — | — | — |
| Escala 5 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | — | — | — |
| Escala 6 *(opc.)* | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` | — | — | — |

---

## 3. Regla de Cruce PAA ↔ Contratos SECOP II ↔ Clasificador UNSPSC (R2 y R6)
- **Estado:** `[PENDIENTE FASE 2 — definir tras inspeccionar columnas reales]`
- **Clave entidad-año:** `[NIT normalizado + año fiscal / vigencia]`
- **Regla de normalización del código UNSPSC:**
  - Formato original observado en PAA: `[PENDIENTE FASE 2]`
  - Formato original observado en Contratos SECOP II: `[PENDIENTE FASE 2]`
  - Formato oficial en Clasificador de Colombia Compra Eficiente: `[PENDIENTE FASE 2]`
  - **Nivel jerárquico elegido para el cruce:** `[Segmento (2 dígitos) / Familia (4 dígitos) / Clase (6 dígitos) — justificar cobertura y tasa de emparejamiento]`
  - **Tratamiento de celdas con múltiples códigos UNSPSC:** `[Documentar regla determinística, ej. código principal vs. desagregación proporcional]`

---

## 4. Catálogo de Indicadores Definidos Desde el Inicio (R5 y R7)

| ID | Indicador | Fórmula / Definición exacta | Unidad | Nivel de agregación | Qué aporta a la pregunta |
|---|---|---|---|---|---|
| **I1** | Tasa de ejecución vs. planeación | $\frac{\text{Valor ejecutado SECOP II}}{\text{Valor planeado PAA}} \times 100$ | `%` y brecha en COP | Entidad × Año y Entidad × Segmento UNSPSC | Cuantifica directamente la desviación (subejecución o sobreejecución frente al PAA). |
| **I2** | Peso de la contratación directa | $\frac{\text{Valor (y \#) en Contratación Directa}}{\text{Total contratado SECOP II}} \times 100$ | `%` | Entidad × Año y Modalidad | Identifica si las desviaciones se concentran en modalidades sin competencia abierta. |
| **I3** | Concentración por proveedor | Participación Top-5 proveedores (`CR5`) e Índice Herfindahl-Hirschman ($\text{HHI} = \sum s_i^2$) | `%` y escala `0–10.000` | Entidad × Año | Mide riesgo de concentración de recursos en pocos contratistas. |
| **I4** | Composición y brecha por categoría UNSPSC | Participación y desviación planeado vs. ejecutado por `[Segmento/Familia]` UNSPSC | `%` y COP | Entidad × Categoría UNSPSC | Revela en qué rubros de bienes/servicios se concentran los desvíos. |
| **I5** | Extensión metodológica sugerida por IA *(Rubro 5)* | `[PENDIENTE FASE 5]` | `[PENDIENTE]` | `[PENDIENTE]` | Demuestra el efecto concreto de ir más allá de lo recomendado por los profesores. |

---

## 5. Decisiones de Limpieza y Calidad de Datos (Rubro 1)
- **Estado:** `[PENDIENTE FASE 3]`
- Documentar aquí cada decisión justificada sobre:
  1. **Tipos de datos** (fechas, montos monetarios, NITs y códigos UNSPSC como `str` para no perder ceros a la izquierda).
  2. **Valores faltantes** (conteo explícito, criterio de conservación vs. exclusión o etiquetado `"Sin clasificar"`).
  3. **Duplicados** (identificador único de contrato/ítem PAA y cómo evitar doble conteo de versiones/modificaciones).
  4. **Atípicos y estados contractuales** (ej. contratos anulados/borrador, valores en 0 o negativos, errores de digitación en miles de millones).

---

## 6. Limitaciones Metodológicas Explícitas (Rubro 4)
*(Completar y afinar con cifras empíricas en Fases 3–6)*
1. **Diferencia conceptual entre PAA y contratos firmados:** el PAA refleja intención de gasto y puede actualizarse durante el año; un contrato firmado en un año puede incluir vigencias futuras o adiciones posteriores.
2. **Desfase y calidad de reporte en `datos.gov.co`:** los conjuntos abiertos de SECOP II pueden presentar rezagos de actualización o diferencias frente al portal transaccional vivo.
3. **Alcance descriptivo (no causal):** las desviaciones y niveles de concentración señalan focos de atención para veeduría ciudadana, pero no demuestran por sí solos irregularidades ni relaciones causales.
4. **Validez externa:** los hallazgos corresponden a la muestra seleccionada de entidades nacionales de nivel central (2022–2025) y no se extrapolan mecánicamente a entidades territoriales ni a entidades desconcentradas con red regional.
5. **Granularidad UNSPSC:** `[Documentar porcentaje de registros sin código UNSPSC válido o con múltiples códigos]`.

---

## 7. Matriz de Trazabilidad de Recomendaciones del Equipo Pedagógico (R1–R8 — Rubro 3)

| Código | Recomendación registrada (`3.75` + correo `4.3`) | Evidencia en el repositorio / notebook | Estado |
|---|---|---|---|
| **R1** | Reformular la pregunta hacia el fenómeno (no la herramienta) | Sección 1 del notebook + `docs/decisiones.md` | `[PENDIENTE]` |
| **R2** | Cruzar PAA con contratos ejecutados de SECOP II | `src/limpieza_cruce.py` + Sección de cruce del notebook | `[PENDIENTE]` |
| **R3** | Descargar datos desde `datos.gov.co` vía API (`requests`/SODA) | `src/ingesta.py` + caché en `data/raw/` | `[PENDIENTE]` |
| **R4** | Fijar muestra concreta (5–10 entidades nacionales, 2022–2025) | `src/config.py` + `data/README.md` | `[PENDIENTE]` |
| **R5** | Definir indicadores concretos desde el inicio (`% ejecutado`, contratación directa, concentración por proveedor) | `src/indicadores.py` + `data/dashboard_data/` | `[PENDIENTE]` |
| **R6** | Explicar método exacto de cruce con Clasificador UNSPSC (código y nivel) | `src/limpieza_cruce.py` + Sección 3 de este doc y del notebook | `[PENDIENTE]` |
| **R7** | Especificar qué se calcula en cada paso de la secuencia | Estructura modular en `src/` + introducciones ≤ 3 líneas | `[PENDIENTE]` |
| **R8** | Aportar análisis económico sustantivo con Streamlit como resultado | `A_contraluz_tutorial.ipynb` + `app_streamlit.py` | `[PENDIENTE]` |
