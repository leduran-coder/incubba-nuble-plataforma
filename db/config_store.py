"""
Acceso de lectura/escritura a la tabla `configuracion` (clave -> JSON),
con valores por defecto tomados de config/rubric.py la primera vez que
se usan. Esto permite que el/la administrador/a ajuste pesos y topes de
la bonificación desde la interfaz, sin editar código.
"""
import json

from db.models import ConfiguracionClave
from config.rubric import PESO_ETAPAS_DEFAULT, BONIFICACION_DEFAULT, CRITERIOS_ADICIONALES

DEFAULTS = {
    "peso_etapas": PESO_ETAPAS_DEFAULT,
    "bonificacion": BONIFICACION_DEFAULT,
    "criterios_adicionales": CRITERIOS_ADICIONALES,
}


def get_config(session, clave):
    row = session.get(ConfiguracionClave, clave)
    if row is None:
        valor = DEFAULTS.get(clave, {})
        set_config(session, clave, valor)
        return valor
    return json.loads(row.valor_json)


def set_config(session, clave, valor):
    row = session.get(ConfiguracionClave, clave)
    payload = json.dumps(valor, ensure_ascii=False)
    if row is None:
        row = ConfiguracionClave(clave=clave, valor_json=payload)
        session.add(row)
    else:
        row.valor_json = payload
    session.commit()
    return valor
