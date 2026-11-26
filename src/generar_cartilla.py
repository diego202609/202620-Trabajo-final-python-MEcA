# %% [markdown]
# # Generador de la Cartilla del Equipo (*A contra(luz)*)
#
# Produce automáticamente desde los datos verificados de las 6 entidades:
# 1. `docs/cartilla_equipo.md` (lectura directa en GitHub / VS Code).
# 2. `docs/cartilla_interactiva.html` (navegable con doble clic en cualquier navegador,
#    con menú lateral estilo Session 1–3, tarjetas KPI y las 6 gráficas Plotly interactivas).

# %%
from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd

from src.config import (
    ARCHIVO_AUDITORIA_CALIDAD,
    ARCHIVO_CARTILLA_HTML,
    ARCHIVO_CARTILLA_MD,
    ARCHIVO_CONTRATOS_LIMPIO,
    ARCHIVO_DASH_CONCENTRACION,
    ARCHIVO_DASH_FRANJAS_CUANTIA,
    ARCHIVO_DASH_RESUMEN_ANUAL,
    ARCHIVO_DASH_SEGMENTOS_UNSPSC,
    ARCHIVO_DASH_TOP_PROVEEDORES,
)
from src.visualizacion import (
    graficar_concentracion_hhi,
    graficar_contratacion_directa_entidades,
    graficar_distribucion_franjas_cuantia,
    graficar_evolucion_tasa_ejecucion,
    graficar_planeado_vs_ejecutado_entidad,
    graficar_top_brechas_unspsc,
)


def _fmt_mm(valor_cop: float) -> str:
    signo = "-" if valor_cop < 0 else ""
    mm = abs(float(valor_cop)) / 1e9
    txt = f"{mm:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{signo}${txt}"


def _fmt_cop(valor_cop: float) -> str:
    txt = f"{float(valor_cop):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${txt}"


def _fmt_pct(valor_pct: float) -> str:
    if pd.isna(valor_pct):
        return "—"
    return f"{float(valor_pct):.1f}%".replace(".", ",")


def _fmt_int(valor: float | int) -> str:
    if pd.isna(valor):
        return "0"
    return f"{int(round(float(valor))):,}".replace(",", ".")


# %%
def construir_prompt_rubro5(df_resumen: pd.DataFrame, aud: dict) -> str:
    """Construye el prompt metodológico estructurado listo para enviar a una IA externa (Rubro 5)."""
    entidades = ", ".join(sorted(df_resumen["sigla_entidad"].unique()))
    paa_tot = _fmt_mm(df_resumen["valor_paa_vigencia_sin_dup_atipico"].sum())
    ejec_tot = _fmt_mm(df_resumen["valor_ejecutado"].sum())
    n_cont = _fmt_int(aud["contratos_secop2"]["filas_finales"])
    n_paa = _fmt_int(aud["paa_detalle"]["filas_finales"])

    return (
        "Actúa como un economista experto en contratación pública y econometría aplicada en Colombia.\n\n"
        "CONTEXTO DEL PROYECTO:\n"
        f"Estamos desarrollando un estudio reproducible en Python sobre las desviaciones entre la planeación contractual "
        f"(Plan Anual de Adquisiciones - PAA, dataset 9sue-ezhx) y la ejecución contractual efectiva (Contratos Electrónicos "
        f"SECOP II, dataset jbjy-vk9h) entre 2022 y 2025 para 6 entidades nacionales del nivel central ({entidades}). "
        f"La base limpia integra {n_paa} ítems del PAA ({paa_tot} mil millones COP planeados ajustados) y {n_cont} contratos "
        f"({ejec_tot} mil millones COP ejecutados), cruzados al 99,8%+ con el Clasificador UNSPSC v14.1 a nivel de Clase (6 dígitos) "
        "y Segmento (2 dígitos).\n\n"
        "METODOLOGÍA ACTUAL YA IMPLEMENTADA (RECOMENDACIONES BASE DE LOS PROFESORES):\n"
        "1. Limpieza auditada: rescate de modalidades 'No Definido' desde causal_de_contratacion (Ley 1150/2007), marcación de "
        "contratos sin cuantía ($0 en Acuerdos Marco y cuantías simbólicas <= $1.000 COP) y detección de cuasi-duplicados "
        "administrativos >= $50.000 millones COP en el PAA.\n"
        "2. Indicadores descriptivos nominales por entidad y año: (a) tasa de ejecución (% ejecutado / planeado vigencia actual), "
        "(b) peso de la contratación directa en número y valor, (c) concentración por proveedor (CR1, CR5 e Índice HHI en escala "
        "0–10.000), y (d) brechas en pesos corrientes por segmento UNSPSC.\n\n"
        "OBJETIVO Y RESTRICCIONES:\n"
        "Propón entre 3 y 4 mejoras metodológicas rigurosas desde la teoría económica o el análisis estadístico de compras públicas "
        "que vayan MÁS ALLÁ de los indicadores descriptivos nominales anteriores para responder mejor en dónde y por qué se desvía "
        "la ejecución frente a la planeación. Ten en cuenta estas restricciones reales:\n"
        "- El panel agregado tiene N = 24 observaciones entidad-año (6 entidades × 4 años), aunque a nivel micro tenemos decenas "
        "de miles de contratos con fecha exacta de firma, modalidad, proveedor y segmento UNSPSC.\n"
        "- No existe un identificador único oficial que conecte 1 a 1 una línea del PAA con un id_contrato individual.\n"
        "- Las mejoras deben poder implementarse en Python (pandas/numpy) sin requerir fuentes privadas.\n"
        "Para cada mejora propuesta indica: (1) qué sesgo o limitación corrige, (2) su formulación matemática exacta y "
        "(3) sus posibles riesgos o supuestos."
    )


# %%
def generar_cartilla(
    ruta_md: Path = ARCHIVO_CARTILLA_MD,
    ruta_html: Path = ARCHIVO_CARTILLA_HTML,
) -> tuple[Path, Path]:
    """Genera docs/cartilla_equipo.md y docs/cartilla_interactiva.html con cifras de las 6 entidades."""
    aud = json.loads(ARCHIVO_AUDITORIA_CALIDAD.read_text(encoding="utf-8"))
    df_resumen = pd.read_csv(ARCHIVO_DASH_RESUMEN_ANUAL, dtype={"codigo_entidad": str})
    df_conc = pd.read_csv(ARCHIVO_DASH_CONCENTRACION, dtype={"codigo_entidad": str})
    df_top_prov = pd.read_csv(ARCHIVO_DASH_TOP_PROVEEDORES, dtype={"codigo_entidad": str})
    df_seg = pd.read_csv(ARCHIVO_DASH_SEGMENTOS_UNSPSC, dtype={"codigo_entidad": str, "codigo_segmento": str})
    df_franjas = pd.read_csv(ARCHIVO_DASH_FRANJAS_CUANTIA)
    df_cont = pd.read_csv(ARCHIVO_CONTRATOS_LIMPIO, low_memory=False)

    ap = aud["paa_detalle"]
    ac = aud["contratos_secop2"]

    # Ejemplos reales verificados de cuantías simbólicas (0 < valor <= 1000) y micro-compras (1001..1M)
    ej_simb = (
        df_cont[(df_cont["valor_del_contrato"] > 0) & (df_cont["valor_del_contrato"] <= 1_000)]
        .sort_values("valor_del_contrato")
        .head(6)
    )
    ej_micro = (
        df_cont[(df_cont["valor_del_contrato"] > 1_000) & (df_cont["valor_del_contrato"] <= 1_000_000)]
        .sort_values("valor_del_contrato")
        .head(6)
    )
    ej_sobre = df_resumen[df_resumen["pct_ejecucion_sobre_vigencia_sin_dup"] > 100.0].sort_values(
        "pct_ejecucion_sobre_vigencia_sin_dup", ascending=False
    )

    franjas_todas = df_franjas[df_franjas["sigla_entidad"] == "TODAS"].sort_values("orden_franja")
    prompt_ia = construir_prompt_rubro5(df_resumen, aud)

    total_paa_bruto = float(df_resumen["valor_paa_vigencia"].sum())
    total_paa_ajust = float(df_resumen["valor_paa_vigencia_sin_dup_atipico"].sum())
    total_paa_con_vf = float(df_resumen["valor_paa_total"].sum())
    total_ejec = float(df_resumen["valor_ejecutado"].sum())
    pct_ejec_global = 100.0 * total_ejec / max(total_paa_ajust, 1.0)

    # Construir tablas Markdown
    filas_franjas_md = [
        f"| {int(r['orden_franja'])} | **{r['franja_cuantia']}** | `{r['regla_cop']}` | {_fmt_int(r['n_contratos'])} "
        f"| {_fmt_pct(r['pct_contratos'])} | {_fmt_mm(r['valor_total_cop'])} | {_fmt_pct(r['pct_valor'])} "
        f"| {r['modalidad_predominante']} | {r['tratamiento_limpieza']} |"
        for _, r in franjas_todas.iterrows()
    ]

    filas_simb_md = [
        f"| **{r['sigla_entidad']}** | {int(r['anio'])} | `{_fmt_cop(r['valor_del_contrato'])}` | {r['modalidad_de_contratacion']} | {r['tipo_de_contrato']} | {str(r['nombre_proveedor_limpio'])[:42]} |"
        for _, r in ej_simb.iterrows()
    ]

    filas_micro_md = [
        f"| **{r['sigla_entidad']}** | {int(r['anio'])} | `{_fmt_cop(r['valor_del_contrato'])}` | {r['modalidad_de_contratacion']} | {r['tipo_de_contrato']} | {str(r['nombre_proveedor_limpio'])[:42]} |"
        for _, r in ej_micro.iterrows()
    ]

    filas_anual_md = [
        f"| **{r['sigla_entidad']}** | {int(r['anio'])} | {_fmt_int(r['version_encabezado'])} | {_fmt_mm(r['valor_paa_vigencia_sin_dup_atipico'])} "
        f"| {_fmt_mm(r['valor_ejecutado'])} | **{_fmt_pct(r['pct_ejecucion_sobre_vigencia_sin_dup'])}** "
        f"| {_fmt_pct(r['pct_valor_contratacion_directa'])} | {_fmt_int(r['hhi_proveedores'])} ({r['categoria_hhi']}) |"
        for _, r in df_resumen.iterrows()
    ]

    casos_sobre_txt = (
        ", ".join(
            f"`{r['sigla_entidad']} {int(r['anio'])}` ({_fmt_pct(r['pct_ejecucion_sobre_vigencia_sin_dup'])})"
            for _, r in ej_sobre.iterrows()
        )
        if len(ej_sobre) > 0
        else "ninguno en el agregado anual"
    )

    # ==================== 1. MARKDOWN CARTILLA ====================
    md_lines = [
        "# Cartilla Maestra del Equipo — Proyecto *A contra(luz)* (Grupo 3)",
        "",
        "> **Propósito:** Guía interna completa para que **Diego, Juan Sebastián y Nathalia** dominen cada decisión técnica, económica y jurídica del proyecto sobre las **6 entidades definitivas (`2022–2025`)**. *(Para explorar las 6 gráficas interactivas con zoom y tooltips, abran con doble clic `docs/cartilla_interactiva.html` en cualquier navegador).* ",
        "",
        "---",
        "",
        "## Capítulo 1. Arquitectura del Proyecto: Qué Hicimos y Dónde Está Todo",
        "",
        "Siguiendo lo aprendido en `coding-agents-for-data-science` (Sesiones 1–3) y `Taller 2 Webscraping`, separamos el código pesado en módulos limpios dentro de `src/` que se comunican mediante **contratos CSV**:",
        "",
        "| Capa / Archivo | Qué hace exactamente | Salida que genera |",
        "|---|---|---|",
        "| `src/config.py` | Centraliza rutas relativas, semilla (`42`), los 6 códigos/NITs de entidades y umbrales (`$1.000` simbólico, `$50.000M` duplicado PAA). | Constantes compartidas |",
        f"| `src/ingesta.py` | Consulta la API Socrata de `datos.gov.co` (`b6m4-qgqv`, `9sue-ezhx`, `jbjy-vk9h`) con paginación y reintentos, y convierte el Excel `.xls` del Clasificador UNSPSC v14.1. | `data/raw/*.csv` (`{_fmt_int(ap['filas_finales'])}` ítems PAA, `{_fmt_int(ac['filas_finales'])}` contratos, `49.022` productos UNSPSC) |",
        "| `src/limpieza_cruce.py` | Audita tipos, faltantes, duplicados y atípicos; rescata modalidades desde `causal_de_contratacion`; cruza UNSPSC a nivel Clase (`6d`) y Segmento (`2d`). | `data/processed/*.csv` + `auditoria_calidad.json` |",
        "| `src/indicadores.py` | Calcula tasa de ejecución, contratación directa, concentración por proveedor (`CR1`, `CR5`, `HHI`), brechas UNSPSC y las 7 franjas de cuantías. | `data/dashboard_data/*.csv` (`6` tablas listas para graficar) |",
        "| `src/visualizacion.py` | Funciones puras en **Plotly** con paleta accesible de alto contraste (`acontraluz-charts`), reutilizadas sin duplicar código en Notebook, Streamlit y Cartilla HTML. | Objetos `plotly.graph_objects.Figure` |",
        "| `tests/` | Suite offline con `pytest` y fixtures reales recortados de la API (corre sin internet en segundos). | Verificación automática |",
        "",
        "---",
        "",
        "## Capítulo 2. Respuestas Detalladas a las 5 Inquietudes del Equipo (con Cifras de las 6 Entidades)",
        "",
        "### 2.1 ¿Qué se entiende por «Definido» y «No definido» en las modalidades del PAA?",
        f"- **Origen exacto del término:** En la tabla oficial `9sue-ezhx` de `datos.gov.co`, el campo `modalidad` trae literalmente la cadena `\"No Definido\"` en **`{_fmt_int(ap['items_modalidad_cruda_no_definida'])}` ítems** de las 6 entidades.",
        f"- **Nuestro rescate jurídico-técnico:** Al inspeccionar la columna vecina `causal_de_contratacion`, descubrimos que cuando las entidades suben su PAA mediante plantilla Excel de SECOP II, muchas veces diligencian el código de la causal legal (ej. `CCE-16-Servicios_profesionales_gestion`, `CCE-02-Licitacion_Publica`, `CCE-06-Seleccion_Abreviada_Menor_Cuantia`), pero la vista abierta deja `modalidad` como `\"No Definido\"`. Usando el Estatuto General de Contratación (**Ley 1150 de 2007, art. 2**), rescatamos automáticamente **`{_fmt_int(ap['items_modalidad_recuperada_de_causal'])}` ítems ({_fmt_mm(ap['valor_modalidad_recuperada_de_causal_cop'])} MM)**.",
        f"- **Definición final limpia:**",
        f"  - **Modalidad Definida:** tiene modalidad explícita o causal legal identificable (`{_fmt_int(ap['filas_finales'] - ap['items_modalidad_no_definida'])}` de `{_fmt_int(ap['filas_finales'])}` ítems = `{_fmt_pct(100.0 * (ap['filas_finales'] - ap['items_modalidad_no_definida']) / ap['filas_finales'])}`).",
        f"  - **Modalidad «No definido»:** la entidad dejó sin diligenciar **tanto** `modalidad` como `causal_de_contratacion` (`{_fmt_int(ap['items_modalidad_no_definida'])}` ítems = `{_fmt_pct(100.0 * ap['items_modalidad_no_definida'] / ap['filas_finales'])}`), reflejando una omisión administrativa real en la planeación.",
        "",
        "### 2.2 ¿Cómo son posibles porcentajes de ejecución mayores al 100%?",
        f"En nuestro panel de 24 observaciones (6 entidades × 4 años), observamos tasas `> 100%` en: {casos_sobre_txt} (y también en segmentos UNSPSC específicos). Esto ocurre por **cuatro mecanismos legales y contables reales**:",
        "1. **Asimetría contable en contratos plurianuales con Vigencias Futuras (Ley 819 de 2003, arts. 10–12):** En `Contratos SECOP II` (`jbjy-vk9h`), la variable `valor_del_contrato` registra el **100% del compromiso plurianual en el año de la firma** (ej. MinHacienda firmó en agosto de 2025 el contrato `CONSORCIO PAC FONPET 2025` hasta 2030 por `$62,37 MM`), mientras que en el PAA el campo `valor_esperado_de_presupuesto` registra únicamente la **apropiación de ese año fiscal**.",
        f"2. **Adiciones contractuales en valor (Ley 80 de 1993, art. 40, parágrafo):** La ley permite adicionar cualquier contrato estatal hasta en un **50% de su valor inicial expresado en SMLMV** mediante otrosíes. SECOP II actualiza `valor_del_contrato` al monto modificado acumulado, superando el estimado inicial del PAA.",
        "3. **Carácter flexible e indicativo del PAA (Decreto 1082 de 2015, arts. 2.2.1.1.1.4.1 a 2.2.1.1.1.4.4):** El PAA es un documento de naturaleza informativa que **no obliga** a las entidades a efectuar los procesos exactamente como se estimaron, y puede recibir recursos nuevos por **traslados o adiciones del Presupuesto General de la Nación (PGN)** o atender urgencias manifiestas.",
        "4. **Reclasificación de códigos UNSPSC al contratar:** Una entidad puede planear un proyecto bajo el segmento `84` (Servicios financieros) o `80` (Gestión) en el PAA y adjudicarlo finalmente bajo el segmento `93` (Asuntos cívicos/administración pública), generando `< 100%` en el primero y `> 100%` en el segundo.",
        "",
        "### 2.3 Distribución de cuantías de los contratos y explicación por franja (`6 entidades, 2022–2025`)",
        "*(En `docs/cartilla_interactiva.html` encuentran el gráfico interactivo completo de doble panel).* ",
        "",
        "| # | Franja de cuantía (`COP`) | Criterio | # Contratos | % Contratos | Valor Total (`$ MM`) | % del Dinero | Modalidad predominante | Regla aplicada |",
        "|---:|---|---|---:|---:|---:|---:|---|---|",
        *filas_franjas_md,
        "",
        "**¿Cómo se explica cada franja (especialmente los valores muy bajos `< $1.000.000 COP`)?**",
        f"- **Franja 1 (`= $0`, `{_fmt_int(ac['contratos_valor_exacto_cero'])}` contratos):** No son errores; la mayoría (`{_fmt_int(ac['contratos_sin_cuantia_acuerdo_marco'])}`) son **Acuerdos Marco de Precios** suscritos por ANCP para habilitar catálogos en la Tienda Virtual sin gasto propio inicial, más comodatos y convenios interadministrativos sin flujo de caja.",
        f"- **Franja 2 (`$0,01 – $1.000 COP`, `{_fmt_int(ac['contratos_cuantia_simbolica_hasta_1000'])}` contratos — cuantías simbólicas «dummy»):** En contratos de **monto agotable, bolsas de precios unitarios o acuerdos marco** (ej. combustible de aviación o reciclaje), cuando un flujo del formulario electrónico de SECOP II exige digitar un número mayor a cero, el comprador público ingresa `$0,01`, `$0,10`, `$1` o `$2` como valor nominal de referencia. Por eso en nuestra limpieza los marcamos con `es_cuantia_simbolica = True`.",
        "- **Franja 3 (`$1.001 – $1.000.000 COP` — micro-compras reales):** Son compras reales de bajo monto por mínima cuantía o contratación directa: publicación obligatoria de avisos legales en diarios nacionales (*El Tiempo/CEET*, *La República*, *El Espectador*), correo certificado (*4-72*) o certificados de firma digital (*Camerfirma*).",
        "- **Franja 5 (`$10M – $100M COP` — la gran masa de contratos):** Concentra cerca de dos terceras partes de todos los contratos firmados porque corresponde a los honorarios anuales de **prestación de servicios profesionales y de apoyo a la gestión** en los ministerios y departamentos administrativos.",
        "- **Franja 7 (`> $1.000M COP` — la concentración del dinero):** Aunque son muy pocos contratos en cantidad, concentran la mayoría absoluta del presupuesto ejecutado (grandes licitaciones, fiducias, seguros previsionales y convenios con organismos internacionales).",
        "",
        "**Ejemplos reales en nuestra base de cuantías simbólicas (`$0,01 – $1.000 COP`):**",
        "",
        "| Entidad | Año | Valor Registrado | Modalidad | Tipo de Contrato | Proveedor |",
        "|---|---:|---:|---|---|---|",
        *filas_simb_md,
        "",
        "**Ejemplos reales en nuestra base de micro-compras legítimas (`$1.001 – $1.000.000 COP`):**",
        "",
        "| Entidad | Año | Valor Registrado | Modalidad | Tipo de Contrato | Proveedor |",
        "|---|---:|---:|---|---|---|",
        *filas_micro_md,
        "",
        "### 2.4 ¿Qué elementos procedimentales y de ley justifican cuantías menores o iguales a `$0`?",
        f"- **Estrictamente menores a `$0` (`< 0`):** Verificamos que en los `{_fmt_int(ac['filas_finales'])}` contratos y `{_fmt_int(ap['filas_finales'])}` ítems PAA existen **`0` valores negativos**. En el derecho público colombiano no existe un contrato estatal de cuantía negativa (las deducciones, multas o liberaciones de saldos se registran en liquidación, nunca como valor inicial negativo).",
        "- **Iguales a `$0` (`== 0`):** Están plenamente respaldados por cuatro figuras jurídicas:",
        "  1. **Acuerdos Marco de Precios (Ley 1150/2007, art. 2 num. 2 lit. a; Decreto 1082/2015):** ANCP selecciona proveedores y fija precios techo por catálogo (`$0` de compromiso propio); el gasto presupuestal ocurre después en las órdenes de compra de cada entidad.",
        "  2. **Contratos de Comodato o préstamo de uso gratuito (Código Civil, art. 2200; Ley 9 de 1989, art. 38):** entrega gratuita de bienes muebles o inmuebles entre entidades o sin contraprestación dineraria.",
        "  3. **Convenios interadministrativos o de asociación sin erogación presupuestal (Ley 489 de 1998, arts. 95–96; Decreto 092 de 2017):** cooperación técnica, intercambio de información o alianzas donde los aportes son en especie/capacidad institucional.",
        "  4. **Contratos de concesión o aprovechamiento económico sin desembolso estatal** (donde el privado asume el riesgo o paga contraprestación).",
        "",
        "### 2.5 ¿Qué es la «referencia económica estándar» (`HHI`) y cómo entender las «Vigencias Futuras»?",
        "- **Índice Herfindahl-Hirschman (`HHI`):** Mide qué tan concentrado está el gasto de una entidad entre sus proveedores en un año. Si el proveedor $i$ recibe un porcentaje $s_i$ del gasto anual (de $0$ a $100$), entonces $\\text{HHI} = \\sum_i s_i^2$ (escala de `0` a `10.000`):",
        "  - Si 1 solo proveedor se lleva el `100%` del presupuesto → $\\text{HHI} = 100^2 = 10.000$ (monopolio total).",
        "  - Si 100 proveedores se llevan `1%` cada uno → $\\text{HHI} = 100 \\times 1^2 = 100$ (atomización).",
        "  - **Umbrales internacionales estándar** (*U.S. Department of Justice & Federal Trade Commission Horizontal Merger Guidelines*, adoptados en análisis de competencia por la **SIC en Colombia** y la OCDE): **`< 1.500`** baja concentración, **`1.500 – 2.500`** concentración moderada, **`> 2.500`** alta concentración.",
        f"- **Vigencias Futuras (Ley Orgánica 819 de 2003, arts. 10–12; Estatuto Orgánico del Presupuesto Decreto 111/1996):**",
        "  - En Colombia rige el **principio de anualidad**: el presupuesto aprobado para 2024 solo puede ejecutarse hasta el 31 de diciembre de 2024.",
        "  - Pero muchos bienes y servicios críticos (seguros, nube tecnológica, interventorías, obras, vigilancia continua desde el 1 de enero del año siguiente) superan el 31 de diciembre.",
        f"  - Para poder firmar hoy un contrato que compromete caja de años venideros, el **CONFIS** y el Ministerio de Hacienda otorgan un cupo de **Vigencias Futuras** (ordinarias si inician con presupuesto del año actual, o excepcionales en casos estratégicos). En nuestra base de 6 entidades hay **`{_fmt_int(ap['items_con_vigencias_futuras'])}` ítems PAA** con vigencias futuras, que suman **{_fmt_mm(total_paa_con_vf - total_paa_bruto)} MM** por encima del presupuesto exclusivo del año corriente.",
        "",
        "---",
        "",
        "## Capítulo 3. Panorama Consolidado de las 6 Entidades Definitivas (`2022–2025`)",
        "",
        f"- **Total planeado ajustado (vigencia actual):** **{_fmt_mm(total_paa_ajust)} MM** *(bruto antes de control de cuasi-duplicados: {_fmt_mm(total_paa_bruto)} MM)*.",
        f"- **Total contratado válido en SECOP II (`> $1.000 COP`):** **{_fmt_mm(total_ejec)} MM** (**{_fmt_pct(pct_ejec_global)}** de ejecución agregada).",
        f"- **Cuadre contable exacto entre `b6m4-qgqv` y `9sue-ezhx`:** diferencia máxima de `${aud['cuadre_exacto_paa_encabezado_max_diff_cop']:.4f} COP` en las 24 vigencias.",
        "",
        "| Entidad | Año | Versiones PAA | PAA Ajustado (`$ MM`) | Ejecutado (`$ MM`) | % Ejecución | % Valor Directa | HHI Proveedores |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        *filas_anual_md,
        "",
        "---",
        "",
        "## Capítulo 4. Prompt Listo para Copiar y Enviar a una IA (Rubro 5 — `4/20 pts`)",
        "",
        "Copia el siguiente bloque tal cual en una sesión limpia de ChatGPT, Claude o Gemini y pégame aquí su respuesta completa para integrarla al Notebook e implementar las mejoras acordadas (*IPC DANE + Índice de Disimilitud de Duncan*):",
        "",
        "```text",
        prompt_ia,
        "```",
    ]
    ruta_md.parent.mkdir(parents=True, exist_ok=True)
    ruta_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    # ==================== 2. HTML INTERACTIVO (ESTILO SESSION 1-3) ====================
    fig_franjas = graficar_distribucion_franjas_cuantia(df_franjas, "TODAS")
    fig_brecha = graficar_planeado_vs_ejecutado_entidad(df_resumen, usar_base_ajustada=True)
    fig_evol = graficar_evolucion_tasa_ejecucion(df_resumen, usar_base_ajustada=True)
    fig_directa = graficar_contratacion_directa_entidades(df_resumen)
    fig_hhi = graficar_concentracion_hhi(df_conc)
    fig_unspsc = graficar_top_brechas_unspsc(df_seg, top_n=10)

    div_franjas = fig_franjas.to_html(full_html=False, include_plotlyjs="cdn")
    div_brecha = fig_brecha.to_html(full_html=False, include_plotlyjs=False)
    div_evol = fig_evol.to_html(full_html=False, include_plotlyjs=False)
    div_directa = fig_directa.to_html(full_html=False, include_plotlyjs=False)
    div_hhi = fig_hhi.to_html(full_html=False, include_plotlyjs=False)
    div_unspsc = fig_unspsc.to_html(full_html=False, include_plotlyjs=False)

    filas_html_anual = "\n".join(
        f"<tr><td><b>{html.escape(str(r['sigla_entidad']))}</b></td><td>{int(r['anio'])}</td>"
        f"<td style='text-align:right'>{_fmt_int(r['version_encabezado'])}</td>"
        f"<td style='text-align:right'>{_fmt_mm(r['valor_paa_vigencia_sin_dup_atipico'])}</td>"
        f"<td style='text-align:right'>{_fmt_mm(r['valor_ejecutado'])}</td>"
        f"<td style='text-align:right'><b>{_fmt_pct(r['pct_ejecucion_sobre_vigencia_sin_dup'])}</b></td>"
        f"<td style='text-align:right'>{_fmt_pct(r['pct_valor_contratacion_directa'])}</td>"
        f"<td style='text-align:right'>{_fmt_int(r['hhi_proveedores'])} <span class='badge'>{html.escape(str(r['categoria_hhi']))}</span></td></tr>"
        for _, r in df_resumen.iterrows()
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Cartilla Interactiva del Equipo · A contra(luz)</title>
  <style>
    :root {{
      --navy: #0B3C5D;
      --copper: #C84E00;
      --teal: #1D7874;
      --bg: #F8FAFC;
      --card: #FFFFFF;
      --border: #E2E8F0;
      --text: #1E293B;
      --muted: #475569;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
    header {{ background: var(--navy); color: white; padding: 1.4rem 2rem; border-bottom: 4px solid var(--copper); }}
    header h1 {{ margin: 0; font-size: 1.45rem; }}
    header p {{ margin: 0.35rem 0 0; opacity: 0.9; font-size: 0.95rem; }}
    .layout {{ display: grid; grid-template-columns: 260px 1fr; max-width: 1440px; margin: 0 auto; min-height: calc(100vh - 85px); }}
    nav {{ background: white; border-right: 1px solid var(--border); padding: 1.25rem; position: sticky; top: 0; height: 100vh; overflow-y: auto; }}
    nav h3 {{ margin-top: 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }}
    nav a {{ display: block; padding: 0.45rem 0.6rem; color: var(--navy); text-decoration: none; border-radius: 6px; font-size: 0.92rem; margin-bottom: 0.2rem; }}
    nav a:hover {{ background: #EFF6FF; font-weight: 600; }}
    main {{ padding: 1.75rem 2.25rem; max-width: 1120px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin-bottom: 1.75rem; }}
    .kpi {{ background: var(--card); border: 1px solid var(--border); border-left: 4px solid var(--navy); border-radius: 10px; padding: 1rem 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    .kpi.copper {{ border-left-color: var(--copper); }}
    .kpi.teal {{ border-left-color: var(--teal); }}
    .kpi .label {{ font-size: 0.82rem; color: var(--muted); text-transform: uppercase; font-weight: 600; }}
    .kpi .val {{ font-size: 1.55rem; font-weight: 800; color: var(--text); margin: 0.2rem 0; }}
    .kpi .sub {{ font-size: 0.82rem; color: var(--muted); }}
    section.card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem 1.75rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
    h2 {{ color: var(--navy); margin-top: 0; border-bottom: 2px solid var(--border); padding-bottom: 0.45rem; font-size: 1.25rem; }}
    h3 {{ color: #0F172A; margin-top: 1.2rem; font-size: 1.05rem; }}
    .callout {{ background: #FFF7ED; border-left: 4px solid var(--copper); padding: 0.9rem 1.1rem; border-radius: 6px; margin: 1rem 0; font-size: 0.94rem; }}
    .callout.info {{ background: #F0F9FF; border-left-color: var(--navy); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-top: 0.8rem; }}
    th, td {{ padding: 0.55rem 0.7rem; border-bottom: 1px solid var(--border); text-align: left; }}
    th {{ background: #F1F5F9; color: var(--navy); font-weight: 700; position: sticky; top: 0; }}
    tr:hover td {{ background: #F8FAFC; }}
    .badge {{ background: #E2E8F0; padding: 0.12rem 0.45rem; border-radius: 999px; font-size: 0.76rem; }}
    pre {{ background: #0F172A; color: #F8FAFC; padding: 1rem; border-radius: 8px; overflow-x: auto; font-size: 0.85rem; white-space: pre-wrap; }}
    @media (max-width: 900px) {{ .layout {{ grid-template-columns: 1fr; }} nav {{ position: static; height: auto; }} }}
  </style>
</head>
<body>
  <header>
    <h1>🔦 Cartilla Interactiva del Equipo — A contra(luz) (Grupo 3)</h1>
    <p>Diego Andrés Niño (201719748) · Juan Sebastián Puerto (201532975) · Nathalia Alexandra Acero (202524470) — Muestra definitiva: 6 entidades nacionales (2022–2025)</p>
  </header>
  <div class="layout">
    <nav>
      <h3>En esta cartilla</h3>
      <a href="#resumen">1. Resumen y KPIs (6 entidades)</a>
      <a href="#arquitectura">2. Qué hace cada archivo</a>
      <a href="#duda1">3. Definido vs. No definido</a>
      <a href="#duda2">4. ¿Por qué hay ejecución &gt; 100%?</a>
      <a href="#duda3">5. Gráfica de cuantías y &lt;$100k</a>
      <a href="#duda4">6. Cuantías = $0 y marco legal</a>
      <a href="#duda5">7. Estándar HHI y Vigencias Futuras</a>
      <a href="#panorama">8. Gráficas interactivas clave</a>
      <a href="#tabla24">9. Tabla maestra (24 vigencias)</a>
      <a href="#prompt">10. Prompt listo para Rubro 5 (IA)</a>
    </nav>
    <main>
      <div id="resumen" class="kpi-grid">
        <div class="kpi">
          <div class="label">Planeado PAA Ajustado (2022–2025)</div>
          <div class="val">{_fmt_mm(total_paa_ajust)} MM</div>
          <div class="sub">{_fmt_int(ap['filas_finales'])} ítems en 6 entidades nacionales</div>
        </div>
        <div class="kpi copper">
          <div class="label">Contratado en SECOP II (&gt; $1.000)</div>
          <div class="val">{_fmt_mm(total_ejec)} MM</div>
          <div class="sub">{_fmt_int(ac['contratos_validos_con_cuantia'])} contratos válidos con cuantía</div>
        </div>
        <div class="kpi teal">
          <div class="label">Tasa Global de Ejecución</div>
          <div class="val">{_fmt_pct(pct_ejec_global)}</div>
          <div class="sub">Cuadre Encabezado vs Detalle: $0,00 COP</div>
        </div>
        <div class="kpi">
          <div class="label">Cruce Clasificador UNSPSC</div>
          <div class="val">{_fmt_pct(ap['tasa_match_unspsc_clase_segmento_pct'])} / {_fmt_pct(ac['tasa_match_unspsc_clase_segmento_pct'])}</div>
          <div class="sub">PAA / Contratos a nivel Clase (6d) y Segmento (2d)</div>
        </div>
      </div>

      <section id="arquitectura" class="card">
        <h2>1. Mapa rápido del código: qué hace cada archivo</h2>
        <p>Separamos el trabajo pesado en módulos Python (<code>src/</code>) que producen tablas limpias en <code>data/processed/</code> y <code>data/dashboard_data/</code>. Así el <b>Jupyter Notebook</b> y <b>Streamlit</b> quedan limpios, rápidos y sin código repetido:</p>
        <ul>
          <li><b><code>src/config.py</code></b>: rutas relativas, semilla <code>42</code>, lista de las 6 entidades y umbrales metodológicos (<code>$1.000 COP</code> cuantía simbólica; <code>$50.000M COP</code> cuasi-duplicado PAA).</li>
          <li><b><code>src/ingesta.py</code></b>: descarga paginada desde la API Socrata de <code>datos.gov.co</code> y conversión del Excel <code>.xls</code> del Clasificador UNSPSC v14.1, guardando caché local en <code>data/raw/</code>.</li>
          <li><b><code>src/limpieza_cruce.py</code></b>: audita calidad, rescata modalidades desde <code>causal_de_contratacion</code>, homologa estados y cruza UNSPSC a 6, 4 y 2 dígitos.</li>
          <li><b><code>src/indicadores.py</code></b>: genera los 6 CSVs finales en <code>data/dashboard_data/</code> con su diccionario <code>README.md</code>.</li>
          <li><b><code>src/visualizacion.py</code></b>: funciones Plotly accesibles (alto contraste y símbolos distintos por serie).</li>
        </ul>
      </section>

      <section id="duda1" class="card">
        <h2>2. ¿Qué significa «Definido» vs. «No definido» en el PAA?</h2>
        <p>En la base abierta del PAA (<code>9sue-ezhx</code>), cuando una entidad carga líneas por plantilla sin llenar el campo de modalidad, la plataforma escribe literalmente <code>"No Definido"</code> (ocurría en <b>{_fmt_int(ap['items_modalidad_cruda_no_definida'])}</b> filas crudas).</p>
        <div class="callout info">
          <b>Rescate jurídico implementado:</b> revisando la columna vecina <code>causal_de_contratacion</code> (códigos oficiales como <code>CCE-16-Servicios_profesionales_gestion</code> o <code>CCE-02-Licitacion_Publica</code>) bajo la <b>Ley 1150 de 2007 (art. 2)</b>, recuperamos la modalidad exacta de <b>{_fmt_int(ap['items_modalidad_recuperada_de_causal'])} ítems ({_fmt_mm(ap['valor_modalidad_recuperada_de_causal_cop'])} MM)</b>. Solo quedaron <b>{_fmt_int(ap['items_modalidad_no_definida'])} ítems</b> como «No definido» real (donde ambas columnas estaban vacías).
        </div>
      </section>

      <section id="duda2" class="card">
        <h2>3. ¿Cómo es posible una ejecución mayor al 100% frente al PAA?</h2>
        <p>Casos con ejecución anual &gt; 100% en las 6 entidades: <b>{html.escape(casos_sobre_txt)}</b>. Cuatro razones legales y presupuestales lo explican:</p>
        <ol>
          <li><b>Contratos plurianuales con Vigencias Futuras (Ley 819 de 2003, arts. 10–12):</b> SECOP II registra el <b>valor total de todos los años del contrato</b> en el año en que se firma (p. ej. un contrato 2025–2030 de seguros/administración FONPET por <code>$62,37 MM</code> se suma íntegro en 2025), mientras el PAA de vigencia actual solo contiene la cuota presupuestal de ese año.</li>
          <li><b>Adiciones hasta del 50% en SMLMV (Ley 80 de 1993, art. 40):</b> <code>valor_del_contrato</code> en SECOP II acumula las adiciones firmadas mediante otrosíes después de la adjudicación.</li>
          <li><b>Carácter indicativo y no obligatorio del PAA (Decreto 1082 de 2015, arts. 2.2.1.1.1.4.1–4):</b> el PAA es una herramienta flexible de planeación, no un techo presupuestal rígido; las entidades reciben traslados/adiciones del PGN o atienden urgencias.</li>
          <li><b>Cambio de código UNSPSC entre planeación y adjudicación:</b> al precisar los estudios previos, un proceso planeado en un segmento UNSPSC puede adjudicarse bajo otro segmento conexo.</li>
        </ol>
      </section>

      <section id="duda3" class="card">
        <h2>4. Distribución de cuantías de los contratos y explicación de cada franja</h2>
        <p>Observa la asimetría extrema entre <b>cantidad de contratos (panel izquierdo)</b> y <b>dinero público comprometido (panel derecho)</b>:</p>
        {div_franjas}
        <div class="callout">
          <b>¿Por qué existen contratos entre $0,01 y $100.000 COP?</b><br/>
          • <b>Entre $0,01 y $1.000 COP ({_fmt_int(ac['contratos_cuantia_simbolica_hasta_1000'])} contratos):</b> son <b>cuantías simbólicas («dummy») de plataforma</b> en Acuerdos Marco de Precios (ej. combustible con Terpel por <code>$2 COP</code>) o procesos a precios unitarios/monto agotable donde el formulario web exigía digitar un número positivo. Los marcamos como <code>es_cuantia_simbolica = True</code> para no sesgar promedios.<br/>
          • <b>Entre $1.001 y $1.000.000 COP:</b> son <b>micro-compras reales</b> de mínima cuantía o directa (avisos legales obligatorios en prensa nacional como El Tiempo/La República, correo certificado 4-72 o tokens de firma digital).
        </div>
      </section>

      <section id="duda4" class="card">
        <h2>5. ¿Qué justifica cuantías iguales a $0 (y existen menores a $0)?</h2>
        <ul>
          <li><b>Menores a $0 (<code>&lt; 0</code>):</b> verificamos <b>0 casos</b> tanto en los {_fmt_int(ac['filas_finales'])} contratos como en los {_fmt_int(ap['filas_finales'])} ítems PAA. Jurídicamente no existen contratos estatales negativos.</li>
          <li><b>Iguales a $0 (<code>== 0</code>, {_fmt_int(ac['contratos_valor_exacto_cero'])} contratos):</b> respaldados legalmente por (a) <b>Acuerdos Marco de Precios</b> ({_fmt_int(ac['contratos_sin_cuantia_acuerdo_marco'])} casos en ANCP — Ley 1150/2007 y Decreto 1082/2015, donde las órdenes de compra posteriores de cada entidad son las que ejecutan presupuesto), (b) <b>Comodatos gratuitos</b> (Código Civil art. 2200) y (c) <b>Convenios interadministrativos o de asociación sin desembolso</b> (Ley 489/1998 arts. 95–96; Decreto 092/2017).</li>
        </ul>
      </section>

      <section id="duda5" class="card">
        <h2>6. Referencia económica estándar (HHI) y concepto de Vigencia Futura</h2>
        <h3>Índice Herfindahl-Hirschman (HHI)</h3>
        <p>Suma los cuadrados de las participaciones porcentuales de cada proveedor adjudicado en el año (<code>HHI = Σ s_i²</code>, de <code>0</code> a <code>10.000</code>). Los puntos de corte que usamos son el estándar internacional antimonopolio del <b>DOJ/FTC de EE. UU.</b> y de la <b>Superintendencia de Industria y Comercio (SIC)</b> en Colombia:</p>
        <ul>
          <li><b><code>HHI &lt; 1.500</code>:</b> mercado desconcentrado (gasto repartido entre muchos contratistas).</li>
          <li><b><code>1.500 ≤ HHI ≤ 2.500</code>:</b> concentración moderada.</li>
          <li><b><code>HHI &gt; 2.500</code>:</b> alta concentración (pocos contratistas absorben gran parte del presupuesto anual).</li>
        </ul>
        <h3>Vigencias Futuras (Ley 819 de 2003)</h3>
        <p>Excepción legal al <b>principio de anualidad presupuestal</b>: autorización previa del CONFIS / MinHacienda para asumir hoy obligaciones contractuales que afectarán presupuestos de años siguientes (por ejemplo, proyectos tecnológicos, fiducias o pólizas plurianuales). En las 6 entidades representan <b>{_fmt_int(ap['items_con_vigencias_futuras'])} ítems PAA</b> y explican <b>{_fmt_mm(total_paa_con_vf - total_paa_bruto)} MM</b> de diferencia entre el costo total proyectado y la cuota anual.</p>
      </section>

      <section id="panorama" class="card">
        <h2>7. Visualizaciones interactivas principales (6 entidades, 2022–2025)</h2>
        {div_brecha}
        <hr style="border:0;border-top:1px solid var(--border);margin:1.5rem 0"/>
        {div_evol}
        <hr style="border:0;border-top:1px solid var(--border);margin:1.5rem 0"/>
        {div_directa}
        <hr style="border:0;border-top:1px solid var(--border);margin:1.5rem 0"/>
        {div_hhi}
        <hr style="border:0;border-top:1px solid var(--border);margin:1.5rem 0"/>
        {div_unspsc}
      </section>

      <section id="tabla24" class="card">
        <h2>8. Tabla Maestra de las 24 Vigencias (6 Entidades × 4 Años)</h2>
        <table>
          <thead>
            <tr>
              <th>Entidad</th><th>Año</th><th style="text-align:right">Vers. PAA</th>
              <th style="text-align:right">PAA Ajustado ($ MM)</th><th style="text-align:right">Ejecutado ($ MM)</th>
              <th style="text-align:right">% Ejecución</th><th style="text-align:right">% Valor Directa</th>
              <th style="text-align:right">HHI Proveedores</th>
            </tr>
          </thead>
          <tbody>
            {filas_html_anual}
          </tbody>
        </table>
      </section>

      <section id="prompt" class="card">
        <h2>9. Prompt listo para copiar — Rubro 5 (Uso de IA más allá de la metodología)</h2>
        <p>Copia este texto en una conversación limpia de ChatGPT, Claude o Gemini y comparte su respuesta completa para integrarla al Notebook e implementar nuestras mejoras acordadas (<b>deflación con IPC DANE + Índice de Disimilitud de Duncan</b>):</p>
        <pre>{html.escape(prompt_ia)}</pre>
      </section>
    </main>
  </div>
</body>
</html>
"""
    ruta_html.write_text(html_doc, encoding="utf-8")
    return ruta_md, ruta_html


def main() -> None:
    ruta_md, ruta_html = generar_cartilla()
    print("Cartilla generada exitosamente:")
    print("  - Markdown:", ruta_md)
    print("  - HTML interactivo:", ruta_html)


if __name__ == "__main__":
    main()
