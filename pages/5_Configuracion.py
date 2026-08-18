import pandas as pd
import streamlit as st

from auth import requerir_rol, crear_usuario, hash_password
from db.database import get_session
from db.models import Usuario
from db.config_store import get_config, set_config
from config.theme import css_global, hero, sidebar_branding
from utils.importer import FIELD_DEFINITIONS, sugerir_mapeo, importar_dataframe

st.set_page_config(page_title="Configuración · Incubba Ñuble UBB", page_icon="⚙️", layout="wide")
st.markdown(css_global(), unsafe_allow_html=True)
usuario = requerir_rol("admin")
sidebar_branding(usuario)

st.markdown(hero("Panel de Configuración y Administración", "Importación masiva, gestión del comité evaluador y calibración de ponderaciones", pill="Solo Administradores"), unsafe_allow_html=True)

tab_import, tab_usuarios, tab_bono, tab_pesos, tab_cuenta = st.tabs([
    "📥 Importar postulaciones", "👥 Evaluadores", "🚀 Bonificación",
    "⚖️ Pesos entre etapas", "🔑 Mi cuenta",
])

# ---------------------------------------------------------------------------
with tab_import:
    st.markdown(
        """
        **Cómo obtener el archivo:** abre la hoja de cálculo de "Respuestas" vinculada
        al formulario de Google → **Archivo → Descargar → Valores separados por comas (.csv)**
        → súbelo aquí abajo.
        """
    )
    archivo = st.file_uploader("Sube el CSV de respuestas del formulario", type=["csv"])
    if archivo is not None:
        try:
            df_csv = pd.read_csv(archivo)
        except Exception as e:
            st.error(f"No se pudo leer el archivo: {e}")
            df_csv = None

        if df_csv is not None:
            st.success(f"Se detectaron {len(df_csv)} filas y {len(df_csv.columns)} columnas.")
            st.dataframe(df_csv.head(5), use_container_width=True)

            st.markdown("**Revisa el mapeo de columnas** (se sugiere automáticamente; ajusta si algo no calzó):")
            sugerido = sugerir_mapeo(list(df_csv.columns))
            mapeo_final = {}
            columnas_disponibles = ["(no importar)"] + list(df_csv.columns)
            for campo, label, _kw in FIELD_DEFINITIONS:
                default = sugerido.get(campo)
                idx = columnas_disponibles.index(default) if default in columnas_disponibles else 0
                col_elegida = st.selectbox(label, columnas_disponibles, index=idx, key=f"map_{campo}")
                if col_elegida != "(no importar)":
                    mapeo_final[campo] = col_elegida

            evitar_dup = st.checkbox(
                "Omitir filas que ya fueron importadas antes (mismo RUN o correo)", value=True,
            )

            if st.button("Importar postulaciones", type="primary"):
                nuevas, omitidas = importar_dataframe(df_csv, mapeo_final, evitar_duplicados=evitar_dup)
                st.success(f"Importación completa: {nuevas} postulaciones nuevas, {omitidas} omitidas por duplicado.")
                st.rerun()

# ---------------------------------------------------------------------------
with tab_usuarios:
    st.markdown("**Crear nuevo evaluador/a**")
    with st.form("crear_usuario_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre completo")
        email_nuevo = c2.text_input("Correo")
        c3, c4 = st.columns(2)
        password_nueva = c3.text_input("Contraseña temporal", type="password")
        rol_nuevo = c4.selectbox("Rol", ["evaluador", "admin"])
        crear = st.form_submit_button("Crear usuario")
    if crear:
        if not (nombre and email_nuevo and password_nueva):
            st.error("Completa nombre, correo y contraseña.")
        else:
            try:
                crear_usuario(nombre, email_nuevo, password_nueva, rol_nuevo)
                st.success(f"Usuario {email_nuevo} creado.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.divider()
    st.markdown("**Usuarios existentes**")
    session = get_session()
    try:
        usuarios = session.query(Usuario).order_by(Usuario.rol, Usuario.nombre).all()
        for u in usuarios:
            c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
            c1.write(u.nombre)
            c2.write(u.email)
            c3.write(u.rol)
            estado_actual = "Activo" if u.activo else "Inactivo"
            if c4.button(f"{estado_actual} — clic para cambiar", key=f"toggle_{u.id}"):
                u.activo = not u.activo
                session.commit()
                st.rerun()
    finally:
        session.close()

# ---------------------------------------------------------------------------
with tab_bono:
    session = get_session()
    try:
        config_bono = get_config(session, "bonificacion")
        st.markdown(
            "Ajusta la importancia relativa de cada factor de la bonificación por "
            "**potencial dinámico**. Los pesos se re-normalizan automáticamente aunque no sumen 100."
        )
        activa = st.checkbox("Bonificación activa", value=config_bono.get("activa", True))
        puntaje_maximo = st.number_input(
            "Puntaje máximo de bonificación (puntos extra sobre el puntaje final de 100)",
            min_value=0, max_value=30, value=int(config_bono.get("puntaje_maximo", 10)),
        )
        nuevos_factores = []
        for factor in config_bono.get("factores", []):
            st.markdown(f"**{factor['nombre']}**")
            peso = st.slider(
                f"Peso relativo — {factor['id']}", 0.0, 1.0, float(factor.get("peso", 0)),
                step=0.05, key=f"peso_{factor['id']}",
            )
            nuevo_factor = dict(factor)
            nuevo_factor["peso"] = peso
            nuevos_factores.append(nuevo_factor)

        if st.button("Guardar configuración de bonificación", type="primary"):
            config_bono["activa"] = activa
            config_bono["puntaje_maximo"] = puntaje_maximo
            config_bono["factores"] = nuevos_factores
            set_config(session, "bonificacion", config_bono)
            st.success("Configuración de bonificación actualizada.")
            st.rerun()
    finally:
        session.close()

# ---------------------------------------------------------------------------
with tab_pesos:
    session = get_session()
    try:
        pesos = get_config(session, "peso_etapas")
        st.markdown(
            "Ponderación de la **Etapa 2 (evaluación de proyecto)** y la **Etapa 3 "
            "(entrevista)** en el puntaje final combinado. La Etapa 1 (admisibilidad) "
            "actúa como filtro pasa/no pasa y no suma al puntaje final."
        )
        peso_e2 = st.slider("Peso Etapa 2 · Proyecto", 0.0, 1.0, float(pesos.get("etapa_2", 0.65)), step=0.05)
        peso_e3 = st.slider("Peso Etapa 3 · Entrevista", 0.0, 1.0, float(pesos.get("etapa_3", 0.35)), step=0.05)
        if st.button("Guardar pesos entre etapas", type="primary"):
            pesos["etapa_2"] = peso_e2
            pesos["etapa_3"] = peso_e3
            set_config(session, "peso_etapas", pesos)
            st.success("Pesos actualizados.")
            st.rerun()
    finally:
        session.close()

# ---------------------------------------------------------------------------
with tab_cuenta:
    st.markdown(f"Sesión actual: **{usuario['nombre']}** ({usuario['email']})")
    with st.form("cambiar_password_form"):
        nueva_pass = st.text_input("Nueva contraseña", type="password")
        confirmar_pass = st.text_input("Confirmar nueva contraseña", type="password")
        cambiar = st.form_submit_button("Cambiar contraseña")
    if cambiar:
        if not nueva_pass or nueva_pass != confirmar_pass:
            st.error("Las contraseñas no coinciden o están vacías.")
        else:
            session = get_session()
            try:
                u = session.get(Usuario, usuario["id"])
                u.password_hash = hash_password(nueva_pass)
                session.commit()
                st.success("Contraseña actualizada.")
            finally:
                session.close()
