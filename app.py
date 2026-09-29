import base64
import io
import json
import os
import urllib.parse
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
    /* ESCALA TIPOGRÁFICA GLOBAL Y ACCESIBILIDAD UNIVERSAL */
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
        font-size: 18px !important;
        min-height: 50px !important;
        padding: 10px 24px !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.12) !important;
    }}
    .stButton button:hover {{
        background-color: #3B6B58 !important;
        color: #FFFFFF !important;
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
        margin-bottom: 24px;
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
    
    /* CABECERA FIJA DE CHAT (STICKY) */
    .sticky-chat-header {{
        position: sticky;
        top: 0;
        z-index: 99;
        background-color: #EBF7F2;
        padding: 12px 16px;
        border-radius: 12px;
        border: 1.5px solid #C2EAD9;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }}

    /* GLOBOS DE CHAT CON CONTRASTE REFORZADO */
    [data-testid="stChatMessage"] {{
        padding: 16px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 14px !important;
    }}
    
    /* MENSAJE DEL USUARIO: FONDO OSCURO Y TEXTO BLANCO NÍTIDO OBLIGATORIO */
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

    /* MENSAJE DEL ASISTENTE / OTRO USUARIO */
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
    
    /* CONTROL DE LISTAS Y VIÑETAS DENTRO DEL ASISTENTE */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) ul,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) ol,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li {{
        color: #15382A !important;
        font-size: 18px !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }}

    .avatar-subtitle {{
        color: #1E4D3B !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-top: -6px !important;
        margin-bottom: 6px !important;
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

# Normalización determinista de API_URL para asegurar sufijo /api
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
if "avatares_vinculados" not in st.session_state:
    st.session_state.avatares_vinculados = []
if "token" not in st.session_state:
    st.session_state.token = None
if "horas_restantes_plan" not in st.session_state:
    st.session_state.horas_restantes_plan = None
if "dm_activo_contacto" not in st.session_state:
    st.session_state.dm_activo_contacto = None

ref_url = st.query_params.get("ref", "")

def comprimir_imagen(imagen_archivo) -> str:
    """Comprime cualquier foto subida a un avatar liviano de máx 50KB."""
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

def obtener_ruta_avatar(avatar_data: dict) -> str:
    if not isinstance(avatar_data, dict):
        return ""
    img = avatar_data.get("imagen") or avatar_data.get("foto") or ""
    if img.startswith("http"):
        return img
    local_path = os.path.join("avatares", img)
    if os.path.exists(local_path):
        return local_path
    return f"https://raw.githubusercontent.com/lacontadoraia-hub/somos-libres-de-ansiedad/main/avatares/{img}"

def mostrar_imagen(avatar_data: dict, ancho: int = 120):
    src = obtener_ruta_avatar(avatar_data)
    try:
        st.image(src, width=ancho)
    except Exception:
        st.markdown(f"<div style='width:{ancho}px; height:{ancho}px; background:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:8px; font-size:36px;'>🌿</div>", unsafe_allow_html=True)

if os.path.exists("Logo.png"):
    st.image("Logo.png", width=120)

st.title("🌿 Somos Libres de Ansiedad")

# --- LOGIN / REGISTRO ---
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
                with st.spinner("Verificando tus credenciales... Por favor espera un instante."):
                    try:
                        payload_log = {"correo": correo_log.strip(), "password": pass_log}
                        if preg_secreta:
                            payload_log["pregunta_secreta"] = preg_secreta.strip()

                        res = requests.post(f"{API_URL}/auth/login", json=payload_log, timeout=40)
                        if res.status_code == 200:
                            d = res.json()
                            st.session_state.authenticated = True
                            st.session_state.user_id = d.get("user_id")
                            st.session_state.user_role = d.get("role", "user")
                            st.session_state.user_plan = d.get("plan_actual", "gratis")
                            st.session_state.user_apodo = d.get("apodo", "")
                            st.session_state.token = d.get("access_token")
                            st.session_state.horas_restantes_plan = d.get("horas_restantes")
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
                        st.error("El servidor demoró en responder. Si estaba en reposo, espera 30 segundos y vuelve a presionar el botón.")
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
            * «Somos Libres de Ansiedad» es una plataforma digital de carácter estrictamente educativo, reflexivo y de acompañamiento emocional asistido por Inteligencia Artificial.
            * **NO constituye un servicio médico, psiquiátrico, psicológico clínico ni psicoterapéutico.**
            * El software, sus creadores, colaboradores y avatares virtuales **NO son médicos colegiados ni terapeutas facultativos**, y bajo ninguna circunstancia emiten diagnósticos clínicos, altas, dictámenes patológicos ni prescripción, retiro o modificación de medicamentos o psicofármacos.
            * La utilización de esta herramienta es voluntaria y complementaria a tu desarrollo personal, y jamás debe reemplazar la valoración, consulta, supervisión o tratamiento de un profesional de la salud debidamente certificado.
            
            **2. Protocolo de Crisis y Exención en Emergencias:**
            * Esta aplicación **NO es un servicio de urgencias médicas ni monitoriza crisis en tiempo real.**
            * Si estás atravesando una emergencia médica, angustia invalidante, crisis aguda de pánico o pensamientos relacionados con autolesión o ideación suicida, debes suspender el uso de esta app de inmediato y acudir a un centro asistencial o comunicarte con las líneas gratuitas de auxilio de tu país:
              - **Global:** Befrienders Worldwide (https://www.befrienders.org)
              - **Venezuela:** Línea FPV 0212-4163116 / 0212-4163118 / Emergencias 911
              - **España:** Línea 024 / Teléfono de la Esperanza 717 003 717 / Emergencias 112
              - **EE.UU. / Canadá:** Línea 988 / Emergencias 911
              - **Otros países:** Acudir de inmediato al servicio de urgencias hospitalarias local.
            
            **3. Transparencia Algorítmica y Cero Engaño (Fraude Cero):**
            * Cada «Guía» o «Avatar» disponible en esta aplicación es una representación algorítmica de software diseñada para ofrecer reflexiones basadas en literatura pública de crecimiento y bienestar. Ningún avatar pretende hacerse pasar por una persona humana física ni por un profesional médico.
            * Los planes de suscripción o colaboración económica financian exclusivamente la infraestructura técnica del software y el acceso a funciones digitales, no honorarios facultativos.
            
            **4. Privacidad, Confidencialidad y Seguridad de Datos:**
            * Las contraseñas de acceso son protegidas y cifradas de forma irreversible mediante el algoritmo estándar de la industria `bcrypt`.
            * Toda la información biográfica y emocional que compartas se utiliza única y exclusivamente para contextualizar tus conversaciones dentro de tu propia sesión.
            * **Política de Cero Venta:** Tus datos e interacciones jamás serán vendidos, cedidos, transferidos ni comercializados con terceros ni anunciantes.
            * Tienes el derecho irrevocable de solicitar en cualquier momento la eliminación completa o rectificación de tu cuenta y datos a través de los canales de soporte.
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
                        res = requests.post(f"{API_URL}/auth/register", json=payload, timeout=40)
                        if res.status_code == 404:
                            res = requests.post(f"{API_URL}/auth/registro", json=payload, timeout=40)

                        if res.status_code in [200, 201]:
                            msg = res.json().get("message", "¡Registro completado con éxito! Ve a la pestaña 'Iniciar Sesión' para acceder.")
                            st.success(f"✅ {msg}")
                        else:
                            try:
                                detalle_error = res.json().get("detail", "No fue posible procesar el registro.")
                            except Exception:
                                detalle_error = f"Error en el servidor ({res.status_code}). Verifica los datos."
                            st.error(f"⚠️ {detalle_error}")
                    except requests.exceptions.Timeout:
                        st.error("El servidor tardó en responder durante el registro. Si estaba en reposo, espera 30 segundos e inténtalo de nuevo.")
                    except Exception as e:
                        st.error(f"No se pudo conectar con el servidor: {e}")

# --- PANTALLA PRINCIPAL CON SESIÓN INICIADA ---
else:
    headers_auth = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Sincronización proactiva de plan y contador en tiempo real desde el perfil
    try:
        r_sync = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, timeout=15)
        if r_sync.status_code == 200:
            d_perfil = r_sync.json().get("perfil", {})
            st.session_state.user_plan = d_perfil.get("plan_nivel", "gratis")
            st.session_state.horas_restantes_plan = d_perfil.get("horas_restantes")
    except Exception:
        pass

    # Sincronización de catálogo y avatares vinculados
    catalogo_completo = []
    chats_disp_semana = 25
    try:
        r_cat = requests.get(f"{API_URL}/avatares/catalogo", headers=headers_auth, timeout=15)
        if r_cat.status_code == 200:
            d_c = r_cat.json()
            catalogo_completo = d_c.get("avatares", [])
            chats_disp_semana = d_c.get("chats_restantes", 25)
            vinculados = [av for av in catalogo_completo if av.get("is_activo")]
            st.session_state.avatares_vinculados = vinculados
            
            if not st.session_state.avatar_activo and vinculados:
                st.session_state.avatar_activo = vinculados[0]
            elif st.session_state.avatar_activo and vinculados:
                matching = [v for v in vinculados if v.get("id") == st.session_state.avatar_activo.get("id")]
                if matching:
                    st.session_state.avatar_activo = matching[0]
    except Exception:
        pass

    # Sincronización de contactos de DMs comunitarios
    mis_contactos_dm = []
    try:
        r_dm_contacts = requests.get(f"{API_URL}/comunidad/mis-chats", headers=headers_auth, timeout=15)
        if r_dm_contacts.status_code == 200:
            mis_contactos_dm = r_dm_contacts.json().get("contactos", [])
    except Exception:
        pass

    opciones = ["Seleccionar Avatar", "Chat con Avatar", "Red Social y Comunidad", "Planes y Suscripción"]
    if st.session_state.user_role == "admin":
        opciones.append("Panel de Administración")

    menu = st.sidebar.selectbox("Navegación", opciones)
    st.sidebar.markdown(f"**Plan:** <span style='color:#4E8A72; font-weight:bold;'>{st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)

    # Despliegue del contador de horas de vigencia de plan
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
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- PANEL DE GUÍAS ACTIVOS EN LA BARRA LATERAL ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌿 Tus Guías Activos")
    
    if not st.session_state.avatares_vinculados:
        st.sidebar.caption("Aún no tienes ningún avatar vinculado. Ve a 'Seleccionar Avatar'.")
    else:
        for av_vinc in st.session_state.avatares_vinculados:
            es_actual = (st.session_state.avatar_activo and st.session_state.avatar_activo.get("id") == av_vinc.get("id"))
            label_boton = f"👉 {av_vinc.get('bandera')} {av_vinc.get('nombre')}" if es_actual else f"{av_vinc.get('bandera')} {av_vinc.get('nombre')}"
            
            if st.sidebar.button(label_boton, key=f"side_av_{av_vinc.get('id')}"):
                st.session_state.avatar_activo = av_vinc
                st.rerun()
                
        st.sidebar.caption(f"Mensajes semanales disponibles: **{chats_disp_semana}**")

    # --- PANEL DE CHATS CON MIEMBROS EN LA BARRA LATERAL ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Chats con Miembros")
    if not mis_contactos_dm:
        st.sidebar.caption("Sin chats activos. Puedes conectar en 'Comunidad y Amigos'.")
    else:
        for c_dm in mis_contactos_dm:
            es_dm_sel = (st.session_state.dm_activo_contacto and st.session_state.dm_activo_contacto.get("id") == c_dm.get("id"))
            label_dm = f"💬 👉 {c_dm.get('apodo')}" if es_dm_sel else f"💬 {c_dm.get('apodo')}"
            if st.sidebar.button(label_dm, key=f"side_dm_{c_dm.get('id')}"):
                st.session_state.dm_activo_contacto = c_dm
                st.rerun()

    if menu == "Red Social y Comunidad":
        banner_msg = "Bienvenido a tu red de apoyo emocional y crecimiento mutuo."
    elif menu == "Planes y Suscripción":
        banner_msg = "Adquiere o extiende tu plan para disfrutar de mayor acompañamiento y funciones exclusivas."
    elif menu == "Panel de Administración":
        banner_msg = "Consola Maestra de Operaciones, Finanzas y Métricas de la Comunidad."
    elif st.session_state.avatar_activo:
        banner_msg = f"Tu guía activo es {st.session_state.avatar_activo.get('nombre')}. Puedes consultar en 'Chat con Avatar'."
    else:
        banner_msg = "Selecciona tu avatar guía para iniciar tu acompañamiento reflexivo."

    st.markdown(f"""
        <div class="welcome-banner">
            <h2>🌟 Espacio Activo de {st.session_state.user_apodo}</h2>
            <p>{banner_msg}</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. SELECCIONAR AVATAR
    if menu == "Seleccionar Avatar":
        st.subheader("🛠️ Catálogo Oficial de Guías")
        
        avatares = catalogo_completo
        chats_disp = chats_disp_semana

        if st.session_state.avatar_activo:
            st.success(f"✅ Tu guía activo es **{st.session_state.avatar_activo.get('nombre')}**. Te quedan **{chats_disp} mensajes semanales** disponibles.")
        else:
            if st.session_state.user_plan == "gratis":
                st.info("ℹ️ Tu **Plan Gratis** te permite vincular **1 Avatar activo** y disfrutar de **25 chats reflexivos semanales**.")
            elif st.session_state.user_plan == "comunicador":
                st.info("ℹ️ Tu **Plan Comunicador** te permite alternar entre **hasta 3 Avatares activos** con **100 chats semanales**.")

        c1, c2 = st.columns(2)
        cols = [c1, c2]
        for idx, av in enumerate(avatares):
            with cols[idx % 2]:
                mostrar_imagen(av, ancho=130)
                st.markdown(f"**{av.get('bandera')} {av.get('nombre')}**")
                st.markdown(f"<p class='avatar-subtitle'>Origen: {av.get('pais')} | {av.get('tono')}</p>", unsafe_allow_html=True)
                
                esta_seleccionado = av.get("is_activo", False)
                if esta_seleccionado:
                    st.caption("✅ Ya forma parte de tus guías activos")
                    if st.button("Conversar con este Guía", key=f"sel_act_{av.get('id')}"):
                        st.session_state.avatar_activo = av
                        st.rerun()
                else:
                    if st.button("Seleccionar este Guía", key=f"sel_{av.get('id')}"):
                        try:
                            r = requests.post(f"{API_URL}/avatares/seleccionar", headers=headers_auth, json={"avatar_id": av.get("id")}, timeout=30)
                            if r.status_code == 200:
                                st.session_state.avatar_activo = av
                                st.rerun()
                            else:
                                st.error(r.json().get("detail", "Límite de avatares alcanzado en tu plan."))
                        except Exception as e:
                            st.error(f"Error: {e}")

    # 2. CHAT CON AVATAR (CABECERA STICKY)
    elif menu == "Chat con Avatar":
        if not st.session_state.avatar_activo:
            st.warning("Selecciona un guía primero en la pestaña 'Seleccionar Avatar'.")
        else:
            av = st.session_state.avatar_activo

            col_f, col_t = st.columns([1, 6])
            with col_f:
                mostrar_imagen(av, ancho=85)
            with col_t:
                st.markdown(f"""
                    <div style="margin-top: 4px;">
                        <h3 style="margin: 0; font-size: 1.4rem !important;">Conversando con {av.get('nombre')}</h3>
                        <p class="avatar-subtitle" style="margin: 2px 0 0 0;">{av.get('bandera')} {av.get('pais')} | {av.get('tono')}</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            chat_key = f"messages_{st.session_state.user_id}_{av.get('id')}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = [{"role": "assistant", "content": av.get("disparador_inicial", "Hola, estoy aquí para acompañarte."), "is_crisis": False}]

            for m in st.session_state[chat_key]:
                icono = "🌿" if m["role"] == "assistant" else "👤"
                if m.get("is_crisis"):
                    st.error(m["content"])
                else:
                    with st.chat_message(m["role"], avatar=icono):
                        st.markdown(m["content"])

            if user_text := st.chat_input("Escribe tu pensamiento o inquietud..."):
                historial_reciente = [
                    f"{'Usuario' if m['role'] == 'user' else 'Guía'}: {m['content']}"
                    for m in st.session_state[chat_key][-4:]
                    if not m.get("is_crisis")
                ]

                st.session_state[chat_key].append({"role": "user", "content": user_text, "is_crisis": False})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_text)

                try:
                    payload = {
                        "avatar_id": av.get("id"),
                        "message": user_text,
                        "historial_previo": historial_reciente
                    }
                    r = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload, timeout=60)
                    
                    if r.status_code == 200:
                        try:
                            d_resp = r.json()
                            ans = d_resp.get("respuesta")
                            es_crisis = d_resp.get("is_crisis", False)
                            chats_rest = d_resp.get("chats_restantes")
                            
                            st.session_state[chat_key].append({"role": "assistant", "content": ans, "is_crisis": es_crisis})
                            
                            if es_crisis:
                                st.error(ans)
                            else:
                                with st.chat_message("assistant", avatar="🌿"):
                                    st.markdown(ans)
                                    st.caption(f"Mensajes restantes de tu plan: {chats_rest}")
                        except Exception as e_json:
                            st.error(f"Error interpretando la respuesta del servidor: {e_json}")
                    else:
                        try:
                            detalle = r.json().get("detail", r.text[:250])
                        except Exception:
                            detalle = r.text[:250] if r.text else f"Error HTTP {r.status_code}"
                        st.error(f"Aviso del servidor ({r.status_code}): {detalle}")
                except requests.exceptions.Timeout:
                    st.error("El servidor tardó más de 60 segundos en responder. Si el backend estaba en reposo, espera un momento y vuelve a enviar el mensaje.")
                except Exception as e:
                    st.error(f"Falla de conexión con el backend: {e}")

    # 3. RED SOCIAL Y COMUNIDAD
    elif menu == "Red Social y Comunidad":
        tab_mi_perfil, tab_amigos, tab_muro, tab_reuniones, tab_buzon = st.tabs([
            "Mi Perfil", "Comunidad y Amigos", "Muro de Desahogo", "Reuniones", "Buzón de Sugerencias"
        ])

        with tab_mi_perfil:
            st.markdown("### 👤 Tu Perfil Personal")
            try:
                res_me = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, timeout=30)
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
                    
                    archivo_foto = st.file_uploader("Actualizar foto de perfil (se optimizará a 50 KB automáticamente):", type=["jpg", "jpeg", "png"])
                    foto_b64 = mi_p.get("foto_perfil")
                    if archivo_foto:
                        foto_b64 = comprimir_imagen(archivo_foto)
                        st.success("Foto optimizada con éxito.")
                    
                    nueva_prof = st.text_input("Profesión u Oficio:", value=mi_p.get("profesion") or "")
                    nuevo_estado = st.selectbox("Situación Sentimental:", ["Prefiero no decir", "Soltero/a", "En pareja / Casado/a", "Divorciado/a", "Viudo/a"], index=0)
                    nuevos_hijos = st.number_input("Hijos:", min_value=0, max_value=10, value=mi_p.get("cantidad_hijos") or 0)
                    
                    st.caption("💡 **Tip para tu biografía:** *Defínete como eres, cómo quieres que te vean, qué es lo que haces y cómo es tu día. Escribe entre 100 y 1000 palabras para que tu avatar guía te conozca en profundidad.*")
                    nueva_bio = st.text_area("Biografía / Pensamiento de Serenidad:", value=mi_p.get("biografia") or "", height=150)
                    
                    if st.button("Guardar Cambios de Perfil"):
                        r_up = requests.put(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, json={
                            "profesion": nueva_prof,
                            "situacion_sentimental": None if nuevo_estado == "Prefiero no decir" else nuevo_estado,
                            "cantidad_hijos": int(nuevos_hijos),
                            "biografia": nueva_bio,
                            "foto_perfil": foto_b64
                        }, timeout=30)
                        if r_up.status_code == 200:
                            st.success("Perfil actualizado con éxito.")
                            st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_amigos:
            st.markdown("### 👥 Miembros de la Comunidad")
            if st.session_state.user_plan == "gratis":
                st.info("ℹ️ Estás explorando la comunidad en Plan Gratis. Los miembros de planes superiores aparecen en modo incógnito. Para enviar solicitudes de amistad, asciende a Plan Comunicador.")

            # CHAT ACTIVO CON MIEMBRO SELECCIONADO (ESTILO NATIVO)
            if st.session_state.dm_activo_contacto:
                c_sel = st.session_state.dm_activo_contacto
                st.markdown(f"#### 💬 Conversación Directa con {c_sel.get('apodo')}")
                st.caption(f"Profesión: {c_sel.get('profesion') or 'Miembro'} | *Los mensajes de más de 7 días se purgan automáticamente por privacidad.*")
                
                try:
                    r_chat_m = requests.get(f"{API_URL}/comunidad/conversacion/{c_sel.get('id')}", headers=headers_auth, timeout=30)
                    if r_chat_m.status_code == 200:
                        mensajes_dm = r_chat_m.json().get("mensajes", [])
                        if not mensajes_dm:
                            st.info("Aún no tienes mensajes con este usuario. Escribe el primer mensaje a continuación.")
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
                                }, timeout=30)
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
                res_perf = requests.get(f"{API_URL}/comunidad/perfiles", headers=headers_auth, timeout=30)
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
                                            requests.post(f"{API_URL}/comunidad/amistad/solicitar", headers=headers_auth, json={"usuario_id": p.get("id")}, timeout=30)
                                            st.success("Solicitud enviada.")
                                            st.rerun()
                                elif estatus_a == "pendiente":
                                    if p.get("soy_solicitante"):
                                        st.info("⏳ Solicitud enviada (En espera de confirmación).")
                                    else:
                                        st.warning("📩 Te ha enviado una solicitud de amistad:")
                                        col_si, col_no = st.columns(2)
                                        if col_si.button("Aceptar", key=f"ac_{p.get('amistad_id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/{p.get('amistad_id')}/responder?aceptar=true", headers=headers_auth, timeout=30)
                                            st.rerun()
                                        if col_no.button("Rechazar", key=f"rc_{p.get('amistad_id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/{p.get('amistad_id')}/responder?aceptar=false", headers=headers_auth, timeout=30)
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
                            }, timeout=30)
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
            
            res_muro = requests.get(url_muro, headers=headers_auth, timeout=30)
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

                    # HILO DE COMENTARIOS
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
                                    }, timeout=30)
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
                            }, timeout=30)
                            if r_sol.status_code == 201:
                                st.success("Solicitud enviada con éxito. El Administrador te asignará el enlace en este panel.")
                                st.rerun()
                            else:
                                st.error("No se pudo registrar la solicitud.")

                st.markdown("#### Salas Disponibles y Programadas")
                try:
                    r_salas = requests.get(f"{API_URL}/reuniones/salas", headers=headers_auth, timeout=30)
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
                requests.post(f"{API_URL}/buzon/ticket", headers=headers_auth, json={"categoria": cat, "asunto": asu, "mensaje": det}, timeout=30)
                st.success("Ticket registrado correctamente.")

    # 4. PLANES Y CONCILIACIÓN DE PAGOS PROTEGIDA
    elif menu == "Planes y Suscripción":
        tab_p, tab_c, tab_pago_guiado = st.tabs(["Planes Oficiales", "Canjear y Compartir Referido", "Coordinar Pago Privado con Admin"])

        with tab_p:
            c1, c2, c3 = st.columns(3)
            c1.markdown("### 🌿 Gratis\n- $0 USD\n- 1 Avatar activo\n- 25 chats semanales\n- Comunidad en modo lectura")
            c2.markdown("### ⭐ Comunicador\n- $5 USD / 30 días\n- 3 Avatares activos\n- 100 chats semanales\n- Muro y salas activas\n- Envío de solicitudes de amistad")
            c3.markdown("### 👑 Amigo de Todos\n- $10 USD / 40 días\n- 10 Avatares activos\n- Chats ilimitados\n- Acceso total sin restricciones")

        with tab_c:
            st.markdown("### 🎟️ Canjear Cupón Promocional")
            cod = st.text_input("Introduce tu Código de Cupón (Ej: SL-VERDE-4821):")
            if st.button("Canjear Cupón"):
                r = requests.post(f"{API_URL}/cupones/canjear", headers=headers_auth, json={"codigo": cod.strip()}, timeout=30)
                if r.status_code == 200:
                    st.success(r.json().get("message"))
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Cupón inexistente, expirado o previamente utilizado."))

            st.markdown("---")
            st.markdown("### 📢 Comparte tu Enlace y Gana Recompensas")
            try:
                res_me = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, timeout=30)
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
            st.caption("Tus solicitudes y los datos bancarios se gestionan de forma confidencial dentro del canal privado.")

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
                nota_adicional = st.text_area("Mensaje adicional o duda para el Administrador:")
                
                if st.button("Enviar Reporte de Pago"):
                    if not num_comprobante.strip():
                        st.warning("Por favor ingresa el número de referencia.")
                    else:
                        mensaje_formateado = f"Plan: {opcion_tramite} | Monto: {monto_ref} | Ref: {num_comprobante} | Nota: {nota_adicional}"
                        r_pay = requests.post(f"{API_URL}/pagos/enviar-mensaje", headers=headers_auth, json={
                            "mensaje": mensaje_formateado,
                            "plan_solicitado": opcion_tramite,
                            "metodo_pago": "Reporte de Pago",
                            "monto_referencia": num_comprobante
                        }, timeout=30)
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
                    }, timeout=30)
                    if r_ped.status_code == 200:
                        st.success("Solicitud enviada. El Administrador te suministrará los datos por este chat.")
                        st.rerun()

            st.markdown("#### Conversación Privada y Cupones Entregados")
            try:
                r_my_p = requests.get(f"{API_URL}/pagos/mis-mensajes", headers=headers_auth, timeout=30)
                if r_my_p.status_code == 200:
                    mensajes_pago = r_my_p.json().get("mensajes", [])
                    if not mensajes_pago:
                        st.caption("No tienes mensajes en tu historial de pago.")
                    for mp in mensajes_pago:
                        emisor = "Tú" if mp.get("emisor_rol") == "user" else "🌟 Administrador (Juan Carlos)"
                        st.markdown(f"**{emisor}:** {mp.get('mensaje')}")
            except Exception as e:
                st.error(f"Error: {e}")

    # 5. PANEL ADMIN (JUAN CARLOS)
    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel Maestro (Admin - Juan Carlos)")
        tab_cupones_adm, tab_pagos_adm, tab_reuniones_adm, tab_afiliados_adm, tab_metricas_adm, tab_mantenimiento_adm = st.tabs([
            "Generar Cupones", "Bandeja de Pagos", "Gestionar Salas", "Afiliados y Recompensas", "Métricas Globales", "Mantenimiento y Respaldo"
        ])

        with tab_cupones_adm:
            st.markdown("### Emisión de Cupones de Activación (Válidos por 30 minutos)")
            color = st.selectbox("Color del Cupón:", ["verde", "azul", "rojo", "morado"])
            if st.button("Generar Código"):
                r = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": color}, timeout=30)
                if r.status_code == 200:
                    d = r.json()
                    st.success(f"Código: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Días: {d.get('duracion_dias')}")

        with tab_pagos_adm:
            st.markdown("### Bandeja de Conciliación de Pagos")
            try:
                r_conv = requests.get(f"{API_URL}/admin/pagos/conversaciones", headers=headers_auth, timeout=30)
                if r_conv.status_code == 200:
                    usuarios = r_conv.json().get("usuarios_con_pago", [])
                    if not usuarios:
                        st.info("No hay pagos pendientes de revisión.")
                    for u in usuarios:
                        with st.expander(f"Usuario: {u.get('apodo')} ({u.get('correo')}) - Plan: {u.get('plan')}"):
                            r_hist = requests.get(f"{API_URL}/admin/pagos/usuario/{u.get('id')}", headers=headers_auth, timeout=30)
                            if r_hist.status_code == 200:
                                for h in r_hist.json().get("mensajes", []):
                                    st.caption(f"{'Usuario' if h.get('emisor_rol') == 'user' else 'Admin'}: {h.get('mensaje')}")
                            
                            st.caption("💡 *Plantilla rápida para enviar datos Pago Móvil BDV:*")
                            if st.button("📋 Pegar Coordenadas BDV", key=f"bdv_{u.get('id')}"):
                                texto_bdv = "Datos BDV: Banco de Venezuela (0102) | Tel: 04128014962 | CI: 84608666 | Monto al cambio BCV del día según plan."
                                requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"para_usuario_id": u.get("id"), "mensaje": texto_bdv}, timeout=30)
                                st.success("Coordenadas enviadas.")
                                st.rerun()

                            resp_admin = st.text_area(f"Responder o entregar cupón a {u.get('apodo')}:", key=f"adm_resp_{u.get('id')}")
                            if st.button("Enviar Respuesta", key=f"btn_adm_resp_{u.get('id')}"):
                                requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"para_usuario_id": u.get("id"), "mensaje": resp_admin}, timeout=30)
                                st.success("Respuesta enviada.")
                                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_reuniones_adm:
            st.markdown("### Gestión de Salas de Círculos de Apoyo")
            try:
                r_adm_salas = requests.get(f"{API_URL}/reuniones/salas", headers=headers_auth, timeout=30)
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
                                }, timeout=30)
                                if r_up_s.status_code == 200:
                                    st.success("Sala actualizada.")
                                    st.rerun()
            except Exception as e_adm_s:
                st.error(f"Error administrando salas: {e_adm_s}")

        with tab_afiliados_adm:
            st.markdown("### 👥 Auditoría de Referidos y Programa de Recompensas")
            try:
                r_af = requests.get(f"{API_URL}/admin/afiliados", headers=headers_auth, timeout=30)
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
                                        }, timeout=30)
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
                                        }, timeout=30)
                                        if r_rew.status_code == 200:
                                            st.success(r_rew.json().get("message"))
                                            st.rerun()
                                else:
                                    st.caption(f"Progreso Gran Meta: {a.get('total_referidos')}/100 referidos")
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_metricas_adm:
            try:
                r_m = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth, timeout=30)
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
                    r_bk = requests.get(f"{API_URL}/admin/backup", headers=headers_auth, timeout=40)
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
                    r_cron = requests.post(f"{API_URL}/cron/mantenimiento", headers={"X-Cron-Key": CRON_SECRET_KEY}, timeout=40)
                    if r_cron.status_code == 200:
                        d_res = r_cron.json()
                        st.success(f"Mantenimiento ejecutado: {d_res.get('chats_semanales_reseteados')} chats reseteados, {d_res.get('planes_vencidos_revertidos')} planes expirados, {d_res.get('mensajes_directos_purgados_7d')} DMs purgados (7d), {d_res.get('posts_muro_purgados_72h')} posts del muro purgados (72h) y {d_res.get('salas_reunion_purgadas_24h')} salas cerradas purgadas (24h).")
                    else:
                        st.error("Error al disparar mantenimiento.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
