import pandas as pd
import streamlit as st

from auth import requerir_login
from db.database import get_session
from db.models import Postulacion
from config.theme import css_global, hero, sidebar_branding

st.set_page_config(page_title="Postulaciones · Incubba Ñuble UBB", page_icon="📋", layout="wide")
st.markdown(css_global(), unsafe_allow_html=True)
usuario = requerir_login()
sidebar_branding(usuario)

st.markdown(hero("Postulaciones", "Listado y fichas completas de proyectos postulantes 2026", pill="Registro Oficial"), unsafe_allow_html=True)

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

with st.expander("🔍 Filtros de Búsqueda Avanzada", expanded=False):
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

st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span style="font-weight:700; color:#0F172A; font-size:1.1rem;">Listado General</span>
        <span style="background:rgba(124,58,237,0.1); color:#7C3AED; font-weight:700; font-size:0.85rem; padding:4px 12px; border-radius:999px;">
            Mostrando {len(df_filtrado)} de {len(df)} postulaciones
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 📄 Ficha Técnica de Postulación")
opciones = {f"#{p.id} · {p.nombre_proyecto} — {p.nombre_completo}": p.id for p in postulaciones}
seleccion = st.selectbox("Selecciona una postulación para ver antecedentes", list(opciones.keys()))

if seleccion:
    session = get_session()
    try:
        p = session.get(Postulacion, opciones[seleccion])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:20px; box-shadow:0 2px 6px rgba(0,0,0,0.03); margin-bottom:16px;">
                    <h4 style="color:#7C3AED; margin-top:0; border-bottom:2px solid #F1F5F9; padding-bottom:8px;">👤 Antecedentes del Postulante</h4>
                    <p style="margin:6px 0;"><strong>Postulante:</strong> {p.nombre_completo}</p>
                    <p style="margin:6px 0;"><strong>RUN:</strong> {p.run}</p>
                    <p style="margin:6px 0;"><strong>Contacto:</strong> {p.correo} · {p.telefono}</p>
                    <p style="margin:6px 0;"><strong>Género:</strong> {p.genero}</p>
                    <p style="margin:6px 0;"><strong>Ubicación:</strong> {p.provincia} / {p.comuna} ({p.residencia_tipo})</p>
                    <h4 style="color:#7C3AED; margin-top:16px; border-bottom:2px solid #F1F5F9; padding-bottom:8px;">🏢 Emprendimiento</h4>
                    <p style="margin:6px 0;"><strong>Proyecto:</strong> {p.nombre_proyecto}</p>
                    <p style="margin:6px 0;"><strong>Estado:</strong> {p.tipo_emprendimiento} — {p.estado_detalle}</p>
                    <p style="margin:6px 0;"><strong>Empresa:</strong> {p.nombre_empresa or 'No formalizada'} ({p.rut_empresa or 'S/RUT'})</p>
                    <p style="margin:6px 0;"><strong>Sector:</strong> {p.sector_industria} · <strong>Tamaño:</strong> {p.tamano_empresa}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:20px; box-shadow:0 2px 6px rgba(0,0,0,0.03); margin-bottom:16px;">
                    <h4 style="color:#0D9488; margin-top:0; border-bottom:2px solid #F1F5F9; padding-bottom:8px;">💡 Innovación y Escalabilidad</h4>
                    <p style="margin:6px 0;"><strong>Potencial innovador:</strong> {p.tipo_potencial_innovador}</p>
                    <p style="margin:6px 0;"><strong>Tipo innovación:</strong> {p.tipo_innovacion}</p>
                    <p style="margin:6px 0;"><strong>Alcance territorial:</strong> {p.alcance_innovacion}</p>
                    <p style="margin:6px 0;"><strong>Financiamiento previo:</strong> {p.ha_levantado_financiamiento}</p>
                    <h4 style="color:#0D9488; margin-top:16px; border-bottom:2px solid #F1F5F9; padding-bottom:8px;">👥 Equipo y Pitch</h4>
                    <p style="margin:6px 0;"><strong>Integrantes:</strong> {p.num_personas_equipo} personas</p>
                    <p style="margin:6px 0;"><strong>Video Pitch:</strong> {f'<a href="{p.video_link}" target="_blank" style="color:#2563EB; font-weight:600;">Ver video ↗</a>' if p.video_link and p.video_link.startswith('http') else p.video_link or 'No registrado'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("📖 Respuestas Detalladas del Formulario", expanded=True):
            st.markdown(f"**Descripción del Proyecto:**\n\n{p.descripcion or '—'}")
            st.markdown(f"**Propuesta de Valor:**\n\n{p.propuesta_valor or '—'}")
            st.markdown(f"**Justificación de Innovación:**\n\n{p.por_que_innovador or '—'}")
            st.markdown(f"**Proyección a 3 años:**\n\n{p.resultados_3_anios or '—'}")
            st.markdown(f"**Impacto Esperado:**\n\n{p.impacto_esperado or '—'}")
            st.markdown(f"**Descripción del Equipo:**\n\n{p.descripcion_equipo or '—'}")
    finally:
        session.close()

