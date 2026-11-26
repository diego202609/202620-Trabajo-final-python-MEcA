"""Tablero interactivo de veeduría ciudadana — A contra(luz): PAA vs. SECOP II (2022–2025).

Ejecución local desde la raíz del proyecto:
    streamlit run app_streamlit.py
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import streamlit as st

from src.config import (
    ARCHIVO_AUDITORIA_CALIDAD,
    ARCHIVO_DASH_CONCENTRACION,
    ARCHIVO_DASH_FRANJAS_CUANTIA,
    ARCHIVO_DASH_MODALIDADES,
    ARCHIVO_DASH_RESUMEN_ANUAL,
    ARCHIVO_DASH_RUBRO5_COMPARATIVA,
    ARCHIVO_DASH_RUBRO5_JSON,
    ARCHIVO_DASH_SEGMENTOS_UNSPSC,
    ARCHIVO_DASH_TOP_PROVEEDORES,
)
from src.visualizacion import (
    graficar_concentracion_hhi,
    graficar_contratacion_directa_entidades,
    graficar_distribucion_franjas_cuantia,
    graficar_evolucion_tasa_ejecucion,
    graficar_planeado_vs_ejecutado_entidad,
    graficar_rubro5_antes_despues_ipc,
    graficar_rubro5_ejecucion_vs_duncan,
    graficar_top_brechas_unspsc,
)

st.set_page_config(
    page_title="A contra(luz) — Planeación PAA vs. Ejecución SECOP II",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def cargar_contratos_dashboard() -> dict[str, object]:
    """Carga únicamente los contratos validados de data/dashboard_data/ y auditoría JSON."""
    resumen = pd.read_csv(ARCHIVO_DASH_RESUMEN_ANUAL, dtype={"codigo_entidad": str})
    modalidades = pd.read_csv(ARCHIVO_DASH_MODALIDADES, dtype={"codigo_entidad": str})
    concentracion = pd.read_csv(ARCHIVO_DASH_CONCENTRACION, dtype={"codigo_entidad": str})
    top_prov = pd.read_csv(
        ARCHIVO_DASH_TOP_PROVEEDORES,
        dtype={"codigo_entidad": str, "id_proveedor_limpio": str},
    )
    segmentos = pd.read_csv(
        ARCHIVO_DASH_SEGMENTOS_UNSPSC,
        dtype={"codigo_entidad": str, "codigo_segmento": str},
    )
    franjas = pd.read_csv(ARCHIVO_DASH_FRANJAS_CUANTIA)
    rubro5_df = pd.read_csv(ARCHIVO_DASH_RUBRO5_COMPARATIVA, dtype={"codigo_entidad": str})
    auditoria = json.loads(ARCHIVO_AUDITORIA_CALIDAD.read_text(encoding="utf-8"))
    rubro5_json = (
        json.loads(ARCHIVO_DASH_RUBRO5_JSON.read_text(encoding="utf-8"))
        if ARCHIVO_DASH_RUBRO5_JSON.exists()
        else {}
    )
    return {
        "resumen": resumen,
        "modalidades": modalidades,
        "concentracion": concentracion,
        "top_proveedores": top_prov,
        "segmentos": segmentos,
        "franjas": franjas,
        "rubro5_df": rubro5_df,
        "auditoria": auditoria,
        "rubro5_json": rubro5_json,
    }


def formatear_mm(valor_cop: float) -> str:
    """Formatea valores en pesos colombianos a miles de millones ($ MM)."""
    return f"${valor_cop / 1e9:,.2f} MM"


def renderizar_app() -> None:
    """Construye la interfaz interactiva completa de A contra(luz)."""
    datos = cargar_contratos_dashboard()
    df_resumen: pd.DataFrame = datos["resumen"]  # type: ignore[assignment]
    df_mod: pd.DataFrame = datos["modalidades"]  # type: ignore[assignment]
    df_conc: pd.DataFrame = datos["concentracion"]  # type: ignore[assignment]
    df_top_prov: pd.DataFrame = datos["top_proveedores"]  # type: ignore[assignment]
    df_seg: pd.DataFrame = datos["segmentos"]  # type: ignore[assignment]
    df_franjas: pd.DataFrame = datos["franjas"]  # type: ignore[assignment]
    df_rubro5: pd.DataFrame = datos["rubro5_df"]  # type: ignore[assignment]
    auditoria: dict = datos["auditoria"]  # type: ignore[assignment]
    rubro5_json: dict = datos["rubro5_json"]  # type: ignore[assignment]

    # --- Barra lateral de filtros ---
    st.sidebar.title("🔎 Filtros de Veeduría")
    todas_entidades = sorted(df_resumen["sigla_entidad"].unique().tolist())
    entidades_sel = st.sidebar.multiselect(
        "Entidades nacionales (nivel central):",
        options=todas_entidades,
        default=todas_entidades,
    )
    rango_anios = st.sidebar.slider(
        "Vigencias fiscales:",
        min_value=int(df_resumen["anio"].min()),
        max_value=int(df_resumen["anio"].max()),
        value=(2022, 2025),
        step=1,
    )
    modo_precios = st.sidebar.radio(
        "Expresión monetaria:",
        options=[
            "COP constantes de 2025 (IPC DANE — Mejora IA)",
            "COP corrientes (nominales)",
        ],
        index=0,
    )
    usar_constantes_2025 = modo_precios.startswith("COP constantes")

    modo_paa = st.sidebar.radio(
        "Base presupuestal del PAA:",
        options=[
            "Ajustada (sin cuasi-duplicado atípico >= $50.000M)",
            "Bruta publicada en SECOP II",
        ],
        index=0,
    )
    usar_base_ajustada = modo_paa.startswith("Ajustada")

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "**Grupo 3 — Taller de Python (Uniandes 2026-II)**\n\n"
        "- Diego Andrés Niño Estupiñán (`201719748`)\n"
        "- Juan Sebastián Puerto Sanz (`201532975`)\n"
        "- Nathalia Alexandra Acero Pérez (`202524470`)"
    )

    if not entidades_sel:
        st.warning("Selecciona al menos una entidad en el panel izquierdo para visualizar indicadores.")
        return

    filtro_res = df_resumen[
        df_resumen["sigla_entidad"].isin(entidades_sel)
        & df_resumen["anio"].between(rango_anios[0], rango_anios[1])
    ].copy()
    filtro_mod = df_mod[
        df_mod["sigla_entidad"].isin(entidades_sel)
        & df_mod["anio"].between(rango_anios[0], rango_anios[1])
    ].copy()
    filtro_conc = df_conc[
        df_conc["sigla_entidad"].isin(entidades_sel)
        & df_conc["anio"].between(rango_anios[0], rango_anios[1])
    ].copy()
    filtro_seg = df_seg[
        df_seg["sigla_entidad"].isin(entidades_sel)
        & df_seg["anio"].between(rango_anios[0], rango_anios[1])
    ].copy()

    # --- Encabezado e hilo conductor ---
    st.title("A contra(luz): análisis y veeduría de la contratación pública en Colombia")
    st.markdown(
        "**Pregunta de investigación:** *¿Qué tanto se desvía la contratación ejecutada en SECOP II "
        "frente a lo planeado en el Plan Anual de Adquisiciones (PAA) entre 2022 y 2025 en seis entidades "
        "nacionales del nivel central (`ANCP`, `MinHacienda`, `MinAmbiente`, `MinEducación`, `MinCulturas` "
        "y `DNP`), y en qué entidades, modalidades, proveedores o segmentos UNSPSC se concentra dicha desviación?*"
    )

    # --- Tarjetas KPI dinámicas ---
    if usar_constantes_2025:
        col_paa_kpi = (
            "valor_paa_ajustado_real_2025_cop"
            if usar_base_ajustada
            else "valor_paa_vigencia_real_2025_cop"
        )
        col_ejec_kpi = "valor_ejecutado_real_2025_cop"
        unidad_kpi = "COP constantes 2025"
    else:
        col_paa_kpi = (
            "valor_paa_vigencia_sin_dup_atipico" if usar_base_ajustada else "valor_paa_vigencia"
        )
        col_ejec_kpi = "valor_ejecutado"
        unidad_kpi = "COP corrientes"

    total_paa = float(filtro_res[col_paa_kpi].sum())
    total_ejec = float(filtro_res[col_ejec_kpi].sum())
    brecha_total = total_ejec - total_paa
    tasa_global = 100.0 * total_ejec / total_paa if total_paa > 0 else np.nan
    peso_directa_val = (
        100.0
        * float(filtro_res["valor_directa_cop"].sum())
        / max(float(filtro_res["valor_ejecutado"].sum()), 1.0)
    )
    duncan_medio = float(filtro_res["duncan_pct"].mean()) if not filtro_res.empty else np.nan

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(f"Planeado PAA ({unidad_kpi})", formatear_mm(total_paa))
    k2.metric(
        f"Ejecutado SECOP II ({unidad_kpi})",
        formatear_mm(total_ejec),
        delta=f"{brecha_total / 1e9:+,.2f} MM vs. PAA",
    )
    k3.metric("Tasa de ejecución acumulada", f"{tasa_global:.1f}%")
    k4.metric("Peso contratación directa ($)", f"{peso_directa_val:.1f}%")
    k5.metric("Índice de Duncan promedio", f"{duncan_medio:.1f}%")

    # --- Pestañas temáticas ---
    tabs = st.tabs(
        [
            "📊 1. Planeado vs. Ejecutado",
            "⚖️ 2. Modalidades y Directa",
            "🏢 3. Proveedores y HHI",
            "🧩 4. Segmentos UNSPSC",
            "🔍 5. Calidad y Franjas de Cuantía",
            "🤖 6. Mejoras con IA (Rubro 5)",
        ]
    )

    with tabs[0]:
        c_izq, c_der = st.columns(2)
        with c_izq:
            st.plotly_chart(
                graficar_planeado_vs_ejecutado_entidad(
                    filtro_res,
                    usar_base_ajustada=usar_base_ajustada,
                    usar_precios_constantes_2025=usar_constantes_2025,
                ),
                use_container_width=True,
            )
        with c_der:
            st.plotly_chart(
                graficar_evolucion_tasa_ejecucion(filtro_res, usar_base_ajustada=usar_base_ajustada),
                use_container_width=True,
            )
        st.caption(
            "Lectura económica: las tasas anuales > 100% obedecen al carácter indicativo y modificable del PAA "
            "(Decreto 1082/2015), a contratos plurianuales con vigencias futuras cuyo valor total se registra "
            "al firmarse y a traslados/adiciones presupuestales (Ley 80/1993, art. 40)."
        )
        st.download_button(
            "⬇️ Descargar resumen Entidad × Año filtrado (CSV)",
            data=filtro_res.to_csv(index=False).encode("utf-8"),
            file_name="resumen_entidad_anio_filtrado.csv",
            mime="text/csv",
        )

    with tabs[1]:
        st.plotly_chart(graficar_contratacion_directa_entidades(filtro_res), use_container_width=True)
        st.caption(
            "Hallazgo clave: la contratación directa concentra más del 90% del número de contratos por la "
            "contratación masiva de servicios profesionales, pero su peso en dinero cae sustancialmente en "
            "entidades que licitan seguros, tecnología o infraestructura."
        )
        resumen_mod = (
            filtro_mod.groupby("modalidad_homologada", as_index=False)
            .agg(
                items_paa=("items_paa", "sum"),
                planeado_mm=("valor_paa_ajustado_cop", lambda s: round(float(s.sum()) / 1e9, 2)),
                contratos_ejec=("n_contratos_con_cuantia", "sum"),
                ejecutado_mm=("valor_ejecutado_cop", lambda s: round(float(s.sum()) / 1e9, 2)),
            )
            .sort_values("ejecutado_mm", ascending=False)
        )
        st.dataframe(resumen_mod, use_container_width=True, hide_index=True)

    with tabs[2]:
        st.plotly_chart(graficar_concentracion_hhi(filtro_conc), use_container_width=True)
        st.caption(
            "Referencia estándar antimonopolio (DOJ/FTC y SIC): 22 de las 24 celdas entidad-año operan en baja "
            "concentración (< 1.500). Los dos picos > 2.500 (MinEducación 2023 con FINDETER y MinAmbiente 2023 "
            "con PNUD) corresponden a convenios con banca de desarrollo y cooperación internacional."
        )
        entidad_prov = st.selectbox(
            "Inspeccionar Top 10 contratistas adjudicados (2022–2025) por entidad:",
            options=entidades_sel,
        )
        sub_prov = df_top_prov[df_top_prov["sigla_entidad"] == entidad_prov].copy()
        sub_prov["valor_total_mm"] = (sub_prov["valor_total_cop"] / 1e9).round(2)
        st.dataframe(
            sub_prov[
                [
                    "ranking_entidad",
                    "nombre_proveedor",
                    "n_contratos",
                    "anios_activos",
                    "valor_total_mm",
                    "participacion_entidad_pct",
                    "modalidad_frecuente",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with tabs[3]:
        top_n_seg = st.slider("Número de segmentos UNSPSC principales a visualizar:", 5, 15, 10)
        st.plotly_chart(
            graficar_top_brechas_unspsc(
                filtro_seg,
                top_n=top_n_seg,
                usar_precios_constantes_2025=usar_constantes_2025,
            ),
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Descargar brechas por Segmento UNSPSC (CSV)",
            data=filtro_seg.to_csv(index=False).encode("utf-8"),
            file_name="brechas_segmento_unspsc_filtrado.csv",
            mime="text/csv",
        )

    with tabs[4]:
        a_paa = auditoria.get("paa_detalle", {})
        a_cont = auditoria.get("contratos_secop2", {})
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Match UNSPSC Clase (6d)",
            f"{a_paa.get('tasa_match_unspsc_clase_segmento_pct', 0):.2f}% PAA / "
            f"{a_cont.get('tasa_match_unspsc_clase_segmento_pct', 0):.2f}% Cont.",
        )
        m2.metric(
            "Modalidades PAA rescatadas",
            f"{a_paa.get('items_modalidad_recuperada_de_causal', 0):,} ítems",
        )
        m3.metric(
            "Contratos sin cuantía / simbólicos",
            f"{a_cont.get('contratos_sin_cuantia_cero', 0):,} marcados",
        )
        m4.metric(
            "Cuasi-duplicado PAA detectado",
            f"{a_paa.get('posibles_duplicados_atipicos_50mm', 0)} ($333,54 MM)",
        )

        alcance_franja = st.selectbox(
            "Seleccionar alcance para la distribución en 7 franjas de cuantía:",
            options=["TODAS"] + entidades_sel,
            index=0,
        )
        st.plotly_chart(
            graficar_distribucion_franjas_cuantia(df_franjas, sigla_entidad=alcance_franja),
            use_container_width=True,
        )

    with tabs[5]:
        st.subheader("Extensión metodológica sugerida por IA: Deflactación IPC DANE + Índice de Duncan")
        st.plotly_chart(graficar_rubro5_antes_despues_ipc(df_rubro5), use_container_width=True)
        st.plotly_chart(graficar_rubro5_ejecucion_vs_duncan(filtro_res), use_container_width=True)
        st.dataframe(df_rubro5, use_container_width=True, hide_index=True)

        if rubro5_json:
            with st.expander("Ver Prompt literal enviado a la IA"):
                st.code(rubro5_json.get("prompt_enviado", ""), language="text")
            with st.expander("Ver Respuesta completa de la IA (sin recortes)"):
                st.markdown(rubro5_json.get("respuesta_ia_completa", ""))
            with st.expander("Ver Evaluación crítica del equipo (mejoras aceptadas vs. descartadas)"):
                st.markdown(rubro5_json.get("evaluacion_critica_equipo", ""))


if __name__ == "__main__":
    renderizar_app()
