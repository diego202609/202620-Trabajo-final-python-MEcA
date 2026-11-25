"""Configuración centralizada del proyecto A contra(luz) — Grupo 3.

Todas las rutas son relativas a la raíz del repositorio para garantizar que el
entregable (.zip) sea 100% autocontenido y reproducible en cualquier equipo.
"""

from pathlib import Path

# Rutas relativas a la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DASHBOARD_DATA_DIR = DATA_DIR / "dashboard_data"
PRUEBAS_DIR = DATA_DIR / "pruebas"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

# Semilla fija global para reproducibilidad (Rubro 1)
RANDOM_SEED = 42

# Periodo de estudio acordado (R4)
ANIOS_ESTUDIO = [2022, 2023, 2024, 2025]
FECHA_INICIO_CONTRATOS = "2022-01-01T00:00:00"
FECHA_FIN_EXCLUSIVA_CONTRATOS = "2026-01-01T00:00:00"

# Endpoints oficiales verificados en Fase 2 (datos.gov.co — Socrata SODA API)
SOCRATA_BASE_URL = "https://www.datos.gov.co/resource"
DATASET_PAA_ENCABEZADO = "b6m4-qgqv"  # SECOP II - PAA - Encabezado
DATASET_PAA_DETALLE = "9sue-ezhx"     # SECOP II - Plan Anual De Adquisiciones Detalle
DATASET_CONTRATOS = "jbjy-vk9h"       # SECOP II - Contratos Electrónicos

# Clasificador oficial de Bienes y Servicios UNSPSC v14.1 (Colombia Compra Eficiente)
URL_CLASIFICADOR_UNSPSC = (
    "https://operaciones.colombiacompra.gov.co/sites/cce_public/files/"
    "cce_clasificador/clasificador_de_bienes_y_servicios_v14_1.xls"
)

# Muestra incremental aprobada (orden Nacional, nivel central, Publicado 2022-2025, 100% UNSPSC)
# Clave: codigo_entidad (verificado en b6m4-qgqv, 9sue-ezhx y jbjy-vk9h)
ENTIDADES_PILOTO = {
    "700037070": {
        "nombre_corto": "ANCP (Colombia Compra Eficiente)",
        "sigla": "ANCP",
        "nit": "900514813",
        "sector_analisis": "Rectoría de Compras Públicas",
    },
    "700065089": {
        "nombre_corto": "Ministerio de Hacienda y Crédito Público",
        "sigla": "MinHacienda",
        "nit": "899999090",
        "sector_analisis": "Hacienda y Política Fiscal",
    },
    "700209018": {
        "nombre_corto": "Ministerio de Ambiente y Desarrollo Sostenible",
        "sigla": "MinAmbiente",
        "nit": "830115395",
        "sector_analisis": "Ambiente y Desarrollo Sostenible",
    },
}

ENTIDADES_ESCALA = {
    "700066053": {
        "nombre_corto": "Ministerio de Educación Nacional",
        "sigla": "MinEducación",
        "nit": "899999001",
        "sector_analisis": "Educación",
    },
    "700637010": {
        "nombre_corto": "Ministerio de las Culturas, las Artes y los Saberes",
        "sigla": "MinCulturas",
        "nit": "830034348",
        "sector_analisis": "Cultura",
    },
    "700220049": {
        "nombre_corto": "Departamento Nacional de Planeación",
        "sigla": "DNP",
        "nit": "899999011",
        "sector_analisis": "Planeación Nacional",
    },
}

ENTIDADES_COMPLETO = {**ENTIDADES_PILOTO, **ENTIDADES_ESCALA}

# Modo activo por defecto para Fase 3 (cambiar a "completo" en Fase 4 para escalar a 6 entidades)
MODO_MUESTRA_DEFECTO = "piloto"

# Selección estricta de columnas analíticas (excluye datos personales sensibles y cuentas bancarias)
COLUMNAS_PAA_ENCABEZADO = [
    "identificador_unico",
    "id_plan_anual_de_adquisiciones",
    "anno",
    "codigo_entidad",
    "nombre_entidad",
    "valor_presupuesto_general",
    "presupuesto_menor_cuantia",
    "presupuesto_minima_cuantia",
    "fecha_de_publicacion",
    "fecha_de_creacion",
    "fecha_de_ultima_modificacion",
    "version",
    "estado",
]

COLUMNAS_PAA_DETALLE = [
    "id",
    "identificador_unico",
    "id_plan_anual_de_adquisiciones",
    "id_paa_encabezado",
    "codigo_entidad",
    "nit_entidad",
    "nombre_entidad",
    "annio",
    "version_del_paa",
    "fecha_version",
    "descripcion",
    "fecha_esperada_de_inicio",
    "duracion_esperada",
    "unidad_de_duracion_esperada",
    "origen_recursos",
    "valor_total_esperado",
    "valor_esperado_de_presupuesto",
    "se_requieren_vigencias_futuras",
    "modalidad",
    "causal_de_contratacion",
    "grupo_de_procedimiento",
    "categorias_unspsc",
    "tipo",
]

COLUMNAS_CONTRATOS = [
    "id_contrato",
    "proceso_de_compra",
    "referencia_del_contrato",
    "codigo_entidad",
    "nit_entidad",
    "nombre_entidad",
    "orden",
    "sector",
    "rama",
    "entidad_centralizada",
    "estado_contrato",
    "codigo_de_categoria_principal",
    "tipo_de_contrato",
    "modalidad_de_contratacion",
    "justificacion_modalidad_de",
    "fecha_de_firma",
    "fecha_de_inicio_del_contrato",
    "fecha_de_fin_del_contrato",
    "tipodocproveedor",
    "documento_proveedor",
    "codigo_proveedor",
    "proveedor_adjudicado",
    "es_pyme",
    "origen_de_los_recursos",
    "destino_gasto",
    "valor_del_contrato",
    "valor_pagado",
    "valor_facturado",
    "valor_pendiente_de_ejecucion",
    "dias_adicionados",
    "ultima_actualizacion",
]

# Archivos congelados en data/raw/
ARCHIVO_PAA_ENCABEZADO = RAW_DIR / "paa_encabezado.csv"
ARCHIVO_PAA_DETALLE = RAW_DIR / "paa_detalle.csv"
ARCHIVO_CONTRATOS = RAW_DIR / "contratos_secop2.csv"
ARCHIVO_UNSPSC_RAW_XLS = RAW_DIR / "clasificador_unspsc_v14_1.xls"
ARCHIVO_UNSPSC_CSV = RAW_DIR / "clasificador_unspsc.csv"
ARCHIVO_METADATA_EXTRACCION = RAW_DIR / "metadata_extraccion.json"

# Archivos limpios e integrados en data/processed/
ARCHIVO_PAA_LIMPIO = PROCESSED_DIR / "paa_limpio.csv"
ARCHIVO_CONTRATOS_LIMPIO = PROCESSED_DIR / "contratos_limpio.csv"
ARCHIVO_CRUCE_ENTIDAD_ANIO = PROCESSED_DIR / "cruce_entidad_anio.csv"
ARCHIVO_CRUCE_SEGMENTO = PROCESSED_DIR / "cruce_entidad_anio_segmento.csv"
ARCHIVO_AUDITORIA_CALIDAD = PROCESSED_DIR / "auditoria_calidad.json"
ARCHIVO_HALLAZGOS_PILOTO_MD = PROJECT_ROOT / "docs" / "hallazgos_piloto.md"

# Umbral para marcar posibles registros duplicados administrativos gigantes en PAA (50 mil millones COP)
UMBRAL_DUPLICADO_ATIPICO_PAA_COP = 50_000_000_000


def obtener_entidades(modo: str = MODO_MUESTRA_DEFECTO) -> dict:
    """Retorna el diccionario de entidades según el modo ('piloto' o 'completo')."""
    if modo == "piloto":
        return ENTIDADES_PILOTO
    if modo == "completo":
        return ENTIDADES_COMPLETO
    raise ValueError(f"Modo de muestra no reconocido: {modo!r}. Use 'piloto' o 'completo'.")
