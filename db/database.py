import os
from pathlib import Path
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

logger = logging.getLogger(__name__)

DB_STATUS = "unknown"
DB_ERROR_MSG = None
DATABASE_URL = None
engine = None
SessionLocal = None


def _get_sqlite_url():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return f"sqlite:///{data_dir / 'incubba.db'}"


def _clean_postgres_url(url: str) -> str:
    url = url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Asegurar sslmode=require para conexiones remotas
    if "sslmode=" not in url and not url.startswith("sqlite"):
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


def _init_engine_and_session(url: str):
    is_sqlite = url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    _eng = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    _sess = sessionmaker(bind=_eng, autoflush=False, autocommit=False)
    return _eng, _sess


def _resolve_and_setup():
    global DATABASE_URL, engine, SessionLocal, DB_STATUS, DB_ERROR_MSG
    raw_url = None
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            raw_url = st.secrets["DATABASE_URL"]
    except Exception:
        pass

    if not raw_url:
        raw_url = os.environ.get("DATABASE_URL")

    if raw_url and not raw_url.startswith("sqlite"):
        try:
            target_url = _clean_postgres_url(raw_url)
            eng, sess = _init_engine_and_session(target_url)
            # Probar la conexión ejecutando create_all
            Base.metadata.create_all(eng)
            DATABASE_URL = target_url
            engine = eng
            SessionLocal = sess
            DB_STATUS = "postgres"
            DB_ERROR_MSG = None
            return
        except Exception as e:
            logger.error(f"Error conectando a Postgres ({raw_url}): {e}")
            DB_ERROR_MSG = str(e)
            DB_STATUS = "fallback"

    # Fallback a SQLite
    sqlite_url = _get_sqlite_url()
    eng, sess = _init_engine_and_session(sqlite_url)
    Base.metadata.create_all(eng)
    DATABASE_URL = sqlite_url
    engine = eng
    SessionLocal = sess
    if DB_STATUS != "fallback":
        DB_STATUS = "sqlite"


def init_db():
    """Inicializa la conexión y crea las tablas si no existen."""
    _resolve_and_setup()


def get_session():
    if SessionLocal is None:
        init_db()
    return SessionLocal()

