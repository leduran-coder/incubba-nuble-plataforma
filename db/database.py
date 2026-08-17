"""
Conexión a la base de datos. Prioridad de configuración:

1. st.secrets["DATABASE_URL"]   (recomendado en producción, Streamlit Cloud)
2. variable de entorno DATABASE_URL
3. SQLite local (./data/incubba.db) — útil para probar en tu computador,
   NO recomendado para producción porque no persiste de forma confiable
   en algunos hostings.

Ejemplos de DATABASE_URL válidos:
  postgresql+psycopg2://usuario:password@host:5432/nombre_bd   (Supabase/Neon)
  sqlite:///./data/incubba.db
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base

def _resolve_database_url():
    url = None
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            url = st.secrets["DATABASE_URL"]
    except Exception:
        pass

    if not url:
        url = os.environ.get("DATABASE_URL")

    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return f"sqlite:///{data_dir / 'incubba.db'}"


DATABASE_URL = _resolve_database_url()

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Crea todas las tablas si no existen. Es seguro llamarla varias veces."""
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
