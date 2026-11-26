# Contratos de Datos para Visualización (`data/dashboard_data/README.md`)

Archivos generados automáticamente por `src/indicadores.py` a partir de `data/processed/`. Tanto `A_contraluz_tutorial.ipynb` como `app_streamlit.py` leen exclusivamente estos archivos ya validados.

## Cómo regenerar
```powershell
python -m src.limpieza_cruce
python -m src.indicadores
```

## Inventario y Proveniencia

| Archivo | Filas actuales | Grano (qué representa una fila) | Función generadora (`src/indicadores.py`) |
|---|---:|---|---|
| `resumen_entidad_anio.csv` | `24` | 1 entidad × 1 año (`2022–2025`) con KPIs nominales, reales IPC 2025 e Índice de Duncan | `calcular_resumen_entidad_anio` |
| `modalidades_entidad_anio.csv` | `158` | 1 entidad × 1 año × 1 macro-modalidad | `calcular_modalidades_entidad_anio` |
| `concentracion_proveedores.csv` | `24` | 1 entidad × 1 año (`CR1`, `CR5`, `HHI`) | `calcular_concentracion_proveedores` |
| `top_proveedores_entidad.csv` | `60` | Top 10 proveedores por entidad (`2022–2025`) | `calcular_top_proveedores_entidad` |
| `brechas_segmento_unspsc.csv` | `648` | 1 entidad × 1 año × 1 segmento UNSPSC (`2d`) con contribución a Duncan y valores reales 2025 | `calcular_brechas_segmento_unspsc` |
| `distribucion_franjas_cuantia.csv` | `49` | 1 alcance (`TODAS` o entidad) × 1 franja de valor (`7` franjas) | `calcular_distribucion_franjas_cuantia` |
| `rubro5_antes_despues.csv` | `7` | 1 entidad (más `TOTAL_MUESTRA`) contrastando Antes (nominal) vs. Después (IPC 2025 + Duncan) | `calcular_comparativa_rubro5_antes_despues` |
| `rubro5_registro_ia.json` | `JSON` | Prompt literal, respuesta completa de la IA y evaluación crítica del Rubro 5 | `construir_registro_ia_rubro5` |
