import pandas as pd
import streamlit as st

from auth import requerir_login
from db.database import get_session
from db.models import Postulacion
from config.theme import css_global, hero

st.set_page_config(page_title="Postulaciones · Incubba Ñuble UBB", page_icon="📋", layout="wide")
st.markdown(css_global(), unsafe_allow_html=True)
requerir_login()

st.markdown(hero("Postulaciones", "Listado importado desde el formulario de postulación 2026"), unsafe_allow_html=True)

session = get_session()
try:
    postulaciones = session.query(Postulacion).all()
    filas = [{
        "ID": p.id,
        "Proyecto": p.nombre_proyecto,
        "Postulante": p.nombre_completo,
        "Correo": p.correo,
        "Género": p.genero,
        "Provincia": p.provincia,
        "Comuna": p.comuna,
        "Tipo": p.tipo_emprendimiento,
        "Sector": p.sector_industria,
        "Innovación": p.tipo_potencial_innovador,
        "Alcance": p.alcance_innovacion,
        "Financiamiento previo": p.ha_levantado_financiamiento,
    } for p in postulaciones]
finally:
    session.close()

df = pd.DataFrame(filas)

if df.empty:
    st.info(
        "Todavía no hay postulaciones cargadas. Si eres administrador/a, ve a "
        "**Configuración → Importar postulaciones** y sube el CSV exportado desde "
        "la hoja de respuestas del Google Form."
    )
    st.stop()

with st.expander("Filtros", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    f_provincia = c1.multiselect("Provincia", sorted(df["Provincia"].dropna().unique()))
    f_comuna = c2.multiselect("Comuna", sorted(df["Comuna"].dropna().unique()))
    f_genero = c3.multiselect("Género", sorted(df["Género"].dropna().unique()))
    f_tipo = c4.multiselect("Tipo de emprendimiento", sorted(df["Tipo"].dropna().unique()))

df_filtrado = df.copy()
if f_provincia:
    df_filtrado = df_filtrado[df_filtrado["Provincia"].isin(f_provincia)]
if f_comuna:
    df_filtrado = df_filtrado[df_filtrado["Comuna"].isin(f_comuna)]
if f_genero:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(f_genero)]
if f_tipo:
    df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(f_tipo)]

st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} postulaciones.")
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Ver detalle de una postulación")
opciones = {f"#{p.id} · {p.nombre_proyecto} — {p.nombre_completo}": p.id for p in postulaciones}
seleccion = st.selectbox("Selecciona una postulación", list(opciones.keys()))

if seleccion:
    session = get_session()
    try:
        p = session.get(Postulacion, opciones[seleccion])
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Antecedentes generales**")
            st.write(f"- Postulante: {p.nombre_completo}")
            st.write(f"- RUN: {p.run}")
            st.write(f"- Correo: {p.correo}  ·  Teléfono: {p.telefono}")
            st.write(f"- Género: {p.genero}")
            st.write(f"- Residencia: {p.residencia_tipo} — {p.provincia} / {p.comuna}")
            st.markdown("**Emprendimiento**")
            st.write(f"- Nombre: {p.nombre_proyecto}")
            st.write(f"- Tipo: {p.tipo_emprendimiento} — {p.estado_detalle}")
            st.write(f"- Empresa: {p.nombre_empresa} ({p.rut_empresa}) — {p.tipo_empresa}")
            st.write(f"- Sector/industria: {p.sector_industria}  ·  Tamaño: {p.tamano_empresa}")
        with col2:
            st.markdown("**Innovación y escalabilidad**")
            st.write(f"- ¿Es innovación?: {p.cree_que_es_innovacion}")
            st.write(f"- Tipo de potencial innovador: {p.tipo_potencial_innovador}")
            st.write(f"- Tipo de innovación: {p.tipo_innovacion}")
            st.write(f"- Alcance: {p.alcance_innovacion}")
            st.write(f"- ¿Ha levantado financiamiento?: {p.ha_levantado_financiamiento}")
            st.markdown("**Equipo**")
            st.write(f"- N° de personas: {p.num_personas_equipo}")
            st.write(f"- Video pitch: {p.video_link or 'sin enlace'}")

        st.markdown("**Descripción**")
        st.write(p.descripcion or "—")
        st.markdown("**Propuesta de valor**")
        st.write(p.propuesta_valor or "—")
        st.markdown("**Por qué es innovador**")
        st.write(p.por_que_innovador or "—")
        st.markdown("**Resultados esperados a 3 años**")
        st.write(p.resultados_3_anios or "—")
        st.markdown("**Impacto esperado**")
        st.write(p.impacto_esperado or "—")
        st.markdown("**Equipo (detalle)**")
        st.write(p.descripcion_equipo or "—")
    finally:
        session.close()
