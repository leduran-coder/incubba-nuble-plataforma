"""
Incubba Ñuble UBB · Plataforma de Postulación y Evaluación — Generación 2026
Página principal: inicio de sesión y resumen general.

Ejecutar localmente con:   streamlit run app.py
"""
import streamlit as st

from auth import asegurar_admin_por_defecto, login, cerrar_sesion, ADMIN_POR_DEFECTO_EMAIL, ADMIN_POR_DEFECTO_PASSWORD
from db.database import init_db, get_session
from db.models import Postulacion
from config.theme import css_global, hero

st.set_page_config(
    page_title="Incubba Ñuble UBB",
    page_icon="🌱",
    layout="wide",
)

init_db()
asegurar_admin_por_defecto()

st.markdown(css_global(), unsafe_allow_html=True)
st.markdown(
    hero(
        "Plataforma de Postulación y Evaluación",
        "Generación 2026 · Universidad del Bío-Bío · Proyecto CORFO 24POT-IN-272821",
        pill="Panel de evaluación",
    ),
    unsafe_allow_html=True,
)

if "usuario" in st.session_state:
    usuario = st.session_state["usuario"]
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Sesión iniciada como **{usuario['nombre']}** ({usuario['rol']}).")
    with col2:
        if st.button("Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()

    session = get_session()
    try:
        total = session.query(Postulacion).count()
    finally:
        session.close()

    st.divider()
    st.subheader("Resumen rápido")
    c1, c2, c3 = st.columns(3)
    c1.metric("Postulaciones cargadas", total)
    c2.metric("Cupos disponibles (bases)", 40)
    c3.metric("Duración del programa", "8 meses")

    st.markdown(
        """
        Usa el menú de la izquierda para navegar:

        - **Postulaciones** — ver el listado importado desde el formulario.
        - **Evaluación** — calificar cada postulación según las 3 rúbricas de las bases.
        - **Resultados** — ranking final, con bonificación por potencial dinámico.
        - **Estadísticas** — género, cobertura comunal, estado de formalización, innovación, etc.
        - **Configuración** *(solo administrador/a)* — importar postulaciones, gestionar evaluadores
          y ajustar los pesos de la bonificación.
        """
    )
else:
    st.info(
        "Ingresa con tu correo y contraseña. Si es la primera vez que se usa la plataforma, "
        f"el usuario administrador por defecto es **{ADMIN_POR_DEFECTO_EMAIL}** / "
        f"**{ADMIN_POR_DEFECTO_PASSWORD}** — cámbialo apenas ingreses, desde Configuración."
    )
    with st.form("login_form"):
        email = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Ingresar", use_container_width=True)

    if enviado:
        usuario = login(email, password)
        if usuario is None:
            st.error("Correo o contraseña incorrectos.")
        else:
            st.session_state["usuario"] = usuario
            st.rerun()
