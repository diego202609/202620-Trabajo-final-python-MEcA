# Tablas Limpias e Integradas (`data/processed/README.md`)

Estos archivos son generados automáticamente por `src/limpieza_cruce.py` a partir de los insumos inmutables de `data/raw/`. Constituyen el **contrato de datos intermedio** hacia el cálculo de indicadores (`src/indicadores.py`).

## Cómo regenerar
```powershell
python -m src.limpieza_cruce
```

## Inventario de Archivos y Grano

| Archivo | Qué representa una fila (Grano) | Clave única | Descripción |
|---|---|---|---|
| `paa_limpio.csv` | Un ítem planeado en la última versión del PAA | `id` | PAA Detalle tipificado, con `modalidad_homologada`, cruce jerárquico UNSPSC (`codigo_segmento`, `codigo_familia`, `codigo_clase` y nombres) y banderas de calidad (`requiere_vigencias_futuras`, `es_valor_no_positivo`, `es_posible_duplicado_atipico`, `es_atipico_p99`). |
| `contratos_limpio.csv` | Un contrato electrónico firmado en SECOP II (`2022–2025`) | `id_contrato` | Contratos tipificados, con `estado_contrato_homologado`, `modalidad_homologada`, `id_proveedor_limpio`, cruce jerárquico UNSPSC y banderas (`es_estado_invalido`, `es_contrato_sin_cuantia`, `es_acuerdo_marco`, `es_contratacion_directa`, `es_atipico_p99`). |
| `cruce_entidad_anio.csv` | Un par `(codigo_entidad, anio)` | `(codigo_entidad, anio)` | Panel anual integrado que cruza PAA Encabezado + PAA Detalle + Contratos SECOP II válidos con cuantía, incluyendo `% de ejecución` sobre presupuesto de vigencia actual (con y sin duplicado administrativo atípico) y sobre valor total PAA. |
| `cruce_entidad_anio_segmento.csv` | Una combinación `(codigo_entidad, anio, codigo_segmento)` | `(codigo_entidad, anio, codigo_segmento)` | Cruce `outer` entre lo planeado en el PAA y lo ejecutado en SECOP II desagregado por los 56 segmentos UNSPSC (2 dígitos). |
| `auditoria_calidad.json` | Resumen estructurado de la corrida | N/A | Métricas exactas de tipos, faltantes, duplicados, atípicos, cuadre presupuestal y tasas de emparejamiento UNSPSC (8 dígitos vs. 6/4/2 dígitos). |
