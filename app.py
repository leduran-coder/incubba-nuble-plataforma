"""
Incubba Ñuble UBB · Plataforma de Postulación y Evaluación — Generación 2026
Página principal: inicio de sesión y resumen general.

Ejecutar localmente con:   streamlit run app.py
"""
import streamlit as st

from auth import asegurar_admin_por_defecto, login, cerrar_sesion, ADMIN_POR_DEFECTO_EMAIL, ADMIN_POR_DEFECTO_PASSWORD
from db.database import init_db, get_session, DB_STATUS, DB_ERROR_MSG
from db.models import Postulacion
from config.theme import css_global, hero, sidebar_branding

st.set_page_config(
    page_title="Incubba Ñuble UBB · Portal de Evaluación",
    page_icon="🌱",
    layout="wide",
)

init_db()
asegurar_admin_por_defecto()

st.markdown(css_global(), unsafe_allow_html=True)
sidebar_branding(st.session_state.get("usuario"))

st.markdown(
    hero(
        "Plataforma de Postulación y Evaluación",
        "Generación 2026 · Universidad del Bío-Bío · Proyecto CORFO 24POT-IN-272821",
        pill="Portal Oficial",
    ),
    unsafe_allow_html=True,
)

if DB_STATUS == "fallback":
    with st.expander("ℹ️ Estado de la Base de Datos: Usando almacenamiento local temporal (SQLite)", expanded=False):
        st.warning(
            f"No se pudo establecer conexión remota con PostgreSQL/Supabase. La plataforma está funcionando en modo local temporal.\n\n"
            f"**Detalle del error:** `{DB_ERROR_MSG}`\n\n"
            f"Para persistir en Supabase, verifica la cadena `DATABASE_URL` en los Secrets de Streamlit."
        )

if "usuario" in st.session_state:
    usuario = st.session_state["usuario"]
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #7C3AED; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <span style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">Bienvenido/a, {usuario['nombre']}</span>
                <span style="display:inline-block; margin-left: 10px; background: rgba(124, 58, 237, 0.1); color: #7C3AED; font-weight: 700; font-size: 0.8rem; padding: 2px 10px; border-radius: 999px; text-transform: uppercase;">{usuario['rol']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()

    session = get_session()
    try:
        total = session.query(Postulacion).count()
    finally:
        session.close()

    st.markdown("### 📊 Resumen Ejecutivo del Proceso")
    c1, c2, c3 = st.columns(3)
    c1.metric("Postulaciones Registradas", total)
    c2.metric("Cupos Disponibles (Bases)", 40)
    c3.metric("Duración del Programa", "8 meses")

    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <h4 style="color: #0F172A; margin-top: 0; font-weight: 700;">📌 Navegación Rápida</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 14px;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 12px;">
                    <strong style="color: #7C3AED;">📝 Postulaciones</strong><br/>
                    <small style="color: #64748B;">Revisa y filtra el listado completo importado desde Google Forms.</small>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 12px;">
                    <strong style="color: #7C3AED;">🎯 Evaluación</strong><br/>
                    <small style="color: #64748B;">Califica las 3 etapas oficiales: Admisibilidad, Proyecto y Entrevista.</small>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 12px;">
                    <strong style="color: #7C3AED;">🏆 Resultados</strong><br/>
                    <small style="color: #64748B;">Ranking consolidado, bonificación por potencial dinámico y metas de paridad.</small>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 12px;">
                    <strong style="color: #7C3AED;">📊 Estadísticas</strong><br/>
                    <small style="color: #64748B;">Métricas territoriales de Ñuble, género, sectores y grado de innovación.</small>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 28px; box-shadow: 0 8px 24px rgba(0,0,0,0.04);">
                <h3 style="color: #0F172A; margin-top: 0; font-weight: 800;">🔐 Acceso al Portal</h3>
                <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 20px;">
                    Ingresa con tu correo institucional y contraseña asignada para acceder al panel de evaluación.
                </p>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            email = st.text_input("Correo electrónico", placeholder="ejemplo@incubba.cl")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            enviado = st.form_submit_button("Ingresar al Sistema", use_container_width=True)

        if enviado:
            usuario = login(email, password)
            if usuario is None:
                st.error("Credenciales incorrectas o usuario inactivo.")
            else:
                st.session_state["usuario"] = usuario
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_der:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #FAF8FD 0%, #F1F5F9 100%); border: 1px solid #E2E8F0; border-radius: 18px; padding: 28px; height: 100%;">
                <h4 style="color: #4C1D95; margin-top: 0; font-weight: 700;">🌱 Convocatoria Incubba Ñuble UBB 2026</h4>
                <p style="color: #334155; font-size: 0.92rem; line-height: 1.6;">
                    Plataforma oficial desarrollada para la gestión, admisibilidad y evaluación de proyectos de emprendimiento e innovación en la Región de Ñuble.
                </p>
                <div style="margin-top: 20px; padding: 14px; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;">
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.88rem;">ℹ️ Primer Ingreso (Administrador)</div>
                    <div style="color: #64748B; font-size: 0.85rem; margin-top: 4px;">
                        Usuario: <code style="color:#7C3AED;">{ADMIN_POR_DEFECTO_EMAIL}</code><br/>
                        Clave: <code style="color:#7C3AED;">{ADMIN_POR_DEFECTO_PASSWORD}</code>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

