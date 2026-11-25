# Documentación de Datos (`data/README.md`)

> **Regla de `AGENTS.md`:** Antes de analizar cualquier archivo de `data/raw/`, lee este documento. **No inventes nombres de columnas, códigos ni significados.** Esta plantilla se completará exclusivamente con hechos verificados durante la **Fase 2 (Descubrimiento de APIs en `datos.gov.co`)**.

---

## 1. Inventario de Fuentes Oficiales

| Fuente | Organismo | Endpoint / URL verificada | Dataset ID Socrata | Modo de acceso | Archivo congelado en `data/raw/` |
|---|---|---|---|---|---|
| **Plan Anual de Adquisiciones (PAA) — SECOP II** | Colombia Compra Eficiente (`datos.gov.co`) | `[PENDIENTE FASE 2]` | `[PENDIENTE FASE 2]` | API SODA (`requests`) + caché local | `data/raw/paa_secop2.csv` |
| **Contratos Electrónicos — SECOP II** | Colombia Compra Eficiente (`datos.gov.co`) | `[PENDIENTE FASE 2]` | `[PENDIENTE FASE 2]` | API SODA (`requests`) + caché local | `data/raw/contratos_secop2.csv` |
| **Clasificador de Bienes y Servicios (UNSPSC)** | Colombia Compra Eficiente | `https://operaciones.colombiacompra.gov.co/clasificador-de-bienes-y-servicios` *(verificar descarga exacta)* | N/A (Excel/CSV oficial) | Descarga oficial + copia congelada | `data/raw/clasificador_unspsc.xlsx` *(o `.csv`)* |

---

## 2. Qué Representa una Fila (Grano) y Alcance

### 2.1 `data/raw/paa_secop2.csv`
- **Qué representa una fila:** `[PENDIENTE FASE 2: confirmar si una fila es un ítem/línea del PAA de una entidad en una vigencia, y si hay múltiples versiones por año]`
- **Población vs. Muestra:** `[PENDIENTE FASE 2: universo completo de registros PAA en datos.gov.co para las entidades y periodo seleccionados]`
- **Cobertura temporal verificada:** `[PENDIENTE FASE 2]`
- **Número de filas y columnas:** `[PENDIENTE FASE 2]`

### 2.2 `data/raw/contratos_secop2.csv`
- **Qué representa una fila:** `[PENDIENTE FASE 2: confirmar si una fila es un contrato único por id_contrato o si puede repetirse por modificaciones/lotes]`
- **Población vs. Muestra:** `[PENDIENTE FASE 2]`
- **Cobertura temporal verificada:** `[PENDIENTE FASE 2]`
- **Número de filas y columnas:** `[PENDIENTE FASE 2]`

### 2.3 `data/raw/clasificador_unspsc.*`
- **Qué representa una fila:** `[PENDIENTE FASE 2: un código de producto/clase UNSPSC con su jerarquía Segmento -> Familia -> Clase -> Producto]`
- **Número de filas y columnas:** `[PENDIENTE FASE 2]`

---

## 3. Diccionario de Columnas Verificadas

### 3.1 PAA (`paa_secop2.csv`)
| Columna original (API) | Tipo real | Descripción verificada | Uso en el proyecto | Cautelas |
|---|---|---|---|---|
| `[PENDIENTE FASE 2]` | — | — | — | — |

### 3.2 Contratos SECOP II (`contratos_secop2.csv`)
| Columna original (API) | Tipo real | Descripción verificada | Uso en el proyecto | Cautelas |
|---|---|---|---|---|
| `[PENDIENTE FASE 2]` | — | — | — | — |

### 3.3 Clasificador UNSPSC
| Columna original | Tipo real | Descripción verificada | Uso en el proyecto | Cautelas |
|---|---|---|---|---|
| `[PENDIENTE FASE 2]` | — | — | — | — |

---

## 4. Cautelas Conocidas y Reglas de Interpretación
*(Documentar aquí hallazgos reales en Fases 2 y 3: formatos de NIT con/sin dígito de verificación, prefijos en códigos UNSPSC, años parciales, contratos en estado anulado/borrador, montos atípicos, zonas horarias y fecha exacta de corte de descarga).*

---

## 5. Cómo Regenerar los Datos Crudos
- **Modo por defecto (reproducible / offline):** el notebook y los scripts leen los archivos congelados en `data/raw/` incluidos en el `.zip`.
- **Modo actualización desde API (`datos.gov.co`):**
  ```bash
  python src/ingesta.py --actualizar-api
  ```
- **Fecha de última extracción verificada:** `[PENDIENTE FASE 3/4]`
