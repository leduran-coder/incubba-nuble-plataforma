"""
Motor de cálculo de puntajes: agrega las evaluaciones de uno o varios
evaluadores, calcula el estado de admisibilidad, el puntaje ponderado final
y la bonificación por potencial dinámico. Todo a partir de los pesos y
configuración guardados en la base de datos (ver db/config_store.py), para
que el equipo gestor pueda ajustar ponderaciones sin tocar código.
"""
import pandas as pd

from config.rubric import ETAPA_1, ETAPA_2, ETAPA_3, calcular_puntaje_criterio
from db.config_store import get_config
from db.models import Evaluacion, BonificacionManual, Postulacion

ETAPAS_POR_ID = {"etapa_1": ETAPA_1, "etapa_2": ETAPA_2, "etapa_3": ETAPA_3}


def _evaluaciones_de(session, postulacion_id, etapa_id):
    return (
        session.query(Evaluacion)
        .filter(Evaluacion.postulacion_id == postulacion_id, Evaluacion.etapa_id == etapa_id)
        .all()
    )


def puntaje_etapa_por_evaluador(session, postulacion_id, etapa_id):
    """
    Devuelve dict {evaluador_id: puntaje_0_100} para una etapa, solo para
    evaluadores que hayan calificado TODOS los criterios de esa etapa.
    """
    etapa = ETAPAS_POR_ID[etapa_id]
    criterios_ids = {c["id"] for c in etapa["criterios"]}

    evaluaciones = _evaluaciones_de(session, postulacion_id, etapa_id)
    por_evaluador = {}
    for ev in evaluaciones:
        por_evaluador.setdefault(ev.evaluador_id, {})[ev.criterio_id] = ev

    resultado = {}
    for evaluador_id, respuestas in por_evaluador.items():
        if not criterios_ids.issubset(respuestas.keys()):
            continue  # evaluación incompleta, no se cuenta todavía
        total = 0.0
        for criterio in etapa["criterios"]:
            ev = respuestas[criterio["id"]]
            puntos = ev.puntos if ev.puntos is not None else calcular_puntaje_criterio(ev.nivel_seleccionado, criterio)
            total += puntos * criterio["peso"]
        resultado[evaluador_id] = round(total, 2)
    return resultado


def promedio_etapa(session, postulacion_id, etapa_id):
    puntajes = puntaje_etapa_por_evaluador(session, postulacion_id, etapa_id)
    if not puntajes:
        return None
    return round(sum(puntajes.values()) / len(puntajes), 2)


def estado_admisibilidad(session, postulacion_id):
    """Devuelve ('Admisible' | 'No admisible' | 'Pendiente', puntaje_o_None)."""
    puntaje = promedio_etapa(session, postulacion_id, "etapa_1")
    if puntaje is None:
        return "Pendiente", None
    umbral = ETAPA_1["umbral_aprobacion"]
    return ("Admisible" if puntaje > umbral else "No admisible"), puntaje


def calcular_bonificacion(session, postulacion: Postulacion):
    """
    Calcula la bonificación por potencial dinámico (0..puntaje_maximo) según
    la configuración editable. Devuelve (bono_final, detalle_por_factor).
    """
    config = get_config(session, "bonificacion")
    if not config.get("activa", True):
        return 0.0, {}

    detalle = {}
    total_ponderado = 0.0
    peso_total = 0.0

    campo_por_factor = {
        "tipo_innovacion": postulacion.tipo_potencial_innovador,
        "alcance_innovacion": postulacion.alcance_innovacion,
        "financiamiento_previo": postulacion.ha_levantado_financiamiento,
    }

    for factor in config.get("factores", []):
        fid = factor["id"]
        peso = factor.get("peso", 0)
        if fid == "ambicion_proyeccion":
            valores = [
                b.valor_1_a_5
                for b in session.query(BonificacionManual)
                .filter(BonificacionManual.postulacion_id == postulacion.id)
                .all()
                if b.valor_1_a_5 is not None
            ]
            if not valores:
                continue
            promedio_1_5 = sum(valores) / len(valores)
            puntos_factor = (promedio_1_5 - 1) / 4 * 10
        else:
            valor_postulante = campo_por_factor.get(fid)
            mapeo = factor.get("mapeo", {})
            if valor_postulante not in mapeo:
                continue
            puntos_factor = mapeo[valor_postulante]

        detalle[fid] = round(puntos_factor, 2)
        total_ponderado += puntos_factor * peso
        peso_total += peso

    if peso_total == 0:
        return 0.0, detalle

    # normaliza por si faltan factores (p.ej. nadie ha puesto el bono manual aún)
    puntaje_0_10 = total_ponderado / peso_total
    puntaje_maximo = config.get("puntaje_maximo", 10)
    bono_final = round(puntaje_0_10 / 10 * puntaje_maximo, 2)
    return bono_final, detalle


def calcular_resultado_final(session, postulacion: Postulacion):
    """
    Devuelve un dict con el detalle completo de resultado de una postulación:
    admisibilidad, puntaje etapa 2, puntaje etapa 3, bonificación y puntaje
    final combinado (0-100 + bono), usando los pesos configurables entre
    etapas guardados en la BD.
    """
    peso_etapas = get_config(session, "peso_etapas")

    estado_adm, puntaje_adm = estado_admisibilidad(session, postulacion.id)
    puntaje_e2 = promedio_etapa(session, postulacion.id, "etapa_2")
    puntaje_e3 = promedio_etapa(session, postulacion.id, "etapa_3")
    bono, detalle_bono = calcular_bonificacion(session, postulacion)

    componentes = []
    if puntaje_e2 is not None:
        componentes.append((puntaje_e2, peso_etapas.get("etapa_2", 0)))
    if puntaje_e3 is not None:
        componentes.append((puntaje_e3, peso_etapas.get("etapa_3", 0)))

    peso_usado = sum(p for _, p in componentes)
    if peso_usado > 0:
        base = sum(v * p for v, p in componentes) / peso_usado
    else:
        base = None

    puntaje_final = round(base + bono, 2) if base is not None else None

    return {
        "postulacion_id": postulacion.id,
        "estado_admisibilidad": estado_adm,
        "puntaje_admisibilidad": puntaje_adm,
        "puntaje_etapa_2": puntaje_e2,
        "puntaje_etapa_3": puntaje_e3,
        "bonificacion": bono,
        "detalle_bonificacion": detalle_bono,
        "puntaje_base": round(base, 2) if base is not None else None,
        "puntaje_final": puntaje_final,
    }


def tabla_ranking(session):
    """DataFrame con el ranking completo de todas las postulaciones."""
    filas = []
    for postulacion in session.query(Postulacion).all():
        r = calcular_resultado_final(session, postulacion)
        filas.append({
            "ID": postulacion.id,
            "Proyecto": postulacion.nombre_proyecto,
            "Postulante": postulacion.nombre_completo,
            "Comuna": postulacion.comuna,
            "Género": postulacion.genero,
            "Tipo": postulacion.tipo_emprendimiento,
            "Admisibilidad": r["estado_admisibilidad"],
            "Etapa 2": r["puntaje_etapa_2"],
            "Etapa 3": r["puntaje_etapa_3"],
            "Bonificación": r["bonificacion"],
            "Puntaje final": r["puntaje_final"],
        })
    df = pd.DataFrame(filas)
    if not df.empty:
        # Las postulaciones "No admisibles" quedan fuera de la fase siguiente según
        # las bases (punto 4.5.1), por lo que se ordenan después de las admisibles
        # y las pendientes, aunque tengan un puntaje calculado (se muestra solo
        # como referencia informativa, no participan del cupo final).
        orden_admisibilidad = {"Admisible": 0, "Pendiente": 1, "No admisible": 2}
        df["_orden_admisibilidad"] = df["Admisibilidad"].map(orden_admisibilidad).fillna(1)
        df = df.sort_values(
            ["_orden_admisibilidad", "Puntaje final"], ascending=[True, False], na_position="last"
        ).drop(columns="_orden_admisibilidad").reset_index(drop=True)
        df.insert(0, "Ranking", range(1, len(df) + 1))
    return df
