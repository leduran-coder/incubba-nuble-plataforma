"""
Identidad visual y diseño profesional de Incubba Ñuble UBB.
Centraliza colores, estilos responsive (PC / móvil), logotipo oficial
y componentes de interfaz con alto contraste y micro-interacciones.
"""
import base64
import re
from pathlib import Path

# --- Paleta de Marca Oficial (extraída del logo y bases) ---
MORADO = "#684182"          # Morado institucional principal
MORADO_VIBRANTE = "#7C3AED" # Morado eléctrico para acentos interactivos y botones
MORADO_OSCURO = "#4A2B60"   # Morado profundo para contrastes
MENTA = "#2DD4BF"           # Verde menta/teal luminoso para contrastes y pills
MENTA_CLARO = "#96D4CE"     # Tono menta del logo
NAVY_OSCURO = "#0F172A"     # Azul pizarra profundo (Fondo de barra lateral)
NAVY_MEDIO = "#1E293B"      # Azul pizarra medio
BLANCO = "#FFFFFF"
GRIS_FONDO = "#F8FAFC"      # Fondo limpio estilo SaaS moderno
GRIS_BORDE = "#E2E8F0"      # Borde sutil para tarjetas
GRIS_TEXTO = "#0F172A"      # Texto principal de alta legibilidad
GRIS_MUTED = "#64748B"      # Texto secundario

# --- Degradados ---
GRADIENTE_HERO = "linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #581C87 100%)"
GRADIENTE_BOTON = "linear-gradient(135deg, #7C3AED 0%, #6366F1 100%)"
GRADIENTE_CARD_ACCENT = "linear-gradient(90deg, #7C3AED 0%, #2DD4BF 100%)"

# --- Paletas para Gráficos (Plotly) accesibles y de alto contraste ---
PALETA_CATEGORICA = [
    "#2563EB",  # Azul vibrante
    "#EA580C",  # Naranja
    "#0D9488",  # Teal/Menta
    "#D97706",  # Ámbar
    "#DB2777",  # Magenta
    "#16A34A",  # Verde esmeralda
    "#7C3AED",  # Violeta marca
    "#DC2626",  # Rojo
]
PALETA_SECUENCIAL = ["#E0E7FF", "#A5B4FC", "#6366F1", "#4338CA", "#312E81"]
PALETA_DIVERGENTE = ["#2563EB", "#93C5FD", "#F1F5F9", "#FCA5A5", "#DC2626"]

COLOR_BUENO = "#16A34A"
COLOR_ADVERTENCIA = "#D97706"
COLOR_CRITICO = "#DC2626"


def _flatten_html(html: str) -> str:
    """
    Elimina la indentación de cada línea del HTML antes de pasarlo a
    st.markdown().

    Por qué es necesario: Streamlit pasa el contenido de st.markdown()
    por un parser de Markdown (CommonMark) antes de interpretar el HTML.
    Si una línea del string queda con 4 o más espacios de indentación
    (algo casi inevitable al escribir HTML "prolijo" dentro de funciones
    Python anidadas), Markdown la interpreta como un BLOQUE DE CÓDIGO y
    la muestra como texto plano en vez de renderizarla como HTML.
    Esta función aplana cualquier indentación para evitar ese problema.
    """
    return re.sub(r"(?m)^[ \t]+", "", html).strip()


def get_logo_base64() -> str:
    """Lee el logotipo PNG y lo retorna codificado en Base64 para incrustar en HTML."""
    logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/png;base64,{encoded}"
        except Exception:
            pass
    return ""


def css_global() -> str:
    """CSS profesional inyectado en la app: responsive, alto contraste y animaciones fluidas."""
    return f"""
    <style>
    /* ==========================================================================
       1. ESTILOS GLOBALES Y TIPOGRAFÍA
       ========================================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: {GRIS_FONDO};
        color: {GRIS_TEXTO};
    }}

    /* Scrollbar personalizada */
    ::-webkit-scrollbar {{
        width: 7px;
        height: 7px;
    }}
    ::-webkit-scrollbar-track {{
        background: #F1F5F9;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #CBD5E1;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #94A3B8;
    }}

    /* ==========================================================================
       2. BARRA LATERAL (SIDEBAR) CON ALTO CONTRASTE
       ========================================================================== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.25);
    }}

    /* Textos y títulos dentro del Sidebar */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: #F8FAFC !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown {{
        color: #E2E8F0 !important;
    }}

    /* Enlaces de Navegación del Menú lateral */
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {{
        color: #F1F5F9 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        margin: 4px 0 !important;
        padding: 10px 14px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {{
        background: rgba(255, 255, 255, 0.1) !important;
        color: #38BDF8 !important;
        transform: translateX(4px) !important;
        border-color: rgba(56, 189, 248, 0.2) !important;
    }}

    /* Elemento Activo en el Menú */
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {{
        background: linear-gradient(90deg, #7C3AED 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-left: 4px solid #2DD4BF !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4) !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] svg {{
        fill: #2DD4BF !important;
        color: #2DD4BF !important;
    }}

    /* ==========================================================================
       3. BANNER PRINCIPAL (HERO) CON LOGO Y RESPONSIVIDAD
       ========================================================================== */
    .incubba-hero-container {{
        background: {GRADIENTE_HERO};
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 28px;
        color: #FFFFFF;
        box-shadow: 0 10px 30px -5px rgba(30, 27, 75, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }}

    /* Efecto de luz ambiental en el Hero */
    .incubba-hero-container::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(45, 212, 191, 0.25) 0%, rgba(124, 58, 237, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }}

    .incubba-hero-content {{
        flex: 1;
        z-index: 1;
    }}

    .incubba-hero-logo-box {{
        background: #FFFFFF;
        padding: 14px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        max-width: 240px;
        flex-shrink: 0;
        z-index: 1;
        transition: transform 0.3s ease;
    }}

    .incubba-hero-logo-box:hover {{
        transform: scale(1.03);
    }}

    .incubba-hero-logo-img {{
        max-width: 100%;
        height: auto;
        max-height: 65px;
        object-fit: contain;
        display: block;
    }}

    .incubba-hero-title {{
        font-size: clamp(1.4rem, 2.5vw, 2.2rem);
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
        color: #FFFFFF;
    }}

    .incubba-hero-sub {{
        font-size: clamp(0.9rem, 1.2vw, 1.05rem);
        margin: 0 0 12px 0;
        color: #CBD5E1;
        font-weight: 500;
        line-height: 1.4;
    }}

    .incubba-pill-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(8px);
        color: #2DD4BF;
        border: 1px solid rgba(45, 212, 191, 0.35);
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }}

    .incubba-pill-dot {{
        width: 8px;
        height: 8px;
        background: #2DD4BF;
        border-radius: 50%;
        box-shadow: 0 0 10px #2DD4BF;
        animation: pulseDot 2s infinite;
    }}

    @keyframes pulseDot {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.3); opacity: 0.7; }}
    }}

    /* ==========================================================================
       4. TARJETAS DE MÉTRICAS (METRIC CARDS) PRO
       ========================================================================== */
    div[data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border: 1px solid {GRIS_BORDE} !important;
        border-radius: 16px !important;
        padding: 18px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: {GRADIENTE_CARD_ACCENT};
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -3px rgba(124, 58, 237, 0.12), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        border-color: #CBD5E1 !important;
    }}

    div[data-testid="stMetric"] label {{
        color: {GRIS_MUTED} !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {GRIS_TEXTO} !important;
        font-weight: 800 !important;
        font-size: 1.85rem !important;
    }}

    /* ==========================================================================
       5. BOTONES E INPUTS
       ========================================================================== */
    .stButton > button {{
        background: {GRADIENTE_BOTON} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 10px 22px !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 44px !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45) !important;
        filter: brightness(1.08) !important;
    }}

    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    /* Inputs y Formularios */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {{
        border-radius: 10px !important;
        border: 1px solid {GRIS_BORDE} !important;
        background-color: #FFFFFF !important;
        color: {GRIS_TEXTO} !important;
        font-size: 0.95rem !important;
        min-height: 44px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: {MORADO_VIBRANTE} !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
    }}

    /* ==========================================================================
       6. PESTAÑAS (TABS) Y EXPANDERS
       ========================================================================== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px !important;
        background-color: #F1F5F9 !important;
        padding: 6px !important;
        border-radius: 14px !important;
        border: 1px solid {GRIS_BORDE} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: {GRIS_MUTED} !important;
        padding: 8px 18px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #FFFFFF !important;
        color: {MORADO_VIBRANTE} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }}

    .streamlit-expanderHeader {{
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid {GRIS_BORDE} !important;
        font-weight: 600 !important;
        color: {GRIS_TEXTO} !important;
    }}

    /* ==========================================================================
       7. RESPONSIVIDAD MÓVIL (MEDIA QUERIES)
       ========================================================================== */
    @media (max-width: 768px) {{
        .incubba-hero-container {{
            flex-direction: column-reverse !important;
            text-align: center !important;
            padding: 22px 18px !important;
            gap: 16px !important;
        }}

        .incubba-hero-logo-box {{
            max-width: 180px !important;
            margin: 0 auto !important;
            padding: 10px 16px !important;
        }}

        .incubba-hero-logo-img {{
            max-height: 50px !important;
        }}

        .incubba-pill-badge {{
            margin: 0 auto !important;
        }}

        div[data-testid="stMetric"] {{
            padding: 14px 14px !important;
            margin-bottom: 8px !important;
        }}

        .stButton > button {{
            width: 100% !important;
        }}

        /* Reducción de espaciados laterales en móviles */
        .main .block-container {{
            padding: 1.5rem 1rem !important;
        }}
    }}
    </style>
    """


def hero(titulo: str, subtitulo: str = "", pill: str = "Convocatoria 2026") -> str:
    """
    Genera el HTML del banner Hero responsive con el logotipo oficial incrustado,
    título de la sección, subtítulo y píldora de estado con animación de pulso.
    """
    logo_src = get_logo_base64()

    logo_html = ""
    if logo_src:
        logo_html = f"""
        <div class="incubba-hero-logo-box">
            <img src="{logo_src}" alt="Incubba Ñuble UBB" class="incubba-hero-logo-img" />
        </div>
        """
    else:
        logo_html = """
        <div class="incubba-hero-logo-box" style="color:#0F172A; font-weight:800; font-size:1.1rem;">
            incubba · Ñuble UBB
        </div>
        """

    pill_html = ""
    if pill:
        pill_html = f"""
        <div class="incubba-pill-badge">
            <span class="incubba-pill-dot"></span>
            <span>{pill}</span>
        </div>
        """

    sub_html = f'<p class="incubba-hero-sub">{subtitulo}</p>' if subtitulo else ""

    html = f"""
    <div class="incubba-hero-container">
        <div class="incubba-hero-content">
            <h1 class="incubba-hero-title">{titulo}</h1>
            {sub_html}
            {pill_html}
        </div>
        {logo_html}
    </div>
    """
    return _flatten_html(html)


def sidebar_branding(usuario_info=None):
    """
    Componente visual para la cabecera de la barra lateral con logotipo oficial
    y ficha de usuario activo.
    """
    import streamlit as st
    logo_src = get_logo_base64()
    if logo_src:
        st.sidebar.markdown(
            _flatten_html(f"""
            <div style="background:#FFFFFF; padding:12px 16px; border-radius:14px; margin-bottom:16px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                <img src="{logo_src}" style="max-width:100%; max-height:48px; object-fit:contain;" alt="Incubba" />
            </div>
            """),
            unsafe_allow_html=True,
        )

    if usuario_info:
        rol_badge_color = "#2DD4BF" if usuario_info.get("rol") == "admin" else "#93C5FD"
        rol_label = "Administrador/a" if usuario_info.get("rol") == "admin" else "Evaluador/a"
        st.sidebar.markdown(
            _flatten_html(f"""
            <div style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:10px 14px; margin-bottom:16px;">
                <div style="color:#94A3B8; font-size:0.75rem; text-transform:uppercase; font-weight:700; letter-spacing:0.05em;">Usuario activo</div>
                <div style="color:#FFFFFF; font-weight:700; font-size:0.95rem; margin-top:2px;">{usuario_info.get('nombre', '')}</div>
                <div style="display:inline-block; background:rgba(45,212,191,0.15); color:{rol_badge_color}; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:999px; margin-top:4px;">
                    {rol_label}
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
