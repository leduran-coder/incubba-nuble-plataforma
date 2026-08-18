import streamlit as st

from auth import requerir_login
from db.database import get_session
from db.models import Postulacion, Evaluacion, BonificacionManual
from db.config_store import get_config
from config.rubric import ETAPA_1, ETAPA_2, ETAPA_3, calcular_puntaje_criterio
from config.theme import css_global, hero, sidebar_branding
from utils.scoring import promedio_etapa, estado_admisibilidad, calcular_bonificacion

st.set_page_config(page_title="Evaluación · Incubba Ñuble UBB", page_icon="🎯", layout="wide")
st.markdown(css_global(), unsafe_allow_html=True)
usuario = requerir_login()
sidebar_branding(usuario)

st.markdown(hero("Evaluación de Postulaciones", "Calificación según las rúbricas oficiales de las bases y bonificación dinámica", pill="Pauta de Evaluación"), unsafe_allow_html=True)

session = get_session()
try:
    postulaciones = session.query(Postulacion).order_by(Postulacion.id).all()
finally:
    session.close()

if not postulaciones:
    st.info("Aún no hay postulaciones importadas. Ve a Configuración → Importar postulaciones.")
    st.stop()

opciones = {f"#{p.id} · {p.nombre_proyecto} — {p.nombre_completo}": p.id for p in postulaciones}
seleccion = st.selectbox("Selecciona la postulación a evaluar", list(opciones.keys()))
postulacion_id = opciones[seleccion]


def _cargar_respuestas(session, postulacion_id, evaluador_id, etapa_id):
    filas = (
        session.query(Evaluacion)
        .filter(
            Evaluacion.postulacion_id == postulacion_id,
            Evaluacion.evaluador_id == evaluador_id,
            Evaluacion.etapa_id == etapa_id,
        )
        .all()
    )
    return {f.criterio_id: f.nivel_seleccionado for f in filas}


def _guardar_respuestas(session, postulacion_id, evaluador_id, etapa_id, criterio, nivel, comentario=None):
    fila = (
        session.query(Evaluacion)
        .filter(
            Evaluacion.postulacion_id == postulacion_id,
            Evaluacion.evaluador_id == evaluador_id,
            Evaluacion.etapa_id == etapa_id,
            Evaluacion.criterio_id == criterio["id"],
        )
        .first()
    )
    puntos = calcular_puntaje_criterio(nivel, criterio)
    if fila is None:
        fila = Evaluacion(
            postulacion_id=postulacion_id, evaluador_id=evaluador_id,
            etapa_id=etapa_id, criterio_id=criterio["id"],
        )
        session.add(fila)
    fila.nivel_seleccionado = nivel
    fila.puntos = puntos
    if comentario is not None:
        fila.comentario = comentario


def render_etapa(etapa):
    session = get_session()
    try:
        respuestas_previas = _cargar_respuestas(session, postulacion_id, usuario["id"], etapa["id"])
        st.caption(etapa["descripcion"])
        nuevas_respuestas = {}
        for criterio in etapa["criterios"]:
            niveles = [n["nivel"] for n in criterio["niveles"]]
            valor_previo = respuestas_previas.get(criterio["id"])
            idx = niveles.index(valor_previo) if valor_previo in niveles else None
            seleccion_nivel = st.radio(
                f"{criterio['nombre']}  ·  peso {int(criterio['peso']*100)}%",
                niveles,
                index=idx,
                key=f"{etapa['id']}_{criterio['id']}_{postulacion_id}",
                horizontal=len(niveles) <= 3,
            )
            ayuda_sel = next((n["ayuda"] for n in criterio["niveles"] if n["nivel"] == seleccion_nivel), "")
            if ayuda_sel:
                st.caption(f"ℹ️ {ayuda_sel}")
            nuevas_respuestas[criterio["id"]] = seleccion_nivel

        comentario = st.text_area(
            "Comentarios / justificación (opcional)",
            key=f"comentario_{etapa['id']}_{postulacion_id}",
        )

        if st.button("Guardar evaluación de esta etapa", key=f"guardar_{etapa['id']}_{postulacion_id}", type="primary"):
            faltantes = [c["nombre"] for c in etapa["criterios"] if nuevas_respuestas.get(c["id"]) is None]
            if faltantes:
                st.warning(
                    "Falta calificar: " + ", ".join(faltantes) + ". "
                    "Guarda solo los criterios ya calificados; el promedio de la etapa se "
                    "calculará cuando estén todos completos."
                )
            for criterio in etapa["criterios"]:
                nivel = nuevas_respuestas.get(criterio["id"])
                if nivel is None:
                    continue  # no sobrescribir con un puntaje 0 falso por no responder
                _guardar_respuestas(
                    session, postulacion_id, usuario["id"], etapa["id"],
                    criterio, nivel, comentario,
                )
            session.commit()
            if not faltantes:
                st.success("Evaluación guardada.")
            st.rerun()

        puntaje = promedio_etapa(session, postulacion_id, etapa["id"])
        if puntaje is not None:
            st.metric("Puntaje promedio de esta etapa (todos los evaluadores)", puntaje)
        else:
            st.caption("Aún no hay evaluaciones completas de esta etapa para calcular un promedio.")
    finally:
        session.close()


tab1, tab2, tab3, tab4 = st.tabs([
    "Etapa 1 · Admisibilidad", "Etapa 2 · Proyecto", "Etapa 3 · Entrevista",
    "🚀 Bonificación potencial dinámico",
])

with tab1:
    render_etapa(ETAPA_1)
    session = get_session()
    try:
        estado, puntaje = estado_admisibilidad(session, postulacion_id)
    finally:
        session.close()
    color = {"Admisible": "green", "No admisible": "red", "Pendiente": "gray"}[estado]
    st.markdown(f"**Estado de admisibilidad:** :{color}[{estado}]")

with tab2:
    render_etapa(ETAPA_2)

with tab3:
    render_etapa(ETAPA_3)

with tab4:
    st.caption(
        "Bonificación adicional (no exigida literalmente por las bases) que premia el "
        "potencial dinámico real del proyecto: capacidad de crecer a tasas superiores al "
        "20% anual, según la definición de CORFO citada en el punto 4.1 de las bases. "
        "Los factores automáticos se toman de lo declarado en el formulario; el factor "
        "cualitativo lo calificas tú."
    )
    session = get_session()
    try:
        postulacion = session.get(Postulacion, postulacion_id)
        config = get_config(session, "bonificacion")

        st.markdown("**Factores automáticos (declarados por el postulante)**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tipo de potencial innovador", postulacion.tipo_potencial_innovador or "—")
        c2.metric("Alcance de la innovación", postulacion.alcance_innovacion or "—")
        c3.metric("Financiamiento previo", postulacion.ha_levantado_financiamiento or "—")

        st.markdown("**Factor cualitativo del panel**")
        st.write("¿Qué tan ambiciosa y creíble es la proyección de crecimiento a 3 años del proyecto?")
        bono_previo = (
            session.query(BonificacionManual)
            .filter(
                BonificacionManual.postulacion_id == postulacion_id,
                BonificacionManual.evaluador_id == usuario["id"],
            )
            .first()
        )
        valor_previo = bono_previo.valor_1_a_5 if bono_previo else 3
        valor = st.slider(
            "1 = poco creíble/ambiciosa · 5 = muy creíble y ambiciosa",
            1, 5, value=valor_previo, key=f"bono_slider_{postulacion_id}",
        )
        comentario_bono = st.text_area(
            "Justificación de esta calificación (opcional)",
            value=(bono_previo.comentario if bono_previo else ""),
            key=f"bono_comentario_{postulacion_id}",
        )
        if st.button("Guardar bonificación cualitativa", key=f"guardar_bono_{postulacion_id}"):
            if bono_previo is None:
                bono_previo = BonificacionManual(postulacion_id=postulacion_id, evaluador_id=usuario["id"])
                session.add(bono_previo)
            bono_previo.valor_1_a_5 = valor
            bono_previo.comentario = comentario_bono
            session.commit()
            st.success("Bonificación cualitativa guardada.")
            st.rerun()

        bono_total, detalle = calcular_bonificacion(session, postulacion)
        st.metric(f"Bonificación total estimada (máx. {config.get('puntaje_maximo', 10)} pts)", bono_total)
    finally:
        session.close()
