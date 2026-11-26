# %% [markdown]
# # Construcción de Indicadores Económicos y Contratos de Datos (`data/dashboard_data/`)
#
# Calcula todos los indicadores definidos en la propuesta y recomendaciones del
# equipo pedagógico (R5 y R7) a partir de `data/processed/`, guardando tablas CSV
# listas para consumo directo por `A_contraluz_tutorial.ipynb` y `app_streamlit.py`.

# %%
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import (
    ARCHIVO_CONTRATOS_LIMPIO,
    ARCHIVO_CRUCE_ENTIDAD_ANIO,
    ARCHIVO_CRUCE_SEGMENTO,
    ARCHIVO_DASH_CONCENTRACION,
    ARCHIVO_DASH_FRANJAS_CUANTIA,
    ARCHIVO_DASH_MODALIDADES,
    ARCHIVO_DASH_README,
    ARCHIVO_DASH_RESUMEN_ANUAL,
    ARCHIVO_DASH_RUBRO5_COMPARATIVA,
    ARCHIVO_DASH_RUBRO5_JSON,
    ARCHIVO_DASH_SEGMENTOS_UNSPSC,
    ARCHIVO_DASH_TOP_PROVEEDORES,
    ARCHIVO_PAA_LIMPIO,
    ARCHIVO_RUBRO5_MD,
    DASHBOARD_DATA_DIR,
    FACTOR_DEFLACTOR_IPC_2025,
    IPC_INFLACION_ANUAL_DANE,
    PROCESSED_DIR,
)

FRANJAS_CUANTIA_DEFINICION = [
    (1, "Igual a $0 (AMP / sin erogación)", "valor == 0", "Marcado sin cuantía"),
    (2, "Simbólica ($0,01 – $1.000)", "0 < valor <= 1.000", "Marcado cuantía simbólica"),
    (3, "Micro-compra ($1.001 – $1M)", "1.000 < valor <= 1.000.000", "Incluido en análisis"),
    (4, "Menor ($1M – $10M)", "1M < valor <= 10M", "Incluido en análisis"),
    (5, "Estándar ($10M – $100M)", "10M < valor <= 100M", "Incluido en análisis"),
    (6, "Intermedia ($100M – $1.000M)", "100M < valor <= 1.000M", "Incluido en análisis"),
    (7, "Gran cuantía (> $1.000M)", "valor > 1.000M", "Incluido en análisis"),
]


# %%
def clasificar_categoria_hhi(hhi: float) -> str:
    """Clasifica el Índice Herfindahl-Hirschman según el estándar DOJ/FTC y SIC."""
    if pd.isna(hhi):
        return "Sin datos"
    if hhi < 1500:
        return "Baja (< 1.500)"
    if hhi <= 2500:
        return "Moderada (1.500–2.500)"
    return "Alta (> 2.500)"


def asignar_franja_cuantia(valor: float) -> tuple[int, str]:
    """Asigna el orden y nombre de franja de cuantía en COP a un contrato."""
    if pd.isna(valor) or valor <= 0:
        return FRANJAS_CUANTIA_DEFINICION[0][0], FRANJAS_CUANTIA_DEFINICION[0][1]
    if valor <= 1_000:
        return FRANJAS_CUANTIA_DEFINICION[1][0], FRANJAS_CUANTIA_DEFINICION[1][1]
    if valor <= 1_000_000:
        return FRANJAS_CUANTIA_DEFINICION[2][0], FRANJAS_CUANTIA_DEFINICION[2][1]
    if valor <= 10_000_000:
        return FRANJAS_CUANTIA_DEFINICION[3][0], FRANJAS_CUANTIA_DEFINICION[3][1]
    if valor <= 100_000_000:
        return FRANJAS_CUANTIA_DEFINICION[4][0], FRANJAS_CUANTIA_DEFINICION[4][1]
    if valor <= 1_000_000_000:
        return FRANJAS_CUANTIA_DEFINICION[5][0], FRANJAS_CUANTIA_DEFINICION[5][1]
    return FRANJAS_CUANTIA_DEFINICION[6][0], FRANJAS_CUANTIA_DEFINICION[6][1]


# %%
def calcular_concentracion_proveedores(df_cont: pd.DataFrame) -> pd.DataFrame:
    """Calcula CR1, CR5 e Índice HHI (escala 0–10.000) por Entidad × Año."""
    validos = df_cont[df_cont["es_contrato_valido_con_cuantia"]].copy()
    filas = []

    for (cod, sigla, nom_ent, anio), grp in validos.groupby(
        ["codigo_entidad", "sigla_entidad", "nombre_entidad_corto", "anio"]
    ):
        por_prov = (
            grp.groupby("id_proveedor_limpio", as_index=False)
            .agg(
                nombre_proveedor=("nombre_proveedor_limpio", "first"),
                n_contratos=("id_contrato", "count"),
                valor_proveedor_cop=("valor_del_contrato", "sum"),
            )
            .sort_values("valor_proveedor_cop", ascending=False)
        )
        total_anual = float(por_prov["valor_proveedor_cop"].sum())
        cuotas = por_prov["valor_proveedor_cop"] / max(total_anual, 1.0)

        cr1 = float(100.0 * cuotas.iloc[0]) if len(cuotas) > 0 else 0.0
        cr5 = float(100.0 * cuotas.head(5).sum())
        hhi = float((cuotas.pow(2).sum()) * 10_000.0)
        top_prov = str(por_prov.iloc[0]["nombre_proveedor"]) if len(por_prov) > 0 else "SIN PROVEEDOR"
        top_val = float(por_prov.iloc[0]["valor_proveedor_cop"]) if len(por_prov) > 0 else 0.0

        filas.append(
            {
                "codigo_entidad": str(cod),
                "sigla_entidad": sigla,
                "nombre_entidad_corto": nom_ent,
                "anio": int(anio),
                "n_proveedores_unicos": int(len(por_prov)),
                "valor_ejecutado_cop": total_anual,
                "cr1_pct": round(cr1, 2),
                "cr5_pct": round(cr5, 2),
                "hhi_proveedores": round(hhi, 1),
                "categoria_hhi": clasificar_categoria_hhi(hhi),
                "top1_proveedor": top_prov,
                "top1_valor_cop": top_val,
            }
        )

    return pd.DataFrame(filas).sort_values(["sigla_entidad", "anio"]).reset_index(drop=True)


def calcular_top_proveedores_entidad(df_cont: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Obtiene el Top N de contratistas adjudicados por entidad en el periodo 2022–2025."""
    validos = df_cont[df_cont["es_contrato_valido_con_cuantia"]].copy()
    tablas = []

    for (cod, sigla, nom_ent), grp in validos.groupby(
        ["codigo_entidad", "sigla_entidad", "nombre_entidad_corto"]
    ):
        total_entidad = float(grp["valor_del_contrato"].sum())
        agrupado = (
            grp.groupby("id_proveedor_limpio", as_index=False)
            .agg(
                nombre_proveedor=("nombre_proveedor_limpio", "first"),
                n_contratos=("id_contrato", "count"),
                anios_activos=("anio", "nunique"),
                valor_total_cop=("valor_del_contrato", "sum"),
                modalidad_frecuente=(
                    "modalidad_homologada",
                    lambda s: s.mode().iloc[0] if not s.mode().empty else "Otra modalidad",
                ),
            )
            .sort_values("valor_total_cop", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        agrupado["ranking_entidad"] = agrupado.index + 1
        agrupado["participacion_entidad_pct"] = (
            100.0 * agrupado["valor_total_cop"] / max(total_entidad, 1.0)
        ).round(2)
        agrupado["codigo_entidad"] = str(cod)
        agrupado["sigla_entidad"] = sigla
        agrupado["nombre_entidad_corto"] = nom_ent
        tablas.append(agrupado)

    cols = [
        "codigo_entidad",
        "sigla_entidad",
        "nombre_entidad_corto",
        "ranking_entidad",
        "id_proveedor_limpio",
        "nombre_proveedor",
        "n_contratos",
        "anios_activos",
        "valor_total_cop",
        "participacion_entidad_pct",
        "modalidad_frecuente",
    ]
    return pd.concat(tablas, ignore_index=True)[cols]


# %%
def calcular_modalidades_entidad_anio(
    df_paa: pd.DataFrame,
    df_cont: pd.DataFrame,
) -> pd.DataFrame:
    """Compara la composición planeada vs. ejecutada por macro-modalidad, entidad y año."""
    paa_base = df_paa[~df_paa["es_posible_duplicado_atipico"]].copy()
    cont_base = df_cont[df_cont["es_contrato_valido_con_cuantia"]].copy()

    claves = ["codigo_entidad", "sigla_entidad", "nombre_entidad_corto", "anio", "modalidad_homologada"]
    res_paa = (
        paa_base.groupby(claves, as_index=False)
        .agg(
            items_paa=("id", "count"),
            valor_paa_ajustado_cop=("valor_esperado_de_presupuesto", "sum"),
        )
    )
    res_cont = (
        cont_base.groupby(claves, as_index=False)
        .agg(
            n_contratos_con_cuantia=("id_contrato", "count"),
            valor_ejecutado_cop=("valor_del_contrato", "sum"),
            monto_promedio_contrato_cop=("valor_del_contrato", "mean"),
            monto_mediano_contrato_cop=("valor_del_contrato", "median"),
        )
    )

    tabla = res_paa.merge(res_cont, on=claves, how="outer")
    for col in [
        "items_paa",
        "valor_paa_ajustado_cop",
        "n_contratos_con_cuantia",
        "valor_ejecutado_cop",
        "monto_promedio_contrato_cop",
        "monto_mediano_contrato_cop",
    ]:
        tabla[col] = tabla[col].fillna(0.0)

    tot_paa = tabla.groupby(["codigo_entidad", "anio"])["valor_paa_ajustado_cop"].transform("sum")
    tot_cont_val = tabla.groupby(["codigo_entidad", "anio"])["valor_ejecutado_cop"].transform("sum")
    tot_cont_n = tabla.groupby(["codigo_entidad", "anio"])["n_contratos_con_cuantia"].transform("sum")

    tabla["participacion_paa_pct"] = np.where(
        tot_paa > 0, (100.0 * tabla["valor_paa_ajustado_cop"] / tot_paa).round(2), 0.0
    )
    tabla["participacion_ejec_valor_pct"] = np.where(
        tot_cont_val > 0, (100.0 * tabla["valor_ejecutado_cop"] / tot_cont_val).round(2), 0.0
    )
    tabla["participacion_ejec_num_pct"] = np.where(
        tot_cont_n > 0, (100.0 * tabla["n_contratos_con_cuantia"] / tot_cont_n).round(2), 0.0
    )
    return tabla.sort_values(["sigla_entidad", "anio", "valor_ejecutado_cop"], ascending=[True, True, False]).reset_index(
        drop=True
    )


def calcular_brechas_segmento_unspsc(df_cruce_seg: pd.DataFrame) -> pd.DataFrame:
    """Enriquece el cruce por Segmento UNSPSC con cuotas, contribuciones de Duncan y deflactación IPC 2025."""
    seg = df_cruce_seg.copy()
    seg["codigo_entidad"] = seg["codigo_entidad"].astype(str)
    seg["anio"] = seg["anio"].astype(int)

    tot_paa = seg.groupby(["codigo_entidad", "anio"])["valor_paa_vigencia"].transform("sum")
    tot_ejec = seg.groupby(["codigo_entidad", "anio"])["valor_ejecutado"].transform("sum")

    w_paa = np.where(tot_paa > 0, seg["valor_paa_vigencia"] / tot_paa, 0.0)
    w_ejec = np.where(tot_ejec > 0, seg["valor_ejecutado"] / tot_ejec, 0.0)

    seg["participacion_paa_pct"] = 100.0 * w_paa
    seg["participacion_ejecutado_pct"] = 100.0 * w_ejec
    seg["brecha_participacion_pp"] = (
        seg["participacion_ejecutado_pct"] - seg["participacion_paa_pct"]
    ).round(3)

    # Contribución aditiva al Índice de Disimilitud de Duncan: c_ist = 0.5 * |w_E - w_P|
    ambos_positivos = (tot_paa > 0) & (tot_ejec > 0)
    seg["contribucion_duncan"] = np.where(ambos_positivos, 0.5 * np.abs(w_ejec - w_paa), np.nan)
    seg["contribucion_duncan_pp"] = (100.0 * seg["contribucion_duncan"]).round(3)

    # Deflactación a pesos constantes de 2025 (IPC oficial DANE, base 2025 = 1,000000)
    seg["factor_ipc_2025"] = seg["anio"].map(FACTOR_DEFLACTOR_IPC_2025).fillna(1.0)
    seg["valor_paa_real_2025_cop"] = seg["valor_paa_vigencia"] * seg["factor_ipc_2025"]
    seg["valor_ejecutado_real_2025_cop"] = seg["valor_ejecutado"] * seg["factor_ipc_2025"]
    seg["brecha_real_2025_cop"] = (
        seg["valor_ejecutado_real_2025_cop"] - seg["valor_paa_real_2025_cop"]
    )
    return seg.sort_values(["sigla_entidad", "anio", "codigo_segmento"]).reset_index(drop=True)


def calcular_indice_duncan_unspsc(df_brechas_seg: pd.DataFrame) -> pd.DataFrame:
    """Calcula el Índice de Disimilitud Estructural de Duncan (D_it en [0, 1]) por Entidad × Año.

    D_it = 0.5 * sum_s |w_ist^E - w_ist^P| mide la fracción exacta del gasto ejecutado (0% a 100%)
    que tendría que reasignarse entre segmentos UNSPSC para replicar la composición planeada en el PAA.
    """
    seg = df_brechas_seg.copy()
    seg["codigo_entidad"] = seg["codigo_entidad"].astype(str)
    seg["anio"] = seg["anio"].astype(int)

    filas = []
    for (cod, sigla, anio), grp in seg.groupby(["codigo_entidad", "sigla_entidad", "anio"]):
        tot_p = float(grp["valor_paa_vigencia"].sum())
        tot_e = float(grp["valor_ejecutado"].sum())
        if tot_p <= 0 or tot_e <= 0:
            filas.append(
                {
                    "codigo_entidad": str(cod),
                    "sigla_entidad": str(sigla),
                    "anio": int(anio),
                    "indice_duncan": np.nan,
                    "duncan_pct": np.nan,
                    "codigo_segmento_mayor_desvio": "",
                    "segmento_mayor_desvio": "Sin datos comparables",
                    "contribucion_max_duncan_pp": np.nan,
                }
            )
            continue

        w_p = grp["valor_paa_vigencia"] / tot_p
        w_e = grp["valor_ejecutado"] / tot_e
        contrib = 0.5 * np.abs(w_e - w_p)
        d_it = float(contrib.sum())
        idx_max = contrib.idxmax()
        fila_max = grp.loc[idx_max]
        etiqueta_max = f"{fila_max['codigo_segmento']} - {str(fila_max['nombre_segmento'])[:48]}"

        filas.append(
            {
                "codigo_entidad": str(cod),
                "sigla_entidad": str(sigla),
                "anio": int(anio),
                "indice_duncan": round(d_it, 6),
                "duncan_pct": round(100.0 * d_it, 2),
                "codigo_segmento_mayor_desvio": str(fila_max["codigo_segmento"]),
                "segmento_mayor_desvio": etiqueta_max,
                "contribucion_max_duncan_pp": round(100.0 * float(contrib.loc[idx_max]), 2),
            }
        )

    return pd.DataFrame(filas).sort_values(["sigla_entidad", "anio"]).reset_index(drop=True)


def calcular_resumen_entidad_anio(
    df_cruce_anual: pd.DataFrame,
    df_cont: pd.DataFrame,
    df_conc: pd.DataFrame,
    df_duncan: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Consolida KPIs base y mejoras metodológicas Rubro 5 (IPC DANE 2025 + Duncan) por Entidad × Año."""
    validos = df_cont[df_cont["es_contrato_valido_con_cuantia"]].copy()
    directa = (
        validos.groupby(["codigo_entidad", "anio"], as_index=False)
        .agg(
            n_contratos_directa=("es_contratacion_directa", "sum"),
            valor_directa_cop=(
                "valor_del_contrato",
                lambda s: float(s[validos.loc[s.index, "es_contratacion_directa"]].sum()),
            ),
            monto_promedio_contrato_cop=("valor_del_contrato", "mean"),
            monto_mediano_contrato_cop=("valor_del_contrato", "median"),
        )
    )

    base = df_cruce_anual.copy()
    base["codigo_entidad"] = base["codigo_entidad"].astype(str)
    base["anio"] = base["anio"].astype(int)
    resumen = base.merge(directa, on=["codigo_entidad", "anio"], how="left").merge(
        df_conc[
            [
                "codigo_entidad",
                "anio",
                "cr1_pct",
                "cr5_pct",
                "hhi_proveedores",
                "categoria_hhi",
                "top1_proveedor",
            ]
        ],
        on=["codigo_entidad", "anio"],
        how="left",
    )

    resumen["pct_valor_contratacion_directa"] = np.where(
        resumen["valor_ejecutado"] > 0,
        (100.0 * resumen["valor_directa_cop"] / resumen["valor_ejecutado"]).round(2),
        0.0,
    )
    resumen["pct_num_contratacion_directa"] = np.where(
        resumen["n_contratos_con_cuantia"] > 0,
        (100.0 * resumen["n_contratos_directa"] / resumen["n_contratos_con_cuantia"]).round(2),
        0.0,
    )
    resumen["brecha_ajustada_cop"] = (
        resumen["valor_ejecutado"] - resumen["valor_paa_vigencia_sin_dup_atipico"]
    )

    # Mejora IA #1: Deflactación intertemporal a precios constantes de 2025 (IPC oficial DANE)
    resumen["inflacion_anual_dane_pct"] = (
        100.0 * resumen["anio"].map(IPC_INFLACION_ANUAL_DANE).fillna(0.0)
    ).round(2)
    resumen["factor_ipc_2025"] = resumen["anio"].map(FACTOR_DEFLACTOR_IPC_2025).fillna(1.0)
    resumen["valor_paa_vigencia_real_2025_cop"] = (
        resumen["valor_paa_vigencia"] * resumen["factor_ipc_2025"]
    )
    resumen["valor_paa_ajustado_real_2025_cop"] = (
        resumen["valor_paa_vigencia_sin_dup_atipico"] * resumen["factor_ipc_2025"]
    )
    resumen["valor_ejecutado_real_2025_cop"] = (
        resumen["valor_ejecutado"] * resumen["factor_ipc_2025"]
    )
    resumen["brecha_ajustada_real_2025_cop"] = (
        resumen["valor_ejecutado_real_2025_cop"] - resumen["valor_paa_ajustado_real_2025_cop"]
    )

    # Mejora IA #2: Índice de Disimilitud Estructural de Duncan sobre segmentos UNSPSC
    if df_duncan is not None and not df_duncan.empty:
        resumen = resumen.merge(
            df_duncan[
                [
                    "codigo_entidad",
                    "anio",
                    "indice_duncan",
                    "duncan_pct",
                    "segmento_mayor_desvio",
                    "contribucion_max_duncan_pp",
                ]
            ],
            on=["codigo_entidad", "anio"],
            how="left",
        )

    return resumen.sort_values(["sigla_entidad", "anio"]).reset_index(drop=True)


def calcular_comparativa_rubro5_antes_despues(df_resumen: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla Antes (nominal) vs. Después (IPC 2025 + Duncan) por entidad y muestra total."""
    filas = []
    grupos: list[tuple[str, str, str, str, pd.DataFrame]] = []
    for (cod, sigla, nom_ent), grp in df_resumen.groupby(
        ["codigo_entidad", "sigla_entidad", "nombre_entidad_corto"]
    ):
        grupos.append(("Entidad", str(cod), str(sigla), str(nom_ent), grp.sort_values("anio")))
    grupos.append(
        (
            "Total 6 entidades",
            "TODAS",
            "TOTAL_MUESTRA",
            "Total muestra 6 entidades (2022–2025)",
            df_resumen.copy(),
        )
    )

    for alcance, cod, sigla, nom_ent, sub in grupos:
        paa_nom_mm = float(sub["valor_paa_vigencia_sin_dup_atipico"].sum()) / 1e9
        ejec_nom_mm = float(sub["valor_ejecutado"].sum()) / 1e9
        brecha_nom_mm = ejec_nom_mm - paa_nom_mm
        tasa_nom_pct = 100.0 * ejec_nom_mm / paa_nom_mm if paa_nom_mm > 0 else np.nan

        paa_real_mm = float(sub["valor_paa_ajustado_real_2025_cop"].sum()) / 1e9
        ejec_real_mm = float(sub["valor_ejecutado_real_2025_cop"].sum()) / 1e9
        brecha_real_mm = ejec_real_mm - paa_real_mm
        tasa_real_pct = 100.0 * ejec_real_mm / paa_real_mm if paa_real_mm > 0 else np.nan

        ejec_2022_nom = float(sub.loc[sub["anio"] == 2022, "valor_ejecutado"].sum())
        ejec_2025_nom = float(sub.loc[sub["anio"] == 2025, "valor_ejecutado"].sum())
        ejec_2022_real = float(sub.loc[sub["anio"] == 2022, "valor_ejecutado_real_2025_cop"].sum())
        ejec_2025_real = float(sub.loc[sub["anio"] == 2025, "valor_ejecutado_real_2025_cop"].sum())

        crec_nom = (
            100.0 * (ejec_2025_nom / ejec_2022_nom - 1.0) if ejec_2022_nom > 0 else np.nan
        )
        crec_real = (
            100.0 * (ejec_2025_real / ejec_2022_real - 1.0) if ejec_2022_real > 0 else np.nan
        )

        duncan_prom = (
            float(sub["duncan_pct"].mean())
            if "duncan_pct" in sub.columns and sub["duncan_pct"].notna().any()
            else np.nan
        )
        duncan_max = (
            float(sub["duncan_pct"].max())
            if "duncan_pct" in sub.columns and sub["duncan_pct"].notna().any()
            else np.nan
        )
        seg_moda = (
            str(sub["segmento_mayor_desvio"].mode().iloc[0])
            if "segmento_mayor_desvio" in sub.columns and not sub["segmento_mayor_desvio"].dropna().empty
            else "—"
        )

        filas.append(
            {
                "alcance": alcance,
                "codigo_entidad": cod,
                "sigla_entidad": sigla,
                "nombre_entidad_corto": nom_ent,
                "paa_ajustado_nominal_mm": round(paa_nom_mm, 2),
                "ejecutado_nominal_mm": round(ejec_nom_mm, 2),
                "brecha_nominal_mm": round(brecha_nom_mm, 2),
                "tasa_ejecucion_nominal_pct": round(tasa_nom_pct, 2),
                "crecimiento_ejec_nominal_2022_2025_pct": round(crec_nom, 2) if pd.notna(crec_nom) else np.nan,
                "paa_ajustado_real_2025_mm": round(paa_real_mm, 2),
                "ejecutado_real_2025_mm": round(ejec_real_mm, 2),
                "brecha_real_2025_mm": round(brecha_real_mm, 2),
                "cambio_brecha_real_vs_nominal_mm": round(brecha_real_mm - brecha_nom_mm, 2),
                "tasa_ejecucion_real_acumulada_pct": round(tasa_real_pct, 2),
                "crecimiento_ejec_real_2022_2025_pct": round(crec_real, 2) if pd.notna(crec_real) else np.nan,
                "sesgo_inflacionario_crecimiento_pp": (
                    round(crec_nom - crec_real, 2) if pd.notna(crec_nom) and pd.notna(crec_real) else np.nan
                ),
                "duncan_promedio_pct": round(duncan_prom, 2) if pd.notna(duncan_prom) else np.nan,
                "duncan_max_pct": round(duncan_max, 2) if pd.notna(duncan_max) else np.nan,
                "segmento_desvio_frecuente": seg_moda,
            }
        )

    return pd.DataFrame(filas)


def construir_registro_ia_rubro5(ruta_md: Path = ARCHIVO_RUBRO5_MD) -> dict[str, Any]:
    """Extrae el prompt literal, la respuesta íntegra de la IA y la evaluación crítica desde docs/rubro5_uso_ia.md."""
    if not ruta_md.exists():
        return {}
    texto = ruta_md.read_text(encoding="utf-8")

    match_prompt = re.search(r"## 1\. Prompt.*?\n```text\n(.*?)\n```", texto, flags=re.DOTALL)
    match_resp = re.search(
        r"## 2\. Respuesta Completa de la IA.*?\n\n(.*?)\n---\n\n## 3\.",
        texto,
        flags=re.DOTALL,
    )
    match_mas_alla = re.search(
        r"## 3\. Qué Va Más Allá.*?\n\n(.*?)\n---\n\n## 4\.",
        texto,
        flags=re.DOTALL,
    )
    match_eval = re.search(
        r"## 4\. Evaluación Crítica del Equipo.*?\n\n(.*)$",
        texto,
        flags=re.DOTALL,
    )

    return {
        "fuente_documento": "docs/rubro5_uso_ia.md",
        "prompt_enviado": match_prompt.group(1).strip() if match_prompt else "",
        "respuesta_ia_completa": match_resp.group(1).strip() if match_resp else "",
        "mas_alla_profesores": match_mas_alla.group(1).strip() if match_mas_alla else "",
        "evaluacion_critica_equipo": match_eval.group(1).strip() if match_eval else "",
        "ipc_inflacion_anual_dane": {str(k): v for k, v in IPC_INFLACION_ANUAL_DANE.items()},
        "factor_deflactor_ipc_2025": {str(k): v for k, v in FACTOR_DEFLACTOR_IPC_2025.items()},
        "mejoras_implementadas": [
            "1. Deflactación intertemporal a precios constantes con IPC oficial DANE (base 2025 = 100)",
            "2. Índice de Disimilitud Estructural de Duncan (D_it) sobre composición de Segmentos UNSPSC",
        ],
        "mejoras_descartadas": [
            "4. Emparejamiento micro bipartito 1:1 PAA–Contrato (descartada por bolsas pluripersonales 1:M y consolidación por lotes M:1 que fabricarían falsos no ejecutados)",
            "3. Concentración estacional intra-anual Kullback-Leibler y RIC-Q4 (descartada por ausencia de cronograma mensual de desembolsos en el PAA y estacionalidad operativa legítima en enero)",
        ],
    }


def calcular_distribucion_franjas_cuantia(df_cont: pd.DataFrame) -> pd.DataFrame:
    """Construye la distribución de cuantías en 7 franjas (global 'TODAS' y por entidad)."""
    base = df_cont[~df_cont["es_estado_invalido"]].copy()
    pares = base["valor_del_contrato"].map(asignar_franja_cuantia)
    base["orden_franja"] = [p[0] for p in pares]
    base["franja_cuantia"] = [p[1] for p in pares]

    catalogo_franjas = pd.DataFrame(
        FRANJAS_CUANTIA_DEFINICION,
        columns=["orden_franja", "franja_cuantia", "regla_cop", "tratamiento_limpieza"],
    )

    salidas = []
    grupos = [("TODAS", base)] + list(base.groupby("sigla_entidad"))
    for etiqueta_entidad, sub in grupos:
        n_tot = max(len(sub), 1)
        val_tot = max(float(sub["valor_del_contrato"].sum()), 1.0)
        agg = (
            sub.groupby(["orden_franja", "franja_cuantia"], as_index=False)
            .agg(
                n_contratos=("id_contrato", "count"),
                valor_total_cop=("valor_del_contrato", "sum"),
                modalidad_predominante=(
                    "modalidad_homologada",
                    lambda s: s.mode().iloc[0] if not s.mode().empty else "—",
                ),
            )
        )
        completo = catalogo_franjas.merge(agg, on=["orden_franja", "franja_cuantia"], how="left")
        completo["n_contratos"] = completo["n_contratos"].fillna(0).astype(int)
        completo["valor_total_cop"] = completo["valor_total_cop"].fillna(0.0)
        completo["modalidad_predominante"] = completo["modalidad_predominante"].fillna("Sin registros")
        completo["pct_contratos"] = (100.0 * completo["n_contratos"] / n_tot).round(2)
        completo["pct_valor"] = (100.0 * completo["valor_total_cop"] / val_tot).round(2)
        completo["sigla_entidad"] = etiqueta_entidad
        salidas.append(completo)

    cols = [
        "sigla_entidad",
        "orden_franja",
        "franja_cuantia",
        "regla_cop",
        "tratamiento_limpieza",
        "n_contratos",
        "pct_contratos",
        "valor_total_cop",
        "pct_valor",
        "modalidad_predominante",
    ]
    return pd.concat(salidas, ignore_index=True)[cols]


# %%
def escribir_readme_dashboard_data(directorio: Path, conteos: dict[str, int]) -> None:
    """Documenta el linaje, grano y esquema de los CSVs en data/dashboard_data/README.md."""
    lineas = [
        "# Contratos de Datos para Visualización (`data/dashboard_data/README.md`)",
        "",
        "Archivos generados automáticamente por `src/indicadores.py` a partir de `data/processed/`. Tanto `A_contraluz_tutorial.ipynb` como `app_streamlit.py` leen exclusivamente estos archivos ya validados.",
        "",
        "## Cómo regenerar",
        "```powershell",
        "python -m src.limpieza_cruce",
        "python -m src.indicadores",
        "```",
        "",
        "## Inventario y Proveniencia",
        "",
        "| Archivo | Filas actuales | Grano (qué representa una fila) | Función generadora (`src/indicadores.py`) |",
        "|---|---:|---|---|",
        f"| `resumen_entidad_anio.csv` | `{conteos['resumen_entidad_anio.csv']}` | 1 entidad × 1 año (`2022–2025`) con KPIs nominales, reales IPC 2025 e Índice de Duncan | `calcular_resumen_entidad_anio` |",
        f"| `modalidades_entidad_anio.csv` | `{conteos['modalidades_entidad_anio.csv']}` | 1 entidad × 1 año × 1 macro-modalidad | `calcular_modalidades_entidad_anio` |",
        f"| `concentracion_proveedores.csv` | `{conteos['concentracion_proveedores.csv']}` | 1 entidad × 1 año (`CR1`, `CR5`, `HHI`) | `calcular_concentracion_proveedores` |",
        f"| `top_proveedores_entidad.csv` | `{conteos['top_proveedores_entidad.csv']}` | Top 10 proveedores por entidad (`2022–2025`) | `calcular_top_proveedores_entidad` |",
        f"| `brechas_segmento_unspsc.csv` | `{conteos['brechas_segmento_unspsc.csv']}` | 1 entidad × 1 año × 1 segmento UNSPSC (`2d`) con contribución a Duncan y valores reales 2025 | `calcular_brechas_segmento_unspsc` |",
        f"| `distribucion_franjas_cuantia.csv` | `{conteos['distribucion_franjas_cuantia.csv']}` | 1 alcance (`TODAS` o entidad) × 1 franja de valor (`7` franjas) | `calcular_distribucion_franjas_cuantia` |",
        f"| `rubro5_antes_despues.csv` | `{conteos['rubro5_antes_despues.csv']}` | 1 entidad (más `TOTAL_MUESTRA`) contrastando Antes (nominal) vs. Después (IPC 2025 + Duncan) | `calcular_comparativa_rubro5_antes_despues` |",
        "| `rubro5_registro_ia.json` | `JSON` | Prompt literal, respuesta completa de la IA y evaluación crítica del Rubro 5 | `construir_registro_ia_rubro5` |",
    ]
    (directorio / ARCHIVO_DASH_README.name).write_text("\n".join(lineas) + "\n", encoding="utf-8")


def ejecutar_calculo_indicadores(
    directorio_entrada: Path = PROCESSED_DIR,
    directorio_salida: Path = DASHBOARD_DATA_DIR,
) -> dict[str, pd.DataFrame]:
    """Lee data/processed/, calcula todos los indicadores R5 y Rubro 5 IA y escribe data/dashboard_data/."""
    df_paa = pd.read_csv(
        directorio_entrada / ARCHIVO_PAA_LIMPIO.name,
        dtype={"codigo_entidad": str, "codigo_segmento": str, "codigo_familia": str, "codigo_clase": str},
        low_memory=False,
    )
    df_cont = pd.read_csv(
        directorio_entrada / ARCHIVO_CONTRATOS_LIMPIO.name,
        dtype={
            "codigo_entidad": str,
            "codigo_segmento": str,
            "codigo_familia": str,
            "codigo_clase": str,
            "id_proveedor_limpio": str,
        },
        low_memory=False,
    )
    df_anual = pd.read_csv(
        directorio_entrada / ARCHIVO_CRUCE_ENTIDAD_ANIO.name,
        dtype={"codigo_entidad": str},
    )
    df_seg = pd.read_csv(
        directorio_entrada / ARCHIVO_CRUCE_SEGMENTO.name,
        dtype={"codigo_entidad": str, "codigo_segmento": str},
    )

    df_conc = calcular_concentracion_proveedores(df_cont)
    df_top_prov = calcular_top_proveedores_entidad(df_cont, top_n=10)
    df_mod = calcular_modalidades_entidad_anio(df_paa, df_cont)
    df_brechas_seg = calcular_brechas_segmento_unspsc(df_seg)
    df_duncan = calcular_indice_duncan_unspsc(df_brechas_seg)
    df_resumen = calcular_resumen_entidad_anio(df_anual, df_cont, df_conc, df_duncan=df_duncan)
    df_franjas = calcular_distribucion_franjas_cuantia(df_cont)
    df_rubro5 = calcular_comparativa_rubro5_antes_despues(df_resumen)
    registro_ia = construir_registro_ia_rubro5()

    directorio_salida.mkdir(parents=True, exist_ok=True)
    salidas = {
        ARCHIVO_DASH_RESUMEN_ANUAL.name: df_resumen,
        ARCHIVO_DASH_MODALIDADES.name: df_mod,
        ARCHIVO_DASH_CONCENTRACION.name: df_conc,
        ARCHIVO_DASH_TOP_PROVEEDORES.name: df_top_prov,
        ARCHIVO_DASH_SEGMENTOS_UNSPSC.name: df_brechas_seg,
        ARCHIVO_DASH_FRANJAS_CUANTIA.name: df_franjas,
        ARCHIVO_DASH_RUBRO5_COMPARATIVA.name: df_rubro5,
    }
    conteos = {}
    for nombre_archivo, tabla in salidas.items():
        tabla.to_csv(directorio_salida / nombre_archivo, index=False, encoding="utf-8")
        conteos[nombre_archivo] = int(len(tabla))

    if registro_ia:
        (directorio_salida / ARCHIVO_DASH_RUBRO5_JSON.name).write_text(
            json.dumps(registro_ia, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    escribir_readme_dashboard_data(directorio_salida, conteos)
    return {
        "resumen_anual": df_resumen,
        "modalidades": df_mod,
        "concentracion": df_conc,
        "top_proveedores": df_top_prov,
        "segmentos_unspsc": df_brechas_seg,
        "franjas_cuantia": df_franjas,
        "rubro5_antes_despues": df_rubro5,
    }


def main() -> None:
    tablas = ejecutar_calculo_indicadores()
    print("=== Indicadores R5 + Mejoras IA (Rubro 5) generados en data/dashboard_data/ ===")
    for nombre, df in tablas.items():
        print(f"  - {nombre}: {len(df):,} filas")


if __name__ == "__main__":
    main()
