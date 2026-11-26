# Informe Ejecutivo de Hallazgos — Muestra Piloto (*A contra(luz)*)

> **Nota de trazabilidad:** Este documento se genera automáticamente ejecutando `python -m src.limpieza_cruce` a partir de las bases verificadas de `datos.gov.co` (`2022–2025`). Todas las cifras monetarias están expresadas en **miles de millones de pesos corrientes (`$ MM COP`)**.

---

## 1. Resumen Ejecutivo para Discusión del Equipo

- **Muestra piloto evaluada (`2022–2025`):** `ANCP (Colombia Compra Eficiente)`, `MinAmbiente` y `MinHacienda` (`27.160` ítems de PAA y `25.317` contratos electrónicos en SECOP II).
- **Magnitud agregada del cuatrienio:** frente a un presupuesto planeado de vigencia actual de **$9.677,37 MM** (**$9.343,83 MM** excluyendo un registro cuasi-duplicado administrativo detectado), las tres entidades suscribieron contratos por **$7.780,10 MM** (`83,3%` de ejecución agregada ajustada).
- **Cuatro hallazgos sustantivos que ya perfilan la narrativa del trabajo final:**
  1. **La auditoría de calidad cambia las conclusiones económicas:** en `MinAmbiente 2023` encontramos dos líneas de **$333,54 MM** para constituir el patrimonio autónomo *Fondo para la Vida y la Biodiversidad* (solo varió una cita de artículos de la Ley 2294 de 2023 sin borrar la fila previa). Al corregir ese doble conteo, su ejecución de 2023 sube de **32,9% a 50,9% (+18,0 puntos porcentuales)**.
  2. **La contratación directa domina en número de contratos, pero no siempre en valor:** aunque representa la gran mayoría de contratos firmados (prestación de servicios profesionales), en `MinHacienda` las grandes licitaciones y selecciones abreviadas (seguros previsionales/FONPET) reducen drásticamente su peso en dinero, mientras en `MinAmbiente` el régimen especial concentra convenios de gran cuantía (ej. PNUD).
  3. **Demostración empírica del nivel UNSPSC (respuesta directa a la observación R6):** cruzar por código de Producto (`8` dígitos) pierde más del 82% de los datos (`39,5%` en PAA y `36,4%` en Contratos), porque las entidades planean y contratan usando códigos terminados en `00` (nivel Clase). Al cruzar por **Clase (`6` dígitos) y Segmento (`2` dígitos)**, el emparejamiento sube a **100,0%** en PAA y **99,8%** en Contratos.
  4. **Rescate de modalidades desde `causal_de_contratacion` y efecto de vigencias futuras:** en la columna cruda `modalidad` del PAA venían `2.733` ítems como `"No Definido"`, pero al cruzar con `causal_de_contratacion` rescatamos la modalidad legal exacta de **`2.251` ítems ($1.975,68 MM)**, dejando solo `482` omisiones reales. Además, las vigencias futuras explican **$978,41 MM** de diferencia entre valor total y presupuesto anual.

---

## 2. Planeación (PAA) vs. Ejecución (SECOP II) por Entidad y Año (`$ MM COP`)

| Entidad | Año | Versiones PAA | PAA Vigencia (`$ MM`) | PAA Ajustado sin Dup. (`$ MM`) | Ejecutado SECOP II (`$ MM`) | % Ejec. Bruta | % Ejec. Ajustada | Contratos (> $0) | Proveedores Únicos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **ANCP** | 2022 | 82 | $62,22 | $62,22 | $34,86 | 56,0% | **56,0%** | 305 | 297 |
| **ANCP** | 2023 | 47 | $61,36 | $61,36 | $44,20 | 72,0% | **72,0%** | 381 | 316 |
| **ANCP** | 2024 | 33 | $79,02 | $79,02 | $38,37 | 48,5% | **48,5%** | 406 | 397 |
| **ANCP** | 2025 | 17 | $128,42 | $128,42 | $56,84 | 44,3% | **44,3%** | 420 | 406 |
| **DNP** | 2022 | 29 | $200,19 | $200,19 | $167,46 | 83,7% | **83,7%** | 1.135 | 1.096 |
| **DNP** | 2023 | 38 | $180,12 | $180,12 | $160,27 | 89,0% | **89,0%** | 2.075 | 1.272 |
| **DNP** | 2024 | 53 | $217,26 | $217,26 | $220,26 | 101,4% | **101,4%** | 1.527 | 1.487 |
| **DNP** | 2025 | 33 | $185,60 | $185,60 | $163,42 | 88,1% | **88,1%** | 1.638 | 1.584 |
| **MinAmbiente** | 2022 | 27 | $125,57 | $125,57 | $110,96 | 88,4% | **88,4%** | 1.038 | 993 |
| **MinAmbiente** | 2023 | 28 | $940,90 | $607,37 | $309,25 | 32,9% | **50,9%** | 1.277 | 1.151 |
| **MinAmbiente** | 2024 | 21 | $129,45 | $129,45 | $107,07 | 82,7% | **82,7%** | 1.267 | 1.240 |
| **MinAmbiente** | 2025 | 22 | $114,73 | $114,73 | $107,85 | 94,0% | **94,0%** | 1.231 | 1.211 |
| **MinCulturas** | 2022 | 37 | $256,76 | $256,76 | $196,31 | 76,5% | **76,5%** | 789 | 739 |
| **MinCulturas** | 2023 | 40 | $409,67 | $409,67 | $528,07 | 128,9% | **128,9%** | 1.556 | 1.204 |
| **MinCulturas** | 2024 | 45 | $649,71 | $649,71 | $755,95 | 116,4% | **116,4%** | 1.409 | 1.337 |
| **MinCulturas** | 2025 | 42 | $677,03 | $677,03 | $521,54 | 77,0% | **77,0%** | 1.341 | 1.223 |
| **MinEducación** | 2022 | 40 | $237,10 | $237,10 | $273,00 | 115,1% | **115,1%** | 890 | 869 |
| **MinEducación** | 2023 | 57 | $1.364,80 | $1.364,80 | $1.657,68 | 121,5% | **121,5%** | 1.206 | 1.041 |
| **MinEducación** | 2024 | 43 | $1.414,06 | $1.414,06 | $540,59 | 38,2% | **38,2%** | 1.102 | 910 |
| **MinEducación** | 2025 | 50 | $971,02 | $971,02 | $1.044,86 | 107,6% | **107,6%** | 1.212 | 997 |
| **MinHacienda** | 2022 | 44 | $73,27 | $73,27 | $115,31 | 157,4% | **157,4%** | 365 | 318 |
| **MinHacienda** | 2023 | 56 | $489,67 | $489,67 | $220,68 | 45,1% | **45,1%** | 573 | 411 |
| **MinHacienda** | 2024 | 64 | $597,51 | $597,51 | $219,65 | 36,8% | **36,8%** | 467 | 425 |
| **MinHacienda** | 2025 | 62 | $111,93 | $111,93 | $185,63 | 165,9% | **165,9%** | 743 | 518 |

**Lectura rápida:**
- **ANCP:** planea sistemáticamente por encima de lo que contrata con recursos propios (`44,3%–72,0%`), además de suscribir **559 Acuerdos Marco de Precios** registrados en `$0` (cuyo gasto ejecutan luego las demás entidades compradoras en la Tienda Virtual).
- **MinAmbiente:** muestra alta correspondencia entre planeación y ejecución en 2022, 2024 y 2025 (`82,7%–94,0%`), con una caída en 2023 explicada por la programación del *Fondo para la Vida*.
- **MinHacienda:** exhibe la mayor volatilidad: sobreejecución frente al PAA de vigencia en 2022 (`157,4%`) y 2025 (`165,9%`), y subejecución en 2023–2024 (`45,1%` y `36,8%`) cuando se programaron operaciones financieras/capitalizaciones de gran escala.

---

## 3. Peso de la Contratación Directa: Planeado vs. Ejecutado (`2022–2025`)

| Entidad | PAA Ajustado (`$ MM`) | % PAA en Contratación Directa | % PAA con Modalidad «No definido» | Ejecutado SECOP II (`$ MM`) | % Valor Ejecutado en Contratación Directa | % # Contratos en Contratación Directa |
|---|---:|---:|---:|---:|---:|---:|
| **ANCP** | $331,02 | 53,3% | 25,5% | $174,27 | **91,4%** | 93,6% |
| **DNP** | $783,17 | 75,5% | 6,9% | $711,42 | **66,2%** | 91,1% |
| **MinAmbiente** | $977,11 | 58,2% | 1,7% | $635,14 | **61,5%** | 97,7% |
| **MinCulturas** | $1.993,17 | 45,8% | 1,1% | $2.001,87 | **46,8%** | 87,0% |
| **MinEducación** | $3.986,98 | 60,2% | 3,5% | $3.516,13 | **80,6%** | 91,1% |
| **MinHacienda** | $1.272,37 | 17,3% | 4,1% | $741,27 | **37,2%** | 88,8% |

**Lectura rápida:** Mirar solo el *número* de contratos lleva a creer que casi todo es contratación directa (`> 88%` de los contratos), pero al ponderar por *valor en pesos* aparecen diferencias estructurales enormes entre entidades. Además, rescatar la modalidad desde `causal_de_contratacion` redujo el peso «No definido» de MinHacienda de `56,2%` a solo `4,1%` (mientras en ANCP aún persiste un `25,5%` sin definir ni en modalidad ni en causal).

---

## 4. Concentración por Proveedor (`CR1`, `CR5` e Índice `HHI`)

*(Calculado sobre contratos válidos con cuantía `> $0`. Referencia económica estándar: `HHI < 1.500` desconcentrado, `1.500–2.500` moderado, `> 2.500` alta concentración).* 

| Entidad | Año | Proveedores | Top 1 (`CR1`) | Top 5 (`CR5`) | Índice `HHI` (0–10.000) | Principal Proveedor Adjudicado del Año |
|---|---:|---:|---:|---:|---:|---|
| **ANCP** | 2022 | 297 | 23,0% | **46,9%** | 797 | SIMPLIFAE PORTUGAL, S.A. |
| **ANCP** | 2023 | 316 | 26,1% | **49,6%** | 889 | SIMPLIFAE PORTUGAL, S.A. |
| **ANCP** | 2024 | 397 | 17,7% | **32,8%** | 476 | SIMPLIFAE PORTUGAL, S.A. |
| **ANCP** | 2025 | 406 | 18,4% | **43,7%** | 612 | COMCEL S.A. |
| **DNP** | 2022 | 1.096 | 8,2% | **22,8%** | 146 | SOCIEDAD DE TELEVISIÓN DE CALDAS QUINDÍO Y |
| **DNP** | 2023 | 1.272 | 7,1% | **20,5%** | 119 | SUBATOURS SAS |
| **DNP** | 2024 | 1.487 | 18,9% | **31,4%** | 409 | UNIÓN TEMPORAL LOGÍSTICA Y PLANEACIÓN |
| **DNP** | 2025 | 1.584 | 2,7% | **7,8%** | 25 | CONSORCIO CONSULTOR ESPECIALIZADO H-H |
| **MinAmbiente** | 2022 | 993 | 13,6% | **27,5%** | 262 | ORGANIZACION DE ESTADOS IBEROAMERICANOS OE |
| **MinAmbiente** | 2023 | 1.151 | 51,6% | **62,9%** | 2.716 | PROGRAMA DE LAS NACIONES UNIDAS PARA EL DE |
| **MinAmbiente** | 2024 | 1.240 | 3,6% | **14,5%** | 56 | SOCIEDAD DE TELEVISIÓN DE CALDAS QUINDÍO Y |
| **MinAmbiente** | 2025 | 1.211 | 9,2% | **19,7%** | 125 | ADESCUBRIR TRAVEL & ADVENTURE SAS |
| **MinCulturas** | 2022 | 739 | 9,5% | **25,6%** | 250 | UT AXA COLPATRIA - MAPRE SEGUROS GENERALES |
| **MinCulturas** | 2023 | 1.204 | 30,9% | **50,8%** | 1.152 | CONSORCIO CONSTRUCTOR H.M.I. |
| **MinCulturas** | 2024 | 1.337 | 5,4% | **21,6%** | 212 | FONDO MIXTO PARA LA PROMOCION DE LA CULTUR |
| **MinCulturas** | 2025 | 1.223 | 10,8% | **32,4%** | 326 | FONDO MIXTO PARA LA PROMOCION DE LA CULTUR |
| **MinEducación** | 2022 | 869 | 19,4% | **40,8%** | 535 | INFOTIC S.A |
| **MinEducación** | 2023 | 1.041 | 75,3% | **85,9%** | 5.715 | FINANCIERA DE DESARROLLO TERRITORIAL S.A. |
| **MinEducación** | 2024 | 910 | 13,6% | **50,2%** | 618 | FUNDACION PIES DESCALZOS |
| **MinEducación** | 2025 | 997 | 26,0% | **64,2%** | 1.244 | AGENCIA NACIONAL INMOBILIARIA VIRGILIO BAR |
| **MinHacienda** | 2022 | 318 | 22,8% | **52,4%** | 838 | BANCO DE LA REPUBLICA |
| **MinHacienda** | 2023 | 411 | 28,3% | **64,8%** | 1.223 | CONSORCIO PRAG FONPET 2023 |
| **MinHacienda** | 2024 | 425 | 28,2% | **60,0%** | 1.128 | LA PREVISORA S.A. COMPAÑÍA DE SEGUROS |
| **MinHacienda** | 2025 | 518 | 33,6% | **52,3%** | 1.249 | CONSORCIO PAC FONPET 2025 |

---

## 5. Top 8 Segmentos UNSPSC con Mayor Volumen y Brecha (`2022–2025`)

| Cód. | Segmento UNSPSC (2 dígitos) | PAA Ajustado (`$ MM`) | Ejecutado (`$ MM`) | Brecha Ejec. − PAA (`$ MM`) | % Ejecución |
|---|---|---:|---:|---:|---:|
| `80` | Servicios de Gestión, Servicios Profesionales de Emp | $4.488,62 | $3.154,67 | -$1.333,96 | 70,3% |
| `93` | Servicios Políticos y de Asuntos Cívicos | $1.314,25 | $881,20 | -$433,05 | 67,0% |
| `72` | Servicios de Edificación, Construcción de Instalacio | $688,54 | $1.236,36 | $547,82 | 179,6% |
| `84` | Servicios Financieros y de Seguros | $1.235,50 | $309,53 | -$925,98 | 25,1% |
| `81` | Servicios Basados en Ingeniería, Investigación y Tec | $494,94 | $688,31 | $193,37 | 139,1% |
| `86` | Servicios Educativos y de Formación | $196,24 | $473,33 | $277,10 | 241,2% |
| `77` | Servicios Medioambientales | $172,83 | $237,47 | $64,64 | 137,4% |
| `43` | Difusión de Tecnologías de Información y Telecomunic | $226,54 | $126,57 | -$99,98 | 55,9% |

---

## 6. Síntesis de Auditoría de Calidad de Datos (Base para Rubro 1)

| Dimensión revisada | Hallazgo verificado en piloto (3 entidades) | Regla aplicada y justificación |
|---|---|---|
| **Cuadre Encabezado vs. Detalle PAA** | Diferencia máxima de `$0.0001 COP` | Confirma que `9sue-ezhx` almacena solo la última versión vigente por entidad-año. |
| **Duplicados de llave primaria** | `0` en `paa_detalle` (`id`) y `0` en `contratos` (`id_contrato`) | No hay duplicación técnica de llaves en la extracción paginada. |
| **Cuasi-duplicado administrativo PAA** | `1` caso (`$333,54 MM` en MinAmbiente 2023) | Se conserva en `paa_limpio.csv` con bandera `es_posible_duplicado_atipico` y se reportan indicadores con y sin dicho registro. |
| **Contratos en `$0` (sin cuantía)** | `964` contratos (`565` son Acuerdos Marco de ANCP) | Se marcan con `es_contrato_sin_cuantia` y se excluyen del denominador de montos/HHI para no sesgar indicadores financieros. |
| **Modalidades «No definido» en PAA** | `2.733` crudos → se rescataron **`2.251` ($1.975,68 MM)** desde `causal_de_contratacion` | Solo quedan `482` ítems donde ambas columnas venían sin diligenciar. |
| **Vigencias futuras en PAA** | `945` ítems requieren vigencias futuras | Se usa `valor_esperado_de_presupuesto` (vigencia actual) como denominador principal y `valor_total_esperado` como análisis de sensibilidad. |
| **Emparejamiento UNSPSC** | Producto 8d: `39,5%` / `36,4%` vs. Clase 6d / Segmento 2d: `100,0%` / `99,8%` | Se cruza a nivel Clase (`6d`) y se agrega por Segmento (`2d`) y Familia (`4d`), etiquetando los `51` `UNSPECIFIED` como `"Sin clasificar"`. |

---

## 7. Puntos para Discutir en Grupo antes de Escalar a las 6 Entidades (Fase 4 y Rubro 5)

1. **Validar narrativa central:** ¿Les gusta cómo estos hallazgos responden directamente la pregunta (mostrando que las desviaciones vienen tanto de choques reales de contratación/modalidad como de problemas de calidad en la planeación administrativa: vigencias futuras, ítems `"No definido"` y reediciones sin borrar filas)?
2. **Ideas candidatas para la sección de IA (Rubro 5 — ir más allá de lo recomendado por los profesores):**
   - *Candidata A (Deflación a precios constantes de 2025 con IPC DANE):* entre 2022 y 2025 Colombia tuvo inflación acumulada > 25%; comparar pesos corrientes distorsiona la evolución interanual real del gasto y de los montos promedio.
   - *Candidata B (Índice de concentración de fin de año / estacionalidad pre-Ley de Garantías):* medir qué fracción del valor anual y de la contratación directa se firma en el último trimestre o justo antes de restricciones electorales.
   - *Candidata C (Descomposición formal de la brecha por reasignación intrasectorial vs. escala presupuestal — índice de disimilitud de Duncan entre composición UNSPSC planeada y ejecutada).* 
