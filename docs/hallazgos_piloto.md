# Informe Ejecutivo de Hallazgos — Muestra Piloto (*A contra(luz)*)

> **Nota de trazabilidad:** Este documento se genera automáticamente ejecutando `python -m src.limpieza_cruce` a partir de las bases verificadas de `datos.gov.co` (`2022–2025`). Todas las cifras monetarias están expresadas en **miles de millones de pesos corrientes (`$ MM COP`)**.

---

## 1. Resumen Ejecutivo para Discusión del Equipo

- **Muestra piloto evaluada (`2022–2025`):** `ANCP (Colombia Compra Eficiente)`, `MinAmbiente` y `MinHacienda` (`9.877` ítems de PAA y `9.290` contratos electrónicos en SECOP II).
- **Magnitud agregada del cuatrienio:** frente a un presupuesto planeado de vigencia actual de **$2.914,04 MM** (**$2.580,51 MM** excluyendo un registro cuasi-duplicado administrativo detectado), las tres entidades suscribieron contratos por **$1.550,68 MM** (`60,1%` de ejecución agregada ajustada).
- **Cuatro hallazgos sustantivos que ya perfilan la narrativa del trabajo final:**
  1. **La auditoría de calidad cambia las conclusiones económicas:** en `MinAmbiente 2023` encontramos dos líneas de **$333,54 MM** para constituir el patrimonio autónomo *Fondo para la Vida y la Biodiversidad* (solo varió una cita de artículos de la Ley 2294 de 2023 sin borrar la fila previa). Al corregir ese doble conteo, su ejecución de 2023 sube de **32,9% a 50,9% (+18,0 puntos porcentuales)**.
  2. **La contratación directa domina en número de contratos, pero no siempre en valor:** aunque representa la gran mayoría de contratos firmados (prestación de servicios profesionales), en `MinHacienda` las grandes licitaciones y selecciones abreviadas (seguros previsionales/FONPET) reducen drásticamente su peso en dinero, mientras en `MinAmbiente` el régimen especial concentra convenios de gran cuantía (ej. PNUD).
  3. **Demostración empírica del nivel UNSPSC (respuesta directa a la observación R6):** cruzar por código de Producto (`8` dígitos) pierde más del 82% de los datos (`17,4%` en PAA y `16,1%` en Contratos), porque las entidades planean y contratan usando códigos terminados en `00` (nivel Clase). Al cruzar por **Clase (`6` dígitos) y Segmento (`2` dígitos)**, el emparejamiento sube a **100,0%** en PAA y **99,7%** en Contratos.
  4. **Rescate de modalidades desde `causal_de_contratacion` y efecto de vigencias futuras:** en la columna cruda `modalidad` del PAA venían `1.561` ítems como `"No Definido"`, pero al cruzar con `causal_de_contratacion` rescatamos la modalidad legal exacta de **`1.378` ítems ($727,42 MM)**, dejando solo `183` omisiones reales. Además, las vigencias futuras explican **$632,17 MM** de diferencia entre valor total y presupuesto anual.

---

## 2. Planeación (PAA) vs. Ejecución (SECOP II) por Entidad y Año (`$ MM COP`)

| Entidad | Año | Versiones PAA | PAA Vigencia (`$ MM`) | PAA Ajustado sin Dup. (`$ MM`) | Ejecutado SECOP II (`$ MM`) | % Ejec. Bruta | % Ejec. Ajustada | Contratos (> $0) | Proveedores Únicos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **ANCP** | 2022 | 82 | $62,22 | $62,22 | $34,86 | 56,0% | **56,0%** | 308 | 299 |
| **ANCP** | 2023 | 47 | $61,36 | $61,36 | $44,20 | 72,0% | **72,0%** | 381 | 316 |
| **ANCP** | 2024 | 33 | $79,02 | $79,02 | $38,37 | 48,5% | **48,5%** | 409 | 400 |
| **ANCP** | 2025 | 17 | $128,42 | $128,42 | $56,84 | 44,3% | **44,3%** | 421 | 407 |
| **MinAmbiente** | 2022 | 27 | $125,57 | $125,57 | $110,96 | 88,4% | **88,4%** | 1.038 | 993 |
| **MinAmbiente** | 2023 | 28 | $940,90 | $607,37 | $309,25 | 32,9% | **50,9%** | 1.277 | 1.151 |
| **MinAmbiente** | 2024 | 21 | $129,45 | $129,45 | $107,07 | 82,7% | **82,7%** | 1.267 | 1.240 |
| **MinAmbiente** | 2025 | 22 | $114,73 | $114,73 | $107,85 | 94,0% | **94,0%** | 1.232 | 1.211 |
| **MinHacienda** | 2022 | 44 | $73,27 | $73,27 | $115,31 | 157,4% | **157,4%** | 365 | 318 |
| **MinHacienda** | 2023 | 56 | $489,67 | $489,67 | $220,68 | 45,1% | **45,1%** | 573 | 411 |
| **MinHacienda** | 2024 | 64 | $597,51 | $597,51 | $219,65 | 36,8% | **36,8%** | 468 | 426 |
| **MinHacienda** | 2025 | 62 | $111,93 | $111,93 | $185,63 | 165,9% | **165,9%** | 743 | 518 |

**Lectura rápida:**
- **ANCP:** planea sistemáticamente por encima de lo que contrata con recursos propios (`44,3%–72,0%`), además de suscribir **559 Acuerdos Marco de Precios** registrados en `$0` (cuyo gasto ejecutan luego las demás entidades compradoras en la Tienda Virtual).
- **MinAmbiente:** muestra alta correspondencia entre planeación y ejecución en 2022, 2024 y 2025 (`82,7%–94,0%`), con una caída en 2023 explicada por la programación del *Fondo para la Vida*.
- **MinHacienda:** exhibe la mayor volatilidad: sobreejecución frente al PAA de vigencia en 2022 (`157,4%`) y 2025 (`165,9%`), y subejecución en 2023–2024 (`45,1%` y `36,8%`) cuando se programaron operaciones financieras/capitalizaciones de gran escala.

---

## 3. Peso de la Contratación Directa: Planeado vs. Ejecutado (`2022–2025`)

| Entidad | PAA Ajustado (`$ MM`) | % PAA en Contratación Directa | % PAA con Modalidad «No definido» | Ejecutado SECOP II (`$ MM`) | % Valor Ejecutado en Contratación Directa | % # Contratos en Contratación Directa |
|---|---:|---:|---:|---:|---:|---:|
| **ANCP** | $331,02 | 53,3% | 25,5% | $174,27 | **91,4%** | 93,2% |
| **MinAmbiente** | $977,11 | 58,2% | 1,7% | $635,14 | **61,5%** | 97,6% |
| **MinHacienda** | $1.272,37 | 17,3% | 4,1% | $741,27 | **37,2%** | 88,8% |

**Lectura rápida:** Mirar solo el *número* de contratos lleva a creer que casi todo es contratación directa (`> 88%` de los contratos), pero al ponderar por *valor en pesos* aparecen diferencias estructurales enormes entre entidades. Además, rescatar la modalidad desde `causal_de_contratacion` redujo el peso «No definido» de MinHacienda de `56,2%` a solo `4,1%` (mientras en ANCP aún persiste un `25,5%` sin definir ni en modalidad ni en causal).

---

## 4. Concentración por Proveedor (`CR1`, `CR5` e Índice `HHI`)

*(Calculado sobre contratos válidos con cuantía `> $0`. Referencia económica estándar: `HHI < 1.500` desconcentrado, `1.500–2.500` moderado, `> 2.500` alta concentración).* 

| Entidad | Año | Proveedores | Top 1 (`CR1`) | Top 5 (`CR5`) | Índice `HHI` (0–10.000) | Principal Proveedor Adjudicado del Año |
|---|---:|---:|---:|---:|---:|---|
| **ANCP** | 2022 | 299 | 23,0% | **46,9%** | 797 | SIMPLIFAE PORTUGAL, S.A. |
| **ANCP** | 2023 | 316 | 26,1% | **49,6%** | 889 | SIMPLIFAE PORTUGAL, S.A. |
| **ANCP** | 2024 | 400 | 17,7% | **32,8%** | 476 | SIMPLIFAE PORTUGAL, S.A. |
| **ANCP** | 2025 | 407 | 18,4% | **43,7%** | 612 | COMCEL S.A. |
| **MinAmbiente** | 2022 | 993 | 13,6% | **27,5%** | 262 | ORGANIZACION DE ESTADOS IBEROAMERICANOS OE |
| **MinAmbiente** | 2023 | 1.151 | 51,6% | **62,9%** | 2.716 | PROGRAMA DE LAS NACIONES UNIDAS PARA EL DE |
| **MinAmbiente** | 2024 | 1.240 | 3,6% | **14,5%** | 56 | SOCIEDAD DE TELEVISIÓN DE CALDAS QUINDÍO Y |
| **MinAmbiente** | 2025 | 1.211 | 9,2% | **19,7%** | 125 | ADESCUBRIR TRAVEL & ADVENTURE SAS |
| **MinHacienda** | 2022 | 318 | 22,8% | **52,4%** | 838 | BANCO DE LA REPUBLICA |
| **MinHacienda** | 2023 | 411 | 28,3% | **64,8%** | 1.223 | CONSORCIO PRAG FONPET 2023 |
| **MinHacienda** | 2024 | 426 | 28,2% | **60,0%** | 1.128 | LA PREVISORA S.A. COMPAÑÍA DE SEGUROS |
| **MinHacienda** | 2025 | 518 | 33,6% | **52,3%** | 1.249 | CONSORCIO PAC FONPET 2025 |

---

## 5. Top 8 Segmentos UNSPSC con Mayor Volumen y Brecha (`2022–2025`)

| Cód. | Segmento UNSPSC (2 dígitos) | PAA Ajustado (`$ MM`) | Ejecutado (`$ MM`) | Brecha Ejec. − PAA (`$ MM`) | % Ejecución |
|---|---|---:|---:|---:|---:|
| `84` | Servicios Financieros y de Seguros | $1.191,49 | $267,23 | -$924,26 | 22,4% |
| `80` | Servicios de Gestión, Servicios Profesionales de Emp | $590,44 | $522,07 | -$68,37 | 88,4% |
| `81` | Servicios Basados en Ingeniería, Investigación y Tec | $317,04 | $240,62 | -$76,42 | 75,9% |
| `77` | Servicios Medioambientales | $172,28 | $223,23 | $50,95 | 129,6% |
| `43` | Difusión de Tecnologías de Información y Telecomunic | $92,50 | $69,32 | -$23,18 | 74,9% |
| `78` | Servicios de Transporte, Almacenaje y Correo | $106,38 | $22,22 | -$84,15 | 20,9% |
| `93` | Servicios Políticos y de Asuntos Cívicos | $28,07 | $92,62 | $64,55 | 329,9% |
| `72` | Servicios de Edificación, Construcción de Instalacio | $27,08 | $33,52 | $6,44 | 123,8% |

---

## 6. Síntesis de Auditoría de Calidad de Datos (Base para Rubro 1)

| Dimensión revisada | Hallazgo verificado en piloto (3 entidades) | Regla aplicada y justificación |
|---|---|---|
| **Cuadre Encabezado vs. Detalle PAA** | Diferencia máxima de `$0.0001 COP` | Confirma que `9sue-ezhx` almacena solo la última versión vigente por entidad-año. |
| **Duplicados de llave primaria** | `0` en `paa_detalle` (`id`) y `0` en `contratos` (`id_contrato`) | No hay duplicación técnica de llaves en la extracción paginada. |
| **Cuasi-duplicado administrativo PAA** | `1` caso (`$333,54 MM` en MinAmbiente 2023) | Se conserva en `paa_limpio.csv` con bandera `es_posible_duplicado_atipico` y se reportan indicadores con y sin dicho registro. |
| **Contratos en `$0` (sin cuantía)** | `808` contratos (`559` son Acuerdos Marco de ANCP) | Se marcan con `es_contrato_sin_cuantia` y se excluyen del denominador de montos/HHI para no sesgar indicadores financieros. |
| **Modalidades «No definido» en PAA** | `1.561` crudos → se rescataron **`1.378` ($727,42 MM)** desde `causal_de_contratacion` | Solo quedan `183` ítems donde ambas columnas venían sin diligenciar. |
| **Vigencias futuras en PAA** | `744` ítems requieren vigencias futuras | Se usa `valor_esperado_de_presupuesto` (vigencia actual) como denominador principal y `valor_total_esperado` como análisis de sensibilidad. |
| **Emparejamiento UNSPSC** | Producto 8d: `17,4%` / `16,1%` vs. Clase 6d / Segmento 2d: `100,0%` / `99,7%` | Se cruza a nivel Clase (`6d`) y se agrega por Segmento (`2d`) y Familia (`4d`), etiquetando los `31` `UNSPECIFIED` como `"Sin clasificar"`. |

---

## 7. Puntos para Discutir en Grupo antes de Escalar a las 6 Entidades (Fase 4 y Rubro 5)

1. **Validar narrativa central:** ¿Les gusta cómo estos hallazgos responden directamente la pregunta (mostrando que las desviaciones vienen tanto de choques reales de contratación/modalidad como de problemas de calidad en la planeación administrativa: vigencias futuras, ítems `"No definido"` y reediciones sin borrar filas)?
2. **Ideas candidatas para la sección de IA (Rubro 5 — ir más allá de lo recomendado por los profesores):**
   - *Candidata A (Deflación a precios constantes de 2025 con IPC DANE):* entre 2022 y 2025 Colombia tuvo inflación acumulada > 25%; comparar pesos corrientes distorsiona la evolución interanual real del gasto y de los montos promedio.
   - *Candidata B (Índice de concentración de fin de año / estacionalidad pre-Ley de Garantías):* medir qué fracción del valor anual y de la contratación directa se firma en el último trimestre o justo antes de restricciones electorales.
   - *Candidata C (Descomposición formal de la brecha por reasignación intrasectorial vs. escala presupuestal — índice de disimilitud de Duncan entre composición UNSPSC planeada y ejecutada).* 
