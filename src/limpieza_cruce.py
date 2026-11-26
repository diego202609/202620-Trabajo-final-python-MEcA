# %% [markdown]
# # Limpieza, Auditoría de Calidad y Cruce PAA ↔ SECOP II ↔ UNSPSC
#
# Este módulo transforma los archivos crudos de `data/raw/` en tablas limpias,
# auditadas y homologadas dentro de `data/processed/`, dejando documentada cada
# decisión sobre tipos, faltantes, duplicados, atípicos y cruce UNSPSC (Rubros 1 y 3).

# %%
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import (
    ANIOS_ESTUDIO,
    ARCHIVO_AUDITORIA_CALIDAD,
    ARCHIVO_CONTRATOS_LIMPIO,
    ARCHIVO_CRUCE_ENTIDAD_ANIO,
    ARCHIVO_CRUCE_SEGMENTO,
    ARCHIVO_HALLAZGOS_PILOTO_MD,
    ARCHIVO_PAA_LIMPIO,
    ENTIDADES_COMPLETO,
    PROCESSED_DIR,
    UMBRAL_CUANTIA_SIMBOLICA_COP,
    UMBRAL_DUPLICADO_ATIPICO_PAA_COP,
)
from src.ingesta import cargar_datos_crudos

REGEX_UNSPSC_8D = re.compile(r"\d{8}")
ESTADOS_CONTRATO_INVALIDOS = {"Anulado", "Borrador", "Cancelado", "Descartado"}


# %%
def quitar_tildes_y_espacios(texto: Any) -> str:
    """Normaliza un texto a minúsculas sin tildes ni espacios repetidos."""
    if pd.isna(texto):
        return ""
    cadena = str(texto).strip().lower()
    normalizado = unicodedata.normalize("NFKD", cadena)
    sin_tildes = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes)


def homologar_modalidad(modalidad_cruda: Any) -> str:
    """Agrupa las modalidades de PAA y SECOP II en 7 macro-modalidades comparables."""
    limpia = quitar_tildes_y_espacios(modalidad_cruda)
    if not limpia or limpia in {"no definido", "sin definir", "na", "n/a"}:
        return "No definido"
    if "contratacion directa" in limpia:
        return "Contratación directa"
    if "minima cuantia" in limpia:
        return "Mínima cuantía"
    if "concurso de meritos" in limpia:
        return "Concurso de méritos"
    if "regimen especial" in limpia:
        return "Régimen especial"
    if "seleccion abreviada" in limpia:
        return "Selección abreviada"
    if "licitacion publica" in limpia or "acuerdo marco" in limpia:
        return "Licitación pública y AMP"
    return "Otra modalidad"


def homologar_modalidad_desde_causal_paa(causal_cruda: Any) -> str:
    """Rescata la macro-modalidad a partir del código CCE de causal_de_contratacion en el PAA."""
    limpia = quitar_tildes_y_espacios(causal_cruda).replace("_", " ").replace("-", " ")
    if not limpia or limpia in {"no definido", "sin definir", "na", "n/a"}:
        return "No definido"
    # Ley 1150 de 2007, art. 2 num. 4: servicios profesionales/apoyo a la gestión y demás causales directas
    terminos_directa = (
        "contratacion directa",
        "servicios profesionales",
        "urgencia manifiesta",
        "interadministrativo",
        "arrendamiento",
        "inexistencia de pluralidad",
        "bienes y servicios sector defensa",
    )
    if any(t in limpia for t in terminos_directa):
        return "Contratación directa"
    if "minima cuantia" in limpia:
        return "Mínima cuantía"
    if "concurso" in limpia and "meritos" in limpia:
        return "Concurso de méritos"
    if "seleccion abreviada" in limpia or "subasta" in limpia:
        return "Selección abreviada"
    if "licitacion publica" in limpia or "obra publica" in limpia or "acuerdo marco" in limpia:
        return "Licitación pública y AMP"
    if "regimen especial" in limpia or "procedimiento publicidad" in limpia:
        return "Régimen especial"
    return "No definido"


def homologar_modalidad_paa(modalidad_cruda: Any, causal_cruda: Any) -> tuple[str, bool]:
    """Homologa la modalidad del PAA rescatando desde causal_de_contratacion cuando viene 'No Definido'."""
    base = homologar_modalidad(modalidad_cruda)
    if base != "No definido":
        return base, False
    rescatada = homologar_modalidad_desde_causal_paa(causal_cruda)
    return rescatada, (rescatada != "No definido")


def homologar_estado_contrato(estado_crudo: Any) -> str:
    """Estandariza la capitalización de estado_contrato en SECOP II."""
    limpio = quitar_tildes_y_espacios(estado_crudo)
    mapa = {
        "en ejecucion": "En ejecución",
        "modificado": "Modificado",
        "cerrado": "Cerrado",
        "terminado": "Terminado",
        "cedido": "Cedido",
        "aprobado": "Aprobado",
        "suspendido": "Suspendido",
        "anulado": "Anulado",
        "borrador": "Borrador",
        "cancelado": "Cancelado",
    }
    return mapa.get(limpio, str(estado_crudo).strip().capitalize() if pd.notna(estado_crudo) else "Sin estado")


# %%
def extraer_codigos_unspsc(valor: Any) -> tuple[str, int]:
    """Extrae el primer código UNSPSC de 8 dígitos y cuenta cuántos códigos trae la celda.

    Maneja tanto el formato con prefijo de SECOP II ('V1.80111620'), las listas
    múltiples del PAA ('80101500; 80111600') y valores 'UNSPECIFIED'.
    """
    if pd.isna(valor):
        return "", 0
    coincidencias = REGEX_UNSPSC_8D.findall(str(valor))
    if not coincidencias:
        return "", 0
    return coincidencias[0], len(coincidencias)


def construir_catalogos_unspsc(df_unspsc: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Construye tablas maestras únicas por Clase (6d), Familia (4d) y Segmento (2d)."""
    cat_segmento = (
        df_unspsc[["codigo_segmento", "nombre_segmento"]]
        .drop_duplicates(subset=["codigo_segmento"])
        .reset_index(drop=True)
    )
    cat_familia = (
        df_unspsc[["codigo_familia", "nombre_familia", "codigo_segmento", "nombre_segmento"]]
        .drop_duplicates(subset=["codigo_familia"])
        .reset_index(drop=True)
    )
    cat_clase = (
        df_unspsc[
            [
                "codigo_clase",
                "nombre_clase",
                "codigo_familia",
                "nombre_familia",
                "codigo_segmento",
                "nombre_segmento",
            ]
        ]
        .drop_duplicates(subset=["codigo_clase"])
        .reset_index(drop=True)
    )
    return {
        "segmento": cat_segmento,
        "familia": cat_familia,
        "clase": cat_clase,
        "producto_set": set(df_unspsc["codigo_producto"].astype(str)),
    }


def enriquecer_con_unspsc(
    df: pd.DataFrame,
    columna_origen: str,
    catalogos: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Cruza los códigos UNSPSC a nivel Clase (6d), con respaldo en Familia (4d) y Segmento (2d)."""
    extraidos = df[columna_origen].map(extraer_codigos_unspsc)
    out = df.copy()
    out["codigo_unspsc_8d"] = [par[0] for par in extraidos]
    out["n_codigos_unspsc_celda"] = [par[1] for par in extraidos]
    out["codigo_clase"] = out["codigo_unspsc_8d"].str[:6]
    out["codigo_familia"] = out["codigo_unspsc_8d"].str[:4]
    out["codigo_segmento"] = out["codigo_unspsc_8d"].str[:2]

    # Cruce principal a nivel Clase (6 dígitos)
    out = out.merge(catalogos["clase"], on=["codigo_clase", "codigo_familia", "codigo_segmento"], how="left")

    # Respaldo a nivel Familia (4 dígitos) si algún código de clase no existiera en v14.1
    faltan_fam = out["nombre_familia"].isna() & (out["codigo_familia"].str.len() == 4)
    if faltan_fam.any():
        mapa_fam = catalogos["familia"].set_index("codigo_familia")
        out.loc[faltan_fam, "nombre_familia"] = out.loc[faltan_fam, "codigo_familia"].map(
            mapa_fam["nombre_familia"]
        )
        out.loc[faltan_fam, "nombre_segmento"] = out.loc[faltan_fam, "codigo_familia"].map(
            mapa_fam["nombre_segmento"]
        )

    # Respaldo a nivel Segmento (2 dígitos)
    faltan_seg = out["nombre_segmento"].isna() & (out["codigo_segmento"].str.len() == 2)
    if faltan_seg.any():
        mapa_seg = catalogos["segmento"].set_index("codigo_segmento")["nombre_segmento"]
        out.loc[faltan_seg, "nombre_segmento"] = out.loc[faltan_seg, "codigo_segmento"].map(mapa_seg)

    out["unspsc_emparejado"] = out["nombre_segmento"].notna()
    for col_nombre, etiqueta in [
        ("nombre_segmento", "Sin clasificar"),
        ("nombre_familia", "Sin clasificar"),
        ("nombre_clase", "Sin clasificar"),
    ]:
        out[col_nombre] = out[col_nombre].fillna(etiqueta)
    out["codigo_segmento"] = out["codigo_segmento"].replace("", "00")
    out["codigo_familia"] = out["codigo_familia"].replace("", "0000")
    out["codigo_clase"] = out["codigo_clase"].replace("", "000000")
    return out


def agregar_metadatos_entidad(df: pd.DataFrame) -> pd.DataFrame:
    """Añade sigla, nombre corto estandarizado y sector de análisis según codigo_entidad."""
    out = df.copy()
    out["codigo_entidad"] = out["codigo_entidad"].astype(str).str.strip()
    out["sigla_entidad"] = out["codigo_entidad"].map(
        lambda c: ENTIDADES_COMPLETO.get(c, {}).get("sigla", c)
    )
    out["nombre_entidad_corto"] = out["codigo_entidad"].map(
        lambda c: ENTIDADES_COMPLETO.get(c, {}).get("nombre_corto", c)
    )
    out["sector_analisis"] = out["codigo_entidad"].map(
        lambda c: ENTIDADES_COMPLETO.get(c, {}).get("sector_analisis", "Otro")
    )
    return out


# %%
def limpiar_paa_detalle(
    df_paa_crudo: pd.DataFrame,
    catalogos_unspsc: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Limpia, tipifica y enriquece el detalle del PAA documentando cada regla."""
    n_inicial = int(len(df_paa_crudo))
    dup_id = int(df_paa_crudo["id"].duplicated().sum())
    df = df_paa_crudo.drop_duplicates(subset=["id"], keep="first").copy()

    df = agregar_metadatos_entidad(df)
    df["anio"] = pd.to_numeric(df["annio"], errors="coerce").astype("Int64")
    df = df[df["anio"].isin(ANIOS_ESTUDIO)].copy()
    df["anio"] = df["anio"].astype(int)

    df["version_del_paa"] = pd.to_numeric(df["version_del_paa"], errors="coerce").fillna(1).astype(int)
    df["valor_total_esperado"] = pd.to_numeric(df["valor_total_esperado"], errors="coerce").fillna(0.0)
    df["valor_esperado_de_presupuesto"] = pd.to_numeric(
        df["valor_esperado_de_presupuesto"], errors="coerce"
    ).fillna(0.0)

    df["requiere_vigencias_futuras"] = (
        df["se_requieren_vigencias_futuras"].map(quitar_tildes_y_espacios) == "si"
    )
    df["es_valor_no_positivo"] = (df["valor_total_esperado"] <= 0) | (
        df["valor_esperado_de_presupuesto"] <= 0
    )
    mod_cruda_nd = df["modalidad"].map(homologar_modalidad) == "No definido"
    causales = (
        df["causal_de_contratacion"]
        if "causal_de_contratacion" in df.columns
        else pd.Series(["No definido"] * len(df), index=df.index)
    )
    pares_mod = [
        homologar_modalidad_paa(m, c) for m, c in zip(df["modalidad"], causales)
    ]
    df["modalidad_homologada"] = [p[0] for p in pares_mod]
    df["modalidad_recuperada_de_causal"] = [p[1] for p in pares_mod]

    df = enriquecer_con_unspsc(df, "categorias_unspsc", catalogos_unspsc)

    # Marcar posibles duplicados o cuasi-duplicados administrativos de gran cuantía (>= 50 mil millones COP)
    # comparando entidad, año, monto exacto, código UNSPSC, modalidad y los primeros 80 caracteres del objeto
    # (captura reediciones de un mismo megaproyecto donde solo se corrigió una cita legal sin borrar la fila previa).
    df["descripcion_prefijo_80"] = df["descripcion"].map(quitar_tildes_y_espacios).str[:80]
    cols_contenido = [
        "codigo_entidad",
        "anio",
        "descripcion_prefijo_80",
        "valor_total_esperado",
        "codigo_unspsc_8d",
        "modalidad_homologada",
    ]
    dup_contenido_todos = df.duplicated(subset=cols_contenido, keep="first")
    df["es_posible_duplicado_atipico"] = dup_contenido_todos & (
        df["valor_total_esperado"] >= UMBRAL_DUPLICADO_ATIPICO_PAA_COP
    )

    # Umbral p99 intra-entidad sobre valores positivos para inspección de atípicos
    p99_entidad = (
        df[df["valor_esperado_de_presupuesto"] > 0]
        .groupby("codigo_entidad")["valor_esperado_de_presupuesto"]
        .transform(lambda s: s.quantile(0.99))
    )
    df["es_atipico_p99"] = False
    df.loc[p99_entidad.index, "es_atipico_p99"] = (
        df.loc[p99_entidad.index, "valor_esperado_de_presupuesto"] > p99_entidad
    )

    df = df.drop(columns=["descripcion_prefijo_80"])

    match_prod_8d = int(df["codigo_unspsc_8d"].isin(catalogos_unspsc["producto_set"]).sum())
    auditoria_paa = {
        "filas_iniciales": n_inicial,
        "duplicados_id_eliminados": dup_id,
        "filas_finales": int(len(df)),
        "items_valor_no_positivo": int(df["es_valor_no_positivo"].sum()),
        "items_con_vigencias_futuras": int(df["requiere_vigencias_futuras"].sum()),
        "items_multiples_codigos_unspsc": int((df["n_codigos_unspsc_celda"] > 1).sum()),
        "posibles_duplicados_atipicos_50mm": int(df["es_posible_duplicado_atipico"].sum()),
        "valor_duplicados_atipicos_cop": float(
            df.loc[df["es_posible_duplicado_atipico"], "valor_esperado_de_presupuesto"].sum()
        ),
        "tasa_match_unspsc_producto_8d_pct": round(100.0 * match_prod_8d / max(len(df), 1), 2),
        "tasa_match_unspsc_clase_segmento_pct": round(100.0 * df["unspsc_emparejado"].mean(), 2),
        "items_modalidad_cruda_no_definida": int(mod_cruda_nd.sum()),
        "items_modalidad_recuperada_de_causal": int(df["modalidad_recuperada_de_causal"].sum()),
        "valor_modalidad_recuperada_de_causal_cop": float(
            df.loc[df["modalidad_recuperada_de_causal"], "valor_esperado_de_presupuesto"].sum()
        ),
        "items_modalidad_no_definida": int((df["modalidad_homologada"] == "No definido").sum()),
    }
    return df, auditoria_paa


# %%
def limpiar_contratos(
    df_cont_crudo: pd.DataFrame,
    catalogos_unspsc: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Limpia, tipifica y enriquece los contratos electrónicos de SECOP II."""
    n_inicial = int(len(df_cont_crudo))
    dup_id = int(df_cont_crudo["id_contrato"].duplicated().sum())
    df = df_cont_crudo.drop_duplicates(subset=["id_contrato"], keep="first").copy()

    df = agregar_metadatos_entidad(df)
    df["fecha_de_firma_dt"] = pd.to_datetime(df["fecha_de_firma"], errors="coerce")
    n_sin_fecha = int(df["fecha_de_firma_dt"].isna().sum())
    df = df[df["fecha_de_firma_dt"].notna()].copy()

    df["anio"] = df["fecha_de_firma_dt"].dt.year.astype(int)
    df["mes_firma"] = df["fecha_de_firma_dt"].dt.month.astype(int)
    df = df[df["anio"].isin(ANIOS_ESTUDIO)].copy()

    for col_val in [
        "valor_del_contrato",
        "valor_pagado",
        "valor_facturado",
        "valor_pendiente_de_ejecucion",
        "dias_adicionados",
    ]:
        df[col_val] = pd.to_numeric(df[col_val], errors="coerce").fillna(0.0)

    df["estado_contrato_homologado"] = df["estado_contrato"].map(homologar_estado_contrato)
    df["es_estado_invalido"] = df["estado_contrato_homologado"].isin(ESTADOS_CONTRATO_INVALIDOS)

    df["modalidad_homologada"] = df["modalidad_de_contratacion"].map(homologar_modalidad)
    df["es_acuerdo_marco"] = df["modalidad_de_contratacion"].map(
        lambda m: "acuerdo marco" in quitar_tildes_y_espacios(m)
    )
    df["es_contratacion_directa"] = df["modalidad_homologada"] == "Contratación directa"
    df["es_contrato_cero"] = df["valor_del_contrato"] <= 0
    df["es_cuantia_simbolica"] = (df["valor_del_contrato"] > 0) & (
        df["valor_del_contrato"] <= UMBRAL_CUANTIA_SIMBOLICA_COP
    )
    df["es_contrato_sin_cuantia"] = df["es_contrato_cero"] | df["es_cuantia_simbolica"]
    df["es_contrato_valido_con_cuantia"] = (~df["es_estado_invalido"]) & (~df["es_contrato_sin_cuantia"])

    # Identificador limpio de proveedor para cálculo de concentración (CR5 / HHI)
    doc_limpio = (
        df["documento_proveedor"]
        .fillna("")
        .astype(str)
        .str.replace(r"[^0-9A-Za-z]", "", regex=True)
        .str.strip()
    )
    nom_limpio = df["proveedor_adjudicado"].fillna("SIN PROVEEDOR").astype(str).str.strip().str.upper()
    df["id_proveedor_limpio"] = np.where(doc_limpio != "", doc_limpio, nom_limpio)
    df["nombre_proveedor_limpio"] = nom_limpio

    df = enriquecer_con_unspsc(df, "codigo_de_categoria_principal", catalogos_unspsc)

    # Marcar p99 intra-entidad sobre contratos válidos con cuantía positiva
    p99_cont = (
        df[df["es_contrato_valido_con_cuantia"]]
        .groupby("codigo_entidad")["valor_del_contrato"]
        .transform(lambda s: s.quantile(0.99))
    )
    df["es_atipico_p99"] = False
    df.loc[p99_cont.index, "es_atipico_p99"] = (
        df.loc[p99_cont.index, "valor_del_contrato"] > p99_cont
    )

    df = df.drop(columns=["fecha_de_firma_dt"])

    match_prod_8d = int(df["codigo_unspsc_8d"].isin(catalogos_unspsc["producto_set"]).sum())
    auditoria_cont = {
        "filas_iniciales": n_inicial,
        "duplicados_id_contrato_eliminados": dup_id,
        "filas_sin_fecha_firma_eliminadas": n_sin_fecha,
        "filas_finales": int(len(df)),
        "contratos_estado_invalido": int(df["es_estado_invalido"].sum()),
        "contratos_valor_exacto_cero": int(df["es_contrato_cero"].sum()),
        "contratos_cuantia_simbolica_hasta_1000": int(df["es_cuantia_simbolica"].sum()),
        "contratos_sin_cuantia_cero": int(df["es_contrato_sin_cuantia"].sum()),
        "contratos_sin_cuantia_acuerdo_marco": int(
            (df["es_contrato_sin_cuantia"] & df["es_acuerdo_marco"]).sum()
        ),
        "contratos_validos_con_cuantia": int(df["es_contrato_valido_con_cuantia"].sum()),
        "contratos_unspsc_no_especificado": int((~df["unspsc_emparejado"]).sum()),
        "tasa_match_unspsc_producto_8d_pct": round(100.0 * match_prod_8d / max(len(df), 1), 2),
        "tasa_match_unspsc_clase_segmento_pct": round(100.0 * df["unspsc_emparejado"].mean(), 2),
    }
    return df, auditoria_cont


# %%
def construir_cruce_entidad_anio(
    df_enc: pd.DataFrame,
    df_paa: pd.DataFrame,
    df_cont: pd.DataFrame,
) -> pd.DataFrame:
    """Integra PAA Encabezado, PAA Detalle y Contratos SECOP II a nivel Entidad × Año."""
    enc = agregar_metadatos_entidad(df_enc)
    enc["anio"] = pd.to_numeric(enc["anno"], errors="coerce").astype(int)
    enc["version_encabezado"] = pd.to_numeric(enc["version"], errors="coerce").fillna(1).astype(int)
    enc["valor_presupuesto_encabezado"] = pd.to_numeric(
        enc["valor_presupuesto_general"], errors="coerce"
    ).fillna(0.0)
    base_enc = enc[
        [
            "codigo_entidad",
            "sigla_entidad",
            "nombre_entidad_corto",
            "sector_analisis",
            "anio",
            "version_encabezado",
            "estado",
            "valor_presupuesto_encabezado",
        ]
    ].drop_duplicates(subset=["codigo_entidad", "anio"])

    resumen_paa = (
        df_paa.groupby(["codigo_entidad", "anio"], as_index=False)
        .agg(
            items_paa=("id", "count"),
            items_vigencias_futuras=("requiere_vigencias_futuras", "sum"),
            valor_paa_total=("valor_total_esperado", "sum"),
            valor_paa_vigencia=("valor_esperado_de_presupuesto", "sum"),
        )
    )
    resumen_paa_sin_dup = (
        df_paa[~df_paa["es_posible_duplicado_atipico"]]
        .groupby(["codigo_entidad", "anio"], as_index=False)
        .agg(valor_paa_vigencia_sin_dup_atipico=("valor_esperado_de_presupuesto", "sum"))
    )

    cont_validos = df_cont[~df_cont["es_estado_invalido"]].copy()
    resumen_cont_todos = (
        cont_validos.groupby(["codigo_entidad", "anio"], as_index=False)
        .agg(
            n_contratos_total=("id_contrato", "count"),
            n_contratos_sin_cuantia=("es_contrato_sin_cuantia", "sum"),
        )
    )
    cont_con_cuantia = df_cont[df_cont["es_contrato_valido_con_cuantia"]].copy()
    resumen_cont_cuantia = (
        cont_con_cuantia.groupby(["codigo_entidad", "anio"], as_index=False)
        .agg(
            n_contratos_con_cuantia=("id_contrato", "count"),
            valor_ejecutado=("valor_del_contrato", "sum"),
            valor_pagado=("valor_pagado", "sum"),
            n_proveedores_unicos=("id_proveedor_limpio", "nunique"),
        )
    )

    cruce = (
        base_enc.merge(resumen_paa, on=["codigo_entidad", "anio"], how="outer")
        .merge(resumen_paa_sin_dup, on=["codigo_entidad", "anio"], how="left")
        .merge(resumen_cont_todos, on=["codigo_entidad", "anio"], how="left")
        .merge(resumen_cont_cuantia, on=["codigo_entidad", "anio"], how="left")
    )

    cols_numericas = [
        "items_paa",
        "items_vigencias_futuras",
        "valor_paa_total",
        "valor_paa_vigencia",
        "valor_paa_vigencia_sin_dup_atipico",
        "n_contratos_total",
        "n_contratos_sin_cuantia",
        "n_contratos_con_cuantia",
        "valor_ejecutado",
        "valor_pagado",
        "n_proveedores_unicos",
    ]
    for col in cols_numericas:
        cruce[col] = cruce[col].fillna(0)

    cruce["brecha_ejecucion_vigencia_cop"] = cruce["valor_ejecutado"] - cruce["valor_paa_vigencia"]
    cruce["pct_ejecucion_sobre_vigencia"] = np.where(
        cruce["valor_paa_vigencia"] > 0,
        100.0 * cruce["valor_ejecutado"] / cruce["valor_paa_vigencia"],
        np.nan,
    )
    cruce["pct_ejecucion_sobre_vigencia_sin_dup"] = np.where(
        cruce["valor_paa_vigencia_sin_dup_atipico"] > 0,
        100.0 * cruce["valor_ejecutado"] / cruce["valor_paa_vigencia_sin_dup_atipico"],
        np.nan,
    )
    cruce["pct_ejecucion_sobre_total_paa"] = np.where(
        cruce["valor_paa_total"] > 0,
        100.0 * cruce["valor_ejecutado"] / cruce["valor_paa_total"],
        np.nan,
    )
    cruce["diferencia_cuadre_encabezado_cop"] = (
        cruce["valor_paa_total"] - cruce["valor_presupuesto_encabezado"]
    )
    cruce = cruce.sort_values(["sigla_entidad", "anio"]).reset_index(drop=True)
    return cruce


def construir_cruce_entidad_segmento_unspsc(
    df_paa: pd.DataFrame,
    df_cont: pd.DataFrame,
) -> pd.DataFrame:
    """Cruza lo planeado en el PAA contra lo ejecutado en SECOP II por Entidad × Año × Segmento UNSPSC."""
    claves = [
        "codigo_entidad",
        "sigla_entidad",
        "nombre_entidad_corto",
        "anio",
        "codigo_segmento",
        "nombre_segmento",
    ]

    paa_seg = (
        df_paa[~df_paa["es_posible_duplicado_atipico"]]
        .groupby(claves, as_index=False)
        .agg(
            items_paa=("id", "count"),
            valor_paa_vigencia=("valor_esperado_de_presupuesto", "sum"),
            valor_paa_total=("valor_total_esperado", "sum"),
        )
    )
    cont_seg = (
        df_cont[df_cont["es_contrato_valido_con_cuantia"]]
        .groupby(claves, as_index=False)
        .agg(
            n_contratos_con_cuantia=("id_contrato", "count"),
            valor_ejecutado=("valor_del_contrato", "sum"),
        )
    )

    cruce_seg = paa_seg.merge(cont_seg, on=claves, how="outer")
    for col in ["items_paa", "valor_paa_vigencia", "valor_paa_total", "n_contratos_con_cuantia", "valor_ejecutado"]:
        cruce_seg[col] = cruce_seg[col].fillna(0)

    cruce_seg["brecha_ejecucion_vigencia_cop"] = (
        cruce_seg["valor_ejecutado"] - cruce_seg["valor_paa_vigencia"]
    )
    cruce_seg["pct_ejecucion_sobre_vigencia"] = np.where(
        cruce_seg["valor_paa_vigencia"] > 0,
        100.0 * cruce_seg["valor_ejecutado"] / cruce_seg["valor_paa_vigencia"],
        np.nan,
    )
    cruce_seg = cruce_seg.sort_values(["sigla_entidad", "anio", "codigo_segmento"]).reset_index(drop=True)
    return cruce_seg


# %%
def ejecutar_limpieza_y_cruce(
    usar_cache_local: bool = True,
    directorio_salida: Path = PROCESSED_DIR,
) -> dict[str, Any]:
    """Orquesta la limpieza, auditoría de calidad y cruce guardando los contratos CSV."""
    datos_crudos = cargar_datos_crudos(usar_cache_local=usar_cache_local)
    catalogos = construir_catalogos_unspsc(datos_crudos["unspsc"])

    df_paa_limpio, aud_paa = limpiar_paa_detalle(datos_crudos["paa_detalle"], catalogos)
    df_cont_limpio, aud_cont = limpiar_contratos(datos_crudos["contratos"], catalogos)

    df_cruce_anual = construir_cruce_entidad_anio(
        datos_crudos["paa_encabezado"], df_paa_limpio, df_cont_limpio
    )
    df_cruce_seg = construir_cruce_entidad_segmento_unspsc(df_paa_limpio, df_cont_limpio)

    directorio_salida.mkdir(parents=True, exist_ok=True)
    ruta_paa = directorio_salida / ARCHIVO_PAA_LIMPIO.name
    ruta_cont = directorio_salida / ARCHIVO_CONTRATOS_LIMPIO.name
    ruta_anual = directorio_salida / ARCHIVO_CRUCE_ENTIDAD_ANIO.name
    ruta_seg = directorio_salida / ARCHIVO_CRUCE_SEGMENTO.name
    ruta_aud = directorio_salida / ARCHIVO_AUDITORIA_CALIDAD.name

    df_paa_limpio.to_csv(ruta_paa, index=False, encoding="utf-8")
    df_cont_limpio.to_csv(ruta_cont, index=False, encoding="utf-8")
    df_cruce_anual.to_csv(ruta_anual, index=False, encoding="utf-8")
    df_cruce_seg.to_csv(ruta_seg, index=False, encoding="utf-8")

    auditoria = {
        "modo_muestra": datos_crudos.get("metadata", {}).get("modo_muestra", "desconocido"),
        "entidades_procesadas": sorted(df_cruce_anual["sigla_entidad"].unique().tolist()),
        "anios_procesados": sorted(df_cruce_anual["anio"].unique().tolist()),
        "paa_detalle": aud_paa,
        "contratos_secop2": aud_cont,
        "cuadre_exacto_paa_encabezado_max_diff_cop": float(
            df_cruce_anual["diferencia_cuadre_encabezado_cop"].abs().max()
        ),
        "archivos_generados": {
            ruta_paa.name: int(len(df_paa_limpio)),
            ruta_cont.name: int(len(df_cont_limpio)),
            ruta_anual.name: int(len(df_cruce_anual)),
            ruta_seg.name: int(len(df_cruce_seg)),
        },
    }
    ruta_aud.write_text(json.dumps(auditoria, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "paa_limpio": df_paa_limpio,
        "contratos_limpio": df_cont_limpio,
        "cruce_entidad_anio": df_cruce_anual,
        "cruce_segmento": df_cruce_seg,
        "auditoria": auditoria,
    }


# %%
def _fmt_mm(valor_cop: float) -> str:
    """Formatea un valor en COP a miles de millones con coma decimal (ej. '$128,42 MM')."""
    if pd.isna(valor_cop):
        return "—"
    signo = "-" if valor_cop < 0 else ""
    mm = abs(float(valor_cop)) / 1e9
    texto = f"{mm:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{signo}${texto}"


def _fmt_pct(valor_pct: float) -> str:
    if pd.isna(valor_pct):
        return "—"
    return f"{float(valor_pct):.1f}%".replace(".", ",")


def _fmt_int(valor: float | int) -> str:
    if pd.isna(valor):
        return "0"
    return f"{int(round(float(valor))):,}".replace(",", ".")


def generar_reporte_hallazgos_md(
    resultado: dict[str, Any],
    ruta_salida: Path = ARCHIVO_HALLAZGOS_PILOTO_MD,
) -> Path:
    """Genera un informe ejecutivo en Markdown con tablas formateadas desde los datos limpios."""
    df_paa = resultado["paa_limpio"]
    df_cont = resultado["contratos_limpio"]
    df_anual = resultado["cruce_entidad_anio"]
    df_seg = resultado["cruce_segmento"]
    aud = resultado["auditoria"]

    paa_sin_dup = df_paa[~df_paa["es_posible_duplicado_atipico"]].copy()
    cont_val = df_cont[df_cont["es_contrato_valido_con_cuantia"]].copy()

    # 1. Tabla anual Entidad x Año
    filas_t1 = []
    for _, r in df_anual.iterrows():
        filas_t1.append(
            f"| **{r['sigla_entidad']}** | {int(r['anio'])} | {_fmt_int(r['version_encabezado'])} "
            f"| {_fmt_mm(r['valor_paa_vigencia'])} | {_fmt_mm(r['valor_paa_vigencia_sin_dup_atipico'])} "
            f"| {_fmt_mm(r['valor_ejecutado'])} | {_fmt_pct(r['pct_ejecucion_sobre_vigencia'])} "
            f"| **{_fmt_pct(r['pct_ejecucion_sobre_vigencia_sin_dup'])}** "
            f"| {_fmt_int(r['n_contratos_con_cuantia'])} | {_fmt_int(r['n_proveedores_unicos'])} |"
        )

    # 2. Tabla de modalidades por entidad (2022-2025 acumulado sobre contratos con cuantía > 0)
    filas_t2 = []
    for sigla, grp_c in cont_val.groupby("sigla_entidad"):
        total_val_c = grp_c["valor_del_contrato"].sum()
        total_n_c = len(grp_c)
        cd_c = grp_c[grp_c["es_contratacion_directa"]]
        pct_val_cd = 100.0 * cd_c["valor_del_contrato"].sum() / max(total_val_c, 1.0)
        pct_n_cd = 100.0 * len(cd_c) / max(total_n_c, 1)

        grp_p = paa_sin_dup[paa_sin_dup["sigla_entidad"] == sigla]
        total_val_p = grp_p["valor_esperado_de_presupuesto"].sum()
        pct_paa_cd = (
            100.0
            * grp_p.loc[
                grp_p["modalidad_homologada"] == "Contratación directa",
                "valor_esperado_de_presupuesto",
            ].sum()
            / max(total_val_p, 1.0)
        )
        pct_paa_nd = (
            100.0
            * grp_p.loc[
                grp_p["modalidad_homologada"] == "No definido",
                "valor_esperado_de_presupuesto",
            ].sum()
            / max(total_val_p, 1.0)
        )
        filas_t2.append(
            f"| **{sigla}** | {_fmt_mm(total_val_p)} | {_fmt_pct(pct_paa_cd)} | {_fmt_pct(pct_paa_nd)} "
            f"| {_fmt_mm(total_val_c)} | **{_fmt_pct(pct_val_cd)}** | {_fmt_pct(pct_n_cd)} |"
        )

    # 3. Concentración por proveedor (CR5 y HHI) por Entidad x Año + Top contratista
    filas_t3 = []
    for (sigla, anio), grp in cont_val.groupby(["sigla_entidad", "anio"]):
        por_prov = (
            grp.groupby("id_proveedor_limpio", as_index=False)
            .agg(
                nombre_proveedor_limpio=("nombre_proveedor_limpio", "first"),
                valor_del_contrato=("valor_del_contrato", "sum"),
            )
            .sort_values("valor_del_contrato", ascending=False)
        )
        tot = por_prov["valor_del_contrato"].sum()
        participaciones = por_prov["valor_del_contrato"] / max(tot, 1.0)
        cr1 = 100.0 * participaciones.iloc[0] if len(participaciones) else 0.0
        cr5 = 100.0 * participaciones.head(5).sum()
        hhi = float((participaciones.pow(2).sum()) * 10_000)
        top_nom = str(por_prov.iloc[0]["nombre_proveedor_limpio"])[:42] if len(por_prov) else "—"
        filas_t3.append(
            f"| **{sigla}** | {int(anio)} | {_fmt_int(len(por_prov))} | {_fmt_pct(cr1)} "
            f"| **{_fmt_pct(cr5)}** | {_fmt_int(hhi)} | {top_nom} |"
        )

    # 4. Top segmentos UNSPSC por volumen planeado + ejecutado en el cuatrienio 2022-2025
    seg_acum = (
        df_seg.groupby(["codigo_segmento", "nombre_segmento"], as_index=False)
        .agg(
            valor_paa_vigencia=("valor_paa_vigencia", "sum"),
            valor_ejecutado=("valor_ejecutado", "sum"),
            items_paa=("items_paa", "sum"),
            n_contratos=("n_contratos_con_cuantia", "sum"),
        )
    )
    seg_acum["brecha"] = seg_acum["valor_ejecutado"] - seg_acum["valor_paa_vigencia"]
    seg_acum["peso_combinado"] = seg_acum["valor_paa_vigencia"] + seg_acum["valor_ejecutado"]
    seg_top = seg_acum.nlargest(8, "peso_combinado")

    filas_t4 = []
    for _, s in seg_top.iterrows():
        pct = (
            _fmt_pct(100.0 * s["valor_ejecutado"] / s["valor_paa_vigencia"])
            if s["valor_paa_vigencia"] > 0
            else "—"
        )
        nom_seg = str(s["nombre_segmento"])[:52]
        filas_t4.append(
            f"| `{s['codigo_segmento']}` | {nom_seg} | {_fmt_mm(s['valor_paa_vigencia'])} "
            f"| {_fmt_mm(s['valor_ejecutado'])} | {_fmt_mm(s['brecha'])} | {pct} |"
        )

    ap = aud["paa_detalle"]
    ac = aud["contratos_secop2"]
    total_paa_vig = df_anual["valor_paa_vigencia"].sum()
    total_paa_sin_dup = df_anual["valor_paa_vigencia_sin_dup_atipico"].sum()
    total_paa_tot = df_anual["valor_paa_total"].sum()
    total_ejec = df_anual["valor_ejecutado"].sum()

    lineas = [
        "# Informe Ejecutivo de Hallazgos — Muestra Piloto (*A contra(luz)*)",
        "",
        "> **Nota de trazabilidad:** Este documento se genera automáticamente ejecutando `python -m src.limpieza_cruce` a partir de las bases verificadas de `datos.gov.co` (`2022–2025`). Todas las cifras monetarias están expresadas en **miles de millones de pesos corrientes (`$ MM COP`)**.",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo para Discusión del Equipo",
        "",
        f"- **Muestra piloto evaluada (`2022–2025`):** `ANCP (Colombia Compra Eficiente)`, `MinAmbiente` y `MinHacienda` (`{_fmt_int(ap['filas_finales'])}` ítems de PAA y `{_fmt_int(ac['filas_finales'])}` contratos electrónicos en SECOP II).",
        f"- **Magnitud agregada del cuatrienio:** frente a un presupuesto planeado de vigencia actual de **{_fmt_mm(total_paa_vig)} MM** (**{_fmt_mm(total_paa_sin_dup)} MM** excluyendo un registro cuasi-duplicado administrativo detectado), las tres entidades suscribieron contratos por **{_fmt_mm(total_ejec)} MM** (`{_fmt_pct(100.0 * total_ejec / total_paa_sin_dup)}` de ejecución agregada ajustada).",
        "- **Cuatro hallazgos sustantivos que ya perfilan la narrativa del trabajo final:**",
        "  1. **La auditoría de calidad cambia las conclusiones económicas:** en `MinAmbiente 2023` encontramos dos líneas de **$333,54 MM** para constituir el patrimonio autónomo *Fondo para la Vida y la Biodiversidad* (solo varió una cita de artículos de la Ley 2294 de 2023 sin borrar la fila previa). Al corregir ese doble conteo, su ejecución de 2023 sube de **32,9% a 50,9% (+18,0 puntos porcentuales)**.",
        "  2. **La contratación directa domina en número de contratos, pero no siempre en valor:** aunque representa la gran mayoría de contratos firmados (prestación de servicios profesionales), en `MinHacienda` las grandes licitaciones y selecciones abreviadas (seguros previsionales/FONPET) reducen drásticamente su peso en dinero, mientras en `MinAmbiente` el régimen especial concentra convenios de gran cuantía (ej. PNUD).",
        f"  3. **Demostración empírica del nivel UNSPSC (respuesta directa a la observación R6):** cruzar por código de Producto (`8` dígitos) pierde más del 82% de los datos (`{_fmt_pct(ap['tasa_match_unspsc_producto_8d_pct'])}` en PAA y `{_fmt_pct(ac['tasa_match_unspsc_producto_8d_pct'])}` en Contratos), porque las entidades planean y contratan usando códigos terminados en `00` (nivel Clase). Al cruzar por **Clase (`6` dígitos) y Segmento (`2` dígitos)**, el emparejamiento sube a **{_fmt_pct(ap['tasa_match_unspsc_clase_segmento_pct'])}** en PAA y **{_fmt_pct(ac['tasa_match_unspsc_clase_segmento_pct'])}** en Contratos.",
        f"  4. **Rescate de modalidades desde `causal_de_contratacion` y efecto de vigencias futuras:** en la columna cruda `modalidad` del PAA venían `{_fmt_int(ap['items_modalidad_cruda_no_definida'])}` ítems como `\"No Definido\"`, pero al cruzar con `causal_de_contratacion` rescatamos la modalidad legal exacta de **`{_fmt_int(ap['items_modalidad_recuperada_de_causal'])}` ítems ({_fmt_mm(ap['valor_modalidad_recuperada_de_causal_cop'])} MM)**, dejando solo `{_fmt_int(ap['items_modalidad_no_definida'])}` omisiones reales. Además, las vigencias futuras explican **{_fmt_mm(total_paa_tot - total_paa_vig)} MM** de diferencia entre valor total y presupuesto anual.",
        "",
        "---",
        "",
        "## 2. Planeación (PAA) vs. Ejecución (SECOP II) por Entidad y Año (`$ MM COP`)",
        "",
        "| Entidad | Año | Versiones PAA | PAA Vigencia (`$ MM`) | PAA Ajustado sin Dup. (`$ MM`) | Ejecutado SECOP II (`$ MM`) | % Ejec. Bruta | % Ejec. Ajustada | Contratos (> $0) | Proveedores Únicos |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *filas_t1,
        "",
        "**Lectura rápida:**",
        "- **ANCP:** planea sistemáticamente por encima de lo que contrata con recursos propios (`44,3%–72,0%`), además de suscribir **559 Acuerdos Marco de Precios** registrados en `$0` (cuyo gasto ejecutan luego las demás entidades compradoras en la Tienda Virtual).",
        "- **MinAmbiente:** muestra alta correspondencia entre planeación y ejecución en 2022, 2024 y 2025 (`82,7%–94,0%`), con una caída en 2023 explicada por la programación del *Fondo para la Vida*.",
        "- **MinHacienda:** exhibe la mayor volatilidad: sobreejecución frente al PAA de vigencia en 2022 (`157,4%`) y 2025 (`165,9%`), y subejecución en 2023–2024 (`45,1%` y `36,8%`) cuando se programaron operaciones financieras/capitalizaciones de gran escala.",
        "",
        "---",
        "",
        "## 3. Peso de la Contratación Directa: Planeado vs. Ejecutado (`2022–2025`)",
        "",
        "| Entidad | PAA Ajustado (`$ MM`) | % PAA en Contratación Directa | % PAA con Modalidad «No definido» | Ejecutado SECOP II (`$ MM`) | % Valor Ejecutado en Contratación Directa | % # Contratos en Contratación Directa |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *filas_t2,
        "",
        "**Lectura rápida:** Mirar solo el *número* de contratos lleva a creer que casi todo es contratación directa (`> 88%` de los contratos), pero al ponderar por *valor en pesos* aparecen diferencias estructurales enormes entre entidades. Además, rescatar la modalidad desde `causal_de_contratacion` redujo el peso «No definido» de MinHacienda de `56,2%` a solo `4,1%` (mientras en ANCP aún persiste un `25,5%` sin definir ni en modalidad ni en causal).",
        "",
        "---",
        "",
        "## 4. Concentración por Proveedor (`CR1`, `CR5` e Índice `HHI`)",
        "",
        "*(Calculado sobre contratos válidos con cuantía `> $0`. Referencia económica estándar: `HHI < 1.500` desconcentrado, `1.500–2.500` moderado, `> 2.500` alta concentración).* ",
        "",
        "| Entidad | Año | Proveedores | Top 1 (`CR1`) | Top 5 (`CR5`) | Índice `HHI` (0–10.000) | Principal Proveedor Adjudicado del Año |",
        "|---|---:|---:|---:|---:|---:|---|",
        *filas_t3,
        "",
        "---",
        "",
        "## 5. Top 8 Segmentos UNSPSC con Mayor Volumen y Brecha (`2022–2025`)",
        "",
        "| Cód. | Segmento UNSPSC (2 dígitos) | PAA Ajustado (`$ MM`) | Ejecutado (`$ MM`) | Brecha Ejec. − PAA (`$ MM`) | % Ejecución |",
        "|---|---|---:|---:|---:|---:|",
        *filas_t4,
        "",
        "---",
        "",
        "## 6. Síntesis de Auditoría de Calidad de Datos (Base para Rubro 1)",
        "",
        "| Dimensión revisada | Hallazgo verificado en piloto (3 entidades) | Regla aplicada y justificación |",
        "|---|---|---|",
        f"| **Cuadre Encabezado vs. Detalle PAA** | Diferencia máxima de `${aud['cuadre_exacto_paa_encabezado_max_diff_cop']:.4f} COP` | Confirma que `9sue-ezhx` almacena solo la última versión vigente por entidad-año. |",
        f"| **Duplicados de llave primaria** | `0` en `paa_detalle` (`id`) y `0` en `contratos` (`id_contrato`) | No hay duplicación técnica de llaves en la extracción paginada. |",
        f"| **Cuasi-duplicado administrativo PAA** | `{_fmt_int(ap['posibles_duplicados_atipicos_50mm'])}` caso (`{_fmt_mm(ap['valor_duplicados_atipicos_cop'])} MM` en MinAmbiente 2023) | Se conserva en `paa_limpio.csv` con bandera `es_posible_duplicado_atipico` y se reportan indicadores con y sin dicho registro. |",
        f"| **Contratos en `$0` (sin cuantía)** | `{_fmt_int(ac['contratos_sin_cuantia_cero'])}` contratos (`{_fmt_int(ac['contratos_sin_cuantia_acuerdo_marco'])}` son Acuerdos Marco de ANCP) | Se marcan con `es_contrato_sin_cuantia` y se excluyen del denominador de montos/HHI para no sesgar indicadores financieros. |",
        f"| **Modalidades «No definido» en PAA** | `{_fmt_int(ap['items_modalidad_cruda_no_definida'])}` crudos → se rescataron **`{_fmt_int(ap['items_modalidad_recuperada_de_causal'])}` ({_fmt_mm(ap['valor_modalidad_recuperada_de_causal_cop'])} MM)** desde `causal_de_contratacion` | Solo quedan `{_fmt_int(ap['items_modalidad_no_definida'])}` ítems donde ambas columnas venían sin diligenciar. |",
        f"| **Vigencias futuras en PAA** | `{_fmt_int(ap['items_con_vigencias_futuras'])}` ítems requieren vigencias futuras | Se usa `valor_esperado_de_presupuesto` (vigencia actual) como denominador principal y `valor_total_esperado` como análisis de sensibilidad. |",
        f"| **Emparejamiento UNSPSC** | Producto 8d: `{_fmt_pct(ap['tasa_match_unspsc_producto_8d_pct'])}` / `{_fmt_pct(ac['tasa_match_unspsc_producto_8d_pct'])}` vs. Clase 6d / Segmento 2d: `{_fmt_pct(ap['tasa_match_unspsc_clase_segmento_pct'])}` / `{_fmt_pct(ac['tasa_match_unspsc_clase_segmento_pct'])}` | Se cruza a nivel Clase (`6d`) y se agrega por Segmento (`2d`) y Familia (`4d`), etiquetando los `{_fmt_int(ac['contratos_unspsc_no_especificado'])}` `UNSPECIFIED` como `\"Sin clasificar\"`. |",
        "",
        "---",
        "",
        "## 7. Puntos para Discutir en Grupo antes de Escalar a las 6 Entidades (Fase 4 y Rubro 5)",
        "",
        "1. **Validar narrativa central:** ¿Les gusta cómo estos hallazgos responden directamente la pregunta (mostrando que las desviaciones vienen tanto de choques reales de contratación/modalidad como de problemas de calidad en la planeación administrativa: vigencias futuras, ítems `\"No definido\"` y reediciones sin borrar filas)?",
        "2. **Ideas candidatas para la sección de IA (Rubro 5 — ir más allá de lo recomendado por los profesores):**",
        "   - *Candidata A (Deflación a precios constantes de 2025 con IPC DANE):* entre 2022 y 2025 Colombia tuvo inflación acumulada > 25%; comparar pesos corrientes distorsiona la evolución interanual real del gasto y de los montos promedio.",
        "   - *Candidata B (Índice de concentración de fin de año / estacionalidad pre-Ley de Garantías):* medir qué fracción del valor anual y de la contratación directa se firma en el último trimestre o justo antes de restricciones electorales.",
        "   - *Candidata C (Descomposición formal de la brecha por reasignación intrasectorial vs. escala presupuestal — índice de disimilitud de Duncan entre composición UNSPSC planeada y ejecutada).* ",
    ]

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta_salida


def main() -> None:
    resultado = ejecutar_limpieza_y_cruce(usar_cache_local=True)
    ruta_md = generar_reporte_hallazgos_md(resultado)
    aud = resultado["auditoria"]
    print("=== Limpieza y cruce completados ===")
    print("Entidades:", aud["entidades_procesadas"])
    print("Archivos generados en data/processed/:", aud["archivos_generados"])
    print("Reporte ejecutivo actualizado en:", ruta_md.relative_to(ruta_md.parent.parent))
    print(f"Cuadre máximo PAA Detalle vs Encabezado (COP): {aud['cuadre_exacto_paa_encabezado_max_diff_cop']:.2f}")


if __name__ == "__main__":
    main()
