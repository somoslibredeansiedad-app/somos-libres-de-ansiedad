import os
from dotenv import load_dotenv

load_dotenv()

import base64
import io
import json
import urllib.parse
from datetime import datetime, timedelta, timezone
from PIL import Image
import requests
import streamlit as st

THEME_COLORS = {
    "primary": "#A8E6CF",
    "background": "#EBF7F2",
    "surface": "#FFFFFF",
    "secondary": "#4E8A72",
    "text_primary": "#1E4D3B",
    "text_secondary": "#5C7A6F",
    "border": "#C2EAD9"
}

st.set_page_config(page_title="Somos Libres de Ansiedad", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    /* ESCALA TIPOGRÁFICA GLOBAL Y ACCESIBILIDAD */
    html, body, [class*="css"], .stMarkdown, p, span, label, div {{
        font-size: 18px !important;
        color: {THEME_COLORS['text_primary']};
    }}
    .stApp {{ background-color: {THEME_COLORS['background']}; }}
    
    h1 {{ font-size: 2.3rem !important; font-weight: 800 !important; color: {THEME_COLORS['text_primary']} !important; }}
    h2 {{ font-size: 1.85rem !important; font-weight: 700 !important; color: {THEME_COLORS['text_primary']} !important; }}
    h3 {{ font-size: 1.5rem !important; font-weight: 700 !important; color: {THEME_COLORS['text_primary']} !important; }}
    h4, h5, h6 {{ font-size: 1.3rem !important; font-weight: 600 !important; color: {THEME_COLORS['text_primary']} !important; }}
    
    /* ENTRADAS Y FORMULARIOS */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {{
        font-size: 18px !important;
        font-weight: 600 !important;
        margin-bottom: 6px !important;
        color: {THEME_COLORS['text_primary']} !important;
    }}
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        font-size: 18px !important;
        min-height: 48px !important;
        border: 1.5px solid {THEME_COLORS['secondary']} !important;
        border-radius: 8px !important;
    }}
    
    .stTextArea textarea {{
        min-height: 120px !important;
    }}

    .stButton button {{
        background-color: {THEME_COLORS['secondary']} !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        min-height: 46px !important;
        padding: 8px 16px !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.08) !important;
    }}
    .stButton button:hover {{
        background-color: #3B6B58 !important;
        color: #FFFFFF !important;
    }}

    /* TARJETA DE DEFINICIÓN DEL PROBLEMA */
    .problem-box {{
        background-color: #FFFFFF;
        border: 1.5px solid #C2EAD9;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.04);
        margin-bottom: 24px;
    }}
    .problem-box h3 {{
        margin: 0 0 8px 0 !important;
        font-size: 20px !important;
        color: #1E4D3B !important;
    }}
    .problem-box .problem-desc {{
        font-size: 15px !important;
        color: #5C7A6F !important;
        line-height: 1.5 !important;
        margin-bottom: 16px;
    }}
    
    /* SUB-TARJETA DE AVATAR IDÓNEO */
    .avatar-expert-card {{
        background-color: #F8FDFB;
        border: 1px solid #C2EAD9;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-top: 8px;
        min-height: 290px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .avatar-expert-card h4 {{
        margin: 8px 0 2px 0 !important;
        font-size: 16px !important;
        color: #1E4D3B !important;
    }}
    .avatar-expert-card .avatar-spec {{
        font-size: 13px !important;
        color: #4E8A72 !important;
        font-weight: 600;
        margin-bottom: 6px;
    }}

    /* BOTONES DE RUTAS CONVERSACIONALES GUIADAS */
    .btn-opcion-chat button {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        border: 1.5px solid {THEME_COLORS['secondary']} !important;
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        margin-bottom: 6px !important;
        font-size: 16px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }}
    .btn-opcion-chat button:hover {{
        background-color: #EBF7F2 !important;
        border-color: #2ECC71 !important;
        color: #15382A !important;
    }}

    /* PESTAÑAS Y TABS */
    button[data-baseweb="tab"] {{
        padding: 14px 24px !important;
    }}
    button[data-baseweb="tab"] div {{
        font-size: 19px !important;
        font-weight: 700 !important;
    }}

    /* BARRA LATERAL */
    [data-testid="stSidebar"] {{
        background-color: {THEME_COLORS['background']} !important;
        border-right: 1px solid {THEME_COLORS['border']} !important;
    }}
    [data-testid="stSidebar"] * {{
        font-size: 17px !important;
    }}
    
    .welcome-banner {{
        background: linear-gradient(135deg, #4E8A72 0%, #A8E6CF 100%);
        padding: 24px 20px;
        border-radius: 14px;
        color: #1E4D3B;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }}
    .welcome-banner h2 {{
        margin: 0 0 10px 0 !important;
        font-size: 1.9rem !important;
    }}
    .welcome-banner p {{
        margin: 0 !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
    }}
    
    /* CABECERA FIJA DE CHAT */
    .avatar-header-box {{
        background-color: #FFFFFF;
        padding: 14px 18px;
        border-radius: 12px;
        border: 1.5px solid #C2EAD9;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 14px;
    }}

    /* GLOBOS DE CHAT */
    [data-testid="stChatMessage"] {{
        padding: 14px 18px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
    }}
    
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: #2D4036 !important;
        border-left: 6px solid #4E8A72 !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {{
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }}

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        background-color: #FFFFFF !important;
        border-left: 6px solid #2ECC71 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) * {{
        color: #15382A !important;
        font-size: 18px !important;
        line-height: 1.65 !important;
    }}

    .avatar-subtitle {{
        color: #1E4D3B !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-top: -4px !important;
        margin-bottom: 4px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        font-size: 18px !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{
        color: #6A8277 !important;
        font-weight: 600 !important;
    }}

    .social-btn {{
        display: inline-block;
        padding: 10px 16px;
        margin: 6px 4px;
        border-radius: 8px;
        text-decoration: none;
        color: white !important;
        font-weight: bold;
        font-size: 15px;
    }}
    .post-card {{
        background: #FFFFFF;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 14px;
        border-left: 6px solid #4E8A72;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    
    .comment-card {{
        background: #F7FCF9;
        padding: 10px 14px;
        border-radius: 8px;
        margin-top: 8px;
        margin-left: 20px;
        border-left: 3px solid #A8E6CF;
        font-size: 16px !important;
    }}
    
    .timer-badge {{
        background-color: #FFFFFF;
        border: 1px solid #C2EAD9;
        border-left: 4px solid #4E8A72;
        padding: 8px 12px;
        border-radius: 8px;
        margin-top: 6px;
        margin-bottom: 14px;
        font-size: 14px !important;
        color: #1E4D3B;
        font-weight: 600;
    }}
    
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

raw_api_url = os.getenv("API_URL", "https://somos-libres-de-ansiedad-1.onrender.com").rstrip("/")
API_URL = raw_api_url if raw_api_url.endswith("/api") else f"{raw_api_url}/api"
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://somoslibredeansiedad-app.streamlit.app")
CRON_SECRET_KEY = os.getenv("CRON_SECRET_KEY", "somos-libres-cron-mantenimiento-2026")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_role" not in st.session_state:
    st.session_state.user_role = "user"
if "user_plan" not in st.session_state:
    st.session_state.user_plan = "gratis"
if "user_apodo" not in st.session_state:
    st.session_state.user_apodo = ""
if "avatar_activo" not in st.session_state:
    st.session_state.avatar_activo = None
if "problema_activo" not in st.session_state:
    st.session_state.problema_activo = None
if "token" not in st.session_state:
    st.session_state.token = None
if "horas_restantes_plan" not in st.session_state:
    st.session_state.horas_restantes_plan = None
if "dm_activo_contacto" not in st.session_state:
    st.session_state.dm_activo_contacto = None
if "menu_nav_seleccionado" not in st.session_state:
    st.session_state.menu_nav_seleccionado = "Definir el problema"
if "last_profile_sync" not in st.session_state:
    st.session_state.last_profile_sync = 0.0

ref_url = st.query_params.get("ref", "")

# CATÁLOGO DE LOS 5 AVATARES CON DATOS Y ESPECIALIDADES
GUIA_INFO = {
    "mariana": {
        "id": "mariana",
        "nombre": "Mariana Elena Rivas Delgado",
        "pais": "Venezuela",
        "bandera": "🇻🇪",
        "especialidad": "Relacionista Industrial y Clima Laboral",
        "resumen": "Especialista en sobrecarga laboral, burnout, mobbing y límites saludables."
    },
    "camilo": {
        "id": "camilo",
        "nombre": "Camilo Ernesto Valdés Portuondo",
        "pais": "Cuba",
        "bandera": "🇨🇺",
        "especialidad": "Médico General y Fisioterapeuta",
        "resumen": "Regulación somática, control de taquicardia, respiración diafragmática y duelo."
    },
    "rodrigo": {
        "id": "rodrigo",
        "nombre": "Rodrigo Javier Navas Serrano",
        "pais": "España",
        "bandera": "🇪🇸",
        "especialidad": "Abogado Penalista y Mediador",
        "resumen": "Pragmatismo estoico, desescalada de deudas, defensa ante abusos e insomnio."
    },
    "larissa": {
        "id": "larissa",
        "nombre": "Larissa Beatriz Fonseca de Oliveira",
        "pais": "Brasil",
        "bandera": "🇧🇷",
        "especialidad": "Psicóloga Somática y Arteterapeuta",
        "resumen": "Anclaje sensorial 5-4-3-2-1, contención ante acoso, trauma y autocompasión."
    },
    "anastasia": {
        "id": "anastasia",
        "nombre": "Anastasia Yurievna Volkova",
        "pais": "Rusia",
        "bandera": "🇷🇺",
        "especialidad": "Neuropsicóloga Clínica y Lingüista",
        "resumen": "Desarticulación de rumiación mental, niebla cognitiva, desrealización y ciclos de ánimo."
    }
}

# MATRIZ DE LAS 13 PROBLEMÁTICAS Y SUS AVATARES IDÓNEOS
LOCAL_PROBLEMAS = [
    {
        "id": "ansiedad_panico",
        "titulo": "💓 Ansiedad y Ataques de Pánico",
        "descripcion": "Taquicardia, palpitaciones, falta de aire, opresión en el pecho y mareos.",
        "avatares": ["camilo", "larissa"]
    },
    {
        "id": "depresion_vacio",
        "titulo": "🌧️ Depresión, Vacío y Desesperanza",
        "descripcion": "Tristeza profunda, falta de energía, apatía, aislamiento y pérdida de sentido.",
        "avatares": ["anastasia", "larissa"]
    },
    {
        "id": "angustia_deudas",
        "titulo": "🌙 Angustia por Deudas y Finanzas",
        "descripcion": "Insomnio por dinero, compromisos económicos urgentes, quiebras y vergüenza.",
        "avatares": ["rodrigo", "mariana"]
    },
    {
        "id": "bullying_acoso_escolar",
        "titulo": "📱 Bullying y Ciberacoso",
        "descripcion": "Burlas escolares o juveniles, difamación en grupos digitales, stickers y exclusión.",
        "avatares": ["larissa", "mariana"]
    },
    {
        "id": "acoso_sexual",
        "titulo": "🛑 Acoso Sexual y Abuso de Poder",
        "descripcion": "Insinuaciones indebidas, tocamientos no consentidos, chantaje y culpa inducida.",
        "avatares": ["larissa", "rodrigo"]
    },
    {
        "id": "acoso_laboral_mobbing",
        "titulo": "💼 Acoso Laboral (Mobbing) y Burnout",
        "descripcion": "Descalificaciones del jefe, sobrecarga injusta, humillación y desgaste ocupacional.",
        "avatares": ["mariana", "rodrigo"]
    },
    {
        "id": "victimas_abuso_violencia",
        "titulo": "⚡ Víctimas de Violencia Física o Abusos",
        "descripcion": "Sobrevivientes de agresiones directas, golpes, asaltos y relaciones violentas.",
        "avatares": ["rodrigo", "larissa"]
    },
    {
        "id": "miedos_fobias",
        "titulo": "🚪 Personas que no Pueden Superar sus Miedos",
        "descripcion": "Agorafobia, miedo a salir a la calle o pánico a transportes cerrados.",
        "avatares": ["camilo", "anastasia"]
    },
    {
        "id": "duelo_perdida",
        "titulo": "🕊️ Duelo por Pérdida de un Ser Querido",
        "descripcion": "Fallecimiento repentino, pérdidas sin despedida y culpa del sobreviviente.",
        "avatares": ["camilo", "rodrigo"]
    },
    {
        "id": "trauma_complejo_desrealizacion",
        "titulo": "🌫️ Traumas Psicológicos y Desrealización",
        "descripcion": "Sensación de flotar, desconexión del cuerpo o ver la realidad como una película.",
        "avatares": ["anastasia", "larissa"]
    },
    {
        "id": "desregulacion_bipolar",
        "titulo": "🎢 Desregulación Afectiva y Ciclos de Ánimo",
        "descripcion": "Oscilaciones marcadas entre entusiasmo sin freno y bajones profundos de energía.",
        "avatares": ["anastasia"]
    },
    {
        "id": "conversacion_abierta",
        "titulo": "☕ Solo Deseo Conversar y Desahogarme",
        "descripcion": "Acompañamiento humano, soledad cotidiana, empatía y escucha sin juicios.",
        "avatares": ["mariana", "camilo"]
    },
    {
        "id": "aprender_habitos_neurociencia",
        "titulo": "🧠 Aprender Neurociencia, Técnicas y Hábitos",
        "descripcion": "Regulación del sistema nervioso, dosificación de energía (pacing) y auto-perdón.",
        "avatares": ["anastasia", "camilo"]
    }
]

def comprimir_imagen(imagen_archivo) -> str:
    try:
        img = Image.open(imagen_archivo)
        img = img.convert("RGB")
        img.thumbnail((150, 150))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=75, optimize=True)
        img_bytes = buffer.getvalue()
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return ""

def resolver_imagen_pil(avatar_id_o_dict):
    if isinstance(avatar_id_o_dict, dict):
        avatar_id = avatar_id_o_dict.get("id", "")
    else:
        avatar_id = str(avatar_id_o_dict)

    avatar_id = avatar_id.replace(".png", "").replace(".jpg", "").strip()

    rutas = [
        os.path.join("avatares", f"{avatar_id}.png"),
        os.path.join("avatares", f"{avatar_id}.jpg"),
        f"{avatar_id}.png",
        f"{avatar_id}.jpg"
    ]
    for r in rutas:
        if os.path.exists(r):
            try:
                return Image.open(r)
            except Exception:
                pass
    return None

def mostrar_imagen_avatar(avatar_id_o_dict, ancho: int = 110):
    img = resolver_imagen_pil(avatar_id_o_dict)
    if img:
        st.image(img, width=ancho)
    else:
        st.markdown(f"<div style='width:{ancho}px; height:{ancho}px; margin:0 auto; background:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:50%; font-size:36px;'>🌿</div>", unsafe_allow_html=True)

if os.path.exists("Logo.png"):
    st.image("Logo.png", width=120)

st.title("🌿 Somos Libres de Ansiedad")

# ==================================================================================================
# INICIO DE SESIÓN / REGISTRO
# ==================================================================================================
if not st.session_state.authenticated:
    st.markdown("""
        <div class="welcome-banner">
            <h2>✨ Tu Refugio Seguro y Sin Fármacos ✨</h2>
            <p>Un espacio confidencial para recuperar tu calma interior y ordenar tus emociones.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

    with tab_login:
        correo_log = st.text_input("Correo Electrónico", key="log_correo")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        preg_secreta = None
        if correo_log.strip().lower() == "somos.libredeansiedad@gmail.com":
            st.info("🔒 Cuenta Maestra: Se requiere confirmación de seguridad.")
            preg_secreta = st.text_input("Palabra clave de seguridad:", type="password", key="log_admin_sec")

        if st.button("Ingresar a mi espacio", key="btn_ingresar_login"):
            if not correo_log.strip() or not pass_log.strip():
                st.warning("Por favor introduce tu correo electrónico y tu contraseña.")
            else:
                with st.spinner("Verificando credenciales..."):
                    try:
                        payload_log = {"correo": correo_log.strip(), "password": pass_log}
                        if preg_secreta:
                            payload_log["pregunta_secreta"] = preg_secreta.strip()

                        res = requests.post(f"{API_URL}/auth/login", json=payload_log, timeout=35)
                        if res.status_code == 200:
                            d = res.json()
                            st.session_state.authenticated = True
                            st.session_state.user_id = d.get("user_id")
                            st.session_state.user_role = d.get("role", "user")
                            st.session_state.user_plan = d.get("plan_actual", "gratis")
                            st.session_state.user_apodo = d.get("apodo", "")
                            st.session_state.token = d.get("access_token")
                            st.session_state.horas_restantes_plan = d.get("horas_restantes")
                            st.session_state.menu_nav_seleccionado = "Definir el problema"
                            st.session_state.last_profile_sync = datetime.now().timestamp()
                            st.success(f"¡Bienvenido/a {st.session_state.user_apodo}!")
                            if d.get("pensamiento_dia"):
                                st.info(f"💡 {d.get('pensamiento_dia')}")
                            st.rerun()
                        else:
                            try:
                                err_msg = res.json().get("detail", "Credenciales incorrectas o usuario no encontrado.")
                            except Exception:
                                err_msg = f"Error del servidor ({res.status_code}). Intenta de nuevo en unos segundos."
                            st.error(err_msg)
                    except requests.exceptions.Timeout:
                        st.error("El servidor demoró en responder. Espera 30 segundos y vuelve a presionar el botón.")
                    except Exception as e:
                        st.error(f"Falla de conexión con el servidor: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)", key="reg_nombre")
        apodo = st.text_input("Apodo o Nombre de Preferencia (*)", key="reg_apodo")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25, key="reg_edad")
        
        with st.expander("➕ Datos del Perfil (Opcionales para personalizar tu experiencia)"):
            sexo = st.selectbox("Sexo", ["Prefiero no decir", "Femenino", "Masculino", "Otro"], key="reg_sexo")
            profesion = st.text_input("Profesión u Ocupación", key="reg_profesion")
            situacion = st.selectbox("Situación Sentimental", ["Prefiero no decir", "Soltero/a", "En pareja / Casado/a", "Divorciado/a", "Viudo/a"], key="reg_situacion")
            hijos = st.number_input("Cantidad de Hijos", min_value=0, max_value=10, value=0, key="reg_hijos")

        codigo_ref = st.text_input("Código de Referido (opcional)", value=ref_url, key="reg_codigo_ref")
        
        with st.expander("📜 Términos de Servicio, Descargo Legal y Política de Privacidad Oficial", expanded=False):
            st.markdown("""
            ### Marco Legal, Ético y Sanitario
            
            **1. Naturaleza No Médica y Deslinde Sanitario Absoluto:**
            * «Somos Libres de Ansiedad» es una plataforma digital de carácter estrictamente educativo, reflexivo y de acompañamiento emocional asistido por Inteligencia Artificial[cite: 1, 2, 6].
            * **NO constituye un servicio médico, psiquiátrico, psicológico clínico ni psicoterapéutico[cite: 1, 2, 6].**
            * El software, sus creadores, colaboradores y avatares virtuales **NO son médicos colegiados ni terapeutas facultativos**, y bajo ninguna circunstancia emiten diagnósticos clínicos, altas ni prescripción de psicofármacos[cite: 1, 6].
            
            **2. Protocolo de Crisis y Exención en Emergencias:**
            * Si estás atravesando una emergencia médica, angustia invalidante o pensamientos de autolesión, acude de inmediato a un centro asistencial o a las líneas de auxilio gratuitas de tu país[cite: 1, 2, 6].
            """)

        t1 = st.checkbox("He leído, comprendo y acepto los Términos de Servicio y la Política de Privacidad. (*)", key="chk_terms")
        t2 = st.checkbox("Reconozco que este programa es una herramienta psicoeducativa de IA y no un servicio médico ni farmacológico. (*)", key="chk_disclaimer")
        
        if st.button("Completar mi Registro", key="btn_completar_registro"):
            if not t1 or not t2:
                st.warning("Debes marcar ambas casillas de aceptación de términos y descargo sanitario para registrarte.")
            elif not nombre.strip() or not apodo.strip() or not correo_reg.strip() or not pass_reg.strip():
                st.warning("Por favor completa los campos obligatorios marcados con (*).")
            else:
                with st.spinner("Registrando tu cuenta de forma segura..."):
                    payload = {
                        "nombre_completo": nombre.strip(),
                        "apodo": apodo.strip(),
                        "correo": correo_reg.strip(),
                        "password": pass_reg,
                        "edad": int(edad),
                        "sexo": None if sexo == "Prefiero no decir" else sexo,
                        "profesion": profesion.strip() or None,
                        "situacion_sentimental": None if situacion == "Prefiero no decir" else situacion,
                        "cantidad_hijos": int(hijos) if hijos > 0 else 0,
                        "codigo_referido": codigo_ref.strip() or None,
                        "terms_accepted": t1,
                        "disclaimer_accepted": t2
                    }
                    try:
                        res = requests.post(f"{API_URL}/auth/register", json=payload, timeout=35)
                        if res.status_code == 404:
                            res = requests.post(f"{API_URL}/auth/registro", json=payload, timeout=35)

                        if res.status_code in [200, 201]:
                            msg = res.json().get("message", "¡Registro completado con éxito! Ve a la pestaña 'Iniciar Sesión' para acceder.")
                            st.success(f"✅ {msg}")
                        else:
                            try:
                                detalle_error = res.json().get("detail", "No fue posible procesar el registro.")
                            except Exception:
                                detalle_error = f"Error en el servidor ({res.status_code}). Verifica los datos."
                            st.error(f"⚠️ {detalle_error}")
                    except Exception as e:
                        st.error(f"No se pudo conectar con el servidor: {e}")

# ==================================================================================================
# PANTALLA PRINCIPAL CON SESIÓN INICIADA
# ==================================================================================================
else:
    headers_auth = {"Authorization": f"Bearer {st.session_state.token}"}
    ahora_ts = datetime.now().timestamp()
    
    if ahora_ts - st.session_state.last_profile_sync > 60:
        try:
            r_sync = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, timeout=12)
            if r_sync.status_code == 200:
                d_perfil = r_sync.json().get("perfil", {})
                st.session_state.user_plan = d_perfil.get("plan_nivel", "gratis")
                st.session_state.horas_restantes_plan = d_perfil.get("horas_restantes")
                st.session_state.last_profile_sync = ahora_ts
        except Exception:
            pass

    # Sincronización de cuota de mensajes
    chats_disp_semana = 25
    try:
        r_cat = requests.get(f"{API_URL}/avatares/catalogo", headers=headers_auth, timeout=10)
        if r_cat.status_code == 200:
            chats_disp_semana = r_cat.json().get("chats_restantes", 25)
    except Exception:
        pass

    mis_contactos_dm = []
    if st.session_state.menu_nav_seleccionado == "Red Social y Comunidad":
        try:
            r_dm_contacts = requests.get(f"{API_URL}/comunidad/mis-chats", headers=headers_auth, timeout=10)
            if r_dm_contacts.status_code == 200:
                mis_contactos_dm = r_dm_contacts.json().get("contactos", [])
        except Exception:
            pass

    # MENÚ OFICIAL REESTRUCTURADO
    opciones = ["Definir el problema", "Chat con el Guía", "Red Social y Comunidad", "Planes y Suscripción"]
    if st.session_state.user_role == "admin":
        opciones.append("Panel de Administración")

    idx_actual = opciones.index(st.session_state.menu_nav_seleccionado) if st.session_state.menu_nav_seleccionado in opciones else 0
    menu = st.sidebar.selectbox("Navegación", opciones, index=idx_actual, key="sb_nav_menu")
    st.session_state.menu_nav_seleccionado = menu

    st.sidebar.markdown(f"**Plan:** <span style='color:#4E8A72; font-weight:bold;'>{st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)

    if st.session_state.user_role != "admin" and st.session_state.horas_restantes_plan is not None:
        horas = st.session_state.horas_restantes_plan
        if horas > 0:
            dias_calc = round(horas / 24, 1)
            st.sidebar.markdown(f"""
                <div class="timer-badge">
                    ⏱️ <strong>Vence en:</strong> {horas}h ({dias_calc} días)
                </div>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown("""
                <div class="timer-badge" style="border-left-color: #E74C3C; color: #C0392B;">
                    ⚠️ Plan vencido. Revertido a Gratis.
                </div>
            """, unsafe_allow_html=True)
            st.session_state.user_plan = "gratis"
            st.session_state.horas_restantes_plan = None
            st.rerun()

    if st.sidebar.button("Cerrar Sesión"):
        saved_ref = st.query_params.get("ref", "")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if saved_ref:
            st.query_params["ref"] = saved_ref
        st.rerun()

    # Barra lateral de información y acceso directo al guía en curso
    if menu in ["Definir el problema", "Chat con el Guía"]:
        st.sidebar.markdown("---")
        if st.session_state.avatar_activo:
            av_side = GUIA_INFO.get(st.session_state.avatar_activo, {})
            st.sidebar.markdown("### 🌿 Tu Guía Asignado")
            mostrar_imagen_avatar(st.session_state.avatar_activo, ancho=85)
            st.sidebar.write(f"**{av_side.get('nombre', '')}**")
            st.sidebar.caption(f"{av_side.get('bandera', '')} {av_side.get('pais', '')}")
            if st.sidebar.button("💬 Abrir Conversación", key="btn_side_open_chat"):
                st.session_state.menu_nav_seleccionado = "Chat con el Guía"
                st.rerun()
        st.sidebar.caption(f"Mensajes semanales disponibles: **{chats_disp_semana}**")

    elif menu == "Red Social y Comunidad":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💬 Chats con Miembros")
        if not mis_contactos_dm:
            st.sidebar.caption("Sin chats activos. Explora en 'Comunidad y Amigos'.")
        else:
            for c_dm in mis_contactos_dm:
                es_dm_sel = (st.session_state.dm_activo_contacto and st.session_state.dm_activo_contacto.get("id") == c_dm.get("id"))
                label_dm = f"💬 👉 {c_dm.get('apodo')}" if es_dm_sel else f"💬 {c_dm.get('apodo')}"
                if st.sidebar.button(label_dm, key=f"side_dm_{c_dm.get('id')}"):
                    st.session_state.dm_activo_contacto = c_dm
                    st.rerun()

    banner_msg = "Selecciona el problema o síntoma que necesitas tratar para activar de inmediato al guía más idóneo."
    if st.session_state.avatar_activo:
        av_name = GUIA_INFO.get(st.session_state.avatar_activo, {}).get("nombre", st.session_state.avatar_activo)
        banner_msg = f"Tu guía activo es {av_name}. Puedes continuar tu sesión directamente en 'Chat con el Guía'."

    st.markdown(f"""
        <div class="welcome-banner">
            <h2>🌟 Espacio de Acompañamiento de {st.session_state.user_apodo}</h2>
            <p>{banner_msg}</p>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------------------------------------------
    # 1. DEFINIR EL PROBLEMA (SELECCIÓN POR TRASTORNO / CONDICIÓN CON FOTO DEL GUÍA IDÓNEO)
    # ----------------------------------------------------------------------------------------------
    if menu == "Definir el problema":
        st.subheader("🎯 ¿Qué situación o dolor necesitas ordenar hoy?")
        st.caption("Selecciona el problema de la lista. Se te presentará el avatar con mayor autoridad clínica y biográfica para acompañarte:")

        for prob in LOCAL_PROBLEMAS:
            with st.container():
                st.markdown(f"""
                    <div class="problem-box">
                        <h3>{prob['titulo']}</h3>
                        <p class="problem-desc">{prob['descripcion']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Presentación de 1 o 2 avatares idóneos con su foto de perfil
                num_avs = len(prob["avatares"])
                cols_av = st.columns(num_avs)
                for i_a, a_id in enumerate(prob["avatares"]):
                    info_a = GUIA_INFO.get(a_id, {})
                    with cols_av[i_a]:
                        st.markdown("<div class='avatar-expert-card'>", unsafe_allow_html=True)
                        mostrar_imagen_avatar(a_id, ancho=110)
                        st.markdown(f"<h4>{info_a.get('nombre')}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<div class='avatar-spec'>{info_a.get('bandera')} {info_a.get('especialidad')}</div>", unsafe_allow_html=True)
                        st.caption(info_a.get("resumen"))
                        
                        btn_label = f"Consultar con {info_a.get('nombre').split()[0]}"
                        if st.button(btn_label, key=f"sel_prob_{prob['id']}_{a_id}"):
                            st.session_state.avatar_activo = a_id
                            st.session_state.problema_activo = prob["id"]
                            st.session_state.menu_nav_seleccionado = "Chat con el Guía"
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------------------------------------------------
    # 2. CHAT CON EL GUÍA (BANCO CLÍNICO DETERMINISTA + TEXTO LIBRE)
    # ----------------------------------------------------------------------------------------------
    elif menu == "Chat con el Guía":
        if not st.session_state.avatar_activo:
            st.warning("Por favor selecciona primero un motivo en la pestaña 'Definir el problema'.")
        else:
            av_id = st.session_state.avatar_activo
            av_info = GUIA_INFO.get(av_id, {"nombre": av_id.capitalize(), "pais": "Internacional", "bandera": "🌿", "especialidad": "Guía de Serenidad"})
            prob_id = st.session_state.problema_activo or "ansiedad_panico"

            with st.container():
                st.markdown(f"""
                    <div class="avatar-header-box">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <h3 style="margin: 0; font-size: 1.4rem !important;">{av_info['bandera']} {av_info['nombre']}</h3>
                                <p class="avatar-subtitle" style="margin: 2px 0 0 0;">{av_info['especialidad']} | En línea</p>
                            </div>
                            <span style="background:#EBF7F2; padding:4px 12px; border-radius:12px; font-weight:bold; color:#4E8A72; font-size:14px;">Mensajes disponibles: {chats_disp_semana}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            chat_key = f"messages_{st.session_state.user_id}_{av_id}_{prob_id}"
            opciones_key = f"opciones_activas_{st.session_state.user_id}_{av_id}_{prob_id}"

            # Opciones iniciales por defecto según el problema
            if opciones_key not in st.session_state:
                opciones_base = {
                    "ansiedad_panico": [
                        {"id": "p1_panico", "texto": "💓 Siento que el corazón se me va a salir y me falta el aire"},
                        {"id": "sub_p1_nudo", "texto": "🫁 ¿Cómo aflojo el nudo en la garganta o el estómago ahora mismo?"},
                        {"id": "sub_p2_desmayo", "texto": "🌫️ Siento que me voy a desmayar por respirar corto"},
                        {"id": "sub_p3_infarto", "texto": "🩺 ¿Qué diferencia hay entre este pánico y un infarto real?"}
                    ],
                    "depresion_vacio": [
                        {"id": "p2_vacio", "texto": "🌧️ Siento un vacío que no se quita y no tengo ganas de nada"},
                        {"id": "sub_p4_atencion", "texto": "🧠 No logro concentrarme ni leer dos páginas seguidas"},
                        {"id": "sub_p5_pesimismo", "texto": "🔄 ¿Cómo desarmo la idea de que todo me saldrá mal?"},
                        {"id": "sub_p6_culpa_triste", "texto": "😔 Me siento culpable por estar triste teniendo 'todo'"}
                    ],
                    "angustia_deudas": [
                        {"id": "p3_deudas", "texto": "🌙 No puedo dormir pensando en deudas y siento vergüenza"},
                        {"id": "sub_p15_familia", "texto": "👨‍👩‍👧 ¿Cómo le explico a mi familia la quiebra sin derrumbarlos?"},
                        {"id": "mar_micro_accion", "texto": "📋 ¿Cómo ordeno los pagos para salir de la parálisis?"}
                    ],
                    "bullying_acoso_escolar": [
                        {"id": "p4_bullying", "texto": "📱 Se burlan de mí en WhatsApp y no quiero volver a clases"},
                        {"id": "sub_p7_pasillo", "texto": "🚶‍♂️ ¿Cómo reacciono si me acorralan en el pasillo o la salida?"},
                        {"id": "sub_p8_perfil_falso", "texto": "🛡️ Crearon un perfil falso con mis fotos, ¿qué hago?"},
                        {"id": "sub_p9_panico_lunes", "texto": "🚪 Tengo terror de pisar el aula el lunes"}
                    ],
                    "acoso_sexual": [
                        {"id": "p5_acoso_sex", "texto": "🛑 Un conocido/superior me tocó sin permiso y me amenazó"},
                        {"id": "sub_p10_asco", "texto": "🪞 ¿Cómo manejo el asco y el rechazo a mi propio cuerpo?"},
                        {"id": "sub_p11_credibilidad", "texto": "⚖️ Me da pánico denunciar y que no me crean"},
                        {"id": "sub_p12_contacto", "texto": "✋ No soporto que nadie se me acerque físicamente"}
                    ],
                    "acoso_laboral_mobbing": [
                        {"id": "p6_mobbing", "texto": "💼 Mi jefe me descalifica delante de todos y me satura"},
                        {"id": "sub_p13_puerta_cerrada", "texto": "🚪 Me grita o presiona a solas donde no hay testigos"},
                        {"id": "sub_p14_miedo_renuncia", "texto": "⏳ Tengo pánico de renunciar y quedarme sin sustento"},
                        {"id": "mar_limites", "texto": "🛡️ Enséñame a responder con firmeza sin perder el empleo"}
                    ],
                    "victimas_abuso_violencia": [
                        {"id": "p7_violencia", "texto": "⚡ Fui víctima de una agresión violenta y vivo con terror"},
                        {"id": "sub_p17_sirenas", "texto": "🚨 Un sonido fuerte o seco me hace temblar incontrolable"},
                        {"id": "sub_p18_repeticion", "texto": "🌪️ Siento que en cualquier momento se repetirá el ataque"}
                    ],
                    "miedos_fobias": [
                        {"id": "p8_miedo_calle", "texto": "🚪 Tengo terror a salir a la calle después de lo ocurrido"},
                        {"id": "sub_p16_transporte", "texto": "🚌 Pánico a subir a un autobús o transporte cerrado"},
                        {"id": "cam_respiracion_vago", "texto": "🫀 ¿Cómo desactivo la señal de alarma de mi cuerpo?"}
                    ],
                    "duelo_perdida": [
                        {"id": "p9_duelo", "texto": "🕊️ Perdí a alguien muy amado de golpe y siento culpa por vivir"},
                        {"id": "sub_p19_habitacion", "texto": "📦 No he sido capaz de mover ni tocar sus cosas"},
                        {"id": "sub_p20_rabia", "texto": "🔥 Siento mucha rabia con Dios y con la vida por esto"},
                        {"id": "sub_p21_fuerte", "texto": "💔 Me dicen que 'debo ser fuerte', pero ya no aguanto más"}
                    ],
                    "trauma_complejo_desrealizacion": [
                        {"id": "p10_desrealizacion", "texto": "🌫️ Siento que floto o no estoy en mi cuerpo; temo enloquecer"},
                        {"id": "ana_rumiacion", "texto": "🔄 Pensamientos en bucle que no se apagan"},
                        {"id": "lar_anclaje_54321", "texto": "🌿 Guíame en un anclaje sensorial inmediato (5-4-3-2-1)"}
                    ],
                    "desregulacion_bipolar": [
                        {"id": "sub_p22_montana_rusa", "texto": "🎢 Paso de días sin dormir a semanas postrado sin energía"},
                        {"id": "sub_p23_alarma_euforia", "texto": "⚡ ¿Cómo distingo entusiasmo sano de una fase hipomaníaca?"},
                        {"id": "sub_p24_incomprension", "texto": "👥 Siento que nadie a mi alrededor comprende estos cambios"}
                    ],
                    "conversacion_abierta": [
                        {"id": "sub_p25_soledad", "texto": "☕ Hoy no tengo crisis grave, solo me siento solo/a y quiero hablar"},
                        {"id": "sub_p26_esperanza", "texto": "🌱 ¿Cómo haces tú para tener fe tras lo que viviste?"},
                        {"id": "sub_p27_desconfianza", "texto": "🛡️ Me cuesta confiar en la gente porque siempre me fallan"}
                    ],
                    "aprender_habitos_neurociencia": [
                        {"id": "sub_p28_pacing", "texto": "🔋 ¿Qué es la técnica del 'pacing' para no fundirme a media tarde?"},
                        {"id": "sub_p29_mente_blanco", "texto": "🧠 ¿Qué ejercicio hago si mi mente se nubla en el trabajo?"},
                        {"id": "sub_p30_perdon_sabio", "texto": "🕊️ ¿Cómo perdono sin volverme ingenuo/a ante quien me dañó?"}
                    ]
                }
                st.session_state[opciones_key] = opciones_base.get(prob_id, opciones_base["ansiedad_panico"])

            if chat_key not in st.session_state:
                st.session_state[chat_key] = [{
                    "role": "assistant",
                    "content": f"Hola, soy {av_info['nombre']}. Estoy aquí para acompañarte y darte orientación en lo que estás atravesando. Selecciona una opción o escribe con total libertad.",
                    "is_crisis": False,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }]

            chat_container = st.container(height=460)
            with chat_container:
                for m in st.session_state[chat_key]:
                    icono = "🌿" if m["role"] == "assistant" else "👤"
                    if m.get("is_crisis"):
                        st.error(m["content"])
                    else:
                        with st.chat_message(m["role"], avatar=icono):
                            st.markdown(m["content"])

            # BOTONERA INTERACTIVA DETERMINISTA ($0 USD)
            opciones_actuales = st.session_state.get(opciones_key, [])
            if opciones_actuales:
                st.markdown("<p style='font-size:16px; font-weight:600; margin-bottom:4px; color:#4E8A72;'>💡 Opciones recomendadas para continuar:</p>", unsafe_allow_html=True)
                cols_opc = st.columns(min(len(opciones_actuales), 2))
                for i, opc in enumerate(opciones_actuales):
                    col_target = cols_opc[i % 2]
                    with col_target:
                        st.markdown('<div class="btn-opcion-chat">', unsafe_allow_html=True)
                        if st.button(opc["texto"], key=f"btn_opc_{av_id}_{opc['id']}_{i}"):
                            st.session_state[chat_key].append({
                                "role": "user",
                                "content": opc["texto"],
                                "is_crisis": False,
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            })
                            try:
                                payload = {
                                    "avatar_id": av_id,
                                    "message": opc["texto"],
                                    "opcion_id": opc["id"],
                                    "problema_id": prob_id
                                }
                                r = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload, timeout=25)
                                if r.status_code == 200:
                                    d_resp = r.json()
                                    st.session_state[chat_key].append({
                                        "role": "assistant",
                                        "content": d_resp.get("respuesta"),
                                        "is_crisis": d_resp.get("is_crisis", False),
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    })
                                    st.session_state[opciones_key] = d_resp.get("opciones_siguientes", [])
                                    st.rerun()
                                else:
                                    st.error("Error al procesar la respuesta.")
                            except Exception as e_opc:
                                st.error(f"Falla de conexión: {e_opc}")
                        st.markdown('</div>', unsafe_allow_html=True)

            if user_text := st.chat_input("O escribe tu propio pensamiento o inquietud libremente..."):
                historial_reciente = [
                    f"{'Usuario' if m['role'] == 'user' else 'Guía'}: {m['content']}"
                    for m in st.session_state[chat_key][-4:]
                    if not m.get("is_crisis")
                ]

                ahora_msg = datetime.now(timezone.utc).isoformat()
                st.session_state[chat_key].append({"role": "user", "content": user_text, "is_crisis": False, "timestamp": ahora_msg})

                try:
                    payload = {
                        "avatar_id": av_id,
                        "message": user_text,
                        "opcion_id": None,
                        "problema_id": prob_id,
                        "historial_previo": historial_reciente
                    }
                    r = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload, timeout=30)
                    
                    if r.status_code == 200:
                        d_resp = r.json()
                        st.session_state[chat_key].append({
                            "role": "assistant", 
                            "content": d_resp.get("respuesta"), 
                            "is_crisis": d_resp.get("is_crisis", False),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        st.session_state[opciones_key] = d_resp.get("opciones_siguientes", [])
                        st.rerun()
                    else:
                        try:
                            detalle = r.json().get("detail", r.text[:250])
                        except Exception:
                            detalle = r.text[:250] if r.text else f"Error HTTP {r.status_code}"
                        st.error(f"Aviso del servidor ({r.status_code}): {detalle}")
                except Exception as e:
                    st.error(f"Falla de conexión con el backend: {e}")

    # ----------------------------------------------------------------------------------------------
    # 3. RED SOCIAL Y COMUNIDAD (TODAS LAS PESTAÑAS Y FUNCIONES COMPLETAS)
    # ----------------------------------------------------------------------------------------------
    elif menu == "Red Social y Comunidad":
        tab_mi_perfil, tab_amigos, tab_muro, tab_reuniones, tab_buzon = st.tabs([
            "Mi Perfil", "Comunidad y Amigos", "Muro de Desahogo", "Reuniones", "Buzón de Sugerencias"
        ])

        with tab_mi_perfil:
            st.markdown("### 👤 Tu Perfil Personal")
            try:
                res_me = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, timeout=15)
                if res_me.status_code == 200:
                    mi_p = res_me.json().get("perfil", {})
                    col_p1, col_p2 = st.columns([1, 4])
                    with col_p1:
                        if mi_p.get("foto_perfil"):
                            st.image(mi_p.get("foto_perfil"), width=100)
                        else:
                            st.markdown(f"<div style='width:90px; height:90px; background:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:50%; font-size:40px;'>👤</div>", unsafe_allow_html=True)
                    with col_p2:
                        st.write(f"**Nombre:** {mi_p.get('nombre_completo')} | **Apodo:** {mi_p.get('apodo')}")
                        st.write(f"**Edad:** {mi_p.get('edad')} años | **Sexo:** {mi_p.get('sexo') or 'No especificado'}")
                        st.write(f"**Hijos:** {mi_p.get('cantidad_hijos', 0)} | **Profesión:** {mi_p.get('profesion') or 'No especificada'}")
                        st.write(f"**Código de Referido:** `{mi_p.get('codigo_referido')}`")
                        if mi_p.get("horas_restantes") is not None:
                            st.write(f"**Vigencia del Plan:** {mi_p.get('horas_restantes')} horas restantes")
                    
                    st.markdown("---")
                    st.markdown("#### Actualizar Datos")
                    
                    archivo_foto = st.file_uploader("Actualizar foto de perfil (se optimiza automáticamente a 50 KB):", type=["jpg", "jpeg", "png"], key="fu_perfil_foto")
                    foto_b64 = mi_p.get("foto_perfil")
                    if archivo_foto:
                        foto_b64 = comprimir_imagen(archivo_foto)
                        st.success("Foto optimizada con éxito.")
                    
                    nueva_prof = st.text_input("Profesión u Oficio:", value=mi_p.get("profesion") or "")
                    nuevo_estado = st.selectbox("Situación Sentimental:", ["Prefiero no decir", "Soltero/a", "En pareja / Casado/a", "Divorciado/a", "Viudo/a"], index=0)
                    nuevos_hijos = st.number_input("Hijos:", min_value=0, max_value=10, value=mi_p.get("cantidad_hijos") or 0)
                    
                    st.caption("💡 **Tip para tu biografía:** *Defínete como eres, cómo quieres que te vean y qué haces día a día para que tu guía te conozca en profundidad.*")
                    nueva_bio = st.text_area("Biografía / Pensamiento de Serenidad:", value=mi_p.get("biografia") or "", height=150)
                    
                    if st.button("Guardar Cambios de Perfil"):
                        r_up = requests.put(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, json={
                            "profesion": nueva_prof.strip() or None,
                            "situacion_sentimental": None if nuevo_estado == "Prefiero no decir" else nuevo_estado,
                            "cantidad_hijos": int(nuevos_hijos),
                            "biografia": nueva_bio.strip() or None,
                            "foto_perfil": foto_b64
                        }, timeout=25)
                        if r_up.status_code == 200:
                            st.session_state.last_profile_sync = 0.0
                            st.success("Perfil actualizado con éxito.")
                            st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_amigos:
            st.markdown("### 👥 Miembros de la Comunidad")
            if st.session_state.user_plan == "gratis":
                st.info("ℹ️ Estás explorando la comunidad en Plan Gratis. Los miembros de planes superiores aparecen en modo incógnito. Para enviar solicitudes de amistad, asciende a Plan Comunicador.")

            if st.session_state.dm_activo_contacto:
                c_sel = st.session_state.dm_activo_contacto
                st.markdown(f"#### 💬 Conversación Directa con {c_sel.get('apodo')}")
                st.caption(f"Profesión: {c_sel.get('profesion') or 'Miembro'} | *Los mensajes de más de 7 días se purgan automáticamente.*")
                
                try:
                    r_chat_m = requests.get(f"{API_URL}/comunidad/conversacion/{c_sel.get('id')}", headers=headers_auth, timeout=15)
                    if r_chat_m.status_code == 200:
                        mensajes_dm = r_chat_m.json().get("mensajes", [])
                        if not mensajes_dm:
                            st.info("Aún no tienes mensajes con este usuario. Escribe el primer mensaje a continuación.")
                        
                        dm_container = st.container(height=380)
                        with dm_container:
                            for m_dm in mensajes_dm:
                                es_propio = (m_dm.get("remitente_id") == st.session_state.user_id)
                                rol_msg = "user" if es_propio else "assistant"
                                ico = "👤" if es_propio else "🌿"
                                with st.chat_message(rol_msg, avatar=ico):
                                    st.markdown(m_dm.get("contenido"))
                                
                    nuevo_dm_texto = st.text_input("Escribe tu mensaje privado:", key=f"dm_input_box_{c_sel.get('id')}")
                    col_dm1, col_dm2 = st.columns([1, 4])
                    with col_dm1:
                        if st.button("Enviar Mensaje", key=f"btn_send_dm_{c_sel.get('id')}"):
                            if nuevo_dm_texto.strip():
                                r_post_dm = requests.post(f"{API_URL}/comunidad/dm", headers=headers_auth, json={
                                    "destinatario_id": c_sel.get("id"),
                                    "contenido": nuevo_dm_texto.strip()
                                }, timeout=20)
                                if r_post_dm.status_code == 200:
                                    st.success("Mensaje enviado.")
                                    st.rerun()
                                else:
                                    st.error(r_post_dm.json().get("detail", "Límite de mensajes alcanzado."))
                    with col_dm2:
                        if st.button("Cerrar Chat con Miembro", key="btn_close_dm_chat"):
                            st.session_state.dm_activo_contacto = None
                            st.rerun()
                except Exception as e_dm_chat:
                    st.error(f"Error cargando conversación: {e_dm_chat}")
                st.markdown("---")

            try:
                res_perf = requests.get(f"{API_URL}/comunidad/perfiles", headers=headers_auth, timeout=15)
                if res_perf.status_code == 200:
                    for p in res_perf.json().get("perfiles", []):
                        es_incog = p.get("es_incognito", False)
                        titulo_exp = f"👤 {p.get('apodo')}" if es_incog else f"👤 {p.get('apodo')} ({p.get('edad')} años) - {p.get('profesion')}"
                        
                        with st.expander(titulo_exp):
                            if p.get("foto_perfil") and not es_incog:
                                st.image(p.get("foto_perfil"), width=70)
                            st.write(f"**Biografía:** {p.get('biografia')}")
                            if not es_incog:
                                st.caption(f"Situación: {p.get('situacion_sentimental')}")
                            
                            if es_incog:
                                st.warning("🔒 Para descubrir este perfil y chatear, asciende a Plan Comunicador.")
                            else:
                                estatus_a = p.get("amistad_estatus")
                                if estatus_a == "ninguna":
                                    if st.session_state.user_plan == "gratis":
                                        st.caption("⚠️ Para enviar solicitud de amistad a este usuario debes ascender a Plan Comunicador.")
                                    else:
                                        if st.button("Enviar Solicitud de Amistad", key=f"sol_{p.get('id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/solicitar", headers=headers_auth, json={"usuario_id": p.get("id")}, timeout=20)
                                            st.success("Solicitud enviada.")
                                            st.rerun()
                                elif estatus_a == "pendiente":
                                    if p.get("soy_solicitante"):
                                        st.info("⏳ Solicitud enviada (En espera de confirmación).")
                                    else:
                                        st.warning("📩 Te ha enviado una solicitud de amistad:")
                                        col_si, col_no = st.columns(2)
                                        if col_si.button("Aceptar", key=f"ac_{p.get('amistad_id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/{p.get('amistad_id')}/responder?aceptar=true", headers=headers_auth, timeout=20)
                                            st.rerun()
                                        if col_no.button("Rechazar", key=f"rc_{p.get('amistad_id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/{p.get('amistad_id')}/responder?aceptar=false", headers=headers_auth, timeout=20)
                                            st.rerun()
                                elif estatus_a == "aceptada":
                                    st.success("🤝 ¡Son Amigos! (Chat directo ilimitado habilitado)")

                                if st.button(f"Abrir Chat con {p.get('apodo')}", key=f"open_dm_{p.get('id')}"):
                                    st.session_state.dm_activo_contacto = p
                                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_muro:
            st.markdown("### 💬 Muro de Desahogo y Esperanza")
            st.caption("🌿 *Las reflexiones de la comunidad son visibles para todos y se renuevan cada 72 horas.*")
            
            if st.session_state.user_plan != "gratis":
                with st.expander("✍️ Compartir una reflexión en el Muro", expanded=False):
                    post_txt = st.text_area("¿Qué deseas compartir hoy?:")
                    cat_emocional = st.selectbox("Estado de ánimo / Categoría:", [
                        "🟢 Superación / Gratitud",
                        "🟡 Ansiedad cotidiana / Trabajo y familia",
                        "🟠 Momento difícil / Buscando desahogo"
                    ])
                    map_cat = {
                        "🟢 Superación / Gratitud": "superacion",
                        "🟡 Ansiedad cotidiana / Trabajo y familia": "ansiedad_cotidiana",
                        "🟠 Momento difícil / Buscando desahogo": "momento_dificil"
                    }
                    anon = st.checkbox("Publicar como anónimo")
                    if st.button("Publicar en el Muro"):
                        if post_txt.strip():
                            requests.post(f"{API_URL}/muro", headers=headers_auth, json={
                                "contenido": post_txt.strip(),
                                "categoria_emocional": map_cat[cat_emocional],
                                "is_anonimo": anon
                            }, timeout=25)
                            st.success("Publicación realizada.")
                            st.rerun()
            else:
                st.caption("ℹ️ El Plan Gratis permite leer testimonios. Para publicar tus propias reflexiones o comentar, activa el Plan Comunicador.")

            st.markdown("---")
            filtro_cat = st.selectbox("Filtrar testimonios por categoría:", [
                "Todas las reflexiones",
                "🟢 Superación / Gratitud",
                "🟡 Ansiedad cotidiana / Trabajo y familia",
                "🟠 Momento difícil / Buscando desahogo"
            ])
            map_filtro = {
                "Todas las reflexiones": "todas",
                "🟢 Superación / Gratitud": "superacion",
                "🟡 Ansiedad cotidiana / Trabajo y familia": "ansiedad_cotidiana",
                "🟠 Momento difícil / Buscando desahogo": "momento_dificil"
            }
            cat_query = map_filtro[filtro_cat]
            url_muro = f"{API_URL}/muro" if cat_query == "todas" else f"{API_URL}/muro?categoria={cat_query}"
            
            res_muro = requests.get(url_muro, headers=headers_auth, timeout=20)
            if res_muro.status_code == 200:
                posts = res_muro.json().get("posts", [])
                if not posts:
                    st.info("No hay testimonios en esta categoría por el momento.")
                for post in posts:
                    borde_color = {
                        "superacion": "#2ECC71",
                        "ansiedad_cotidiana": "#F1C40F",
                        "momento_dificil": "#E67E22"
                    }.get(post.get("categoria_emocional"), "#4E8A72")
                    
                    tag_nombre = {
                        "superacion": "🟢 Superación / Gratitud",
                        "ansiedad_cotidiana": "🟡 Ansiedad Cotidiana",
                        "momento_dificil": "🟠 Momento Difícil"
                    }.get(post.get("categoria_emocional"), "🌿 Reflexión")
                    
                    st.markdown(f"""
                        <div class="post-card" style="border-left: 6px solid {borde_color};">
                            <span style="font-size:15px; font-weight:bold; color:{THEME_COLORS['text_secondary']};">[{tag_nombre}] {post.get('autor')}</span>
                            <p style="margin-top:8px; font-size:18px; color:{THEME_COLORS['text_primary']};">{post.get('contenido')}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    comentarios = post.get("comentarios", [])
                    with st.expander(f"💬 Comentarios ({len(comentarios)})", expanded=False):
                        if not comentarios:
                            st.caption("Aún no hay comentarios en esta reflexión.")
                        for com in comentarios:
                            st.markdown(f"""
                                <div class="comment-card">
                                    <strong>{com.get('autor')}:</strong> {com.get('contenido')}
                                </div>
                            """, unsafe_allow_html=True)
                        
                        if st.session_state.user_plan != "gratis":
                            nuevo_com = st.text_input("Añadir un comentario de apoyo:", key=f"com_in_{post.get('id')}")
                            anon_com = st.checkbox("Comentar como anónimo", key=f"anon_com_{post.get('id')}")
                            if st.button("Publicar Comentario", key=f"btn_com_{post.get('id')}"):
                                if nuevo_com.strip():
                                    r_c = requests.post(f"{API_URL}/muro/{post.get('id')}/comentar", headers=headers_auth, json={
                                        "contenido": nuevo_com.strip(),
                                        "is_anonimo": anon_com
                                    }, timeout=20)
                                    if r_c.status_code == 201:
                                        st.success("Comentario publicado.")
                                        st.rerun()
                                    else:
                                        st.error("No se pudo publicar el comentario.")
                        else:
                            st.caption("🔒 Para comentar en las publicaciones, asciende al Plan Comunicador.")

        with tab_reuniones:
            st.markdown("### 👥 Reunidos para Compartir (Salas de Círculos)")
            st.caption("✨ *Las salas cerradas permanecen disponibles durante 24 horas y luego se purgan automáticamente.*")
            
            if st.session_state.user_plan == "gratis":
                st.warning("🔒 Debes pertenecer al Plan Comunicador o Amigo de Todos para solicitar y coordinar una sala de reunión con el Administrador.")
            else:
                st.success("✨ Tienes acceso a salas sincrónicas. Puedes solicitar tu espacio al Administrador a continuación:")
                
                with st.expander("📅 Solicitar Sala de Reunión al Administrador", expanded=False):
                    tema_sala = st.text_input("Tema o título del círculo:")
                    desc_sala = st.text_area("Objetivo o temática a compartir:")
                    fecha_sala = st.text_input("Fecha y hora propuesta (Ej: Sábado 15 de Octubre, 6:00 PM):")
                    
                    if st.button("Enviar Solicitud al Administrador"):
                        if not tema_sala.strip() or not fecha_sala.strip():
                            st.warning("Por favor completa el tema y la fecha propuesta.")
                        else:
                            r_sol = requests.post(f"{API_URL}/reuniones/solicitar", headers=headers_auth, json={
                                "tema": tema_sala.strip(),
                                "descripcion": desc_sala.strip(),
                                "fecha_propuesta": fecha_sala.strip()
                            }, timeout=25)
                            if r_sol.status_code == 201:
                                st.success("Solicitud enviada con éxito. El Administrador te asignará el enlace en este panel.")
                                st.rerun()
                            else:
                                st.error("No se pudo registrar la solicitud.")

                st.markdown("#### Salas Disponibles y Programadas")
                try:
                    r_salas = requests.get(f"{API_URL}/reuniones/salas", headers=headers_auth, timeout=15)
                    if r_salas.status_code == 200:
                        salas_list = r_salas.json().get("salas", [])
                        if not salas_list:
                            st.info("No hay reuniones programadas en este momento.")
                        for s in salas_list:
                            with st.expander(f"📌 {s.get('tema')} — Solicitada por {s.get('solicitante')} ({s.get('estatus').upper()})"):
                                st.write(f"**Descripción:** {s.get('descripcion')}")
                                st.write(f"**Fecha y Hora:** {s.get('fecha_propuesta')}")
                                if s.get("enlace_reunion"):
                                    st.markdown(f"🔗 **Enlace de Acceso:** [{s.get('enlace_reunion')}]({s.get('enlace_reunion')})")
                                else:
                                    st.info("⏳ Enlace pendiente por asignar por el Administrador.")
                                if s.get("estatus") == "cerrada":
                                    st.caption("⚠️ Esta reunión ha concluido y desaparecerá a las 24 horas de su cierre.")
                except Exception as e_s:
                    st.error(f"Error cargando salas: {e_s}")

        with tab_buzon:
            st.markdown("### 📬 Buzón y Tickets de Soporte")
            cat = st.selectbox("Categoría:", ["Falla técnica", "Duda de facturación/plan", "Sugerencia", "Consulta general"])
            asu = st.text_input("Asunto:")
            det = st.text_area("Mensaje detallado:")
            if st.button("Enviar al Administrador"):
                if asu.strip() and det.strip():
                    requests.post(f"{API_URL}/buzon/ticket", headers=headers_auth, json={"categoria": cat, "asunto": asu.strip(), "mensaje": det.strip()}, timeout=20)
                    st.success("Ticket registrado correctamente.")
                else:
                    st.warning("Completa el asunto y el mensaje.")

    # ----------------------------------------------------------------------------------------------
    # 4. PLANES Y CONCILIACIÓN DE PAGOS PROTEGIDA (CON SUBIDA DE COMPROBANTE)
    # ----------------------------------------------------------------------------------------------
    elif menu == "Planes y Suscripción":
        tab_p, tab_c, tab_pago_guiado = st.tabs(["Planes Oficiales", "Canjear y Compartir Referido", "Coordinar Pago Privado con Admin"])

        with tab_p:
            c1, c2, c3 = st.columns(3)
            c1.markdown("### 🌿 Gratis\n- $0 USD\n- Acceso guiado a problemáticas\n- 25 chats semanales\n- Comunidad en modo lectura")
            c2.markdown("### ⭐ Comunicador\n- $5 USD / 30 días\n- Acceso total a los 5 guías\n- 100 chats semanales\n- Muro y salas activas\n- Envío de solicitudes de amistad")
            c3.markdown("### 👑 Amigo de Todos\n- $10 USD / 40 días\n- Acceso irrestricto\n- Chats ilimitados\n- Acceso total sin restricciones")

        with tab_c:
            st.markdown("### 🎟️ Canjear Cupón Promocional")
            cod = st.text_input("Introduce tu Código de Cupón (Ej: SL-VERDE-4821):")
            if st.button("Canjear Cupón"):
                r = requests.post(f"{API_URL}/cupones/canjear", headers=headers_auth, json={"codigo": cod.strip()}, timeout=20)
                if r.status_code == 200:
                    st.session_state.last_profile_sync = 0.0
                    st.success(r.json().get("message"))
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Cupón inexistente, expirado o previamente utilizado."))

            st.markdown("---")
            st.markdown("### 📢 Comparte tu Enlace y Gana Recompensas")
            try:
                res_me = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, timeout=15)
                cod_ref_mio = res_me.json().get("perfil", {}).get("codigo_referido", "") if res_me.status_code == 200 else ""
            except Exception:
                cod_ref_mio = ""

            enlace_invitacion = f"{FRONTEND_URL}/?ref={cod_ref_mio}"
            msg_compartir = f"Hola, te invito a unirte a Somos Libres de Ansiedad, un refugio seguro para la calma emocional. Regístrate aquí: {enlace_invitacion}"
            msg_encoded = urllib.parse.quote(msg_compartir)

            st.info(f"Tu enlace personal: **{enlace_invitacion}**")
            
            st.markdown(f"""
                <div style="margin-top:10px;">
                    <a href="https://api.whatsapp.com/send?text={msg_encoded}" target="_blank" class="social-btn" style="background:#25D366;">🟢 WhatsApp</a>
                    <a href="https://www.facebook.com/sharer/sharer.php?u={enlace_invitacion}" target="_blank" class="social-btn" style="background:#1877F2;">🔵 Facebook</a>
                    <a href="https://t.me/share/url?url={enlace_invitacion}&text={msg_encoded}" target="_blank" class="social-btn" style="background:#0088CC;">✈️ Telegram</a>
                    <a href="sms:?body={msg_encoded}" class="social-btn" style="background:#5C7A6F;">💬 SMS</a>
                </div>
            """, unsafe_allow_html=True)

        with tab_pago_guiado:
            st.markdown("### 🔒 Coordinación de Pago Privado con el Administrador")
            st.caption("Tus solicitudes y los comprobantes se gestionan de forma confidencial dentro del canal privado.")

            opcion_tramite = st.selectbox("1. ¿Qué operación deseas realizar?:", [
                "Comprar Plan Comunicador ($5 USD / 30 días)",
                "Comprar Plan Amigo de Todos ($10 USD / 40 días)",
                "Solicitar Cupón Verde al Administrador",
                "Solicitar Cupón Azul al Administrador",
                "Solicitar Cupón Rojo al Administrador"
            ])

            accion_pago = st.selectbox("2. Canal o acción requerida:", [
                "Solicitar datos de Pago Móvil BDV (Banco de Venezuela)",
                "Solicitar coordenadas de Binance Pay (USDT)",
                "Solicitar cuenta PayPal",
                "Ya realicé mi pago y deseo enviar el reporte con comprobante"
            ])

            if accion_pago == "Ya realicé mi pago y deseo enviar el reporte con comprobante":
                monto_ref = st.text_input("Monto cancelado en Bs / USD y Banco Emisor:")
                num_comprobante = st.text_input("Número de Referencia del Comprobante:")
                archivo_comprobante = st.file_uploader("Adjuntar captura del comprobante (se optimiza a <50 KB):", type=["jpg", "jpeg", "png"], key="fu_comprobante_pago")
                nota_adicional = st.text_area("Mensaje adicional para el Administrador:")
                
                if st.button("Enviar Reporte de Pago"):
                    if not num_comprobante.strip():
                        st.warning("Por favor ingresa el número de referencia.")
                    else:
                        comp_b64 = comprimir_imagen(archivo_comprobante) if archivo_comprobante else None
                        mensaje_formateado = f"Plan: {opcion_tramite} | Monto: {monto_ref} | Ref: {num_comprobante} | Nota: {nota_adicional}"
                        r_pay = requests.post(f"{API_URL}/pagos/enviar-mensaje", headers=headers_auth, json={
                            "mensaje": mensaje_formateado,
                            "plan_solicitado": opcion_tramite,
                            "metodo_pago": "Reporte de Pago",
                            "monto_referencia": num_comprobante.strip(),
                            "comprobante_url": comp_b64
                        }, timeout=25)
                        if r_pay.status_code == 200:
                            st.success("Reporte enviado al Administrador. Te responderá por este canal.")
                            st.rerun()
            else:
                if st.button("Solicitar Datos Privados al Administrador"):
                    mensaje_pedido = f"Hola, solicito los datos para realizar la siguiente operación: {opcion_tramite} mediante {accion_pago}."
                    r_ped = requests.post(f"{API_URL}/pagos/enviar-mensaje", headers=headers_auth, json={
                        "mensaje": mensaje_pedido,
                        "plan_solicitado": opcion_tramite,
                        "metodo_pago": accion_pago
                    }, timeout=25)
                    if r_ped.status_code == 200:
                        st.success("Solicitud enviada. El Administrador te suministrará los datos por este chat.")
                        st.rerun()

            st.markdown("#### Conversación Privada y Cupones Entregados")
            try:
                r_my_p = requests.get(f"{API_URL}/pagos/mis-mensajes", headers=headers_auth, timeout=15)
                if r_my_p.status_code == 200:
                    mensajes_pago = r_my_p.json().get("mensajes", [])
                    if not mensajes_pago:
                        st.caption("No tienes mensajes en tu historial de pago.")
                    for mp in mensajes_pago:
                        emisor = "Tú" if mp.get("emisor_rol") == "user" else "🌟 Administrador (Juan Carlos)"
                        st.markdown(f"**{emisor}:** {mp.get('mensaje')}")
                        if mp.get("comprobante_url"):
                            st.image(mp.get("comprobante_url"), width=160, caption="Comprobante Adjunto")
            except Exception as e:
                st.error(f"Error: {e}")

    # ----------------------------------------------------------------------------------------------
    # 5. PANEL DE ADMINISTRACIÓN MAESTRO (JUAN CARLOS)
    # ----------------------------------------------------------------------------------------------
    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel Maestro (Admin - Juan Carlos)")
        tab_cupones_adm, tab_pagos_adm, tab_reuniones_adm, tab_afiliados_adm, tab_metricas_adm, tab_mantenimiento_adm = st.tabs([
            "Generar Cupones", "Bandeja de Pagos", "Gestionar Salas", "Afiliados y Recompensas", "Métricas Globales", "Mantenimiento y Respaldo"
        ])

        with tab_cupones_adm:
            st.markdown("### Emisión de Cupones de Activación (Válidos por 30 minutos)")
            color = st.selectbox("Color del Cupón:", ["verde", "azul", "rojo", "morado"])
            if st.button("Generar Código"):
                r = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": color}, timeout=20)
                if r.status_code == 200:
                    d = r.json()
                    st.success(f"Código: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Días: {d.get('duracion_dias')}")

        with tab_pagos_adm:
            st.markdown("### Bandeja de Conciliación de Pagos")
            try:
                r_conv = requests.get(f"{API_URL}/admin/pagos/conversaciones", headers=headers_auth, timeout=15)
                if r_conv.status_code == 200:
                    usuarios = r_conv.json().get("usuarios_con_pago", [])
                    if not usuarios:
                        st.info("No hay pagos pendientes de revisión.")
                    for u in usuarios:
                        with st.expander(f"Usuario: {u.get('apodo')} ({u.get('correo')}) - Plan: {u.get('plan')}"):
                            r_hist = requests.get(f"{API_URL}/admin/pagos/usuario/{u.get('id')}", headers=headers_auth, timeout=15)
                            if r_hist.status_code == 200:
                                for h in r_hist.json().get("mensajes", []):
                                    st.caption(f"{'Usuario' if h.get('emisor_rol') == 'user' else 'Admin'}: {h.get('mensaje')}")
                                    if h.get("comprobante_url"):
                                        st.image(h.get("comprobante_url"), width=150, caption="Comprobante Adjunto")
                            
                            st.caption("💡 *Plantilla rápida para enviar datos Pago Móvil BDV:*")
                            if st.button("📋 Pegar Coordenadas BDV", key=f"bdv_{u.get('id')}"):
                                texto_bdv = "Datos BDV: Banco de Venezuela (0102) | Tel: 04128014962 | CI: 84608666 | Monto al cambio BCV del día según plan."
                                requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"para_usuario_id": u.get("id"), "mensaje": texto_bdv}, timeout=20)
                                st.success("Coordenadas enviadas.")
                                st.rerun()

                            resp_admin = st.text_area(f"Responder o entregar cupón a {u.get('apodo')}:", key=f"adm_resp_{u.get('id')}")
                            if st.button("Enviar Respuesta", key=f"btn_adm_resp_{u.get('id')}"):
                                if resp_admin.strip():
                                    requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"para_usuario_id": u.get("id"), "mensaje": resp_admin.strip()}, timeout=20)
                                    st.success("Respuesta enviada.")
                                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_reuniones_adm:
            st.markdown("### Gestión de Salas de Círculos de Apoyo")
            try:
                r_adm_salas = requests.get(f"{API_URL}/reuniones/salas", headers=headers_auth, timeout=15)
                if r_adm_salas.status_code == 200:
                    salas_adm = r_adm_salas.json().get("salas", [])
                    if not salas_adm:
                        st.info("No hay solicitudes de salas pendientes.")
                    for s_a in salas_adm:
                        with st.expander(f"Sala #{s_a.get('id')} — {s_a.get('tema')} ({s_a.get('solicitante')})"):
                            st.write(f"**Fecha Propuesta:** {s_a.get('fecha_propuesta')}")
                            st.write(f"**Descripción:** {s_a.get('descripcion')}")
                            st.write(f"**Estatus:** `{s_a.get('estatus')}`")
                            
                            enlace_input = st.text_input("Asignar enlace Meet / Jitsi:", value=s_a.get("enlace_reunion") or "", key=f"link_adm_{s_a.get('id')}")
                            nuevo_est = st.selectbox("Cambiar Estatus:", ["pendiente", "activa", "cerrada"], index=["pendiente", "activa", "cerrada"].index(s_a.get("estatus")), key=f"est_adm_{s_a.get('id')}")
                            
                            if st.button("Actualizar Sala", key=f"btn_up_sala_{s_a.get('id')}"):
                                r_up_s = requests.post(f"{API_URL}/admin/reuniones/gestionar", headers=headers_auth, json={
                                    "sala_id": s_a.get("id"),
                                    "enlace_reunion": enlace_input.strip() or None,
                                    "estatus": nuevo_est
                                }, timeout=20)
                                if r_up_s.status_code == 200:
                                    st.success("Sala actualizada.")
                                    st.rerun()
            except Exception as e_adm_s:
                st.error(f"Error administrando salas: {e_adm_s}")

        with tab_afiliados_adm:
            st.markdown("### 👥 Auditoría de Referidos y Programa de Recompensas")
            try:
                r_af = requests.get(f"{API_URL}/admin/afiliados", headers=headers_auth, timeout=15)
                if r_af.status_code == 200:
                    afiliados = r_af.json().get("afiliados", [])
                    afiliados_activos = [a for a in afiliados if a.get("total_referidos", 0) > 0]
                    if not afiliados_activos:
                        st.info("Aún no hay usuarios con referidos registrados.")
                    for a in afiliados_activos:
                        with st.expander(f"👤 {a.get('apodo')} (`{a.get('codigo_referido')}`) | Total: {a.get('total_referidos')} | Pagos: {a.get('referidos_pagos')}"):
                            st.write(f"**Correo:** {a.get('correo')} | **Plan Actual:** {a.get('plan_actual').upper()}")
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if a.get("aplica_bono_conversion"):
                                    st.success("✅ ¡Aplica a Bono de Conversión!")
                                    if st.button("🏆 Adjudicar Bono Conversión (7 días)", key=f"btn_bono_{a.get('usuario_id')}"):
                                        r_rew = requests.post(f"{API_URL}/admin/afiliados/premiar", headers=headers_auth, json={
                                            "usuario_id": a.get("usuario_id"), "tipo_premio": "bono_conversion"
                                        }, timeout=20)
                                        if r_rew.status_code == 200:
                                            st.success(r_rew.json().get("message"))
                                            st.rerun()
                                else:
                                    st.info(f"Progreso Conversión: {a.get('total_referidos')}/10 ({a.get('referidos_pagos')}/5 pagos)")

                            with col_b2:
                                if a.get("aplica_gran_meta"):
                                    st.success("👑 ¡Cumplió la Gran Meta!")
                                    if st.button("👑 Adjudicar Gran Meta (1 año)", key=f"btn_meta_{a.get('usuario_id')}"):
                                        r_rew = requests.post(f"{API_URL}/admin/afiliados/premiar", headers=headers_auth, json={
                                            "usuario_id": a.get("usuario_id"), "tipo_premio": "gran_meta"
                                        }, timeout=20)
                                        if r_rew.status_code == 200:
                                            st.success(r_rew.json().get("message"))
                                            st.rerun()
                                else:
                                    st.caption(f"Progreso Gran Meta: {a.get('total_referidos')}/100 referidos")
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_metricas_adm:
            try:
                r_m = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth, timeout=15)
                if r_m.status_code == 200:
                    met = r_m.json().get("metricas", {})
                    st.metric("Total Usuarios Registrados", met.get("total_registrados", 0))
                    st.metric("Registrados en las últimas 24 horas", met.get("registros_ultimas_24h", 0))
            except Exception as e:
                st.error(f"Error al obtener métricas: {e}")

        with tab_mantenimiento_adm:
            st.markdown("### 💾 Respaldo Integral de la Base de Datos")
            if st.button("Generar Respaldo JSON"):
                try:
                    r_bk = requests.get(f"{API_URL}/admin/backup", headers=headers_auth, timeout=30)
                    if r_bk.status_code == 200:
                        st.download_button(
                            label="📥 Descargar Archivo de Respaldo",
                            data=json.dumps(r_bk.json(), indent=2, ensure_ascii=False),
                            file_name="backup_somos_libres.json",
                            mime="application/json"
                        )
                except Exception as e:
                    st.error(f"Error generando backup: {e}")

            st.markdown("---")
            st.markdown("### ⚙️ Disparador Manual de Mantenimiento Semanal")
            if st.button("🚀 Ejecutar Mantenimiento Ahora"):
                try:
                    r_cron = requests.post(f"{API_URL}/cron/mantenimiento", headers={"X-Cron-Key": CRON_SECRET_KEY}, timeout=30)
                    if r_cron.status_code == 200:
                        d_res = r_cron.json()
                        st.success(f"Mantenimiento ejecutado: {d_res.get('chats_semanales_reseteados')} chats reseteados, {d_res.get('planes_vencidos_revertidos')} planes expirados, {d_res.get('mensajes_directos_purgados_7d')} DMs purgados (7d), {d_res.get('posts_muro_purgados_72h')} posts del muro purgados (72h), {d_res.get('salas_reunion_purgadas_24h')} salas cerradas purgadas (24h) y {d_res.get('chats_avatares_purgados_72h')} mensajes de avatares purgados (72h).")
                    else:
                        st.error("Error al disparar mantenimiento.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")