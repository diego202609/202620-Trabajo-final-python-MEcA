"""Funciones puras de visualización interactiva en Plotly (estándar acontraluz-charts).

Todas las funciones reciben DataFrames ya procesados desde `data/dashboard_data/` y
retornan objetos `plotly.graph_objects.Figure` reutilizables tanto en el Jupyter
Notebook (`A_contraluz_tutorial.ipynb`), en `app_streamlit.py` y en la Cartilla HTML.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Paleta accesible de alto contraste (>= 3:1 sobre blanco, amigable con daltonismo)
PALETA = {
    "azul_planeado": "#0B3C5D",
    "cobre_ejecutado": "#C84E00",
    "teal_competencia": "#1D7874",
    "ambar_directa": "#D9822B",
    "morado_acento": "#5B4B8A",
    "gris_neutro": "#4A5568",
    "gris_claro": "#CBD5E1",
    "grilla": "#E2E8F0",
    "rojo_alerta": "#9B2C2C",
}

COLORES_ENTIDADES = [
    "#0B3C5D",
    "#C84E00",
    "#1D7874",
    "#5B4B8A",
    "#D9822B",
    "#2B6CB0",
]

SIMBOLOS_ENTIDADES = ["circle", "square", "diamond", "triangle-up", "cross", "x"]
ESTILOS_LINEA = ["solid", "dash", "dot", "dashdot", "longdash", "solid"]
FUENTE_PIE = "Fuente: elaboración propia con datos de SECOP II y PAA vía datos.gov.co (2022–2025)."


def _aplicar_layout_estandar(
    fig: go.Figure,
    titulo: str,
    subtitulo: str = "",
    altura: int = 480,
) -> go.Figure:
    """Aplica tipografía, fondo blanco limpio y nota de fuente del skill acontraluz-charts."""
    texto_titulo = (
        f"<b>{titulo}</b><br><span style='font-size:13px;color:{PALETA['gris_neutro']}'>{subtitulo}</span>"
        if subtitulo
        else f"<b>{titulo}</b>"
    )
    fig.update_layout(
        title=dict(text=texto_titulo, x=0.01, xanchor="left", font=dict(size=17, color="#1A202C")),
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#1A202C"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=altura,
        margin=dict(l=60, r=35, t=85, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1.0, font=dict(size=12)),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, Arial, sans-serif"),
    )
    fig.add_annotation(
        text=FUENTE_PIE,
        xref="paper",
        yref="paper",
        x=0.0,
        y=-0.16,
        showarrow=False,
        xanchor="left",
        font=dict(size=11, color=PALETA["gris_neutro"]),
    )
    return fig


def graficar_distribucion_franjas_cuantia(
    df_franjas: pd.DataFrame,
    sigla_entidad: str = "TODAS",
) -> go.Figure:
    """Compara el % del número de contratos vs. % del valor en COP en las 7 franjas de cuantía."""
    sub = (
        df_franjas[df_franjas["sigla_entidad"] == sigla_entidad]
        .sort_values("orden_franja")
        .copy()
    )
    sub["valor_mm"] = sub["valor_total_cop"] / 1e9

    colores_n = [
        PALETA["gris_claro"] if o in (1, 2) else PALETA["azul_planeado"]
        for o in sub["orden_franja"]
    ]
    colores_val = [
        PALETA["gris_claro"] if o in (1, 2) else PALETA["cobre_ejecutado"]
        for o in sub["orden_franja"]
    ]

    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.08,
        subplot_titles=(
            "A. Participación en número de contratos (%)",
            "B. Participación en dinero contratado (%)",
        ),
    )

    fig.add_trace(
        go.Bar(
            y=sub["franja_cuantia"],
            x=sub["pct_contratos"],
            orientation="h",
            name="% Número de contratos",
            marker=dict(color=colores_n, line=dict(color="white", width=1)),
            text=[f"{v:.1f}% ({n:,})" for v, n in zip(sub["pct_contratos"], sub["n_contratos"])],
            textposition="outside",
            cliponaxis=False,
            customdata=np.stack([sub["n_contratos"], sub["modalidad_predominante"], sub["tratamiento_limpieza"]], axis=-1),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Contratos: %{customdata[0]:,} (%{x:.2f}%)<br>"
                "Modalidad frecuente: %{customdata[1]}<br>"
                "Regla de limpieza: %{customdata[2]}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            y=sub["franja_cuantia"],
            x=sub["pct_valor"],
            orientation="h",
            name="% Valor contratado (COP)",
            marker=dict(color=colores_val, line=dict(color="white", width=1)),
            text=[f"{v:.1f}% (${m:,.1f} MM)" for v, m in zip(sub["pct_valor"], sub["valor_mm"])],
            textposition="outside",
            cliponaxis=False,
            customdata=np.stack([sub["valor_mm"], sub["n_contratos"]], axis=-1),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Valor total: $%{customdata[0]:,.2f} mil millones (%{x:.2f}%)<br>"
                "Contratos en la franja: %{customdata[1]:,}<extra></extra>"
            ),
        ),
        row=1,
        col=2,
    )

    alcance_txt = "Muestra completa (6 entidades)" if sigla_entidad == "TODAS" else sigla_entidad
    _aplicar_layout_estandar(
        fig,
        titulo=f"Asimetría estructural por franja de cuantía — {alcance_txt} (2022–2025)",
        subtitulo="En gris claro: cuantías en $0 y simbólicas (<= $1.000 COP) marcadas en la auditoría de calidad",
        altura=490,
    )
    fig.update_layout(showlegend=False, margin=dict(l=210, r=95, t=95, b=85))
    fig.update_xaxes(title_text="% de contratos", range=[0, max(sub["pct_contratos"].max() * 1.32, 25)], gridcolor=PALETA["grilla"], row=1, col=1)
    fig.update_xaxes(title_text="% del valor (COP)", range=[0, max(sub["pct_valor"].max() * 1.35, 25)], gridcolor=PALETA["grilla"], row=1, col=2)
    fig.update_yaxes(autorange="reversed")
    return fig


def graficar_planeado_vs_ejecutado_entidad(
    df_resumen: pd.DataFrame,
    usar_base_ajustada: bool = True,
) -> go.Figure:
    """Compara el monto total planeado vs. ejecutado (2022–2025) por entidad."""
    col_paa = "valor_paa_vigencia_sin_dup_atipico" if usar_base_ajustada else "valor_paa_vigencia"
    agg = (
        df_resumen.groupby(["sigla_entidad", "nombre_entidad_corto"], as_index=False)
        .agg(
            paa_cop=(col_paa, "sum"),
            ejec_cop=("valor_ejecutado", "sum"),
            contratos=("n_contratos_con_cuantia", "sum"),
        )
    )
    agg["paa_mm"] = agg["paa_cop"] / 1e9
    agg["ejec_mm"] = agg["ejec_cop"] / 1e9
    agg["pct_ejec"] = 100.0 * agg["ejec_cop"] / agg["paa_cop"].replace(0, np.nan)
    agg = agg.sort_values("paa_mm", ascending=False)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=agg["sigla_entidad"],
            y=agg["paa_mm"],
            name="Planeado en PAA (vigencia)",
            marker=dict(color=PALETA["azul_planeado"], line=dict(color="white", width=1)),
            text=[f"${v:,.0f} MM" for v in agg["paa_mm"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Planeado PAA: $%{y:,.2f} mil millones<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=agg["sigla_entidad"],
            y=agg["ejec_mm"],
            name="Ejecutado en SECOP II",
            marker=dict(color=PALETA["cobre_ejecutado"], line=dict(color="white", width=1)),
            text=[f"${v:,.0f} MM ({p:.0f}%)" for v, p in zip(agg["ejec_mm"], agg["pct_ejec"])],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Ejecutado SECOP II: $%{y:,.2f} mil millones<extra></extra>",
        )
    )

    etiqueta_base = "base ajustada sin cuasi-duplicado atípico" if usar_base_ajustada else "base bruta"
    _aplicar_layout_estandar(
        fig,
        titulo="Brecha acumulada entre planeación (PAA) y contratación ejecutada (2022–2025)",
        subtitulo=f"Miles de millones de COP corrientes por entidad ({etiqueta_base})",
        altura=470,
    )
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Miles de millones de COP ($ MM)", gridcolor=PALETA["grilla"], range=[0, agg[["paa_mm", "ejec_mm"]].to_numpy().max() * 1.18])
    fig.update_xaxes(title_text="Entidad del orden nacional")
    return fig


def graficar_evolucion_tasa_ejecucion(
    df_resumen: pd.DataFrame,
    usar_base_ajustada: bool = True,
) -> go.Figure:
    """Muestra la trayectoria anual 2022–2025 del % de ejecución con marcadores accesibles."""
    col_pct = "pct_ejecucion_sobre_vigencia_sin_dup" if usar_base_ajustada else "pct_ejecucion_sobre_vigencia"
    fig = go.Figure()

    entidades = sorted(df_resumen["sigla_entidad"].unique())
    for idx, sigla in enumerate(entidades):
        sub = df_resumen[df_resumen["sigla_entidad"] == sigla].sort_values("anio")
        color = COLORES_ENTIDADES[idx % len(COLORES_ENTIDADES)]
        simbolo = SIMBOLOS_ENTIDADES[idx % len(SIMBOLOS_ENTIDADES)]
        estilo = ESTILOS_LINEA[idx % len(ESTILOS_LINEA)]
        fig.add_trace(
            go.Scatter(
                x=sub["anio"],
                y=sub[col_pct],
                mode="lines+markers",
                name=sigla,
                line=dict(color=color, width=3, dash=estilo),
                marker=dict(symbol=simbolo, size=10, color=color, line=dict(color="white", width=1)),
                customdata=np.stack(
                    [sub["valor_paa_vigencia_sin_dup_atipico"] / 1e9, sub["valor_ejecutado"] / 1e9, sub["version_encabezado"]],
                    axis=-1,
                ),
                hovertemplate=(
                    f"<b>{sigla} (%{{x}})</b><br>"
                    "Tasa de ejecución: %{y:.1f}%<br>"
                    "PAA ajustado: $%{customdata[0]:,.2f} MM<br>"
                    "Ejecutado: $%{customdata[1]:,.2f} MM<br>"
                    "Versiones publicadas del PAA: %{customdata[2]}<extra></extra>"
                ),
            )
        )

    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color=PALETA["gris_neutro"],
        annotation_text="100% (Ejecución = Planeación anual)",
        annotation_position="top left",
    )
    _aplicar_layout_estandar(
        fig,
        titulo="Evolución anual de la tasa de ejecución frente al PAA (2022–2025)",
        subtitulo="Valores > 100% reflejan contratos plurianuales firmados en el año, adiciones o traslados PGN",
        altura=470,
    )
    fig.update_xaxes(title_text="Vigencia fiscal", tickmode="array", tickvals=[2022, 2023, 2024, 2025])
    fig.update_yaxes(title_text="Ejecución sobre PAA (%)", ticksuffix="%", gridcolor=PALETA["grilla"])
    return fig


def graficar_contratacion_directa_entidades(df_resumen: pd.DataFrame) -> go.Figure:
    """Contrasta el peso de la contratación directa en número de contratos vs. valor en pesos."""
    agg = (
        df_resumen.groupby("sigla_entidad", as_index=False)
        .agg(
            n_directa=("n_contratos_directa", "sum"),
            n_total=("n_contratos_con_cuantia", "sum"),
            val_directa=("valor_directa_cop", "sum"),
            val_total=("valor_ejecutado", "sum"),
        )
    )
    agg["pct_num"] = 100.0 * agg["n_directa"] / agg["n_total"].replace(0, np.nan)
    agg["pct_val"] = 100.0 * agg["val_directa"] / agg["val_total"].replace(0, np.nan)
    agg = agg.sort_values("pct_val", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=agg["sigla_entidad"],
            x=agg["pct_val"],
            orientation="h",
            name="% del Valor en pesos (COP)",
            marker=dict(color=PALETA["ambar_directa"], line=dict(color="white", width=1)),
            text=[f"{v:.1f}%" for v in agg["pct_val"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>% del dinero en contratación directa: %{x:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=agg["sigla_entidad"],
            x=agg["pct_num"],
            orientation="h",
            name="% del Número de contratos",
            marker=dict(color=PALETA["azul_planeado"], line=dict(color="white", width=1)),
            text=[f"{v:.1f}%" for v in agg["pct_num"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>% de contratos en contratación directa: %{x:.1f}%<extra></extra>",
        )
    )

    _aplicar_layout_estandar(
        fig,
        titulo="Peso de la contratación directa: cantidad de contratos vs. dinero comprometido (2022–2025)",
        subtitulo="Contratos válidos con cuantía > $1.000 COP — diferenciar número vs. valor evita sesgos de lectura",
        altura=460,
    )
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Participación de la contratación directa (%)", range=[0, 112], ticksuffix="%", gridcolor=PALETA["grilla"])
    fig.update_yaxes(title_text="Entidad")
    return fig


def graficar_concentracion_hhi(df_conc: pd.DataFrame) -> go.Figure:
    """Grafica el Índice Herfindahl-Hirschman (HHI) anual por entidad frente a umbrales DOJ/FTC."""
    fig = go.Figure()
    entidades = sorted(df_conc["sigla_entidad"].unique())
    for idx, sigla in enumerate(entidades):
        sub = df_conc[df_conc["sigla_entidad"] == sigla].sort_values("anio")
        color = COLORES_ENTIDADES[idx % len(COLORES_ENTIDADES)]
        simbolo = SIMBOLOS_ENTIDADES[idx % len(SIMBOLOS_ENTIDADES)]
        fig.add_trace(
            go.Scatter(
                x=sub["anio"],
                y=sub["hhi_proveedores"],
                mode="lines+markers",
                name=sigla,
                line=dict(color=color, width=3),
                marker=dict(symbol=simbolo, size=10, color=color, line=dict(color="white", width=1)),
                customdata=np.stack([sub["cr5_pct"], sub["top1_proveedor"], sub["n_proveedores_unicos"]], axis=-1),
                hovertemplate=(
                    f"<b>{sigla} (%{{x}})</b><br>"
                    "Índice HHI: %{y:,.0f}<br>"
                    "Participación Top 5 (CR5): %{customdata[0]:.1f}%<br>"
                    "Proveedores únicos: %{customdata[2]:,}<br>"
                    "Mayor contratista: %{customdata[1]}<extra></extra>"
                ),
            )
        )

    fig.add_hline(y=1500, line_dash="dash", line_color=PALETA["teal_competencia"], annotation_text="Umbral concentración moderada (HHI = 1.500)")
    fig.add_hline(y=2500, line_dash="dot", line_color=PALETA["rojo_alerta"], annotation_text="Umbral alta concentración (HHI = 2.500)")

    _aplicar_layout_estandar(
        fig,
        titulo="Concentración del gasto por proveedor adjudicado — Índice HHI (2022–2025)",
        subtitulo="Referencia estándar antimonopolio (DOJ/FTC y SIC): < 1.500 baja, 1.500–2.500 moderada, > 2.500 alta",
        altura=470,
    )
    fig.update_xaxes(title_text="Vigencia fiscal", tickmode="array", tickvals=[2022, 2023, 2024, 2025])
    fig.update_yaxes(title_text="Índice HHI (escala 0 – 10.000)", gridcolor=PALETA["grilla"])
    return fig


def graficar_top_brechas_unspsc(df_seg: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Muestra los Top N segmentos UNSPSC por volumen con su brecha Ejecutado − Planeado."""
    agg = (
        df_seg.groupby(["codigo_segmento", "nombre_segmento"], as_index=False)
        .agg(
            paa_cop=("valor_paa_vigencia", "sum"),
            ejec_cop=("valor_ejecutado", "sum"),
        )
    )
    agg["volumen_total"] = agg["paa_cop"] + agg["ejec_cop"]
    agg["brecha_mm"] = (agg["ejec_cop"] - agg["paa_cop"]) / 1e9
    agg["paa_mm"] = agg["paa_cop"] / 1e9
    agg["ejec_mm"] = agg["ejec_cop"] / 1e9
    agg["etiqueta"] = agg["codigo_segmento"] + " - " + agg["nombre_segmento"].str.slice(0, 42)
    top = agg.nlargest(top_n, "volumen_total").sort_values("brecha_mm", ascending=True)

    colores = [PALETA["cobre_ejecutado"] if b >= 0 else PALETA["azul_planeado"] for b in top["brecha_mm"]]
    fig = go.Figure(
        go.Bar(
            y=top["etiqueta"],
            x=top["brecha_mm"],
            orientation="h",
            marker=dict(color=colores, line=dict(color="white", width=1)),
            text=[f"{b:+,.1f} MM" for b in top["brecha_mm"]],
            textposition="outside",
            cliponaxis=False,
            customdata=np.stack([top["paa_mm"], top["ejec_mm"]], axis=-1),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Planeado PAA: $%{customdata[0]:,.2f} MM<br>"
                "Ejecutado SECOP II: $%{customdata[1]:,.2f} MM<br>"
                "Brecha (Ejec − PAA): $%{x:+,.2f} MM<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=0, line_color="#1A202C", line_width=1.5)
    _aplicar_layout_estandar(
        fig,
        titulo=f"Brecha sectorial (Ejecutado − Planeado) en los {top_n} principales segmentos UNSPSC (2022–2025)",
        subtitulo="Valores negativos (azul) = subejecución frente al PAA; positivos (cobre) = ejecución superior a lo planeado",
        altura=500,
    )
    fig.update_layout(showlegend=False, margin=dict(l=275, r=85, t=90, b=80))
    rango_min = min(top["brecha_mm"].min() * 1.28, -50)
    rango_max = max(top["brecha_mm"].max() * 1.28, 50)
    fig.update_xaxes(title_text="Brecha Ejecutado − Planeado ($ Miles de millones COP)", range=[rango_min, rango_max], gridcolor=PALETA["grilla"])
    return fig
