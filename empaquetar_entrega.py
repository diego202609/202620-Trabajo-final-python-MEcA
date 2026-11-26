"""Empaqueta el entregable final autocontenido (entrega_grupo3_acontraluz.zip).

Incluye únicamente los artefactos requeridos para ejecutar de forma autónoma y sin
internet tanto A_contraluz_tutorial.ipynb como app_streamlit.py, excluyendo archivos
temporales, entornos virtuales, historiales Git y borradores internos.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from src.config import PROJECT_ROOT

NOMBRE_ZIP_DEFECTO = "entrega_grupo3_acontraluz.zip"

# Lista explícita y auditada de archivos incluidos en el paquete de entrega
ARCHIVOS_ENTREGA_RELATIVOS = [
    # Raíz del entregable
    "A_contraluz_tutorial.ipynb",
    "app_streamlit.py",
    "empaquetar_entrega.py",
    "README.md",
    "requirements.txt",
    ".env.example",
    # Código fuente modular
    "src/__init__.py",
    "src/config.py",
    "src/ingesta.py",
    "src/limpieza_cruce.py",
    "src/indicadores.py",
    "src/visualizacion.py",
    # Documentación metodológica y trazabilidad Rubro 5
    "docs/decisiones.md",
    "docs/rubro5_uso_ia.md",
    # Diccionario y caché congelado de datos crudos (API Socrata + UNSPSC)
    "data/README.md",
    "data/raw/paa_encabezado.csv",
    "data/raw/paa_detalle.csv",
    "data/raw/contratos_secop2.csv",
    "data/raw/clasificador_unspsc.csv",
    "data/raw/metadata_extraccion.json",
    # Datos limpios y cruzados
    "data/processed/README.md",
    "data/processed/paa_limpio.csv",
    "data/processed/contratos_limpio.csv",
    "data/processed/cruce_entidad_anio.csv",
    "data/processed/cruce_entidad_anio_segmento.csv",
    "data/processed/auditoria_calidad.json",
    # Contratos finales para Notebook y Streamlit
    "data/dashboard_data/README.md",
    "data/dashboard_data/resumen_entidad_anio.csv",
    "data/dashboard_data/modalidades_entidad_anio.csv",
    "data/dashboard_data/concentracion_proveedores.csv",
    "data/dashboard_data/top_proveedores_entidad.csv",
    "data/dashboard_data/brechas_segmento_unspsc.csv",
    "data/dashboard_data/distribucion_franjas_cuantia.csv",
    "data/dashboard_data/rubro5_antes_despues.csv",
    "data/dashboard_data/rubro5_registro_ia.json",
]

PATRONES_PROHIBIDOS = (
    ".git/",
    ".venv/",
    "__pycache__",
    ".pytest_cache",
    ".ipynb_checkpoints",
    "data/pruebas",
    "cartilla_",
    ".xls",
)


def construir_zip_entrega(ruta_zip: Path | None = None) -> dict[str, object]:
    """Construye el archivo .zip limpio y verifica la ausencia de basura o faltantes."""
    destino = ruta_zip or (PROJECT_ROOT / NOMBRE_ZIP_DEFECTO)

    faltantes = [rel for rel in ARCHIVOS_ENTREGA_RELATIVOS if not (PROJECT_ROOT / rel).exists()]
    if faltantes:
        raise FileNotFoundError(f"Faltan archivos obligatorios para el entregable .zip: {faltantes}")

    for rel in ARCHIVOS_ENTREGA_RELATIVOS:
        for prohibido in PATRONES_PROHIBIDOS:
            if prohibido in rel:
                raise ValueError(f"Ruta prohibida detectada en manifiesto de entrega: {rel}")

    with zipfile.ZipFile(destino, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for rel in ARCHIVOS_ENTREGA_RELATIVOS:
            ruta_abs = PROJECT_ROOT / rel
            zf.write(ruta_abs, arcname=rel)

    tamano_mb = round(destino.stat().st_size / (1024 * 1024), 2)
    return {
        "ruta_zip": str(destino),
        "n_archivos": len(ARCHIVOS_ENTREGA_RELATIVOS),
        "tamano_mb": tamano_mb,
        "archivos": list(ARCHIVOS_ENTREGA_RELATIVOS),
    }


def main() -> None:
    res = construir_zip_entrega()
    print("=== Paquete final generado exitosamente ===")
    print(f"  - Archivo: {res['ruta_zip']}")
    print(f"  - Archivos incluidos: {res['n_archivos']}")
    print(f"  - Tamaño comprimido: {res['tamano_mb']} MB")


if __name__ == "__main__":
    main()
