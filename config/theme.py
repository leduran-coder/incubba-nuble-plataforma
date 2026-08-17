"""
Identidad visual de Incubba Ñuble UBB, extraída de las Bases del Concurso
(portada y elementos gráficos). Un único lugar para colores y estilos, para
que la marca se pueda ajustar sin tocar cada página.
"""

# Colores muestreados directamente de la portada oficial (PDF de bases)
MORADO = "#966FC6"        # morado principal del degradé
MORADO_OSCURO = "#6B4A96"  # variante más oscura, para hover/estados activos
MENTA = "#ADE0DB"          # verde menta de acentos ("Ñuble UBB", texto sobre fondo oscuro)
AZUL_CLARO = "#ABD5E1"     # celeste del degradé superior derecho de la portada
NAVY = "#2A3F56"           # azul marino oscuro de la píldora "Bases del concurso"
BLANCO = "#FFFFFF"
GRIS_TEXTO = "#1F2A3C"

GRADIENTE_HERO = f"linear-gradient(135deg, {MORADO} 0%, {MORADO} 55%, {AZUL_CLARO} 100%)"

# Paleta categórica para gráficos: se usa la paleta de referencia validada del
# skill de dataviz (orden fijo verificado contra daltonismo/contraste con
# scripts/validate_palette.js), en vez de inventar tonos derivados de la marca
# sin validar. El violeta (slot 7) da un guiño a la marca sin sacrificar la
# validación. El morado/menta de marca se reserva para el "chrome" (encabezados,
# botones), nunca para codificar categorías de datos.
PALETA_CATEGORICA = [
    "#2a78d6",  # azul
    "#eb6834",  # naranjo
    "#1baf7a",  # aqua
    "#eda100",  # amarillo
    "#e87ba4",  # magenta
    "#008300",  # verde
    "#4a3aa7",  # violeta (más cercano a la marca)
    "#e34948",  # rojo
]

# Rampa secuencial (magnitud, un solo tono azul, claro→oscuro)
PALETA_SECUENCIAL = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]

# Par divergente (polaridad): azul ↔ rojo con punto medio neutro
PALETA_DIVERGENTE = ["#2a78d6", "#9ec5f4", "#f0efec", "#f0a19f", "#e34948"]

# Paleta de estado (fija, nunca para series de datos)
COLOR_BUENO = "#0ca30c"
COLOR_ADVERTENCIA = "#fab219"
COLOR_CRITICO = "#d03b3b"


def css_global():
    """CSS inyectado en todas las páginas para dar identidad visual Incubba."""
    return f"""
    <style>
    .stApp {{
        background-color: {BLANCO};
    }}
    .incubba-hero {{
        background: {GRADIENTE_HERO};
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: {BLANCO};
        box-shadow: 0 4px 18px rgba(107, 74, 150, 0.25);
    }}
    .incubba-hero h1 {{
        font-size: 2.1rem;
        margin: 0 0 4px 0;
        color: {BLANCO};
        font-weight: 800;
    }}
    .incubba-hero .accent {{
        color: {MENTA};
    }}
    .incubba-hero p {{
        margin: 2px 0 0 0;
        font-size: 1.0rem;
        opacity: 0.95;
    }}
    .incubba-pill {{
        display: inline-block;
        background: {NAVY};
        color: {MENTA};
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        margin-top: 10px;
    }}
    div[data-testid="stMetric"] {{
        background: #FAFAFC;
        border: 1px solid #ECE7F5;
        border-radius: 12px;
        padding: 12px 14px;
    }}
    section[data-testid="stSidebar"] {{
        background-color: #FAF8FD;
        border-right: 1px solid #ECE7F5;
    }}
    </style>
    """


def hero(titulo, subtitulo="", pill=None):
    """Devuelve el HTML del encabezado de marca para pegar con st.markdown(..., unsafe_allow_html=True)."""
    pill_html = f'<div class="incubba-pill">{pill}</div>' if pill else ""
    return f"""
    <div class="incubba-hero">
        <h1>inc<span class="accent">ubb</span>a · Ñuble UBB</h1>
        <p>{titulo}</p>
        {f'<p style="opacity:0.85;font-size:0.9rem">{subtitulo}</p>' if subtitulo else ''}
        {pill_html}
    </div>
    """
