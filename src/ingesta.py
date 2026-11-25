# %% [markdown]
# # Ingesta reproducible — API Socrata (`datos.gov.co`) y Clasificador UNSPSC
#
# Este módulo descarga de forma parametrizada y paginada las tres fuentes
# oficiales del proyecto *A contra(luz)* y conserva una copia local congelada
# en `data/raw/` para que el tutorial sea 100% reproducible sin conexión.

# %%
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import (
    ANIOS_ESTUDIO,
    ARCHIVO_CONTRATOS,
    ARCHIVO_METADATA_EXTRACCION,
    ARCHIVO_PAA_DETALLE,
    ARCHIVO_PAA_ENCABEZADO,
    ARCHIVO_UNSPSC_CSV,
    ARCHIVO_UNSPSC_RAW_XLS,
    COLUMNAS_CONTRATOS,
    COLUMNAS_PAA_DETALLE,
    COLUMNAS_PAA_ENCABEZADO,
    DATASET_CONTRATOS,
    DATASET_PAA_DETALLE,
    DATASET_PAA_ENCABEZADO,
    FECHA_FIN_EXCLUSIVA_CONTRATOS,
    FECHA_INICIO_CONTRATOS,
    FIXTURES_DIR,
    MODO_MUESTRA_DEFECTO,
    RAW_DIR,
    SOCRATA_BASE_URL,
    URL_CLASIFICADOR_UNSPSC,
    obtener_entidades,
)

USER_AGENT = "a-contraluz-secop-uniandes/1.0"
TIMEOUT_SEGUNDOS = 90
LIMITE_PAGINA_SOCRATA = 5000


# %%
def crear_sesion_http(app_token: str | None = None) -> requests.Session:
    """Crea una sesión HTTP con reintentos automáticos ante fallos transitorios."""
    sesion = requests.Session()
    estrategia_reintento = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adaptador = HTTPAdapter(max_retries=estrategia_reintento)
    sesion.mount("https://", adaptador)
    sesion.mount("http://", adaptador)

    headers = {"User-Agent": USER_AGENT}
    if app_token:
        headers["X-App-Token"] = app_token
    sesion.headers.update(headers)
    return sesion


def consultar_socrata_paginado(
    dataset_id: str,
    columnas: list[str],
    where_clause: str,
    order_col: str,
    sesion: requests.Session | None = None,
    limite_pagina: int = LIMITE_PAGINA_SOCRATA,
) -> list[dict[str, Any]]:
    """Consulta un recurso Socrata SODA paginando hasta agotar todos los registros."""
    sesion_activa = sesion or crear_sesion_http()
    url = f"{SOCRATA_BASE_URL}/{dataset_id}.json"
    registros: list[dict[str, Any]] = []
    offset = 0

    while True:
        parametros = {
            "$select": ", ".join(columnas),
            "$where": where_clause,
            "$order": order_col,
            "$limit": limite_pagina,
            "$offset": offset,
        }
        respuesta = sesion_activa.get(url, params=parametros, timeout=TIMEOUT_SEGUNDOS)
        respuesta.raise_for_status()
        pagina = respuesta.json()

        if not isinstance(pagina, list):
            raise ValueError(f"Respuesta inesperada de {dataset_id}: se esperaba una lista JSON.")

        registros.extend(pagina)
        if len(pagina) < limite_pagina:
            break
        offset += limite_pagina

    return registros


def _normalizar_dataframe_columnas(
    registros: list[dict[str, Any]],
    columnas_esperadas: list[str],
) -> pd.DataFrame:
    """Construye un DataFrame asegurando el orden exacto de columnas esperadas."""
    df = pd.DataFrame(registros)
    for col in columnas_esperadas:
        if col not in df.columns:
            df[col] = pd.NA
    return df[columnas_esperadas].copy()


# %%
def descargar_paa_encabezado(
    entidades: dict[str, dict[str, str]],
    anios: list[int] = ANIOS_ESTUDIO,
    sesion: requests.Session | None = None,
) -> pd.DataFrame:
    """Descarga el encabezado publicado del PAA (b6m4-qgqv) para las entidades y años dados."""
    codigos_num = ", ".join(entidades.keys())
    anio_min = min(anios)
    anio_max = max(anios)
    where = f"codigo_entidad in ({codigos_num}) AND anno >= {anio_min} AND anno <= {anio_max}"

    registros = consultar_socrata_paginado(
        dataset_id=DATASET_PAA_ENCABEZADO,
        columnas=COLUMNAS_PAA_ENCABEZADO,
        where_clause=where,
        order_col="codigo_entidad ASC, anno ASC, version DESC",
        sesion=sesion,
    )
    df = _normalizar_dataframe_columnas(registros, COLUMNAS_PAA_ENCABEZADO)
    df["codigo_entidad"] = df["codigo_entidad"].astype(str).str.strip()
    return df


def descargar_paa_detalle(
    entidades: dict[str, dict[str, str]],
    anios: list[int] = ANIOS_ESTUDIO,
    sesion: requests.Session | None = None,
) -> pd.DataFrame:
    """Descarga el detalle del PAA (9sue-ezhx) entidad por entidad para evitar timeouts."""
    anio_min = min(anios)
    anio_max = max(anios)
    tablas: list[pd.DataFrame] = []

    for codigo, info in entidades.items():
        t0 = time.time()
        where = f"codigo_entidad = '{codigo}' AND annio >= {anio_min} AND annio <= {anio_max}"
        registros = consultar_socrata_paginado(
            dataset_id=DATASET_PAA_DETALLE,
            columnas=COLUMNAS_PAA_DETALLE,
            where_clause=where,
            order_col="annio ASC, id ASC",
            sesion=sesion,
        )
        df_ent = _normalizar_dataframe_columnas(registros, COLUMNAS_PAA_DETALLE)
        tablas.append(df_ent)
        print(
            f"  [PAA Detalle] {info['sigla']} ({codigo}): "
            f"{len(df_ent):,} filas en {time.time() - t0:.1f}s",
            flush=True,
        )

    df_total = pd.concat(tablas, ignore_index=True) if tablas else pd.DataFrame(columns=COLUMNAS_PAA_DETALLE)
    df_total["codigo_entidad"] = df_total["codigo_entidad"].astype(str).str.strip()
    return df_total


def descargar_contratos(
    entidades: dict[str, dict[str, str]],
    sesion: requests.Session | None = None,
) -> pd.DataFrame:
    """Descarga los contratos electrónicos de SECOP II (jbjy-vk9h) entidad por entidad."""
    tablas: list[pd.DataFrame] = []

    for codigo, info in entidades.items():
        t0 = time.time()
        where = (
            f"codigo_entidad = {codigo} "
            f"AND fecha_de_firma >= '{FECHA_INICIO_CONTRATOS}' "
            f"AND fecha_de_firma < '{FECHA_FIN_EXCLUSIVA_CONTRATOS}'"
        )
        registros = consultar_socrata_paginado(
            dataset_id=DATASET_CONTRATOS,
            columnas=COLUMNAS_CONTRATOS,
            where_clause=where,
            order_col="fecha_de_firma ASC, id_contrato ASC",
            sesion=sesion,
        )
        df_ent = _normalizar_dataframe_columnas(registros, COLUMNAS_CONTRATOS)
        tablas.append(df_ent)
        print(
            f"  [Contratos]   {info['sigla']} ({codigo}): "
            f"{len(df_ent):,} filas en {time.time() - t0:.1f}s",
            flush=True,
        )

    df_total = pd.concat(tablas, ignore_index=True) if tablas else pd.DataFrame(columns=COLUMNAS_CONTRATOS)
    df_total["codigo_entidad"] = df_total["codigo_entidad"].astype(str).str.strip()
    return df_total


# %%
def _formatear_codigo_unspsc(serie: pd.Series, longitud: int) -> pd.Series:
    """Convierte códigos numéricos UNSPSC a texto con ceros a la izquierda."""
    numerico = pd.to_numeric(serie, errors="coerce")
    texto = numerico.map(lambda val: f"{int(val):0{longitud}d}" if pd.notna(val) else "")
    return texto


def parsear_clasificador_unspsc(ruta_xls: Path) -> pd.DataFrame:
    """Lee la hoja oficial 'Clasificador' del Excel v14.1 de Colombia Compra Eficiente."""
    df_crudo = pd.read_excel(ruta_xls, sheet_name="Clasificador", header=3, engine="xlrd")
    mapeo_columnas = {
        "Código Segmento": "codigo_segmento",
        "Nombre Segmento": "nombre_segmento",
        "Código Familia": "codigo_familia",
        "Nombre Familia": "nombre_familia",
        "Código Clase": "codigo_clase",
        "Nombre Clase": "nombre_clase",
        "Código Producto": "codigo_producto",
        "Nombre Producto": "nombre_producto",
    }
    faltantes = [col for col in mapeo_columnas if col not in df_crudo.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes en el Clasificador UNSPSC: {faltantes}")

    df = df_crudo[list(mapeo_columnas.keys())].rename(columns=mapeo_columnas).copy()
    df["codigo_segmento"] = _formatear_codigo_unspsc(df["codigo_segmento"], 2)
    df["codigo_familia"] = _formatear_codigo_unspsc(df["codigo_familia"], 4)
    df["codigo_clase"] = _formatear_codigo_unspsc(df["codigo_clase"], 6)
    df["codigo_producto"] = _formatear_codigo_unspsc(df["codigo_producto"], 8)

    for col_texto in ["nombre_segmento", "nombre_familia", "nombre_clase", "nombre_producto"]:
        df[col_texto] = df[col_texto].astype(str).str.strip()

    df = df[df["codigo_producto"].str.len() == 8].drop_duplicates(subset=["codigo_producto"]).reset_index(drop=True)
    return df


def descargar_clasificador_unspsc(
    ruta_xls: Path = ARCHIVO_UNSPSC_RAW_XLS,
    ruta_csv: Path = ARCHIVO_UNSPSC_CSV,
    forzar_descarga: bool = False,
    sesion: requests.Session | None = None,
) -> pd.DataFrame:
    """Descarga (si hace falta) y normaliza el Clasificador UNSPSC oficial a CSV UTF-8."""
    ruta_xls.parent.mkdir(parents=True, exist_ok=True)
    if forzar_descarga or not ruta_xls.exists():
        sesion_activa = sesion or crear_sesion_http()
        print("  [UNSPSC] Descargando archivo oficial de Colombia Compra Eficiente...", flush=True)
        respuesta = sesion_activa.get(URL_CLASIFICADOR_UNSPSC, timeout=TIMEOUT_SEGUNDOS)
        respuesta.raise_for_status()
        ruta_xls.write_bytes(respuesta.content)

    df_unspsc = parsear_clasificador_unspsc(ruta_xls)
    df_unspsc.to_csv(ruta_csv, index=False, encoding="utf-8")
    print(f"  [UNSPSC] Normalizado y guardado en {ruta_csv.name}: {len(df_unspsc):,} productos", flush=True)
    return df_unspsc


# %%
def _sha256_archivo(ruta: Path) -> str:
    """Calcula el hash SHA-256 de un archivo para trazabilidad de insumos."""
    hasher = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            hasher.update(bloque)
    return hasher.hexdigest()


def guardar_fixtures_offline(
    df_enc: pd.DataFrame,
    df_paa: pd.DataFrame,
    df_cont: pd.DataFrame,
    df_unspsc: pd.DataFrame,
    n_filas: int = 5,
) -> None:
    """Guarda muestras reales recortadas en tests/fixtures/ para pruebas unitarias sin red."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    df_enc.head(n_filas).to_json(
        FIXTURES_DIR / "paa_encabezado_muestra.json", orient="records", force_ascii=False, indent=2
    )
    df_paa.head(n_filas).to_json(
        FIXTURES_DIR / "paa_detalle_muestra.json", orient="records", force_ascii=False, indent=2
    )
    df_cont.head(n_filas).to_json(
        FIXTURES_DIR / "contratos_muestra.json", orient="records", force_ascii=False, indent=2
    )
    df_unspsc.head(20).to_csv(FIXTURES_DIR / "clasificador_unspsc_muestra.csv", index=False, encoding="utf-8")


def ejecutar_extraccion_api(modo: str = MODO_MUESTRA_DEFECTO, guardar_fixtures: bool = True) -> dict[str, Any]:
    """Ejecuta la extracción completa desde datos.gov.co y congela los CSVs en data/raw/."""
    load_dotenv()
    app_token = os.getenv("SOCRATA_APP_TOKEN") or None
    entidades = obtener_entidades(modo)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sesion = crear_sesion_http(app_token=app_token)

    print(f"=== Iniciando extracción API (modo={modo}, entidades={len(entidades)}, años={ANIOS_ESTUDIO}) ===", flush=True)
    df_enc = descargar_paa_encabezado(entidades, ANIOS_ESTUDIO, sesion=sesion)
    df_enc.to_csv(ARCHIVO_PAA_ENCABEZADO, index=False, encoding="utf-8")
    print(f"  [PAA Encab.]  Total guardado: {len(df_enc):,} filas", flush=True)

    df_paa = descargar_paa_detalle(entidades, ANIOS_ESTUDIO, sesion=sesion)
    df_paa.to_csv(ARCHIVO_PAA_DETALLE, index=False, encoding="utf-8")

    df_cont = descargar_contratos(entidades, sesion=sesion)
    df_cont.to_csv(ARCHIVO_CONTRATOS, index=False, encoding="utf-8")

    df_unspsc = descargar_clasificador_unspsc(forzar_descarga=False, sesion=sesion)

    if guardar_fixtures:
        guardar_fixtures_offline(df_enc, df_paa, df_cont, df_unspsc)

    metadata = {
        "fecha_extraccion_utc": datetime.now(timezone.utc).isoformat(),
        "modo_muestra": modo,
        "anios_estudio": ANIOS_ESTUDIO,
        "entidades": entidades,
        "datasets_socrata": {
            "paa_encabezado": DATASET_PAA_ENCABEZADO,
            "paa_detalle": DATASET_PAA_DETALLE,
            "contratos": DATASET_CONTRATOS,
        },
        "url_unspsc": URL_CLASIFICADOR_UNSPSC,
        "conteos": {
            "paa_encabezado": int(len(df_enc)),
            "paa_detalle": int(len(df_paa)),
            "contratos": int(len(df_cont)),
            "unspsc": int(len(df_unspsc)),
        },
        "sha256": {
            ARCHIVO_PAA_ENCABEZADO.name: _sha256_archivo(ARCHIVO_PAA_ENCABEZADO),
            ARCHIVO_PAA_DETALLE.name: _sha256_archivo(ARCHIVO_PAA_DETALLE),
            ARCHIVO_CONTRATOS.name: _sha256_archivo(ARCHIVO_CONTRATOS),
            ARCHIVO_UNSPSC_CSV.name: _sha256_archivo(ARCHIVO_UNSPSC_CSV),
        },
    }
    ARCHIVO_METADATA_EXTRACCION.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"=== Extracción completada y metadata guardada en {ARCHIVO_METADATA_EXTRACCION.name} ===", flush=True)
    return metadata


# %%
def cargar_datos_crudos(
    usar_cache_local: bool = True,
    modo: str = MODO_MUESTRA_DEFECTO,
) -> dict[str, Any]:
    """Carga los cuatro insumos crudos desde caché local (por defecto) o desde la API.

    Preserva explícitamente como texto los códigos de entidad, NITs y códigos UNSPSC
    para no perder ceros a la izquierda.
    """
    if not usar_cache_local:
        ejecutar_extraccion_api(modo=modo, guardar_fixtures=False)

    archivos_requeridos = [
        ARCHIVO_PAA_ENCABEZADO,
        ARCHIVO_PAA_DETALLE,
        ARCHIVO_CONTRATOS,
        ARCHIVO_UNSPSC_CSV,
    ]
    faltantes = [p.name for p in archivos_requeridos if not p.exists()]
    if faltantes:
        raise FileNotFoundError(
            f"Faltan archivos en data/raw/: {faltantes}. "
            "Ejecute 'python src/ingesta.py --actualizar-api' para regenerarlos."
        )

    df_enc = pd.read_csv(
        ARCHIVO_PAA_ENCABEZADO,
        dtype={"codigo_entidad": str, "identificador_unico": str, "id_plan_anual_de_adquisiciones": str},
    )
    df_paa = pd.read_csv(
        ARCHIVO_PAA_DETALLE,
        dtype={
            "id": str,
            "identificador_unico": str,
            "id_paa_encabezado": str,
            "codigo_entidad": str,
            "nit_entidad": str,
            "categorias_unspsc": str,
        },
    )
    df_cont = pd.read_csv(
        ARCHIVO_CONTRATOS,
        dtype={
            "id_contrato": str,
            "proceso_de_compra": str,
            "codigo_entidad": str,
            "nit_entidad": str,
            "codigo_de_categoria_principal": str,
            "documento_proveedor": str,
            "codigo_proveedor": str,
        },
    )
    df_unspsc = pd.read_csv(
        ARCHIVO_UNSPSC_CSV,
        dtype={
            "codigo_segmento": str,
            "codigo_familia": str,
            "codigo_clase": str,
            "codigo_producto": str,
        },
    )
    metadata = (
        json.loads(ARCHIVO_METADATA_EXTRACCION.read_text(encoding="utf-8"))
        if ARCHIVO_METADATA_EXTRACCION.exists()
        else {}
    )
    return {
        "paa_encabezado": df_enc,
        "paa_detalle": df_paa,
        "contratos": df_cont,
        "unspsc": df_unspsc,
        "metadata": metadata,
    }


# %%
def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta reproducible de datos SECOP II, PAA y UNSPSC.")
    parser.add_argument(
        "--modo",
        choices=["piloto", "completo"],
        default=MODO_MUESTRA_DEFECTO,
        help="Muestra de entidades a extraer ('piloto'=3 entidades, 'completo'=6 entidades).",
    )
    parser.add_argument(
        "--actualizar-api",
        action="store_true",
        help="Consulta la API de datos.gov.co y actualiza los archivos congelados en data/raw/.",
    )
    args = parser.parse_args()

    if args.actualizar_api:
        ejecutar_extraccion_api(modo=args.modo, guardar_fixtures=True)
    else:
        datos = cargar_datos_crudos(usar_cache_local=True, modo=args.modo)
        print("Datos cargados desde caché local en data/raw/:")
        for nombre in ["paa_encabezado", "paa_detalle", "contratos", "unspsc"]:
            print(f"  - {nombre}: {len(datos[nombre]):,} filas")


if __name__ == "__main__":
    main()
