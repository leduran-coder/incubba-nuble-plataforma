"""
Autenticación simple basada en usuario/contraseña propios (no depende de
servicios externos). Dos roles:

  - admin:     puede importar postulaciones, crear/editar evaluadores,
               ajustar la bonificación y ver todo.
  - evaluador: solo puede calificar postulaciones y ver resultados/estadísticas
               (según se configure).

Las contraseñas se guardan con hash bcrypt, nunca en texto plano.
"""
import bcrypt
import streamlit as st

from db.database import get_session
from db.models import Usuario

ADMIN_POR_DEFECTO_EMAIL = "admin@incubba.cl"
ADMIN_POR_DEFECTO_PASSWORD = "incubba2026"  # el admin DEBE cambiarla en su primer ingreso


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def asegurar_admin_por_defecto():
    """Crea un usuario admin inicial si la tabla de usuarios está vacía."""
    session = get_session()
    try:
        existe_alguno = session.query(Usuario).first()
        if existe_alguno is None:
            admin = Usuario(
                nombre="Administrador/a",
                email=ADMIN_POR_DEFECTO_EMAIL,
                password_hash=hash_password(ADMIN_POR_DEFECTO_PASSWORD),
                rol="admin",
                activo=True,
            )
            session.add(admin)
            session.commit()
    finally:
        session.close()


def login(email: str, password: str):
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.email == email.strip().lower()).first()
        if usuario is None or not usuario.activo:
            return None
        if not verificar_password(password, usuario.password_hash):
            return None
        return {"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email, "rol": usuario.rol}
    finally:
        session.close()


def crear_usuario(nombre: str, email: str, password: str, rol: str = "evaluador"):
    session = get_session()
    try:
        email_norm = email.strip().lower()
        if session.query(Usuario).filter(Usuario.email == email_norm).first():
            raise ValueError("Ya existe un usuario con ese correo.")
        usuario = Usuario(
            nombre=nombre.strip(),
            email=email_norm,
            password_hash=hash_password(password),
            rol=rol,
            activo=True,
        )
        session.add(usuario)
        session.commit()
        return usuario.id
    finally:
        session.close()


def requerir_login():
    """Bloquea el acceso a la página actual si no hay sesión iniciada.
    Debe llamarse al comienzo de cada página de Streamlit."""
    if "usuario" not in st.session_state:
        st.warning("Debes iniciar sesión para ver esta página. Ve a la página principal (Inicio).")
        st.stop()
    return st.session_state["usuario"]


def requerir_rol(*roles_permitidos):
    usuario = requerir_login()
    if usuario["rol"] not in roles_permitidos:
        st.error("No tienes permisos para ver esta página.")
        st.stop()
    return usuario


def cerrar_sesion():
    for k in ["usuario"]:
        if k in st.session_state:
            del st.session_state[k]
