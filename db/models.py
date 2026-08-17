"""
Modelo de datos (SQLAlchemy ORM) de la plataforma Incubba Ñuble UBB.

Funciona tanto con SQLite (uso local / pruebas, un archivo .db) como con
PostgreSQL (producción, por ejemplo un proyecto gratuito de Supabase o
Neon) sin cambiar una línea de código: solo cambia la variable de entorno
DATABASE_URL.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    rol = Column(String(20), nullable=False, default="evaluador")  # "admin" | "evaluador"
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=_now)

    evaluaciones = relationship("Evaluacion", back_populates="evaluador")


class Postulacion(Base):
    __tablename__ = "postulaciones"

    id = Column(Integer, primary_key=True)
    fuente_timestamp = Column(String(50))  # timestamp original del Google Form
    correo = Column(String(200))
    nombres = Column(String(200))
    apellido_paterno = Column(String(200))
    apellido_materno = Column(String(200))
    run = Column(String(20))
    fecha_nacimiento = Column(String(20))
    genero = Column(String(30))
    telefono = Column(String(50))

    residencia_tipo = Column(String(80))
    provincia = Column(String(40))
    comuna = Column(String(60))

    participa_programa_similar = Column(String(120))

    tipo_emprendimiento = Column(String(20))  # "Idea" | "Formalizado"
    estado_detalle = Column(String(160))      # sub-alternativa (idea o formalizado)
    nombre_emprendimiento = Column(String(250))
    nombre_empresa = Column(String(250))
    rut_empresa = Column(String(20))
    tipo_empresa = Column(String(80))
    sector_industria = Column(String(160))
    tamano_empresa = Column(String(20))

    descripcion = Column(Text)
    propuesta_valor = Column(Text)

    ha_levantado_financiamiento = Column(String(10))  # "Sí" | "No"
    detalle_financiamiento = Column(Text)

    cree_que_es_innovacion = Column(String(10))
    por_que_innovador = Column(Text)
    tipo_potencial_innovador = Column(String(20))  # Marginal | Incremental | Disruptiva
    tipo_innovacion = Column(String(60))
    alcance_innovacion = Column(String(20))  # Regional | Nacional | Internacional
    sector_area_impacto = Column(String(160))

    resultados_3_anios = Column(Text)
    impacto_esperado = Column(Text)

    num_personas_equipo = Column(Integer)
    descripcion_equipo = Column(Text)

    video_link = Column(String(500))
    video_password = Column(String(120))

    raw_json = Column(Text)  # respaldo íntegro de la fila original del CSV

    creado_en = Column(DateTime, default=_now)

    evaluaciones = relationship("Evaluacion", back_populates="postulacion", cascade="all, delete-orphan")
    bonificaciones_manuales = relationship("BonificacionManual", back_populates="postulacion", cascade="all, delete-orphan")

    @property
    def nombre_completo(self):
        partes = [self.nombres, self.apellido_paterno, self.apellido_materno]
        return " ".join(p for p in partes if p)

    @property
    def nombre_proyecto(self):
        return self.nombre_emprendimiento or self.nombre_empresa or "(sin nombre)"


class Evaluacion(Base):
    """Un puntaje de UN evaluador para UN criterio de UNA etapa de UNA postulación."""
    __tablename__ = "evaluaciones"
    __table_args__ = (
        UniqueConstraint("postulacion_id", "evaluador_id", "etapa_id", "criterio_id",
                          name="uq_evaluacion_unica"),
    )

    id = Column(Integer, primary_key=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"), nullable=False)
    evaluador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    etapa_id = Column(String(20), nullable=False)     # "etapa_1" | "etapa_2" | "etapa_3"
    criterio_id = Column(String(60), nullable=False)
    nivel_seleccionado = Column(String(60))
    puntos = Column(Float)
    comentario = Column(Text)
    creado_en = Column(DateTime, default=_now)
    actualizado_en = Column(DateTime, default=_now, onupdate=_now)

    postulacion = relationship("Postulacion", back_populates="evaluaciones")
    evaluador = relationship("Usuario", back_populates="evaluaciones")


class BonificacionManual(Base):
    """Componente cualitativo de la bonificación (ambición/credibilidad 1-5) por evaluador."""
    __tablename__ = "bonificaciones_manuales"
    __table_args__ = (
        UniqueConstraint("postulacion_id", "evaluador_id", name="uq_bono_manual_unico"),
    )

    id = Column(Integer, primary_key=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"), nullable=False)
    evaluador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    valor_1_a_5 = Column(Integer)
    comentario = Column(Text)
    creado_en = Column(DateTime, default=_now)
    actualizado_en = Column(DateTime, default=_now, onupdate=_now)

    postulacion = relationship("Postulacion", back_populates="bonificaciones_manuales")


class ConfiguracionClave(Base):
    """Tabla genérica clave/valor (JSON) para configuración editable desde la app:
    pesos de etapas, parámetros de bonificación, etc. Así no hay que tocar código
    para ajustar la ponderación entre convocatorias."""
    __tablename__ = "configuracion"

    clave = Column(String(80), primary_key=True)
    valor_json = Column(Text, nullable=False)
    actualizado_en = Column(DateTime, default=_now, onupdate=_now)
