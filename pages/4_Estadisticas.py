import pandas as pd
import streamlit as st

from auth import requerir_login
from db.database import get_session
from db.models import Postulacion
from config.theme import css_global, hero
from utils.charts import barra_magnitud, meter
from utils.scoring import tabla_ranking

st.set_page_config(page_title="Estadísticas · Incubba Ñuble UBB", page_icon="📊", layout="wide")
st.markdown(css_global(), unsafe_allow_html=True)
requerir_login()

st.markdown(hero("Estadísticas de postulaciones", "Género, cobertura territorial, formalización e innovación"), unsafe_allow_html=True)

session = get_session()
try:
    postulaciones = session.query(Postulacion).all()
    ranking = tabla_ranking(session)
finally:
    session.close()

if not postulaciones:
    st.info("Aún no hay postulaciones cargadas.")
    st.stop()

df = pd.DataFrame([{
    "genero": p.genero or "Sin dato",
    "provincia": p.provincia or "Sin dato",
    "comuna": p.comuna or "Sin dato",
    "tipo_emprendimiento": p.tipo_emprendimiento or "Sin dato",
    "tipo_potencial_innovador": p.tipo_potencial_innovador or "Sin dato",
    "alcance_innovacion": p.alcance_innovacion or "Sin dato",
    "ha_levantado_financiamiento": p.ha_levantado_financiamiento or "Sin dato",
    "sector_industria": (p.sector_industria or "Sin dato").strip().title(),
} for p in postulaciones])

total = len(df)
pct_mujeres = (df["genero"].str.lower() == "femenino").mean() * 100
comunas_cubiertas = df.loc[df["comuna"] != "Sin dato", "comuna"].nunique()
pct_formalizado = (df["tipo_emprendimiento"].str.lower() == "formalizado").mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total postulaciones", total)
c2.metric("% liderado por mujeres", f"{pct_mujeres:.0f}%")
c3.metric("Comunas representadas", f"{comunas_cubiertas} / 21")
c4.metric("% formalizados", f"{pct_formalizado:.0f}%")

st.divider()

col1, col2 = st.columns([1, 2])
with col1:
    st.plotly_chart(meter(pct_mujeres, 50, "Paridad de género (meta 50%)"), use_container_width=True)
with col2:
    conteo_genero = df["genero"].value_counts().reset_index()
    conteo_genero.columns = ["genero", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_genero, "genero", "cantidad", "Postulaciones por género"),
        use_container_width=True,
    )

st.divider()
st.subheader("Cobertura territorial")
c1, c2 = st.columns(2)
with c1:
    conteo_provincia = df["provincia"].value_counts().reset_index()
    conteo_provincia.columns = ["provincia", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_provincia, "provincia", "cantidad", "Postulaciones por provincia"),
        use_container_width=True,
    )
with c2:
    conteo_comuna = df["comuna"].value_counts().reset_index()
    conteo_comuna.columns = ["comuna", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_comuna, "comuna", "cantidad", "Postulaciones por comuna (todas)", altura=520),
        use_container_width=True,
    )

st.divider()
st.subheader("Estado de formalización e innovación")
c1, c2 = st.columns(2)
with c1:
    conteo_tipo = df["tipo_emprendimiento"].value_counts().reset_index()
    conteo_tipo.columns = ["tipo", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_tipo, "tipo", "cantidad", "Idea vs. Formalizado"),
        use_container_width=True,
    )
with c2:
    conteo_innov = df["tipo_potencial_innovador"].value_counts().reset_index()
    conteo_innov.columns = ["tipo", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_innov, "tipo", "cantidad", "Potencial innovador (marginal/incremental/disruptiva)"),
        use_container_width=True,
    )

c1, c2 = st.columns(2)
with c1:
    conteo_alcance = df["alcance_innovacion"].value_counts().reset_index()
    conteo_alcance.columns = ["alcance", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_alcance, "alcance", "cantidad", "Alcance proyectado (regional/nacional/internacional)"),
        use_container_width=True,
    )
with c2:
    conteo_fin = df["ha_levantado_financiamiento"].value_counts().reset_index()
    conteo_fin.columns = ["financiamiento", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_fin, "financiamiento", "cantidad", "¿Ha levantado financiamiento previo?"),
        use_container_width=True,
    )

st.divider()
st.subheader("Sectores / industrias más frecuentes")
top_sectores = df["sector_industria"].value_counts().head(12).reset_index()
top_sectores.columns = ["sector", "cantidad"]
st.plotly_chart(
    barra_magnitud(top_sectores, "sector", "cantidad", "Top 12 sectores declarados", altura=420),
    use_container_width=True,
)

if not ranking.empty and ranking["Admisibilidad"].notna().any():
    st.divider()
    st.subheader("Estado de admisibilidad (Etapa 1)")
    conteo_adm = ranking["Admisibilidad"].value_counts().reset_index()
    conteo_adm.columns = ["estado", "cantidad"]
    st.plotly_chart(
        barra_magnitud(conteo_adm, "estado", "cantidad", "Admisible / No admisible / Pendiente", horizontal=False),
        use_container_width=True,
    )

with st.expander("Ver datos en tabla"):
    st.dataframe(df, use_container_width=True, hide_index=True)
