"""
Prueba de humo (sin Streamlit): valida que el importador, el motor de
rúbricas y el cálculo de resultados funcionen de punta a punta con datos
de ejemplo, antes de entregar la plataforma.

Uso:  python tests/smoke_test.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
db_path = Path(__file__).resolve().parent.parent / "data" / "incubba.db"
if db_path.exists():
    db_path.unlink()
    print(f"(Eliminada BD anterior en {db_path} para partir limpio)")

import pandas as pd

from db.database import init_db, get_session
from db.models import Postulacion, Usuario, BonificacionManual
from auth import asegurar_admin_por_defecto, crear_usuario, login
from utils.importer import sugerir_mapeo, importar_dataframe
from utils.scoring import (
    puntaje_etapa_por_evaluador, promedio_etapa, estado_admisibilidad,
    calcular_bonificacion, calcular_resultado_final, tabla_ranking,
)
from config.rubric import ETAPA_1, ETAPA_2, ETAPA_3

init_db()
asegurar_admin_por_defecto()
print("[OK] Base de datos inicializada.")

admin = login("admin@incubba.cl", "incubba2026")
assert admin is not None and admin["rol"] == "admin"
print("[OK] Login de administrador por defecto funciona.")

eval_id = crear_usuario("Evaluador Uno", "evaluador1@ubb.cl", "clave123", "evaluador")
eval2_id = crear_usuario("Evaluador Dos", "evaluador2@ubb.cl", "clave123", "evaluador")
print(f"[OK] Evaluadores creados: {eval_id}, {eval2_id}")

csv_path = Path(__file__).resolve().parent.parent / "sample_data" / "postulaciones_ejemplo.csv"
df = pd.read_csv(csv_path)
mapeo = sugerir_mapeo(list(df.columns))
faltantes = [campo for campo, col in mapeo.items() if col is None]
print(f"[INFO] Campos sin columna sugerida (revisar si es grave): {faltantes}")

nuevas, omitidas = importar_dataframe(df, mapeo, evitar_duplicados=True)
print(f"[OK] Importación: {nuevas} nuevas, {omitidas} omitidas.")

session = get_session()
total_postulaciones = session.query(Postulacion).count()
print(f"[OK] Total postulaciones en BD: {total_postulaciones}")
assert total_postulaciones == nuevas

primera = session.query(Postulacion).first()
print("[INFO] Ejemplo de postulación importada:")
for campo in ["correo", "nombres", "apellido_paterno", "genero", "provincia", "comuna",
              "tipo_emprendimiento", "sector_industria", "tipo_potencial_innovador",
              "alcance_innovacion", "ha_levantado_financiamiento", "num_personas_equipo"]:
    print(f"    {campo}: {getattr(primera, campo)!r}")

assert primera.correo and "@" in primera.correo, "El correo no se mapeó correctamente"
assert primera.genero in ("Femenino", "Masculino", "Prefiero no decirlo"), "El género no se mapeó correctamente"
assert primera.comuna, "La comuna no se mapeó correctamente"
print("[OK] Verificación de mapeo de campos clave: correcta.")

# --- Evaluar 3 postulaciones con 2 evaluadores distintos ------------------
postulaciones = session.query(Postulacion).limit(3).all()
for idx, p in enumerate(postulaciones):
    for etapa in (ETAPA_1, ETAPA_2, ETAPA_3):
        for evaluador_id in (eval_id, eval2_id):
            from db.models import Evaluacion
            for criterio in etapa["criterios"]:
                nivel = criterio["niveles"][idx % len(criterio["niveles"])]["nivel"]
                fila = Evaluacion(
                    postulacion_id=p.id, evaluador_id=evaluador_id,
                    etapa_id=etapa["id"], criterio_id=criterio["id"],
                    nivel_seleccionado=nivel,
                    puntos=criterio["niveles"][idx % len(criterio["niveles"])]["puntos"],
                )
                session.add(fila)
    bono_manual = BonificacionManual(postulacion_id=p.id, evaluador_id=eval_id, valor_1_a_5=4)
    session.add(bono_manual)
session.commit()
print(f"[OK] Evaluaciones de prueba creadas para {len(postulaciones)} postulaciones.")

for p in postulaciones:
    estado, puntaje_adm = estado_admisibilidad(session, p.id)
    p_e2 = promedio_etapa(session, p.id, "etapa_2")
    p_e3 = promedio_etapa(session, p.id, "etapa_3")
    bono, detalle = calcular_bonificacion(session, p)
    resultado = calcular_resultado_final(session, p)
    print(f"[INFO] Postulación #{p.id} ({p.nombre_proyecto}): "
          f"admisibilidad={estado} ({puntaje_adm}), etapa2={p_e2}, etapa3={p_e3}, "
          f"bono={bono} {detalle}, final={resultado['puntaje_final']}")
    assert resultado["puntaje_final"] is not None

df_ranking = tabla_ranking(session)
print(f"[OK] Ranking calculado para {len(df_ranking)} postulaciones (top 5):")
print(df_ranking.head(5).to_string(index=False))

session.close()
print("\n✅ TODAS LAS PRUEBAS DE HUMO PASARON CORRECTAMENTE.")
