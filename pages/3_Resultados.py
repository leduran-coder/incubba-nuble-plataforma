import streamlit as st

from auth import requerir_login
from db.database import get_session
from config.theme import css_global, hero
from config.rubric import CRITERIOS_ADICIONALES
from utils.scoring import tabla_ranking

st.set_page_config(page_title="Resultados · Incubba Ñuble UBB", page_icon="🏆", layout="wide")
st.markdown(css_global(), unsafe_allow_html=True)
requerir_login()

st.markdown(hero("Resultados y ranking final", "Puntaje ponderado por etapas + bonificación por potencial dinámico"), unsafe_allow_html=True)

session = get_session()
try:
    df = tabla_ranking(session)
finally:
    session.close()

if df.empty:
    st.info("Aún no hay postulaciones cargadas.")
    st.stop()

cupo_maximo = CRITERIOS_ADICIONALES["cupo_maximo"]
st.caption(
    "El ranking ordena primero las postulaciones **Admisibles**, luego las **Pendientes** "
    "de evaluación y al final las **No admisibles** (quedan fuera de la fase siguiente según "
    "el punto 4.5.1 de las bases). El puntaje final de una 'No admisible' se muestra solo como "
    "referencia informativa."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Postulaciones evaluadas", int(df["Puntaje final"].notna().sum()))
c2.metric("Admisibles", int((df["Admisibilidad"] == "Admisible").sum()))
top_cupo = df.head(cupo_maximo)
pct_mujeres_top = (top_cupo["Género"].str.lower() == "femenino").mean() * 100 if not top_cupo.empty else 0
c3.metric(f"% liderado por mujeres (top {cupo_maximo})", f"{pct_mujeres_top:.0f}%",
          help="Meta de las bases: al menos 50%.")
comunas_top = top_cupo["Comuna"].dropna().nunique()
c4.metric(f"Comunas cubiertas (top {cupo_maximo})", f"{comunas_top} / 21")

if pct_mujeres_top < 50:
    st.warning(
        f"El top {cupo_maximo} por puntaje puro no alcanza el 50% de proyectos liderados por "
        "mujeres exigido en las bases (criterio 4.4). Este ajuste se aplica DESPUÉS del ranking "
        "por rúbrica — revisa manualmente qué proyectos liderados por mujeres, mejor evaluados "
        "fuera del corte, podrían incorporarse para cumplir la meta."
    )

st.divider()

with st.expander("Filtros", expanded=False):
    c1, c2 = st.columns(2)
    f_admisibilidad = c1.multiselect("Admisibilidad", sorted(df["Admisibilidad"].dropna().unique()))
    solo_con_puntaje = c2.checkbox("Mostrar solo postulaciones con puntaje final calculado", value=False)

df_filtrado = df.copy()
if f_admisibilidad:
    df_filtrado = df_filtrado[df_filtrado["Admisibilidad"].isin(f_admisibilidad)]
if solo_con_puntaje:
    df_filtrado = df_filtrado[df_filtrado["Puntaje final"].notna()]

st.dataframe(
    df_filtrado.style.apply(
        lambda fila: ["background-color: #F4F1FA" if fila["Ranking"] <= cupo_maximo else "" for _ in fila],
        axis=1,
    ),
    use_container_width=True, hide_index=True,
)
st.caption(f"Las filas resaltadas corresponden al top {cupo_maximo} (cupo máximo según las bases).")

st.download_button(
    "Descargar ranking como CSV",
    df.to_csv(index=False).encode("utf-8"),
    file_name="ranking_incubba_nuble_2026.csv",
    mime="text/csv",
)
