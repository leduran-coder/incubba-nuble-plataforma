"""
Importador de postulaciones desde el CSV de respuestas del Google Form.

Cómo se obtiene ese CSV (instrucciones para el equipo Incubba):
  1. Abrir la hoja de cálculo de "Respuestas" vinculada al formulario.
  2. Archivo > Descargar > Valores separados por comas (.csv).
  3. Subir ese archivo en la página "Importar postulaciones" de esta app.

Como el texto EXACTO de cada columna puede variar levemente según cómo
Google Forms exporte los encabezados (saltos de línea, tildes, preguntas
repetidas como "Correo"), el importador NO asume nombres de columna fijos:
sugiere automáticamente la mejor columna para cada campo por similitud de
texto, y el/la administrador/a confirma o corrige el mapeo antes de
importar. Así nunca se pierde información aunque cambie el formulario.
"""
import difflib
import json

import pandas as pd

from db.database import get_session
from db.models import Postulacion

# Cada campo interno del modelo, con una etiqueta legible y palabras clave
# tomadas literalmente de las preguntas del formulario de postulación 2026,
# usadas para sugerir automáticamente la columna correcta del CSV.
FIELD_DEFINITIONS = [
    ("correo", "Correo electrónico", ["correo"]),
    ("nombres", "Nombres", ["nombres"]),
    ("apellido_paterno", "Apellido paterno", ["apellido paterno"]),
    ("apellido_materno", "Apellido materno", ["apellido materno"]),
    ("run", "RUN", ["run"]),
    ("fecha_nacimiento", "Fecha de nacimiento", ["fecha de nacimiento"]),
    ("genero", "Género", ["género", "genero"]),
    ("telefono", "Número de contacto / teléfono", ["número de contacto", "telefono", "teléfono"]),
    ("residencia_tipo", "Residencia del emprendedor o el emprendimiento", ["residencia del emprendedor"]),
    ("provincia", "Provincia de residencia", ["provincia de residencia", "provincia"]),
    ("comuna", "Comuna de residencia", ["comuna de residencia", "comuna"]),
    ("participa_programa_similar", "¿Participando en otro programa similar?", ["programa similar de formación"]),
    ("tipo_emprendimiento", "Tipo de emprendimiento (Idea/Formalizado)", ["tipo de emprendimiento"]),
    ("estado_detalle", "Alternativa que corresponde a su caso", ["alternativa que corresponda a su caso"]),
    ("nombre_emprendimiento", "Nombre del emprendimiento/negocio/idea", ["nombre del emprendimiento"]),
    ("nombre_empresa", "Nombre empresa o razón social", ["nombre empresa", "razón social"]),
    ("rut_empresa", "RUT de la empresa", ["rut de la empresa"]),
    ("tipo_empresa", "Tipo de empresa", ["tipo de empresa"]),
    ("sector_industria", "Sector o industria", ["sector o industria"]),
    ("tamano_empresa", "Tamaño de la empresa", ["tamaño de la empresa"]),
    ("descripcion", "Descripción de la idea o emprendimiento", ["descripción de mi idea"]),
    ("propuesta_valor", "Propuesta de valor", ["propuesta de valor"]),
    ("ha_levantado_financiamiento", "¿Ha levantado financiamiento?", ["levantado financiamiento"]),
    ("detalle_financiamiento", "Indique qué financiamiento ha levantado", ["qué financiamiento ha levantado"]),
    ("cree_que_es_innovacion", "¿Cree que su emprendimiento es innovación?", ["cree usted que su emprendimiento es innovación"]),
    ("por_que_innovador", "¿Por qué cree que es innovador?", ["por qué cree usted que su emprendimiento es innovador"]),
    ("tipo_potencial_innovador", "Tipo de potencial innovador", ["qué tipo potencial innovador"]),
    ("tipo_innovacion", "Tipo de innovación", ["tipo de innovación"]),
    ("alcance_innovacion", "Alcance de la innovación", ["alcance de la innovación"]),
    ("sector_area_impacto", "Sector o área económica de impacto", ["sector o área económica de impacto"]),
    ("resultados_3_anios", "Resultados esperados próximos 3 años", ["resultados espera lograr"]),
    ("impacto_esperado", "Impacto social/económico/ambiental esperado", ["impacto social, económico o ambiental"]),
    ("num_personas_equipo", "N° de personas en el equipo", ["cuántas personas conforman su equipo"]),
    ("descripcion_equipo", "Descripción del equipo", ["describa a su equipo"]),
    ("video_link", "Enlace del video pitch", ["enlace donde podamos ver su video"]),
    ("video_password", "Contraseña del video", ["contraseña"]),
]


def _normaliza(texto):
    return str(texto).strip().lower()


def sugerir_mapeo(columnas_csv):
    """Devuelve dict {campo_interno: columna_csv_sugerida_o_None}."""
    mapeo = {}
    columnas_norm = {c: _normaliza(c) for c in columnas_csv}
    for campo, _label, keywords in FIELD_DEFINITIONS:
        mejor_columna = None
        mejor_score = 0.0
        for col, col_norm in columnas_norm.items():
            score = 0.0
            for kw in keywords:
                if kw in col_norm:
                    score = max(score, 0.9 + 0.1 * (len(kw) / max(len(col_norm), 1)))
            if score == 0.0:
                score = difflib.SequenceMatcher(None, col_norm, keywords[0]).ratio() * 0.5
            if score > mejor_score:
                mejor_score = score
                mejor_columna = col
        mapeo[campo] = mejor_columna if mejor_score >= 0.35 else None
    return mapeo


def importar_dataframe(df: pd.DataFrame, mapeo: dict, evitar_duplicados: bool = True):
    """
    Inserta cada fila del DataFrame como una Postulacion, según `mapeo`
    (campo_interno -> nombre_columna_csv). Devuelve (num_nuevas, num_omitidas).
    """
    session = get_session()
    nuevas, omitidas = 0, 0
    try:
        existentes = set()
        if evitar_duplicados:
            for run, correo in session.query(Postulacion.run, Postulacion.correo).all():
                existentes.add((run or "", correo or ""))

        for _, fila in df.iterrows():
            def val(campo):
                col = mapeo.get(campo)
                if col is None or col not in fila:
                    return None
                v = fila[col]
                if pd.isna(v):
                    return None
                return str(v).strip()

            run = val("run")
            correo = val("correo")
            if evitar_duplicados and (run or correo) and (run or "", correo or "") in existentes:
                omitidas += 1
                continue

            num_equipo = val("num_personas_equipo")
            try:
                num_equipo = int(float(num_equipo)) if num_equipo else None
            except ValueError:
                num_equipo = None

            postulacion = Postulacion(
                correo=correo,
                nombres=val("nombres"),
                apellido_paterno=val("apellido_paterno"),
                apellido_materno=val("apellido_materno"),
                run=run,
                fecha_nacimiento=val("fecha_nacimiento"),
                genero=val("genero"),
                telefono=val("telefono"),
                residencia_tipo=val("residencia_tipo"),
                provincia=val("provincia"),
                comuna=val("comuna"),
                participa_programa_similar=val("participa_programa_similar"),
                tipo_emprendimiento=val("tipo_emprendimiento"),
                estado_detalle=val("estado_detalle"),
                nombre_emprendimiento=val("nombre_emprendimiento"),
                nombre_empresa=val("nombre_empresa"),
                rut_empresa=val("rut_empresa"),
                tipo_empresa=val("tipo_empresa"),
                sector_industria=val("sector_industria"),
                tamano_empresa=val("tamano_empresa"),
                descripcion=val("descripcion"),
                propuesta_valor=val("propuesta_valor"),
                ha_levantado_financiamiento=val("ha_levantado_financiamiento"),
                detalle_financiamiento=val("detalle_financiamiento"),
                cree_que_es_innovacion=val("cree_que_es_innovacion"),
                por_que_innovador=val("por_que_innovador"),
                tipo_potencial_innovador=val("tipo_potencial_innovador"),
                tipo_innovacion=val("tipo_innovacion"),
                alcance_innovacion=val("alcance_innovacion"),
                sector_area_impacto=val("sector_area_impacto"),
                resultados_3_anios=val("resultados_3_anios"),
                impacto_esperado=val("impacto_esperado"),
                num_personas_equipo=num_equipo,
                descripcion_equipo=val("descripcion_equipo"),
                video_link=val("video_link"),
                video_password=val("video_password"),
                raw_json=json.dumps(fila.dropna().to_dict(), ensure_ascii=False, default=str),
            )
            session.add(postulacion)
            nuevas += 1

        session.commit()
    finally:
        session.close()
    return nuevas, omitidas
