# Registro Íntegro — Rubro 5: Uso de IA para Ir Más Allá de la Metodología

Este documento conserva de forma íntegra y literal: (1) el prompt enviado a la IA, (2) la respuesta completa recibida, (3) la identificación precisa de qué supera lo recomendado por el equipo pedagógico y (4) la evaluación crítica del Grupo 3 (qué mejoras se implementaron en código y cuáles se descartaron con justificación técnica).

---

## 1. Prompt Formulado y Enviado a la IA

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

---

## 2. Respuesta Completa de la IA (Literal, sin Recortes)

Desde la economía de las compras públicas y la econometría aplicada al sector público colombiano, los cuatro indicadores descriptivos actuales caracterizan bien *cuánto* se ejecuta y *quién* recibe los recursos en términos nominales, pero enfrentan cuatro sesgos analíticos para explicar **en dónde y por qué** ocurren las desviaciones: (i) distorsión inflacionaria intertemporal, (ii) compensación agregada entre rubros, (iii) pérdida de grados de libertad en el panel macro ($N = 24$) frente a dinámicas estacionales del ciclo presupuestal y (iv) imposibilidad de separar el margen extensivo del intensivo ante la ausencia de llave única PAA–Contrato.

A continuación propongo **cuatro mejoras metodológicas** rigurosas, ordenadas de menor a mayor exigencia de supuestos e implementables íntegramente en Python (`pandas`/`numpy`) con información pública oficial.

### 1. Deflactación Intertemporal a Precios Constantes (IPC DANE, base $2025 = 100$)

1. **Sesgo o limitación que corrige:**
   Corrige el **sesgo de ilusión monetaria y distorsión en la agregación plurianual**. Entre 2022 y 2025 Colombia experimentó un choque inflacionario agudo (inflación anual certificada por el DANE de 13,12% en 2022 y 9,28% en 2023, moderándose en 2024–2025). Sumar directamente los \$9.343,83 mil millones COP planeados y \$7.780,10 mil millones COP ejecutados en pesos corrientes subpondera en poder adquisitivo real las brechas de 2022–2023 frente a las de 2024–2025 y sesga al alza el crecimiento aparente del gasto y de las brechas nominales por segmento UNSPSC.

2. **Formulación matemática exacta:**
   Sea $I_t$ el Índice de Precios al Consumidor oficial del DANE (cierre de diciembre o promedio anual) para la vigencia $t \in \{2022, 2023, 2024, 2025\}$, fijando como año base $t_0 = 2025$. El factor de actualización a pesos constantes de 2025 es $d_t = I_{2025} / I_t$. Para cada entidad $i$, segmento UNSPSC $s$ y año $t$, el valor planeado real ($P_{ist}^{\text{real}}$), el ejecutado real ($E_{ist}^{\text{real}}$) y la brecha real acumulada en el cuatrienio ($\Delta_{is}^{\text{real}}$) se definen como:

   $$P_{ist}^{\text{real}} = P_{ist}^{\text{nom}} \cdot \frac{I_{2025}}{I_t}, \qquad E_{ist}^{\text{real}} = E_{ist}^{\text{nom}} \cdot \frac{I_{2025}}{I_t}$$

   $$\Delta_{is}^{\text{real}} = \sum_{t=2022}^{2025} \left(E_{ist}^{\text{real}} - P_{ist}^{\text{real}}\right) = \sum_{t=2022}^{2025} \frac{I_{2025}}{I_t}\left(E_{ist}^{\text{nom}} - P_{ist}^{\text{nom}}\right)$$

   En `pandas` basta con mapear un diccionario de cuatro escalares anuales del DANE mediante `Series.map()` y multiplicar vectorialmente las series monetarias.

3. **Riesgos o supuestos:**
   - *Invarianza algebraica del cociente intra-anual:* Al multiplicar numerador y denominador del mismo año por el escalar $d_t$, la tasa de ejecución anual $E_{it}^{\text{real}} / P_{it}^{\text{real}} = E_{it}^{\text{nom}} / P_{it}^{\text{nom}}$ permanece idéntica. La corrección modifica **brechas absolutas en COP, agregados 2022–2025, participaciones interanuales y tasas de crecimiento real**, salvo que se deflacte cada contrato con el IPC mensual exacto de su fecha de firma frente a enero del PAA.
   - *Representatividad de la canasta:* El IPC mide precios al consumidor urbano, mientras que la compra estatal combina servicios profesionales indexados al salario mínimo (SMLMV) e insumos especializados más cercanos al IPP.

### 2. Índice de Disimilitud Estructural de Duncan ($D_{it}$) sobre la Composición UNSPSC

1. **Sesgo o limitación que corrige:**
   Corrige el **sesgo de compensación o enmascaramiento agregado** de la tasa global de ejecución ($E_{it}/P_{it}$). Una entidad puede registrar 98% de ejecución total —aparentando alta fidelidad al PAA— porque subejecutó proyectos misionales o tecnológicos en unos segmentos UNSPSC y compensó el monto sobreejecutando servicios de gestión o apoyo administrativo en otros (amparada en el carácter indicativo y modificable del PAA bajo el Decreto 1082 de 2015 o por reclasificación de códigos al adjudicar).

2. **Formulación matemática exacta:**
   Para la entidad $i$ en el año $t$, sean $w_{ist}^{P}$ y $w_{ist}^{E}$ las participaciones relativas de cada categoría UNSPSC $s \in \mathcal{S}$ (a nivel de Segmento de 2 dígitos o Clase de 6 dígitos) sobre el presupuesto total planeado y ejecutado de esa vigencia:

   $$w_{ist}^{P} = \frac{P_{ist}}{\sum_{k \in \mathcal{S}} P_{ikt}}, \qquad w_{ist}^{E} = \frac{E_{ist}}{\sum_{k \in \mathcal{S}} E_{ikt}}$$

   El Índice de Disimilitud (Duncan & Duncan, 1955) adaptado a reasignación presupuestal se expresa como:

   $$D_{it} = \frac{1}{2} \sum_{s \in \mathcal{S}} \left| w_{ist}^{E} - w_{ist}^{P} \right|, \qquad D_{it} \in [0, 1]$$

   Cada sumando $c_{ist} = \frac{1}{2} |w_{ist}^{E} - w_{ist}^{P}|$ mide la contribución aditiva exacta del segmento $s$ al desvío estructural ($\sum_{s} c_{ist} = D_{it}$). Económicamente, $D_{it}$ indica **qué fracción del gasto ejecutado (de 0% a 100%) tendría que reasignarse entre segmentos UNSPSC para replicar exactamente la canasta planeada en el PAA**. Se implementa en `pandas`/`numpy` con agregaciones `groupby`, `merge(..., how="outer").fillna(0)` y `np.abs()`.

3. **Riesgos o supuestos:**
   - *Invarianza de escala:* $D_{it}$ evalúa fidelidad en la *composición relativa*, no en el *nivel de gasto*. Si una entidad recorta o infla todos sus segmentos exactamente en la misma proporción, $D_{it} = 0$; por ello debe leerse en conjunto con la tasa de ejecución agregada (por ejemplo, en un plano cartesiano Tasa de Ejecución vs. $D_{it}$).
   - *Sensibilidad a la granularidad UNSPSC:* Evaluado en Clase (6 dígitos), $D_{it}$ puede sobredimensionar la desviación cuando el comprador corrige códigos contiguos dentro de una misma familia funcional; evaluado en Segmento (2 dígitos, 56 grupos), aísla verdaderos giros sectoriales pero atenúa sustituciones finas intra-segmento.

### 3. Concentración Estacional Intra-anual («Fiebre de Fin de Año») y Ciclo Institucional

1. **Sesgo o limitación que corrige:**
   Supera la **limitación estadística de $N = 24$ celdas entidad-año** aprovechando los 25.317 contratos a nivel micro y su fecha exacta de firma para explicar el *porqué institucional* de las desviaciones. En la teoría de contratación pública (Liebman & Mahoney, *American Economic Review*, 2017), el principio presupuestal de anualidad (Decreto 111 de 1996) genera incentivos de expiración de saldos (*use-it-or-lose-it*) que aceleran contrataciones de menor calidad competitiva al cierre fiscal. En Colombia se suma además el choque exógeno de la **Ley de Garantías Electorales (Ley 996 de 2005)** en el primer semestre de 2022, que restringió convenios interadministrativos y contratación directa antes de elecciones nacionales, forzando picos anticipados en enero de 2022.

2. **Formulación matemática exacta:**
   Sea $E_{itm}$ el monto (o conteo) contratado por la entidad $i$ en el año $t$ y mes de firma $m \in \{1, \dots, 12\}$, y $q_{itm} = E_{itm} / \sum_{r=1}^{12} E_{itr}$ la cuota mensual dentro del año. Se proponen dos métricas complementarias calculables también por subgrupos de modalidad (Directa vs. Competitiva):

   1. *Índice de Divergencia Estacional de Kullback-Leibler normalizado (frente a flujo uniforme $1/12$):*

      $$S_{it} = \frac{1}{\ln(12)} \sum_{m=1}^{12} q_{itm} \ln\left(12 \, q_{itm}\right), \qquad S_{it} \in [0, 1]$$

      adoptando $0 \ln 0 = 0$ (donde $S_{it} = 0$ denota ejecución perfectamente uniforme en el año y $S_{it} = 1$ concentración total en un único mes).
   2. *Razón de Intensidad en Ventanas Críticas ($\text{RIC}$):* Para medir agotamiento de cierre en el cuarto trimestre ($m \in \{10,11,12\}$) —o análogamente anticipación pre-veda en enero ($m = 1$)— frente al promedio mensual del resto de la vigencia:

      $$\text{RIC}_{it}^{\text{Q4}} = \frac{\frac{1}{3}\sum_{m=10}^{12} E_{itm}}{\frac{1}{9}\sum_{m=1}^{9} E_{itm}}$$

   En `pandas`/`numpy` se obtiene extrayendo el mes con `.dt.month` y aplicando `np.where(q > 0, q * np.log(12 * q), 0)`.

3. **Riesgos o supuestos:**
   - *Estacionalidad operativa legítima:* En ministerios del nivel central, firmar contratos anuales de prestación de servicios y pólizas en enero–febrero obedece a continuidad operativa y no a improvisación; por ello, el efecto de Ley de Garantías debe identificarse por contraste interanual (enero 2022 vs. eneros 2023–2025).
   - *Sensibilidad a megacontratos plurianuales:* Un solo contrato con vigencias futuras (Ley 819 de 2003) firmado en noviembre o diciembre puede inflar $\text{RIC}_{it}^{\text{Q4}}$ en dinero, por lo que debe reportarse simultáneamente en **valor** y en **número de contratos**.

### 4. Emparejamiento Micro Bloqueado por Distancia Compuesta (Asignación Bipartita PAA–Contrato)

1. **Sesgo o limitación que corrige:**
   Enfrenta la **ausencia de identificador único 1 a 1 entre líneas del PAA y contratos de SECOP II**. Sin cruce micro, la brecha agregada confunde el *margen extensivo* (proyectos planeados que se cancelan y contratos imprevistos fuera del PAA) con el *margen intensivo* (sobrecostos, adiciones o ahorros de licitación sobre ítems efectivamente ejecutados).

2. **Formulación matemática exacta:**
   Inspirado en el enlace probabilístico con bloqueo exacto (Fellegi & Sunter, 1969), se particionan ambas bases en celdas estrictas $b = (i, t, c_6, \tilde{m})$ definidas por entidad $i$, año $t$, Clase UNSPSC a 6 dígitos $c_6$ y macro-modalidad homologada $\tilde{m}$. Para cada par candidato $(j, k) \in \mathcal{P}_b \times \mathcal{C}_b$ con cuantías positivas ($P_j > 0, E_k > 0$), se define la discrepancia proporcional simétrica en logaritmos:

   $$d(j, k) = \left| \ln(E_k) - \ln(P_j) \right|$$

   Dentro de cada celda $b$, se busca la asignación uno a uno sin reemplazo $x_{jk} \in \{0, 1\}$ acotada por un umbral económico máximo $\tau > 0$ (por ejemplo, $\tau = \ln(1{,}5) \approx 0{,}405$, consistente con el tope legal del 50% para adiciones contractuales del art. 40 de la Ley 80 de 1993):

   $$\min_{\mathbf{X} \in \{0,1\}^{|\mathcal{P}_b| \times |\mathcal{C}_b|}} \sum_{j \in \mathcal{P}_b} \sum_{k \in \mathcal{C}_b} d(j, k) \, x_{jk} \quad \text{s.a.} \quad \sum_{k \in \mathcal{C}_b} x_{jk} \le 1, \quad \sum_{j \in \mathcal{P}_b} x_{jk} \le 1, \quad x_{jk} = 0 \text{ si } d(j,k) > \tau$$

   En `pandas`/`numpy` puede aproximarse determinísticamente ordenando pares candidatos por $d(j,k)$ ascendente dentro de cada bloque $b$ (emparejamiento *greedy* sin reemplazo), separando tres componentes: ítems PAA huérfanos ($x_{j\cdot}=0$), contratos emergentes ($x_{\cdot k}=0$) y brecha intensiva en pares emparejados ($\sum x_{jk}(E_k - P_j)$).

3. **Riesgos o supuestos:**
   - *Violación frecuente de la cardinalidad 1 a 1 (relaciones $1:M$ y $M:1$):* En la práctica presupuestal colombiana, una única línea agregada del PAA (p. ej., una bolsa global para contratistas de apoyo por \$2.000 millones COP) suele ejecutarse mediante decenas de contratos individuales de \$50 millones COP ($1:M$), o múltiples líneas del PAA se consolidan en un solo proceso por lotes ($M:1$). En ambos casos reales $|\ln(E_k) - \ln(P_j)| > \tau$, produciendo **falsos negativos sistemáticos** que sobrestiman artificialmente tanto la "no ejecución" como la "improvisación contractual".
   - *Indistinguibilidad y reclasificación:* En celdas densas con múltiples contratos de prestación de servicios de idéntico valor y Clase UNSPSC, el emparejamiento individual es arbitrario; a la inversa, si al adjudicar cambia la modalidad o el código de Clase frente al PAA, el bloqueo exacto descarta pares verdaderos. Por tanto, solo constituye un ejercicio exploratorio de sensibilidad y no equivale a trazabilidad contable oficial.

### Síntesis Comparativa de Viabilidad Analítica

| Mejora propuesta | Fenómeno económico que aísla | Nivel de datos | Robustez de supuestos |
|---|---|---|---|
| **1. Deflactación IPC DANE** | Poder adquisitivo real y brechas comparables 2022–2025 | Panel / Segmento | **Alta** (supuesto estándar de precios constantes) |
| **2. Índice de Duncan ($D_{it}$)** | Reasignación composicional oculta entre rubros UNSPSC | Entidad × Año × UNSPSC | **Alta** (descomposición contable exacta en $[0, 1]$) |
| **3. Estacionalidad micro ($S_{it}$, $\text{RIC}$)** | Premura de cierre anual (anualidad) y choque Ley de Garantías | Micro (`25.317` contratos) | **Media-Alta** (requiere separar eneros operativos y vigencias futuras) |
| **4. Emparejamiento bloqueado** | Separación tentativa de margen extensivo vs. intensivo | Micro bipartito PAA–SECOP | **Baja-Media** (vulnerable a bolsas $1:M$ y consolidación $M:1$) |

---

## 3. Qué Va Más Allá de lo Recomendado por los Profesores

Las recomendaciones de la evaluación de la propuesta pedían indicadores descriptivos en valores corrientes (`% de lo planeado que se contrata`, `concentración por proveedor`, `peso de la contratación directa` y cruce UNSPSC). Las cuatro sugerencias de la IA van más allá en cuatro frentes distintos:
1. **Corrección macroeconómica de precios (#1):** pasa de sumas nominales (distorsionadas por inflación acumulada >20% entre cierre de 2022 y 2025) a poder adquisitivo constante de 2025 usando la serie certificada del IPC DANE.
2. **Métrica formal de desalineación composicional (#2):** introduce el Índice de Disimilitud de Duncan ($D_{it}$) para cuantificar qué porcentaje del gasto cambió de sector UNSPSC aunque el monto agregado aparente cumplirse.
3. **Economía institucional del calendario de gasto (#3):** plantea medir entropía estacional ($S_{it}$) y ventanas críticas (cierre fiscal Q4 y Ley de Garantías 2022).
4. **Inferencia de enlace de registros sin llave (#4):** propone un algoritmo de optimización bipartita `1:1` tipo Fellegi-Sunter entre líneas del PAA y contratos.

---

## 4. Evaluación Crítica del Equipo: Qué Implementamos y Qué Descartamos

### Mejoras ACEPTADAS e implementadas en código (`src/indicadores.py` y `src/visualizacion.py`)
- **Aceptamos la Mejora #1 (Deflactación con IPC oficial DANE base `2025 = 100`) y la Mejora #2 (Índice de Disimilitud Estructural de Duncan $D_{it}$ a nivel de Segmento UNSPSC, junto con el plano cartesiano *Tasa de Ejecución vs. Duncan*):**
  - **Razón:** Ambas responden **directamente** a nuestra pregunta central sin exigir supuestos frágiles. La primera corrige el sesgo real de comparar pesos de 2022 con pesos de 2025 en las brechas acumuladas; la segunda destapa reasignaciones sectoriales que la simple razón `Ejecutado / Planeado` ocultaba por compensación entre rubros.

### Mejoras DESCARTADAS críticamente por el equipo
1. **Descartamos la Mejora #4 (Emparejamiento micro bipartito `1:1` PAA–Contrato con $|\ln E_k - \ln P_j| \le \ln(1,5)$):**
   - **Por qué la descartamos:** En la gestión presupuestal de los ministerios colombianos, una sola línea del PAA funciona habitualmente como una **bolsa global pluripersonal (`1:M`)** (por ejemplo, una línea de `$2.000 millones` para contratar 40 profesionales de `$50 millones`), o a la inversa, varias líneas de insumos se agrupan en una sola licitación por lotes (`M:1`). Imponer una restricción matemática `1:1` con cota del `50%` ($|\ln(50) - \ln(2000)| = 3,69 \gg 0,405$) rechazaría sistemáticamente ejecuciones `1:M` completamente legítimas, fabricando miles de falsos "ítems abandonados" y falsos "contratos improvisados" que inducirían a conclusiones erróneas de veeduría.
2. **Descartamos la Mejora #3 (Índice de Kullback-Leibler estacional $S_{it}$ y $\text{RIC}^{\text{Q4}}$):**
   - **Por qué la descartamos:** Primero, porque en el PAA (`9sue-ezhx`) la columna `fecha_esperada_de_inicio` es un texto indicativo sin cronograma mensual de desembolsos comparable contra `fecha_de_firma`. Segundo, porque en entidades del nivel central la concentración masiva de firmas en enero responde a la contratación anual ordinaria de servicios profesionales para operar la entidad (y en enero de 2022 a la entrada en vigor de la Ley 996 de 2005), no a una desviación respecto al PAA. Incluirla abriría una subpregunta distinta y restaría foco directo a nuestra pregunta única (criterio explícito del **Rubro 4**).
