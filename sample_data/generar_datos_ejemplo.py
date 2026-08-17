"""
Genera un CSV de ejemplo con la MISMA estructura de encabezados que exportaría
Google Forms para el "Formulario de Postulación - 2026", incluyendo la
columna "Correo" repetida (tal como ocurre en el formulario real), para
probar que el importador de la plataforma funciona con datos realistas.

Uso:  python sample_data/generar_datos_ejemplo.py
"""
import random
import csv
from pathlib import Path

random.seed(7)

COMUNAS = {
    "Punilla": ["Coihueco", "San Fabián", "Ñiquén", "San Carlos", "San Nicolás"],
    "Diguillín": ["Bulnes", "Chillán", "Chillán Viejo", "El Carmen", "Pemuco", "Pinto", "Quillón", "San Ignacio", "Yungay"],
    "Itata": ["Cobquecura", "Coelemu", "Ninhue", "Portezuelo", "Quirihue", "Ránquil", "Trehuaco"],
}

NOMBRES_F = ["María", "Camila", "Javiera", "Fernanda", "Constanza", "Antonia", "Valentina", "Paula", "Carla", "Daniela"]
NOMBRES_M = ["Matías", "Sebastián", "Diego", "Cristóbal", "Felipe", "Tomás", "Ignacio", "Rodrigo", "Andrés", "Pablo"]
APELLIDOS = ["González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva", "Martínez", "Sepúlveda",
             "Morales", "Rodríguez", "López", "Fuentes", "Hernández", "Torres", "Araya", "Flores", "Espinoza", "Valenzuela"]
SECTORES = ["Agroindustria", "Turismo", "Tecnología", "Alimentos", "Educación", "Salud", "Servicios", "Manufactura", "Energía", "Comercio"]
TIPO_EMPRESA = ["Empresa Individual de Responsabilidad Limitada (EIRL)", "Sociedad de Responsabilidad Limitada (Ltda)",
                "Sociedad por Acciones (SpA)"]

HEADERS = [
    "Marca temporal", "Correo",
    "¿Declara que he leído, comprendido y acepto íntegramente las Bases del Concurso...?",
    "Nombres", "Apellido paterno", "Apellido materno", "RUN", "Fecha de nacimiento", "Género",
    "Correo", "Número de contacto",
    "Residencia del emprendedor o el emprendimiento", "Provincia de residencia", "Comuna de residencia",
    "¿Está participando en un programa similar de formación para emprendedores?",
    "Tipo de emprendimiento",
    "Seleccione la alternativa que corresponda a su caso",
    "Nombre del emprendimiento, negocio, idea o proyecto",
    "Nombre empresa o razón social", "RUT de la empresa", "Tipo de empresa", "Sector o industria",
    "Tamaño de la empresa",
    "Descripción de mi idea o emprendimiento", "Propuesta de valor",
    "¿Ha levantado financiamiento público o privado?", "Indique qué financiamiento ha levantado",
    "¿Cree usted que su emprendimiento es innovación?", "¿Por qué cree usted que su emprendimiento es innovador?",
    "¿Qué tipo potencial innovador tiene su emprendimiento?", "Tipo de innovación", "Alcance de la innovación",
    "Indicar el sector o área económica de impacto o interés",
    "¿Qué resultados espera lograr los próximos 3 años para su emprendimiento?",
    "¿Qué impacto social, económico o ambiental espera generar con su emprendimiento en la región de Ñuble?",
    "¿Cuántas personas conforman su equipo? (Incluyéndose usted)", "Describa a su equipo",
    "Ingrese el enlace donde podamos ver su video", "Contraseña (OPCIONAL)",
]

filas = []
for i in range(1, 46):
    genero = random.choices(["Femenino", "Masculino", "Prefiero no decirlo"], weights=[0.55, 0.42, 0.03])[0]
    nombre = random.choice(NOMBRES_F if genero == "Femenino" else NOMBRES_M)
    ap_paterno = random.choice(APELLIDOS)
    ap_materno = random.choice(APELLIDOS)
    provincia = random.choice(list(COMUNAS.keys()))
    comuna = random.choice(COMUNAS[provincia])
    tipo = random.choices(["Idea", "Formalizado"], weights=[0.6, 0.4])[0]
    tipo_innov = random.choices(["Disruptiva", "Incremental", "Marginal"], weights=[0.25, 0.5, 0.25])[0]
    alcance = random.choices(["Regional", "Nacional", "Internacional"], weights=[0.4, 0.4, 0.2])[0]
    financiamiento = random.choices(["Sí", "No"], weights=[0.3, 0.7])[0]
    sector = random.choice(SECTORES)
    nombre_proy = f"{sector}{'Ñuble' if random.random() < 0.3 else ''} {random.choice(['Sur','Andes','Bio','活','Norte','Plus','Lab'])}".strip()

    fila = {
        "Marca temporal": f"2026/07/{(i % 28) + 1:02d} {9 + (i % 8)}:{(i*7) % 60:02d}:00",
        "Correo": f"postulante{i}@ejemplo.cl",
        "¿Declara que he leído, comprendido y acepto íntegramente las Bases del Concurso...?": "Sí",
        "Nombres": nombre,
        "Apellido paterno": ap_paterno,
        "Apellido materno": ap_materno,
        "RUN": f"{10000000 + i*137}-{i % 10}",
        "Fecha de nacimiento": f"199{i % 9}-0{(i % 9)+1}-1{i % 9}",
        "Género": genero,
        "Correo": f"postulante{i}@ejemplo.cl",
        "Número de contacto": f"+56 9 {10000000 + i*991}",
        "Residencia del emprendedor o el emprendimiento": "Mi emprendimiento y mi residencia son en Ñuble",
        "Provincia de residencia": provincia,
        "Comuna de residencia": comuna,
        "¿Está participando en un programa similar de formación para emprendedores?": "No, es el único programa al que he postulado",
        "Tipo de emprendimiento": tipo,
        "Seleccione la alternativa que corresponda a su caso": (
            "Mi proyecto es solo una idea, me gustaría concretarlo" if tipo == "Idea"
            else "Mi emprendimiento está formalizado ante el SII hace menos de 12 meses y no ha generado ventas"
        ),
        "Nombre del emprendimiento, negocio, idea o proyecto": nombre_proy,
        "Nombre empresa o razón social": nombre_proy if tipo == "Formalizado" else "",
        "RUT de la empresa": f"{76000000 + i*13}-{i % 10}" if tipo == "Formalizado" else "",
        "Tipo de empresa": random.choice(TIPO_EMPRESA) if tipo == "Formalizado" else "",
        "Sector o industria": sector,
        "Tamaño de la empresa": "Micro",
        "Descripción de mi idea o emprendimiento": f"Emprendimiento de {sector.lower()} enfocado en la región de Ñuble, con foco en {comuna}.",
        "Propuesta de valor": f"Solución diferenciada en {sector.lower()} que resuelve un problema local concreto.",
        "¿Ha levantado financiamiento público o privado?": financiamiento,
        "Indique qué financiamiento ha levantado": "Capital Semilla CORFO" if financiamiento == "Sí" else "",
        "¿Cree usted que su emprendimiento es innovación?": "Sí",
        "¿Por qué cree usted que su emprendimiento es innovador?": "Porque incorpora un proceso o modelo distinto al existente en la región.",
        "¿Qué tipo potencial innovador tiene su emprendimiento?": tipo_innov,
        "Tipo de innovación": random.choice(["Producto", "Proceso", "Modelo de negocio", "Servicio"]),
        "Alcance de la innovación": alcance,
        "Indicar el sector o área económica de impacto o interés": sector,
        "¿Qué resultados espera lograr los próximos 3 años para su emprendimiento?": "Duplicar ventas cada 3 años y expandirse a nuevas comunas de la región.",
        "¿Qué impacto social, económico o ambiental espera generar con su emprendimiento en la región de Ñuble?": "Generación de empleo local y dinamización económica regional.",
        "¿Cuántas personas conforman su equipo? (Incluyéndose usted)": random.choice([1, 1, 2, 2, 3]),
        "Describa a su equipo": f"{nombre} {ap_paterno} (fundador/a), a cargo de la estrategia y desarrollo del proyecto.",
        "Ingrese el enlace donde podamos ver su video": f"https://youtu.be/ejemplo{i}",
        "Contraseña (OPCIONAL)": "",
    }
    filas.append(fila)

out_path = Path(__file__).parent / "postulaciones_ejemplo.csv"
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    for fila in filas:
        writer.writerow(fila)

print(f"Generadas {len(filas)} filas en {out_path}")
