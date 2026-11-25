"""Pruebas automáticas offline del módulo src/ingesta.py."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.config import (
    COLUMNAS_CONTRATOS,
    COLUMNAS_PAA_DETALLE,
    COLUMNAS_PAA_ENCABEZADO,
    FIXTURES_DIR,
    obtener_entidades,
)
from src.ingesta import (
    _formatear_codigo_unspsc,
    _normalizar_dataframe_columnas,
    cargar_datos_crudos,
    consultar_socrata_paginado,
)


def test_obtener_entidades_piloto_y_completo() -> None:
    piloto = obtener_entidades("piloto")
    completo = obtener_entidades("completo")
    assert len(piloto) == 3
    assert len(completo) == 6
    assert set(piloto.keys()).issubset(set(completo.keys()))

    with pytest.raises(ValueError):
        obtener_entidades("invalido")


def test_consultar_socrata_paginado_multipagina() -> None:
    pagina_1 = [{"id": "1", "val": "100"}, {"id": "2", "val": "200"}]
    pagina_2 = [{"id": "3", "val": "300"}]

    resp_1 = MagicMock()
    resp_1.json.return_value = pagina_1
    resp_1.raise_for_status.return_value = None

    resp_2 = MagicMock()
    resp_2.json.return_value = pagina_2
    resp_2.raise_for_status.return_value = None

    sesion_mock = MagicMock()
    sesion_mock.get.side_effect = [resp_1, resp_2]

    resultado = consultar_socrata_paginado(
        dataset_id="9sue-ezhx",
        columnas=["id", "val"],
        where_clause="annio = 2024",
        order_col="id ASC",
        sesion=sesion_mock,
        limite_pagina=2,
    )

    assert len(resultado) == 3
    assert [r["id"] for r in resultado] == ["1", "2", "3"]
    assert sesion_mock.get.call_count == 2
    assert sesion_mock.get.call_args_list[0].kwargs["params"]["$offset"] == 0
    assert sesion_mock.get.call_args_list[1].kwargs["params"]["$offset"] == 2


def test_formatear_codigo_unspsc_conserva_longitud_y_ceros() -> None:
    serie = pd.Series([10.0, 1010.0, 101015.0, 10101501.0, None, "invalido"])
    assert list(_formatear_codigo_unspsc(serie, 2))[:1] == ["10"]
    assert list(_formatear_codigo_unspsc(pd.Series([5.0, None]), 2)) == ["05", ""]
    assert list(_formatear_codigo_unspsc(pd.Series([10101501.0]), 8)) == ["10101501"]


def test_normalizar_dataframe_columnas_agrega_faltantes() -> None:
    df = _normalizar_dataframe_columnas([{"a": 1}], ["a", "b"])
    assert list(df.columns) == ["a", "b"]
    assert pd.isna(df.loc[0, "b"])


def test_fixtures_reales_y_cache_local_offline() -> None:
    rutas_json = {
        "paa_encabezado_muestra.json": COLUMNAS_PAA_ENCABEZADO,
        "paa_detalle_muestra.json": COLUMNAS_PAA_DETALLE,
        "contratos_muestra.json": COLUMNAS_CONTRATOS,
    }
    for nombre_archivo, columnas_esperadas in rutas_json.items():
        ruta = FIXTURES_DIR / nombre_archivo
        assert ruta.exists(), f"Falta fixture offline: {ruta}"
        registros = json.loads(ruta.read_text(encoding="utf-8"))
        assert len(registros) > 0
        assert set(columnas_esperadas).issubset(set(registros[0].keys()))

    datos = cargar_datos_crudos(usar_cache_local=True)
    for clave in ["paa_encabezado", "paa_detalle", "contratos", "unspsc"]:
        assert len(datos[clave]) > 0, f"Tabla vacía en caché local: {clave}"

    # Verificar que códigos de entidad y UNSPSC se leen como texto (no float)
    assert pd.api.types.is_string_dtype(datos["paa_detalle"]["codigo_entidad"])
    assert pd.api.types.is_string_dtype(datos["contratos"]["codigo_entidad"])
    assert pd.api.types.is_string_dtype(datos["unspsc"]["codigo_producto"])
    assert (datos["unspsc"]["codigo_producto"].str.len() == 8).all()
