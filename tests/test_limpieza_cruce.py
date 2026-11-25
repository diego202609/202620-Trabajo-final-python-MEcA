"""Pruebas automáticas offline del módulo src/limpieza_cruce.py."""

from __future__ import annotations

import pandas as pd

from src.config import PRUEBAS_DIR
from src.ingesta import cargar_datos_crudos
from src.limpieza_cruce import (
    construir_catalogos_unspsc,
    ejecutar_limpieza_y_cruce,
    enriquecer_con_unspsc,
    extraer_codigos_unspsc,
    homologar_modalidad,
    homologar_modalidad_paa,
    limpiar_paa_detalle,
)


def test_homologar_modalidad_paa_rescata_desde_causal() -> None:
    assert homologar_modalidad_paa("No Definido", "CCE-16-Servicios_profesionales_gestion") == (
        "Contratación directa",
        True,
    )
    assert homologar_modalidad_paa("No Definido", "CCE-02-Licitacion_Publica") == (
        "Licitación pública y AMP",
        True,
    )
    assert homologar_modalidad_paa("No Definido", "CCE-06-Seleccion_Abreviada_Menor_Cuantia") == (
        "Selección abreviada",
        True,
    )
    assert homologar_modalidad_paa("No Definido", "CCE-11-Procedimiento_Publicidad") == (
        "Régimen especial",
        True,
    )
    assert homologar_modalidad_paa("No Definido", "No definido") == ("No definido", False)
    assert homologar_modalidad_paa("CONTRATACION DIRECTA", "CCE-16-Servicios_profesionales_gestion") == (
        "Contratación directa",
        False,
    )


def test_homologar_modalidad_unifica_paa_y_secop() -> None:
    assert homologar_modalidad("CONTRATACION DIRECTA") == "Contratación directa"
    assert homologar_modalidad("Contratación directa") == "Contratación directa"
    assert homologar_modalidad("Contratación Directa (con ofertas)") == "Contratación directa"
    assert homologar_modalidad("Licitación Pública Acuerdo Marco de Precios") == "Licitación pública y AMP"
    assert homologar_modalidad("SELECCION ABREVIADA CON SUBASTA INVERSA") == "Selección abreviada"
    assert homologar_modalidad("Mínima cuantía") == "Mínima cuantía"
    assert homologar_modalidad("No Definido") == "No definido"
    assert homologar_modalidad(None) == "No definido"


def test_extraer_codigos_unspsc_prefijo_multiples_e_invalidos() -> None:
    assert extraer_codigos_unspsc("V1.80111620") == ("80111620", 1)
    assert extraer_codigos_unspsc("80101500; 80111600") == ("80101500", 2)
    assert extraer_codigos_unspsc("UNSPECIFIED") == ("", 0)
    assert extraer_codigos_unspsc(None) == ("", 0)


def test_enriquecer_con_unspsc_empareja_clase_y_marca_sin_clasificar() -> None:
    datos = cargar_datos_crudos(usar_cache_local=True)
    catalogos = construir_catalogos_unspsc(datos["unspsc"])
    df_prueba = pd.DataFrame(
        {
            "id": ["1", "2"],
            "cat": ["V1.80111600", "UNSPECIFIED"],  # 80111600 termina en 00 (nivel Clase)
        }
    )
    enriquecido = enriquecer_con_unspsc(df_prueba, "cat", catalogos)
    assert bool(enriquecido.loc[0, "unspsc_emparejado"]) is True
    assert enriquecido.loc[0, "codigo_segmento"] == "80"
    assert enriquecido.loc[0, "nombre_segmento"] != "Sin clasificar"

    assert bool(enriquecido.loc[1, "unspsc_emparejado"]) is False
    assert enriquecido.loc[1, "nombre_segmento"] == "Sin clasificar"
    assert enriquecido.loc[1, "codigo_segmento"] == "00"


def test_limpiar_paa_detalle_marca_solo_duplicados_atipicos_grandes() -> None:
    datos = cargar_datos_crudos(usar_cache_local=True)
    catalogos = construir_catalogos_unspsc(datos["unspsc"])
    muestra = pd.DataFrame(
        [
            # Dos contratistas pequeños idénticos (< 50 MM): legítimo, NO debe marcarse
            {
                "id": "A1",
                "codigo_entidad": "700209018",
                "annio": 2023,
                "version_del_paa": 28,
                "descripcion": "PRESTAR SERVICIOS PROFESIONALES DE APOYO JURIDICO EN EL MINISTERIO",
                "valor_total_esperado": 60_000_000,
                "valor_esperado_de_presupuesto": 60_000_000,
                "se_requieren_vigencias_futuras": "No",
                "modalidad": "CONTRATACION DIRECTA",
                "categorias_unspsc": "80111600",
            },
            {
                "id": "A2",
                "codigo_entidad": "700209018",
                "annio": 2023,
                "version_del_paa": 28,
                "descripcion": "PRESTAR SERVICIOS PROFESIONALES DE APOYO JURIDICO EN EL MINISTERIO",
                "valor_total_esperado": 60_000_000,
                "valor_esperado_de_presupuesto": 60_000_000,
                "se_requieren_vigencias_futuras": "No",
                "modalidad": "CONTRATACION DIRECTA",
                "categorias_unspsc": "80111600",
            },
            # Dos registros gigantes (>= 50 MM) con igual prefijo de objeto y monto exacto: SÍ marca el 2do
            {
                "id": "B1",
                "codigo_entidad": "700209018",
                "annio": 2023,
                "version_del_paa": 28,
                "descripcion": "CONTRATAR UNA SOCIEDAD FIDUCIARIA PARA LA CONSTITUCION DEL PATRIMONIO AUTONOMO FONDO VIDA ART 223",
                "valor_total_esperado": 333_535_000_000,
                "valor_esperado_de_presupuesto": 333_535_000_000,
                "se_requieren_vigencias_futuras": "No",
                "modalidad": "LICITACION PUBLICA",
                "categorias_unspsc": "84121500",
            },
            {
                "id": "B2",
                "codigo_entidad": "700209018",
                "annio": 2023,
                "version_del_paa": 28,
                "descripcion": "CONTRATAR UNA SOCIEDAD FIDUCIARIA PARA LA CONSTITUCION DEL PATRIMONIO AUTONOMO FONDO VIDA ART 49",
                "valor_total_esperado": 333_535_000_000,
                "valor_esperado_de_presupuesto": 333_535_000_000,
                "se_requieren_vigencias_futuras": "No",
                "modalidad": "LICITACION PUBLICA",
                "categorias_unspsc": "84121500",
            },
        ]
    )
    limpio, aud = limpiar_paa_detalle(muestra, catalogos)
    assert list(limpio["es_posible_duplicado_atipico"]) == [False, False, False, True]
    assert aud["posibles_duplicados_atipicos_50mm"] == 1


def test_ejecutar_limpieza_y_cruce_en_directorio_pruebas() -> None:
    salida_pruebas = PRUEBAS_DIR / "limpieza_test"
    resultado = ejecutar_limpieza_y_cruce(usar_cache_local=True, directorio_salida=salida_pruebas)
    aud = resultado["auditoria"]

    assert aud["cuadre_exacto_paa_encabezado_max_diff_cop"] < 1.0
    assert aud["paa_detalle"]["tasa_match_unspsc_clase_segmento_pct"] > 99.0
    assert aud["contratos_secop2"]["tasa_match_unspsc_clase_segmento_pct"] > 99.0

    cruce_anual = resultado["cruce_entidad_anio"]
    assert cruce_anual.duplicated(subset=["codigo_entidad", "anio"]).sum() == 0
    assert (salida_pruebas / "cruce_entidad_anio.csv").exists()
    assert (salida_pruebas / "cruce_entidad_anio_segmento.csv").exists()
