# Documentación Verificada de Datos (`data/README.md`)

> **Regla de `AGENTS.md`:** Antes de analizar cualquier archivo de `data/raw/`, lee este documento. Todos los esquemas, conteos y cautelas aquí consignados fueron **verificados empíricamente** contra la API Socrata de `datos.gov.co` y el archivo oficial de Colombia Compra Eficiente el **25 de noviembre de 2026**.

---

## 1. Inventario de Fuentes Oficiales Verificadas

| Fuente | Organismo | Endpoint / URL verificada | Dataset ID | Archivo congelado (`data/raw/`) | Filas piloto (3 ent.) |
|---|---|---|---|---|---:|
| **SECOP II — PAA Encabezado** | Colombia Compra Eficiente (`datos.gov.co`) | `https://www.datos.gov.co/resource/b6m4-qgqv.json` | `b6m4-qgqv` | `paa_encabezado.csv` | `12` |
| **SECOP II — PAA Detalle** | Colombia Compra Eficiente (`datos.gov.co`) | `https://www.datos.gov.co/resource/9sue-ezhx.json` | `9sue-ezhx` | `paa_detalle.csv` | `9.877` |
| **SECOP II — Contratos Electrónicos** | Colombia Compra Eficiente (`datos.gov.co`) | `https://www.datos.gov.co/resource/jbjy-vk9h.json` | `jbjy-vk9h` | `contratos_secop2.csv` | `9.290` |
| **Clasificador de Bienes y Servicios (UNSPSC v14.1)** | Colombia Compra Eficiente | `https://operaciones.colombiacompra.gov.co/sites/cce_public/files/cce_clasificador/clasificador_de_bienes_y_servicios_v14_1.xls` | N/A (`.xls` → `.csv`) | `clasificador_unspsc.csv` | `49.022` |

*(Metadatos exactos de extracción y huellas SHA-256 en `data/raw/metadata_extraccion.json`.)*

---

## 2. Qué Representa una Fila (Grano) y Alcance

### 2.1 `data/raw/paa_encabezado.csv` (`12` filas × `13` columnas en piloto)
- **Grano:** 1 fila = la **última versión publicada** del Plan Anual de Adquisiciones de una entidad en una vigencia fiscal (`codigo_entidad`, `anno`). Cero duplicados en `(codigo_entidad, anno)`.
- **Alcance:** Población completa (100% de registros publicados en `datos.gov.co`) para las entidades seleccionadas y los años `2022–2025`.
- **Utilidad analítica:** `version` indica cuántas actualizaciones realizó la entidad durante el año; `valor_presupuesto_general` sirve como chequeo de cuadre contra la suma de `valor_total_esperado` en `paa_detalle.csv`.

### 2.2 `data/raw/paa_detalle.csv` (`9.877` filas × `23` columnas en piloto)
- **Grano:** 1 fila = una línea/ítem de adquisición planeada dentro de la **última versión vigente** del PAA de la entidad en el año (`id` único, cero duplicados de `id`; `tipo = 'Adquisicion'` en el 100% de filas).
- **Verificación de cuadre:** `9sue-ezhx` almacena únicamente la versión vigente por entidad-año (no acumula versiones históricas repetidas) y `sum(valor_total_esperado)` cuadra al peso exacto con `valor_presupuesto_general` de `b6m4-qgqv`.
- **Distinción presupuestal clave:**
  - `valor_total_esperado`: costo total proyectado del ítem (incluye vigencias futuras si `se_requieren_vigencias_futuras == 'Si'`).
  - `valor_esperado_de_presupuesto`: valor correspondiente únicamente a la **vigencia fiscal actual**.

### 2.3 `data/raw/contratos_secop2.csv` (`9.290` filas × `31` columnas en piloto)
- **Grano:** 1 fila = un contrato electrónico único en SECOP II (`id_contrato` único, cero duplicados) cuya `fecha_de_firma` cae entre `2022-01-01` y `2025-12-31`.
- **Privacidad y economía de espacio:** la consulta `$select` en `src/ingesta.py` extrae exclusivamente las 31 columnas analíticas y excluye deliberadamente números de cuentas bancarias y cédulas/nombres de supervisores y ordenadores del gasto.

### 2.4 `data/raw/clasificador_unspsc.csv` (`49.022` filas × `8` columnas)
- **Grano:** 1 fila = un código de producto UNSPSC v14.1 de 8 dígitos con su jerarquía completa: **56 segmentos (2 dígitos)**, **420 familias (4 dígitos)**, **3.818 clases (6 dígitos)** y **49.022 productos (8 dígitos)**.
- **Conversión desde fuente oficial:** generado por `src/ingesta.py` leyendo la hoja `'Clasificador'` (`header=3`, omitiendo 3 filas de nota legal) de `clasificador_de_bienes_y_servicios_v14_1.xls` y normalizando los códigos numéricos a texto con ceros a la izquierda.

---

## 3. Diccionario de Columnas Clave Verificadas

### 3.1 PAA Detalle (`paa_detalle.csv`)
| Columna | Tipo al leer | Descripción verificada | Cautelas |
|---|---|---|---|
| `id` | `str` | Identificador único del ítem en `9sue-ezhx` | Sin duplicados |
| `codigo_entidad`, `nit_entidad` | `str` | Claves de entidad estatal | En `9sue-ezhx` llegan como texto; unificar siempre como `str` |
| `annio` | `int` | Año fiscal del PAA (`2022–2025`) | Nombre con doble `n` en la API |
| `version_del_paa` | `int` | Última versión publicada del PAA en esa vigencia | Refleja cuántas actualizaciones tuvo el PAA en el año |
| `valor_total_esperado` | `float` | Valor total planeado del ítem (COP) | Incluye vigencias futuras; `27` ítems con valor `<= 0` en piloto |
| `valor_esperado_de_presupuesto` | `float` | Presupuesto planeado para la vigencia actual (COP) | Menor que `valor_total_esperado` cuando hay vigencias futuras |
| `se_requieren_vigencias_futuras` | `str` | `"Si"` / `"No"` | Explica brechas de planeación multianual |
| `modalidad` | `str` | Modalidad planeada | Viene en MAYÚSCULAS sin tildes y presenta `1.561` filas `"No Definido"` en piloto |
| `categorias_unspsc` | `str` | Código(s) UNSPSC planeados (8 dígitos, sin prefijo) | `626` filas en piloto listan múltiples códigos separados por `;`, `,` o espacio |

### 3.2 Contratos SECOP II (`contratos_secop2.csv`)
| Columna | Tipo al leer | Descripción verificada | Cautelas |
|---|---|---|---|
| `id_contrato` | `str` | Identificador único del contrato (`CO1.PCCNTR...`) | Sin duplicados |
| `codigo_entidad`, `nit_entidad` | `str` | Claves de entidad (en la API son numéricas; se leen como `str`) | 100% consistentes con `paa_detalle` en las 6 entidades seleccionadas |
| `estado_contrato` | `str` | Estado actual (`Modificado`, `En ejecución`, `Cerrado`, `terminado`, `cedido`, `Aprobado`, `Suspendido`) | Mezcla mayúsculas/minúsculas (`terminado`, `cedido`); no hay borradores en piloto |
| `codigo_de_categoria_principal` | `str` | Código UNSPSC principal del contrato | Trae prefijo `V1.` (ej. `V1.80121601`) y `31` registros `"UNSPECIFIED"` (`0,33%`) |
| `modalidad_de_contratacion` | `str` | Modalidad ejecutada | Viene con tildes y capitalización mixta; normalizar a macro-modalidades comparables con PAA |
| `fecha_de_firma` | `datetime` | Fecha de firma del contrato (ISO 8601) | Define el año fiscal de ejecución (`2022–2025`) |
| `documento_proveedor`, `proveedor_adjudicado` | `str` | Identificación y razón social del contratista | Base para concentración por proveedor (`CR5` y `HHI`) |
| `valor_del_contrato` | `float` | Valor total del contrato (COP) | `808` contratos en piloto tienen `valor <= 0` (mayoría: `559` Acuerdos Marco de Precios de ANCP + `160` convenios/otros sin cuantía) |

---

## 4. Cautelas Críticas Verificadas (para `src/limpieza_cruce.py`)
1. **Nivel de cruce UNSPSC (hallazgo empírico R6):** Al cruzar por código exacto de **Producto (8 dígitos)** solo empareja el **17,40%** del PAA y el **16,14%** de Contratos, porque las entidades reportan masivamente a nivel de clase terminada en `00` (ej. `80101500`). Al extraer los primeros **6 dígitos (Clase)**, **4 dígitos (Familia)** o **2 dígitos (Segmento)**, el emparejamiento sube a **99,99%** en PAA y **99,67%** en Contratos (el `0,33%` restante son exactamente los `31` contratos `"UNSPECIFIED"`).
2. **Contratos con `valor_del_contrato == 0`:** En ANCP (Colombia Compra Eficiente), `559` contratos son *Acuerdos Marco de Precios* firmados por valor `$0` (las órdenes de compra las hacen luego otras entidades). Deben marcarse explícitamente (`es_contrato_sin_cuantia`) para no distorsionar montos promedio ni tasas de ejecución, documentando su tratamiento.
3. **Duplicados semánticos / atípicos en PAA:** En piloto existen `632` filas con igual `(entidad, año, descripción, valor, UNSPSC, modalidad)`. Muchas corresponden a múltiples plazas idénticas de prestación de servicios (legítimas), pero también se detectó un posible doble registro atípico de **$333,5 mil millones** en MinAmbiente 2023 (dos ítems idénticos para constituir el patrimonio autónomo *Fondo para la Vida y la Biodiversidad*, `MarketplaceCO1408005152` y `MarketplaceCO1408005376`). Se auditará y documentará explícitamente en `src/limpieza_cruce.py`.
4. **Vigencias futuras:** En MinHacienda 2023 un solo ítem de capitalización tiene `valor_total_esperado = $366,02 MM` frente a `valor_esperado_de_presupuesto = $92,10 MM`. Contrastar ejecución contra ambos montos evita sesgos de interpretación.

---

## 5. Cómo Regenerar los Datos Crudos
- **Modo reproducible / offline (por defecto en notebook y scripts):**
  ```powershell
  python -m src.ingesta
  ```
- **Modo actualización desde API (`datos.gov.co`) — Piloto (3 entidades) o Completo (6 entidades):**
  ```powershell
  python -m src.ingesta --modo piloto --actualizar-api
  python -m src.ingesta --modo completo --actualizar-api
  ```
- **Última extracción verificada:** **2026-11-25** (modo `piloto`: 3 entidades, `2022–2025`; pruebas `pytest` en verde: 5/5).
