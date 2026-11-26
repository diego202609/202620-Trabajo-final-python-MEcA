"""Auditoría programática automática de cumplimiento de la Rúbrica (20/20) sobre A_contraluz_tutorial.ipynb y app_streamlit.py."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import nbformat

import app_streamlit
from src.config import PROJECT_ROOT

RUTA_NOTEBOOK = PROJECT_ROOT / "A_contraluz_tutorial.ipynb"
RUTA_STREAMLIT = PROJECT_ROOT / "app_streamlit.py"


def _cargar_notebook() -> nbformat.NotebookNode:
    assert RUTA_NOTEBOOK.exists(), f"No existe el notebook principal en {RUTA_NOTEBOOK}"
    return nbformat.read(RUTA_NOTEBOOK, as_version=4)


def test_encabezado_integrantes_codigos_y_pregunta_unica() -> None:
    nb = _cargar_notebook()
    primera = nb.cells[0]
    assert primera.cell_type == "markdown"
    texto = primera.source

    # Los 3 integrantes y sus códigos estudiantiles exactos (Rubro 1)
    for token in [
        "Diego Andrés Niño Estupiñán",
        "201719748",
        "Juan Sebastián Puerto Sanz",
        "201532975",
        "Nathalia Alexandra Acero Pérez",
        "202524470",
    ]:
        assert token in texto, f"Falta {token!r} en la celda de encabezado del notebook"

    # Exactamente una pregunta central delimitada
    signos_cierre = texto.count("?")
    assert signos_cierre == 1, f"El encabezado debe formular 1 única pregunta central; tiene {signos_cierre} signos '?'"


def test_unica_celda_de_imports_sin_paquetes_sin_usar() -> None:
    nb = _cargar_notebook()
    celdas_codigo = [c for c in nb.cells if c.cell_type == "code"]
    assert len(celdas_codigo) >= 6

    indices_con_import = []
    nombres_importados: dict[str, str] = {}

    for idx, celda in enumerate(celdas_codigo):
        arbol = ast.parse(celda.source)
        for nodo in ast.walk(arbol):
            if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                indices_con_import.append(idx)
                for alias in nodo.names:
                    nombre_local = alias.asname or alias.name.split(".")[0]
                    nombres_importados[nombre_local] = alias.name

    # Todos los imports deben estar exclusivamente en la primera celda de código (índice 0)
    assert set(indices_con_import) == {0}, (
        f"Existen sentencias import fuera de la única celda de paquetes (índices de código: {set(indices_con_import)})"
    )
    assert "RANDOM_SEED = 42" in celdas_codigo[0].source

    # Verificar que cada símbolo importado se utilice efectivamente en el resto del notebook
    codigo_posterior = "\n\n".join(c.source for c in celdas_codigo[1:])
    codigo_celda_cero_sin_imports = "\n".join(
        linea
        for linea in celdas_codigo[0].source.splitlines()
        if not linea.strip().startswith(("import ", "from ")) and not linea.strip().startswith((")", "("))
    )
    universo_uso = codigo_celda_cero_sin_imports + "\n" + codigo_posterior

    sin_uso = [
        simbolo
        for simbolo in nombres_importados
        if re.search(rf"\b{re.escape(simbolo)}\b", universo_uso) is None
    ]
    assert not sin_uso, f"Paquetes o funciones importados pero no usados en el notebook: {sin_uso}"


def test_cero_celdas_vacias_errores_o_rutas_absolutas() -> None:
    nb = _cargar_notebook()
    patron_ruta_abs = re.compile(r"([A-Za-z]:\\\\|[A-Za-z]:/|/Users/|/home/)")

    for i, celda in enumerate(nb.cells):
        assert celda.source.strip() != "", f"La celda {i} está vacía"
        assert not patron_ruta_abs.search(celda.source), (
            f"La celda {i} contiene una ruta absoluta prohibida por el Rubro 2"
        )
        if celda.cell_type == "code":
            assert celda.execution_count is not None, (
                f"La celda de código {i} no ha sido ejecutada (execution_count is None)"
            )
            for out in celda.get("outputs", []):
                assert out.get("output_type") != "error", (
                    f"La celda de código {i} produjo un error: {out.get('ename')}: {out.get('evalue')}"
                )


def test_introducciones_de_seccion_maximo_tres_lineas() -> None:
    nb = _cargar_notebook()
    secciones_principales = []

    for i, celda in enumerate(nb.cells):
        if celda.cell_type != "markdown":
            continue
        lineas = [ln.rstrip() for ln in celda.source.strip().splitlines()]
        if lineas and re.match(r"^##\s+\d+\.", lineas[0]):
            secciones_principales.append((i, lineas))

    assert len(secciones_principales) == 6, (
        f"Se esperaban las 6 secciones numeradas del tutorial; se hallaron {len(secciones_principales)}"
    )

    for idx_celda, lineas in secciones_principales:
        titulo = lineas[0]
        # Extraer el párrafo introductorio inmediatamente posterior al encabezado ## N.
        resto = [ln for ln in lineas[1:] if ln.strip() != ""]
        assert len(resto) >= 1, f"La sección {titulo!r} (celda {idx_celda}) no tiene introducción"
        # Contar líneas hasta el siguiente subtítulo (###) o bloque especial
        intro_lineas = []
        for ln in lineas[1:]:
            if ln.strip() == "" and not intro_lineas:
                continue
            if ln.strip() == "" and intro_lineas:
                break
            if ln.startswith("###") or ln.startswith("|") or ln.startswith(">") or ln.startswith("```"):
                break
            intro_lineas.append(ln)

        texto_intro = " ".join(intro_lineas)
        assert 1 <= len(intro_lineas) <= 3, (
            f"La introducción de {titulo!r} tiene {len(intro_lineas)} líneas Markdown (máximo 3)"
        )
        # Además controlar longitud total (<= 260 caracteres) para que tampoco supere 3 líneas visuales en pantalla
        assert len(texto_intro) <= 260, (
            f"La introducción de {titulo!r} mide {len(texto_intro)} caracteres (> 260, riesgo de pasar de 3 líneas visuales)"
        )


def test_seccion_rubro5_completa_y_streamlit_funcional() -> None:
    nb = _cargar_notebook()
    todo_md = "\n\n".join(c.source for c in nb.cells if c.cell_type == "markdown")

    # Verificar presencia íntegra del prompt, las 4 propuestas de la IA y la evaluación crítica (Rubro 5)
    for marcador in [
        "Actúa como un economista experto en contratación pública",
        "### 1. Deflactación Intertemporal a Precios Constantes",
        "### 2. Índice de Disimilitud Estructural de Duncan",
        "### 3. Concentración Estacional Intra-anual",
        "### 4. Emparejamiento Micro Bloqueado por Distancia Compuesta",
        "Descartamos la Mejora #4",
        "Limitaciones",
    ]:
        assert marcador in todo_md, f"Falta elemento obligatorio en el notebook: {marcador!r}"

    # Verificar carga limpia de contratos de datos y funciones de app_streamlit.py
    assert RUTA_STREAMLIT.exists()
    datos_app = app_streamlit.cargar_contratos_dashboard.__wrapped__()
    assert len(datos_app["resumen"]) == 24
    assert len(datos_app["rubro5_df"]) == 7
    assert app_streamlit.formatear_mm(1_500_000_000.0) == "$1.50 MM"
