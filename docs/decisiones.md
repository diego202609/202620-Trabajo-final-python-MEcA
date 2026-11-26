# Arquitectura y Decisiones Metodológicas — *A contra(luz)*

> **Regla de integridad:** Todas las decisiones de entidades, formatos de códigos, tasas de emparejamiento y reglas de cruce consignadas aquí están respaldadas por evidencia verificada en `datos.gov.co` sobre la muestra definitiva de 6 entidades nacionales (`2022–2025`).

---

## 1. Pregunta Única de Investigación (R1 y Rubro 4)
- **Estado:** **CONGELADA** (aprobada el 25 de noviembre de 2026).
- **Pregunta central:**
  > *¿Qué tanto se desvía la contratación ejecutada en SECOP II frente a lo planeado en el Plan Anual de Adquisiciones (PAA) entre 2022 y 2025 en seis entidades nacionales del nivel central (ANCP, MinHacienda, MinAmbiente, MinEducación, MinCulturas y DNP), y en qué entidades, modalidades de contratación, proveedores o segmentos UNSPSC se concentra dicha desviación?*
- **Delimitación explícita:**
  - **Población / Muestra:** 6 entidades del orden nacional, nivel central, con `estado = Publicado` en las cuatro vigencias (`ANCP`, `MinHacienda`, `MinAmbiente`, `MinEducación`, `MinCulturas`, `DNP`).
  - **Periodo:** Vigencias fiscales **2022–2025** (4 años completos).
  - **Variables y alcance:** Planeación (PAA Detalle y Encabezado), ejecución contractual (Contratos Electrónicos SECOP II firmados entre `2022-01-01` y `2025-12-31`) y clasificación estándar de bienes y servicios (UNSPSC v14.1).

---

## 2. Selección de Entidades "Sin Complicaciones" (R4)

### Criterios objetivos aplicados en Fase 2
1. **Orden nacional, nivel central sin red regional desconcentrada:** se descartaron entidades como *MinTrabajo* (25 direcciones territoriales con códigos distintos) o redes masivas como ICBF/SENA/Policía.
2. **Cobertura institucional real y estabilidad 2022–2025:** se descartó *MinTIC* (solo 165 contratos propios en 4 años porque su grueso contractual cursa por el fondo autónomo FUTIC).
3. **Estado `Publicado` en los 4 años:** se descartaron *MinTransporte* (2023 en `Borrador`) y *SuperFinanciera* (2022 en `Borrador`).
4. **Clave unívoca (1 `codigo_entidad` = 1 `NIT`):** verificada en `b6m4-qgqv`, `9sue-ezhx` y `jbjy-vk9h`.
5. **Volumen manejable y 100% cobertura UNSPSC en contratos:** se descartaron *MinCIT* y *MinMinas* por picos extremos aislados de varios billones que distorsionan comparaciones entre entidades de tamaño comparable.

### Muestra aprobada (desarrollo incremental: 3 piloto → 6 definitivas)

| Etapa | Entidad | `codigo_entidad` | `NIT` | Sector / Perfil | Contratos 2022–2025 | Ítems PAA 2022–2025 |
|---|---|---:|---:|---|---:|---:|
| **Piloto 1** | **ANCP (Colombia Compra Eficiente)** | `700037070` | `900514813` | Rectoría de compras públicas | `2.315` | `2.072` |
| **Piloto 2** | **MinHacienda** | `700065089` | `899999090` | Hacienda y política fiscal | `2.155` | `2.395` |
| **Piloto 3** | **MinAmbiente** | `700209018` | `830115395` | Ambiente y desarrollo sostenible | `4.820` | `5.410` |
| **Escala 4** | **MinEducación (MEN)** | `700066053` | `899999001` | Educación | `4.484` | `4.688` |
| **Escala 5** | **MinCulturas** | `700637010` | `830034348` | Cultura | `5.159` | `6.706` |
| **Escala 6** | **DNP** | `700220049` | `899999011` | Planeación nacional | `6.384` | `5.889` |

---

## 3. Regla Exacta de Cruce PAA ↔ Contratos SECOP II ↔ Clasificador UNSPSC (R2 y R6)
- **Clave entidad-año:** `codigo_entidad` (texto de 9 dígitos, verificado idéntico en las 3 APIs) + `anio` (`annio` en PAA; año extraído de `fecha_de_firma` en Contratos).
- **Normalización del código UNSPSC:**
  - En **PAA Detalle (`categorias_unspsc`):** texto de 8 dígitos sin prefijo (ej. `80121601`), con `1.462` filas en la muestra completa de 6 entidades que incluyen múltiples códigos separados por `;`, `,` o espacio → se extrae el **primer código de 8 dígitos** (categoría principal del ítem) con la expresión regular `\d{8}`.
  - En **Contratos SECOP II (`codigo_de_categoria_principal`):** texto con prefijo de versión (ej. `V1.80121601`), y `51` registros `"UNSPECIFIED"` (`0,20%` sobre `25.317`) → se extrae el **código de 8 dígitos** tras el prefijo con `\d{8}`; los `"UNSPECIFIED"` se etiquetan explícitamente como `"Sin clasificar"`.
  - En **Clasificador UNSPSC (`clasificador_unspsc.csv`):** `49.022` productos normalizados a texto de longitud fija: `codigo_segmento` (`2` dígitos), `codigo_familia` (`4` dígitos), `codigo_clase` (`6` dígitos), `codigo_producto` (`8` dígitos).
- **Decisión de nivel jerárquico (justificada empíricamente en las 6 entidades):**
  - El cruce por **Producto (8 dígitos)** falla en más del 60% de registros (solo **39,55%** en PAA y **36,37%** en Contratos) porque las entidades reportan códigos terminados en `00` correspondientes a nivel de **Clase**.
  - Por tanto, el cruce oficial contra el Clasificador se realiza a nivel de **Clase (`6` dígitos: `codigo_clase`)** —que logra **99,99%** de emparejamiento en PAA y **99,80%** en Contratos— y las comparaciones sectoriales entre PAA y Contratos se agregan a nivel de **Segmento (`2` dígitos, 56 categorías)** para mantener legibilidad analítica sin pérdida de cobertura.

---

## 4. Normalización de Modalidades y Limpieza de Datos (Rubro 1 y R5)
- **Homologación de modalidades PAA ↔ Contratos:** se construye un diccionario explícito en `src/limpieza_cruce.py` (quitando tildes y mayúsculas) hacia **7 macro-modalidades comparables**, complementado con rescate desde `causal_de_contratacion` (Ley 1150 de 2007, art. 2):
  1. `Contratación directa` (agrupa `CONTRATACION DIRECTA`, `Contratación directa`, `Contratación Directa (con ofertas)`)
  2. `Licitación pública y AMP` (agrupa `Licitación pública`, `Obra pública` y `Acuerdo Marco de Precios`)
  3. `Selección abreviada` (subasta inversa y menor cuantía)
  4. `Mínima cuantía`
  5. `Concurso de méritos`
  6. `Régimen especial`
  7. `No definido` (`2.733` ítems crudos en PAA → `2.251` rescatados desde causal legal por `$1.975,68 MM`, quedando solo `482` omisiones reales, `1,8%`)
- **Tratamiento explícito de valores `<= $1.000 COP` y atípicos:**
  - En Contratos (`25.317` totales, `0` negativos), `951` registros tienen `valor_del_contrato == $0` (`565` son Acuerdos Marco de Precios de ANCP + convenios/comodatos sin erogación) y `13` registros presentan cuantía simbólica de plataforma (`$0,01` a `$1.000 COP`). Los `964` se conservan marcados con bandera `es_contrato_sin_cuantia = True` para el conteo institucional y se excluyen del cálculo de medias e Índice `HHI` (calculados sobre los `24.353` contratos válidos `> $1.000 COP`).
  - En PAA (`27.160` ítems), se documentan ambas bases monetarias: **`valor_esperado_de_presupuesto`** (vigencia actual, base principal) y **`valor_total_esperado`** (incluye vigencias futuras), y se controla el cuasi-duplicado administrativo de `$333,54 MM` en MinAmbiente 2023 (*Fondo para la Vida y la Biodiversidad*), corrigiendo su ejecución anual de `32,9%` a `50,9%` (`+18,0 pp`).

---

## 5. Catálogo de Indicadores Definidos Desde el Inicio (R5 y R7)

| ID | Indicador | Fórmula / Definición | Unidad | Nivel | Qué responde |
|---|---|---|---|---|---|
| **I1** | Tasa de ejecución vs. planeación | $\frac{\sum \text{Valor contratado SECOP II}}{\sum \text{Valor planeado PAA (vigencia actual)}} \times 100$ *(y sensibilidad contra valor total)* | `%` y brecha en miles de millones COP | Entidad × Año y Entidad × Segmento UNSPSC | Cuantifica magnitud y dirección de la desviación planeado vs. ejecutado. |
| **I2** | Peso de la contratación directa | $\frac{\text{Valor (y \#) en Contratación Directa}}{\text{Total contratado con cuantía}>0} \times 100$ | `%` | Entidad × Año y Macro-modalidad | Muestra en qué entidades y modalidades sin competencia se concentra el gasto. |
| **I3** | Concentración por proveedor | Participación Top-5 (`CR5`, %) e Índice Herfindahl-Hirschman ($\text{HHI} = \sum s_i^2 \times 10.000$) sobre proveedores con cuantía > 0 | `%` y escala `0–10.000` | Entidad × Año | Mide si el gasto ejecutado se concentra en pocos contratistas. |
| **I4** | Brecha y composición por Segmento UNSPSC | Participación y desviación planeado vs. ejecutado por `codigo_segmento` (`2` dígitos) y `codigo_familia` (`4` dígitos) | `%` y miles de millones COP | Entidad × Segmento UNSPSC | Identifica en qué tipos de bienes/servicios se concentran los desvíos. |
| **I5a** | Deflactación intertemporal IPC DANE *(Mejora IA #1 — Rubro 5)* | $P_{it}^{\text{real}} = P_{it}^{\text{nom}}\cdot\frac{I_{2025}}{I_t}$, $E_{it}^{\text{real}} = E_{it}^{\text{nom}}\cdot\frac{I_{2025}}{I_t}$ (serie anual certificada DANE base `2025 = 100`) | Miles de millones COP constantes de 2025 y `%` crecimiento real | Entidad × Año y Entidad × Segmento | Corrige la ilusión monetaria (`+20,83%` inflación acumulada 2023–2025): amplía la brecha real total en `-$93,75 MM` y revela contracciones reales de `-19,2%` en DNP y `-19,6%` en MinAmbiente. |
| **I5b** | Índice de Disimilitud Estructural de Duncan *(Mejora IA #2 — Rubro 5)* | $D_{it} = \frac{1}{2}\sum_{s \in \mathcal{S}} \lvert w_{ist}^E - w_{ist}^P \rvert \times 100$ | `%` del gasto reasignado (`0–100%`) | Entidad × Año | Destapa reasignación sectorial oculta por compensación: MinCulturas exhibe `100,4%` de ejecución agregada pero reasigna en promedio `32,1%` de su gasto entre segmentos UNSPSC. |

---

## 6. Limitaciones Metodológicas Explícitas (Rubro 4)
1. **Diferencia conceptual PAA vs. contrato firmado:** el PAA en `datos.gov.co` refleja la **última versión publicada** del plan anual (las entidades realizan entre 17 y 82 actualizaciones al año) y puede incluir vigencias futuras; a su vez, un contrato firmado en un año puede ejecutarse en varios años o recibir adiciones.
2. **Acuerdos Marco de Precios y convenios sin cuantía (`$0`):** en entidades como ANCP, los Acuerdos Marco aparecen firmados por `$0` porque el gasto real se materializa luego en órdenes de compra de otras entidades estatales.
3. **Posibles registros duplicados o errores administrativos en el PAA:** el análisis empírico identificó casos como dos líneas idénticas de $333,5 mil millones en MinAmbiente 2023, recordando que los datos administrativos abiertos reflejan la calidad de diligenciamiento de cada entidad.
4. **Alcance descriptivo (no causal):** las brechas entre planeación y ejecución, el peso de la contratación directa y el HHI son indicadores de alerta para veeduría ciudadana; no prueban por sí solos irregularidades ni relaciones causales.
5. **Validez externa:** los resultados se circunscriben a seis entidades nacionales del nivel central (2022–2025) y no se generalizan automáticamente a alcaldías, gobernaciones ni entidades desconcentradas con redes territoriales.

---

## 7. Matriz de Trazabilidad de Recomendaciones del Equipo Pedagógico (R1–R8 — Rubro 3)

| Código | Recomendación registrada (`3.75` + correo `4.3`) | Evidencia en el repositorio / notebook | Estado |
|---|---|---|---|
| **R1** | Reformular la pregunta hacia el fenómeno (no la herramienta) | Encabezado y Sección 1 de `A_contraluz_tutorial.ipynb` | `COMPLETADO` |
| **R2** | Cruzar PAA con contratos ejecutados de SECOP II | `src/limpieza_cruce.py` + `tests/test_limpieza_cruce.py` | `COMPLETADO (6 ENT.)` |
| **R3** | Descargar datos desde `datos.gov.co` vía API (`requests`/SODA) | `src/ingesta.py` + `tests/test_ingesta.py` | `COMPLETADO (6 ENT.)` |
| **R4** | Fijar muestra concreta (5–10 entidades nacionales, 2022–2025) | `src/config.py` (6 entidades: `27.160` PAA y `25.317` contratos) | `COMPLETADO (6 ENT.)` |
| **R5** | Definir indicadores concretos desde el inicio | `src/indicadores.py` + `data/dashboard_data/*.csv` | `COMPLETADO (6 ENT.)` |
| **R6** | Explicar método exacto de cruce UNSPSC (código y nivel) | `Clase 6d` / `Segmento 2d` (`99,99%` PAA y `99,80%` Contratos) | `COMPLETADO (6 ENT.)` |
| **R7** | Especificar qué se calcula en cada paso de la secuencia | Introducciones de Secciones 1–6 en `A_contraluz_tutorial.ipynb` + `src/` | `COMPLETADO` |
| **R8** | Análisis económico sustantivo con Streamlit como resultado | `A_contraluz_tutorial.ipynb` + `app_streamlit.py` | `COMPLETADO` |
