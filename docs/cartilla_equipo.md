# Cartilla Maestra del Equipo — Proyecto *A contra(luz)* (Grupo 3)

> **Propósito:** Guía interna completa para que **Diego, Juan Sebastián y Nathalia** dominen cada decisión técnica, económica y jurídica del proyecto sobre las **6 entidades definitivas (`2022–2025`)**. *(Para explorar las 6 gráficas interactivas con zoom y tooltips, abran con doble clic `docs/cartilla_interactiva.html` en cualquier navegador).* 

---

## Capítulo 1. Arquitectura del Proyecto: Qué Hicimos y Dónde Está Todo

Siguiendo lo aprendido en `coding-agents-for-data-science` (Sesiones 1–3) y `Taller 2 Webscraping`, separamos el código pesado en módulos limpios dentro de `src/` que se comunican mediante **contratos CSV**:

| Capa / Archivo | Qué hace exactamente | Salida que genera |
|---|---|---|
| `src/config.py` | Centraliza rutas relativas, semilla (`42`), los 6 códigos/NITs de entidades y umbrales (`$1.000` simbólico, `$50.000M` duplicado PAA). | Constantes compartidas |
| `src/ingesta.py` | Consulta la API Socrata de `datos.gov.co` (`b6m4-qgqv`, `9sue-ezhx`, `jbjy-vk9h`) con paginación y reintentos, y convierte el Excel `.xls` del Clasificador UNSPSC v14.1. | `data/raw/*.csv` (`27.160` ítems PAA, `25.317` contratos, `49.022` productos UNSPSC) |
| `src/limpieza_cruce.py` | Audita tipos, faltantes, duplicados y atípicos; rescata modalidades desde `causal_de_contratacion`; cruza UNSPSC a nivel Clase (`6d`) y Segmento (`2d`). | `data/processed/*.csv` + `auditoria_calidad.json` |
| `src/indicadores.py` | Calcula tasa de ejecución, contratación directa, concentración por proveedor (`CR1`, `CR5`, `HHI`), brechas UNSPSC y las 7 franjas de cuantías. | `data/dashboard_data/*.csv` (`6` tablas listas para graficar) |
| `src/visualizacion.py` | Funciones puras en **Plotly** con paleta accesible de alto contraste (`acontraluz-charts`), reutilizadas sin duplicar código en Notebook, Streamlit y Cartilla HTML. | Objetos `plotly.graph_objects.Figure` |
| `tests/` | Suite offline con `pytest` y fixtures reales recortados de la API (corre sin internet en segundos). | Verificación automática |

---

## Capítulo 2. Respuestas Detalladas a las 5 Inquietudes del Equipo (con Cifras de las 6 Entidades)

### 2.1 ¿Qué se entiende por «Definido» y «No definido» en las modalidades del PAA?
- **Origen exacto del término:** En la tabla oficial `9sue-ezhx` de `datos.gov.co`, el campo `modalidad` trae literalmente la cadena `"No Definido"` en **`2.733` ítems** de las 6 entidades.
- **Nuestro rescate jurídico-técnico:** Al inspeccionar la columna vecina `causal_de_contratacion`, descubrimos que cuando las entidades suben su PAA mediante plantilla Excel de SECOP II, muchas veces diligencian el código de la causal legal (ej. `CCE-16-Servicios_profesionales_gestion`, `CCE-02-Licitacion_Publica`, `CCE-06-Seleccion_Abreviada_Menor_Cuantia`), pero la vista abierta deja `modalidad` como `"No Definido"`. Usando el Estatuto General de Contratación (**Ley 1150 de 2007, art. 2**), rescatamos automáticamente **`2.251` ítems ($1.975,68 MM)**.
- **Definición final limpia:**
  - **Modalidad Definida:** tiene modalidad explícita o causal legal identificable (`26.678` de `27.160` ítems = `98,2%`).
  - **Modalidad «No definido»:** la entidad dejó sin diligenciar **tanto** `modalidad` como `causal_de_contratacion` (`482` ítems = `1,8%`), reflejando una omisión administrativa real en la planeación.

### 2.2 ¿Cómo son posibles porcentajes de ejecución mayores al 100%?
En nuestro panel de 24 observaciones (6 entidades × 4 años), observamos tasas `> 100%` en: `MinHacienda 2025` (165,9%), `MinHacienda 2022` (157,4%), `MinCulturas 2023` (128,9%), `MinEducación 2023` (121,5%), `MinCulturas 2024` (116,4%), `MinEducación 2022` (115,1%), `MinEducación 2025` (107,6%), `DNP 2024` (101,4%) (y también en segmentos UNSPSC específicos). Esto ocurre por **cuatro mecanismos legales y contables reales**:
1. **Asimetría contable en contratos plurianuales con Vigencias Futuras (Ley 819 de 2003, arts. 10–12):** En `Contratos SECOP II` (`jbjy-vk9h`), la variable `valor_del_contrato` registra el **100% del compromiso plurianual en el año de la firma** (ej. MinHacienda firmó en agosto de 2025 el contrato `CONSORCIO PAC FONPET 2025` hasta 2030 por `$62,37 MM`), mientras que en el PAA el campo `valor_esperado_de_presupuesto` registra únicamente la **apropiación de ese año fiscal**.
2. **Adiciones contractuales en valor (Ley 80 de 1993, art. 40, parágrafo):** La ley permite adicionar cualquier contrato estatal hasta en un **50% de su valor inicial expresado en SMLMV** mediante otrosíes. SECOP II actualiza `valor_del_contrato` al monto modificado acumulado, superando el estimado inicial del PAA.
3. **Carácter flexible e indicativo del PAA (Decreto 1082 de 2015, arts. 2.2.1.1.1.4.1 a 2.2.1.1.1.4.4):** El PAA es un documento de naturaleza informativa que **no obliga** a las entidades a efectuar los procesos exactamente como se estimaron, y puede recibir recursos nuevos por **traslados o adiciones del Presupuesto General de la Nación (PGN)** o atender urgencias manifiestas.
4. **Reclasificación de códigos UNSPSC al contratar:** Una entidad puede planear un proyecto bajo el segmento `84` (Servicios financieros) o `80` (Gestión) en el PAA y adjudicarlo finalmente bajo el segmento `93` (Asuntos cívicos/administración pública), generando `< 100%` en el primero y `> 100%` en el segundo.

### 2.3 Distribución de cuantías de los contratos y explicación por franja (`6 entidades, 2022–2025`)
*(En `docs/cartilla_interactiva.html` encuentran el gráfico interactivo completo de doble panel).* 

| # | Franja de cuantía (`COP`) | Criterio | # Contratos | % Contratos | Valor Total (`$ MM`) | % del Dinero | Modalidad predominante | Regla aplicada |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | **Igual a $0 (AMP / sin erogación)** | `valor == 0` | 951 | 3,8% | $0,00 | 0,0% | Licitación pública y AMP | Marcado sin cuantía |
| 2 | **Simbólica ($0,01 – $1.000)** | `0 < valor <= 1.000` | 13 | 0,1% | $0,00 | 0,0% | Licitación pública y AMP | Marcado cuantía simbólica |
| 3 | **Micro-compra ($1.001 – $1M)** | `1.000 < valor <= 1.000.000` | 24 | 0,1% | $0,02 | 0,0% | Contratación directa | Incluido en análisis |
| 4 | **Menor ($1M – $10M)** | `1M < valor <= 10M` | 755 | 3,0% | $5,20 | 0,1% | Contratación directa | Incluido en análisis |
| 5 | **Estándar ($10M – $100M)** | `10M < valor <= 100M` | 17.188 | 67,9% | $902,45 | 11,6% | Contratación directa | Incluido en análisis |
| 6 | **Intermedia ($100M – $1.000M)** | `100M < valor <= 1.000M` | 5.678 | 22,4% | $1.006,12 | 12,9% | Contratación directa | Incluido en análisis |
| 7 | **Gran cuantía (> $1.000M)** | `valor > 1.000M` | 708 | 2,8% | $5.866,32 | 75,4% | Contratación directa | Incluido en análisis |

**¿Cómo se explica cada franja (especialmente los valores muy bajos `< $1.000.000 COP`)?**
- **Franja 1 (`= $0`, `951` contratos):** No son errores; la mayoría (`565`) son **Acuerdos Marco de Precios** suscritos por ANCP para habilitar catálogos en la Tienda Virtual sin gasto propio inicial, más comodatos y convenios interadministrativos sin flujo de caja.
- **Franja 2 (`$0,01 – $1.000 COP`, `13` contratos — cuantías simbólicas «dummy»):** En contratos de **monto agotable, bolsas de precios unitarios o acuerdos marco** (ej. combustible de aviación o reciclaje), cuando un flujo del formulario electrónico de SECOP II exige digitar un número mayor a cero, el comprador público ingresa `$0,01`, `$0,10`, `$1` o `$2` como valor nominal de referencia. Por eso en nuestra limpieza los marcamos con `es_cuantia_simbolica = True`.
- **Franja 3 (`$1.001 – $1.000.000 COP` — micro-compras reales):** Son compras reales de bajo monto por mínima cuantía o contratación directa: publicación obligatoria de avisos legales en diarios nacionales (*El Tiempo/CEET*, *La República*, *El Espectador*), correo certificado (*4-72*) o certificados de firma digital (*Camerfirma*).
- **Franja 5 (`$10M – $100M COP` — la gran masa de contratos):** Concentra cerca de dos terceras partes de todos los contratos firmados porque corresponde a los honorarios anuales de **prestación de servicios profesionales y de apoyo a la gestión** en los ministerios y departamentos administrativos.
- **Franja 7 (`> $1.000M COP` — la concentración del dinero):** Aunque son muy pocos contratos en cantidad, concentran la mayoría absoluta del presupuesto ejecutado (grandes licitaciones, fiducias, seguros previsionales y convenios con organismos internacionales).

**Ejemplos reales en nuestra base de cuantías simbólicas (`$0,01 – $1.000 COP`):**

| Entidad | Año | Valor Registrado | Modalidad | Tipo de Contrato | Proveedor |
|---|---:|---:|---|---|---|
| **ANCP** | 2025 | `$0,01` | Mínima cuantía | Suministros | MARIA ALEJANDRA CARDENAS AGUILAR |
| **DNP** | 2025 | `$0,01` | Contratación directa | Prestación de servicios | CRISTHIAN BERNARDO RIVERA PRADA |
| **MinCulturas** | 2022 | `$0,01` | Contratación régimen especial (con ofertas) | Decreto 092 de 2017 | TEATRO R101 |
| **MinAmbiente** | 2025 | `$0,01` | Concurso de méritos abierto | Consultoría | UT JG-MINAMBIENTE 2024 |
| **MinCulturas** | 2022 | `$0,10` | Contratación régimen especial (con ofertas) | Decreto 092 de 2017 | ASOCIACIÓN DE AMIGOS DEL MUSEO NACIONAL |
| **MinHacienda** | 2024 | `$0,10` | Contratación régimen especial (con ofertas) | Otro | ASOCIACION DE RECICLADORES PUERTA DE ORO B |

**Ejemplos reales en nuestra base de micro-compras legítimas (`$1.001 – $1.000.000 COP`):**

| Entidad | Año | Valor Registrado | Modalidad | Tipo de Contrato | Proveedor |
|---|---:|---:|---|---|---|
| **ANCP** | 2022 | `$51.600,00` | Contratación Directa (con ofertas) | Otro | SERVICIOS POSTALES NACIONALES S.A.S |
| **ANCP** | 2023 | `$360.900,00` | Contratación directa | Prestación de servicios | CEET |
| **ANCP** | 2023 | `$449.900,00` | Contratación directa | Prestación de servicios | LA REPUBLICA |
| **DNP** | 2025 | `$465.600,00` | Contratación directa | Prestación de servicios | CÁMARA COLOMBIANA DEL LIBRO |
| **ANCP** | 2022 | `$476.000,00` | Mínima cuantía | Compraventa | CAMERFIRMA |
| **MinHacienda** | 2025 | `$518.500,00` | Contratación directa | Suministros | LA REPUBLICA |

### 2.4 ¿Qué elementos procedimentales y de ley justifican cuantías menores o iguales a `$0`?
- **Estrictamente menores a `$0` (`< 0`):** Verificamos que en los `25.317` contratos y `27.160` ítems PAA existen **`0` valores negativos**. En el derecho público colombiano no existe un contrato estatal de cuantía negativa (las deducciones, multas o liberaciones de saldos se registran en liquidación, nunca como valor inicial negativo).
- **Iguales a `$0` (`== 0`):** Están plenamente respaldados por cuatro figuras jurídicas:
  1. **Acuerdos Marco de Precios (Ley 1150/2007, art. 2 num. 2 lit. a; Decreto 1082/2015):** ANCP selecciona proveedores y fija precios techo por catálogo (`$0` de compromiso propio); el gasto presupuestal ocurre después en las órdenes de compra de cada entidad.
  2. **Contratos de Comodato o préstamo de uso gratuito (Código Civil, art. 2200; Ley 9 de 1989, art. 38):** entrega gratuita de bienes muebles o inmuebles entre entidades o sin contraprestación dineraria.
  3. **Convenios interadministrativos o de asociación sin erogación presupuestal (Ley 489 de 1998, arts. 95–96; Decreto 092 de 2017):** cooperación técnica, intercambio de información o alianzas donde los aportes son en especie/capacidad institucional.
  4. **Contratos de concesión o aprovechamiento económico sin desembolso estatal** (donde el privado asume el riesgo o paga contraprestación).

### 2.5 ¿Qué es la «referencia económica estándar» (`HHI`) y cómo entender las «Vigencias Futuras»?
- **Índice Herfindahl-Hirschman (`HHI`):** Mide qué tan concentrado está el gasto de una entidad entre sus proveedores en un año. Si el proveedor $i$ recibe un porcentaje $s_i$ del gasto anual (de $0$ a $100$), entonces $\text{HHI} = \sum_i s_i^2$ (escala de `0` a `10.000`):
  - Si 1 solo proveedor se lleva el `100%` del presupuesto → $\text{HHI} = 100^2 = 10.000$ (monopolio total).
  - Si 100 proveedores se llevan `1%` cada uno → $\text{HHI} = 100 \times 1^2 = 100$ (atomización).
  - **Umbrales internacionales estándar** (*U.S. Department of Justice & Federal Trade Commission Horizontal Merger Guidelines*, adoptados en análisis de competencia por la **SIC en Colombia** y la OCDE): **`< 1.500`** baja concentración, **`1.500 – 2.500`** concentración moderada, **`> 2.500`** alta concentración.
- **Vigencias Futuras (Ley Orgánica 819 de 2003, arts. 10–12; Estatuto Orgánico del Presupuesto Decreto 111/1996):**
  - En Colombia rige el **principio de anualidad**: el presupuesto aprobado para 2024 solo puede ejecutarse hasta el 31 de diciembre de 2024.
  - Pero muchos bienes y servicios críticos (seguros, nube tecnológica, interventorías, obras, vigilancia continua desde el 1 de enero del año siguiente) superan el 31 de diciembre.
  - Para poder firmar hoy un contrato que compromete caja de años venideros, el **CONFIS** y el Ministerio de Hacienda otorgan un cupo de **Vigencias Futuras** (ordinarias si inician con presupuesto del año actual, o excepcionales en casos estratégicos). En nuestra base de 6 entidades hay **`945` ítems PAA** con vigencias futuras, que suman **$978,41 MM** por encima del presupuesto exclusivo del año corriente.

---

## Capítulo 3. Panorama Consolidado de las 6 Entidades Definitivas (`2022–2025`)

- **Total planeado ajustado (vigencia actual):** **$9.343,83 MM** *(bruto antes de control de cuasi-duplicados: $9.677,37 MM)*.
- **Total contratado válido en SECOP II (`> $1.000 COP`):** **$7.780,10 MM** (**83,3%** de ejecución agregada).
- **Cuadre contable exacto entre `b6m4-qgqv` y `9sue-ezhx`:** diferencia máxima de `$0.0001 COP` en las 24 vigencias.

| Entidad | Año | Versiones PAA | PAA Ajustado (`$ MM`) | Ejecutado (`$ MM`) | % Ejecución | % Valor Directa | HHI Proveedores |
|---|---:|---:|---:|---:|---:|---:|---|
| **ANCP** | 2022 | 82 | $62,22 | $34,86 | **56,0%** | 96,9% | 797 (Baja (< 1.500)) |
| **ANCP** | 2023 | 47 | $61,36 | $44,20 | **72,0%** | 97,3% | 889 (Baja (< 1.500)) |
| **ANCP** | 2024 | 33 | $79,02 | $38,37 | **48,5%** | 96,1% | 476 (Baja (< 1.500)) |
| **ANCP** | 2025 | 17 | $128,42 | $56,84 | **44,3%** | 80,2% | 612 (Baja (< 1.500)) |
| **DNP** | 2022 | 29 | $200,19 | $167,46 | **83,7%** | 68,5% | 146 (Baja (< 1.500)) |
| **DNP** | 2023 | 38 | $180,12 | $160,27 | **89,0%** | 63,4% | 119 (Baja (< 1.500)) |
| **DNP** | 2024 | 53 | $217,26 | $220,26 | **101,4%** | 55,2% | 409 (Baja (< 1.500)) |
| **DNP** | 2025 | 33 | $185,60 | $163,42 | **88,1%** | 81,5% | 25 (Baja (< 1.500)) |
| **MinAmbiente** | 2022 | 27 | $125,57 | $110,96 | **88,4%** | 95,7% | 262 (Baja (< 1.500)) |
| **MinAmbiente** | 2023 | 28 | $607,37 | $309,25 | **50,9%** | 32,2% | 2.716 (Alta (> 2.500)) |
| **MinAmbiente** | 2024 | 21 | $129,45 | $107,07 | **82,7%** | 91,2% | 56 (Baja (< 1.500)) |
| **MinAmbiente** | 2025 | 22 | $114,73 | $107,85 | **94,0%** | 80,9% | 125 (Baja (< 1.500)) |
| **MinCulturas** | 2022 | 37 | $256,76 | $196,31 | **76,5%** | 30,9% | 250 (Baja (< 1.500)) |
| **MinCulturas** | 2023 | 40 | $409,67 | $528,07 | **128,9%** | 22,6% | 1.152 (Baja (< 1.500)) |
| **MinCulturas** | 2024 | 45 | $649,71 | $755,95 | **116,4%** | 47,9% | 212 (Baja (< 1.500)) |
| **MinCulturas** | 2025 | 42 | $677,03 | $521,54 | **77,0%** | 75,6% | 326 (Baja (< 1.500)) |
| **MinEducación** | 2022 | 40 | $237,10 | $273,00 | **115,1%** | 73,7% | 535 (Baja (< 1.500)) |
| **MinEducación** | 2023 | 57 | $1.364,80 | $1.657,68 | **121,5%** | 93,7% | 5.715 (Alta (> 2.500)) |
| **MinEducación** | 2024 | 43 | $1.414,06 | $540,59 | **38,2%** | 47,3% | 618 (Baja (< 1.500)) |
| **MinEducación** | 2025 | 50 | $971,02 | $1.044,86 | **107,6%** | 78,6% | 1.244 (Baja (< 1.500)) |
| **MinHacienda** | 2022 | 44 | $73,27 | $115,31 | **157,4%** | 53,0% | 838 (Baja (< 1.500)) |
| **MinHacienda** | 2023 | 56 | $489,67 | $220,68 | **45,1%** | 23,0% | 1.223 (Baja (< 1.500)) |
| **MinHacienda** | 2024 | 64 | $597,51 | $219,65 | **36,8%** | 43,9% | 1.128 (Baja (< 1.500)) |
| **MinHacienda** | 2025 | 62 | $111,93 | $185,63 | **165,9%** | 36,4% | 1.249 (Baja (< 1.500)) |

---

## Capítulo 4. Prompt Listo para Copiar y Enviar a una IA (Rubro 5 — `4/20 pts`)

Copia el siguiente bloque tal cual en una sesión limpia de ChatGPT, Claude o Gemini y pégame aquí su respuesta completa para integrarla al Notebook e implementar las mejoras acordadas (*IPC DANE + Índice de Disimilitud de Duncan*):

```text
Actúa como un economista experto en contratación pública y econometría aplicada en Colombia.

CONTEXTO DEL PROYECTO:
Estamos desarrollando un estudio reproducible en Python sobre las desviaciones entre la planeación contractual (Plan Anual de Adquisiciones - PAA, dataset 9sue-ezhx) y la ejecución contractual efectiva (Contratos Electrónicos SECOP II, dataset jbjy-vk9h) entre 2022 y 2025 para 6 entidades nacionales del nivel central (ANCP, DNP, MinAmbiente, MinCulturas, MinEducación, MinHacienda). La base limpia integra 27.160 ítems del PAA ($9.343,83 mil millones COP planeados ajustados) y 25.317 contratos ($7.780,10 mil millones COP ejecutados), cruzados al 99,8%+ con el Clasificador UNSPSC v14.1 a nivel de Clase (6 dígitos) y Segmento (2 dígitos).

METODOLOGÍA ACTUAL YA IMPLEMENTADA (RECOMENDACIONES BASE DE LOS PROFESORES):
1. Limpieza auditada: rescate de modalidades 'No Definido' desde causal_de_contratacion (Ley 1150/2007), marcación de contratos sin cuantía ($0 en Acuerdos Marco y cuantías simbólicas <= $1.000 COP) y detección de cuasi-duplicados administrativos >= $50.000 millones COP en el PAA.
2. Indicadores descriptivos nominales por entidad y año: (a) tasa de ejecución (% ejecutado / planeado vigencia actual), (b) peso de la contratación directa en número y valor, (c) concentración por proveedor (CR1, CR5 e Índice HHI en escala 0–10.000), y (d) brechas en pesos corrientes por segmento UNSPSC.

OBJETIVO Y RESTRICCIONES:
Propón entre 3 y 4 mejoras metodológicas rigurosas desde la teoría económica o el análisis estadístico de compras públicas que vayan MÁS ALLÁ de los indicadores descriptivos nominales anteriores para responder mejor en dónde y por qué se desvía la ejecución frente a la planeación. Ten en cuenta estas restricciones reales:
- El panel agregado tiene N = 24 observaciones entidad-año (6 entidades × 4 años), aunque a nivel micro tenemos decenas de miles de contratos con fecha exacta de firma, modalidad, proveedor y segmento UNSPSC.
- No existe un identificador único oficial que conecte 1 a 1 una línea del PAA con un id_contrato individual.
- Las mejoras deben poder implementarse en Python (pandas/numpy) sin requerir fuentes privadas.
Para cada mejora propuesta indica: (1) qué sesgo o limitación corrige, (2) su formulación matemática exacta y (3) sus posibles riesgos o supuestos.
```
