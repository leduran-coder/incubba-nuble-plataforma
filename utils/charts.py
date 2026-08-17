"""
Helpers de gráficos (Plotly) que aplican de forma consistente la paleta y
las reglas de la guía de dataviz: un solo hue para magnitud, paleta
categórica de orden fijo solo cuando las series son la identidad, grillas
tenues, etiquetas legibles y siempre con su tabla de datos disponible.
"""
import plotly.graph_objects as go

from config.theme import (
    PALETA_CATEGORICA, PALETA_SECUENCIAL, GRIS_TEXTO,
)

SUPERFICIE = "#FFFFFF"
GRID = "#E1E0D9"
TEXTO_SECUNDARIO = "#52514E"
TEXTO_MUTED = "#898781"
AZUL_MAGNITUD = PALETA_SECUENCIAL[3]  # #2a78d6, tono ancla para barras de magnitud


def _layout_base(fig, titulo=None, altura=380):
    fig.update_layout(
        title=titulo,
        height=altura,
        paper_bgcolor=SUPERFICIE,
        plot_bgcolor=SUPERFICIE,
        font=dict(color=GRIS_TEXTO, size=13),
        margin=dict(l=10, r=10, t=50 if titulo else 20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


def barra_magnitud(df, x, y, titulo=None, horizontal=True, altura=380):
    """Barra de un solo hue para comparar magnitud entre categorías (no identidad)."""
    df = df.sort_values(y if not horizontal else x)
    fig = go.Figure()
    if horizontal:
        fig.add_bar(
            y=df[x], x=df[y], orientation="h",
            marker_color=AZUL_MAGNITUD,
            text=df[y], textposition="outside",
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    else:
        fig.add_bar(
            x=df[x], y=df[y],
            marker_color=AZUL_MAGNITUD,
            text=df[y], textposition="outside",
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    return _layout_base(fig, titulo, altura)


def barra_categorica(df, x, y, titulo=None, altura=380):
    """Barra donde cada categoría usa un color fijo de la paleta categórica
    (usar solo cuando la identidad de cada barra importa entre gráficos)."""
    df = df.sort_values(y, ascending=False)
    colores = [PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)] for i in range(len(df))]
    fig = go.Figure()
    fig.add_bar(
        x=df[x], y=df[y], marker_color=colores,
        text=df[y], textposition="outside",
        hovertemplate="%{x}: %{y}<extra></extra>",
    )
    return _layout_base(fig, titulo, altura)


def meter(valor, meta, titulo, formato_pct=True):
    """Medidor de una razón contra una meta (ej. % de proyectos liderados por mujeres vs 50%)."""
    rango_max = 100 if formato_pct else max(valor, meta) * 1.2
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        number={"suffix": "%" if formato_pct else "", "font": {"size": 34}},
        title={"text": titulo, "font": {"size": 14}},
        gauge={
            "axis": {
                "range": [0, rango_max],
                "tickmode": "array",
                "tickvals": [0, rango_max * 0.25, rango_max * 0.5, rango_max * 0.75, rango_max],
                "tickfont": {"size": 11},
            },
            "bar": {"color": AZUL_MAGNITUD},
            "threshold": {
                "line": {"color": "#d03b3b", "width": 3},
                "thickness": 0.85,
                "value": meta,
            },
            "steps": [
                {"range": [0, meta], "color": "#F4F1FA"},
            ],
        },
    ))
    fig.update_layout(height=260, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor=SUPERFICIE)
    return fig
