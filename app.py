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
    .stApp {{ background-color: {THEME_COLORS['background']}; color: {THEME_COLORS['text_primary']}; }}
    h1, h2, h3, h4, h5, h6, p, label, span {{ color: {THEME_COLORS['text_primary']}; }}
    
    [data-testid="stSidebar"] {{
        background-color: {THEME_COLORS['background']} !important;
        border-right: 1px solid {THEME_COLORS['border']} !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: {THEME_COLORS['text_primary']} !important;
    }}
    
    .welcome-banner {{
        background: linear-gradient(135deg, #4E8A72 0%, #A8E6CF 100%);
        padding: 20px;
        border-radius: 12px;
        color: #1E4D3B;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }}
    
    /* MEJORA CRÍTICA DE ACCESIBILIDAD Y CONTRASTE EN CHAT */
    [data-testid="stChatMessage"] {{
        padding: 14px 18px !important;
        border-radius: 10px !important;
        margin-bottom: 12px !important;
    }}
    
    /* Mensajes del usuario: Fondo oscuro de alto contraste y texto blanco puro */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: #2D4036 !important;
        border-left: 5px solid #4E8A72 !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) span,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) li {{
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }}

    /* Mensajes del asistente: Fondo blanco nítido con texto y listas en verde bosque profundo */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        background-color: #FFFFFF !important;
        border-left: 5px solid #2ECC71 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) span,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) div,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) strong,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) b,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) em,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) ul,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) ol,
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li {{
        color: #15382A !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }}

    /* Entrada de chat con texto y placeholder de alto contraste */
    [data-testid="stChatInput"] textarea {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        font-size: 15px !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{
        color: #6A8277 !important;
        font-weight: bold !important;
    }}

    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        border-color: {THEME_COLORS['secondary']} !important;
    }}
    .stButton button {{
        background-color: {THEME_COLORS['secondary']} !important;
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: bold;
    }}
    .social-btn {{
        display: inline-block;
        padding: 8px 14px;
        margin: 4px;
        border-radius: 6px;
        text-decoration: none;
        color: white !important;
        font-weight: bold;
        font-size: 13px;
    }}
    .post-card {{
        background: #FFFFFF;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 5px solid #4E8A72;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }}
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "https://somos-libres-de-ansiedad-1.onrender.com/api")
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
if "token" not in st.session_state:
    st.session_state.token = None

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
        st.markdown(f"<div style='width:{ancho}px; height:{ancho}px; background:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:8px;'>🌿</div>", unsafe_allow_html=True)

if os.path.exists("Logo.png"):
    st.image("Logo.png", width=120)

st.title("🌿 Somos Libres de Ansiedad")

# --- LOGIN / REGISTRO ---
if not st.session_state.authenticated:
    st.markdown("""
        <div class="welcome-banner">
            <h2>✨ Tu Refugio Seguro y Sin Fármacos ✨</h2>
            <p>Un espacio confidencial para recuperar tu calma interior.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab_login:
        correo_log = st.text_input("Correo Electrónico", key="log_correo")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        preg_secreta = None
        if correo_log.strip().lower() == "somos.libredeansiedad@gmail.com":
            st.info("🔒 Cuenta Maestra: Se requiere confirmación de seguridad.")
            preg_secreta = st.text_input("Pregunta de resguardo: ¿Cuál es la palabra clave?", type="password", key="log_admin_sec")

        if st.button("Ingresar a mi espacio"):
            try:
                payload_log = {"correo": correo_log.strip(), "password": pass_log}
                if preg_secreta:
                    payload_log["pregunta_secreta"] = preg_secreta.strip()

                res = requests.post(f"{API_URL}/auth/login", json=payload_log)
                if res.status_code == 200:
                    d = res.json()
                    st.session_state.authenticated = True
                    st.session_state.user_id = d.get("user_id")
                    st.session_state.user_role = d.get("role", "user")
                    st.session_state.user_plan = d.get("plan_actual", "gratis")
                    st.session_state.user_apodo = d.get("apodo", "")
                    st.session_state.token = d.get("access_token")
                    st.success(f"¡Bienvenido/a {st.session_state.user_apodo}!")
                    st.info(f"💡 {d.get('pensamiento_dia', '')}")
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Credenciales incorrectas."))
            except Exception as e:
                st.error(f"Error de conexión: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)
        
        with st.expander("➕ Datos del Perfil (Opcionales para personalizar tu experiencia)"):
            sexo = st.selectbox("Sexo", ["Prefiero no decir", "Femenino", "Masculino", "Otro"])
            profesion = st.text_input("Profesión u Ocupación")
            situacion = st.selectbox("Situación Sentimental", ["Prefiero no decir", "Soltero/a", "En pareja / Casado/a", "Divorciado/a", "Viudo/a"])
            hijos = st.number_input("Cantidad de Hijos", min_value=0, max_value=10, value=0)

        codigo_ref = st.text_input("Código de Referido (opcional)", value=ref_url)
        
        col_t1, col_btn_pol = st.columns([3, 1])
        with col_t1:
            t1 = st.checkbox("He leído y acepto los Términos de Servicio y la Política de Privacidad. (*)")
        with col_btn_pol:
            ver_politicas = st.button("📄 Leer Políticas", use_container_width=True)

        if ver_politicas:
            with st.expander("📜 Términos de Servicio y Política de Privacidad Oficial", expanded=True):
                st.markdown("""
                **1. Términos de Servicio y Descargo Médico:**
                * **Naturaleza del Servicio:** «Somos Libres de Ansiedad» es una plataforma digital de bienestar emocional y acompañamiento reflexivo asistido por IA. **No constituye servicio médico, psiquiátrico ni psicoterapéutico clínico**, ni prescribe fármacos.
                * **Emergencias:** En caso de crisis severa, ideación suicida o emergencia médica, acude de inmediato a un centro de urgencias de tu localidad.
                * **Convivencia:** Queda prohibido el acoso, spam o conductas indebidas en la comunidad.

                **2. Política de Privacidad y Tratamiento de Datos:**
                * **Seguridad:** Las contraseñas se almacenan encriptadas con algoritmo `bcrypt`.
                * **Uso Exclusivo:** Los datos de tu perfil solo se usan para enriquecer y contextualizar tu experiencia con tu guía.
                * **Confidencialidad:** Tus datos personales e interacciones nunca se venden, alquilan ni comparten con terceros.
                * **Control:** Puedes solicitar la rectificación o eliminación total de tus registros a través del Buzón de Soporte.
                """)

        t2 = st.checkbox("Acepto que este programa es una herramienta educativa no médica. (*)")
        
        if st.button("Registrarme"):
            if not t1 or not t2 or not nombre or not apodo or not correo_reg or not pass_reg:
                st.warning("Completa los campos obligatorios marcados con (*).")
            else:
                try:
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
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
                    if res.status_code == 201:
                        st.success(res.json().get("message", "¡Registro completado! Ya puedes Iniciar Sesión."))
                    else:
                        st.error(res.json().get("detail", "Error al registrarse."))
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

# --- PANTALLA PRINCIPAL ---
else:
    headers_auth = {"Authorization": f"Bearer {st.session_state.token}"}
    
    opciones = ["Seleccionar Avatar", "Chat con Avatar", "Red Social y Comunidad", "Planes y Suscripción"]
    if st.session_state.user_role == "admin":
        opciones.append("Panel de Administración")

    menu = st.sidebar.selectbox("Navegación", opciones)
    st.sidebar.markdown(f"**Plan:** <span style='color:#4E8A72; font-weight:bold;'>{st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # BANNERS ESPECÍFICOS SEGÚN CADA SECCIÓN
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
        
        try:
            res = requests.get(f"{API_URL}/avatares/catalogo", headers=headers_auth)
            d_cat = res.json() if res.status_code == 200 else {}
            avatares = d_cat.get("avatares", [])
            chats_disp = d_cat.get("chats_restantes", 25)
        except Exception:
            avatares = []
            chats_disp = 25

        if st.session_state.avatar_activo:
            st.success(f"✅ Ya seleccionaste a **{st.session_state.avatar_activo.get('nombre')}** como tu acompañante. Te quedan **{chats_disp} mensajes semanales** disponibles.")
        else:
            if st.session_state.user_plan == "gratis":
                st.info("ℹ️ Tu **Plan Gratis** te permite vincular **1 Avatar activo** y disfrutar de **25 chats reflexivos semanales**.")

        c1, c2 = st.columns(2)
        cols = [c1, c2]
        for idx, av in enumerate(avatares):
            with cols[idx % 2]:
                mostrar_imagen(av, ancho=130)
                st.markdown(f"**{av.get('bandera')} {av.get('nombre')}**")
                st.caption(f"Origen: {av.get('pais')} | {av.get('tono')}")
                if st.button("Seleccionar este Guía", key=f"sel_{av.get('id')}"):
                    try:
                        r = requests.post(f"{API_URL}/avatares/seleccionar", headers=headers_auth, json={"avatar_id": av.get("id")})
                        if r.status_code == 200:
                            st.session_state.avatar_activo = av
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Límite de avatares alcanzado."))
                    except Exception as e:
                        st.error(f"Error: {e}")

    # 2. CHAT CON AVATAR (CON PROTOCOLO SOS Y MEMORIA EN VIVO)
    elif menu == "Chat con Avatar":
        if not st.session_state.avatar_activo:
            st.warning("Selecciona un guía primero en la pestaña 'Seleccionar Avatar'.")
        else:
            av = st.session_state.avatar_activo
            col_f, col_t = st.columns([1, 6])
            with col_f:
                mostrar_imagen(av, ancho=85)
            with col_t:
                st.subheader(f"Conversando con {av.get('nombre')}")
                st.caption(f"{av.get('bandera')} {av.get('tono')}")

            chat_key = f"messages_{st.session_state.user_id}"
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
                st.session_state[chat_key].append({"role": "user", "content": user_text, "is_crisis": False})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_text)

                # Extraer los últimos cuatro mensajes previos a esta entrada
                historial_reciente = [m["content"] for m in st.session_state[chat_key][-5:-1]]

                try:
                    payload = {
                        "avatar_id": av.get("id"),
                        "message": user_text,
                        "historial_previo": historial_reciente
                    }
                    r = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload)
                    if r.status_code == 200:
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
                    else:
                        st.error(r.json().get("detail", "Error al procesar el mensaje."))
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # 3. RED SOCIAL Y COMUNIDAD
    elif menu == "Red Social y Comunidad":
        tab_mi_perfil, tab_amigos, tab_muro, tab_reuniones, tab_buzon = st.tabs([
            "Mi Perfil", "Comunidad y Amigos", "Muro de Desahogo", "Reuniones", "Buzón de Sugerencias"
        ])

        with tab_mi_perfil:
            st.markdown("### 👤 Tu Perfil Personal")
            try:
                res_me = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth)
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
                        })
                        if r_up.status_code == 200:
                            st.success("Perfil actualizado con éxito.")
                            st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_amigos:
            st.markdown("### 👥 Miembros de la Comunidad")
            if st.session_state.user_plan == "gratis":
                st.info("ℹ️ Estás explorando la comunidad en Plan Gratis. Los miembros de planes superiores aparecen en modo incógnito. Para enviar solicitudes de amistad, asciende a Plan Comunicador.")

            try:
                res_perf = requests.get(f"{API_URL}/comunidad/perfiles", headers=headers_auth)
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
                                            requests.post(f"{API_URL}/comunidad/amistad/solicitar", headers=headers_auth, json={"usuario_id": p.get("id")})
                                            st.success("Solicitud enviada.")
                                            st.rerun()
                                elif estatus_a == "pendiente":
                                    if p.get("soy_solicitante"):
                                        st.info("⏳ Solicitud enviada (En espera de confirmación).")
                                    else:
                                        st.warning("📩 Te ha enviado una solicitud de amistad:")
                                        col_si, col_no = st.columns(2)
                                        if col_si.button("Aceptar", key=f"ac_{p.get('amistad_id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/{p.get('amistad_id')}/responder?aceptar=true", headers=headers_auth)
                                            st.rerun()
                                        if col_no.button("Rechazar", key=f"rc_{p.get('amistad_id')}"):
                                            requests.post(f"{API_URL}/comunidad/amistad/{p.get('amistad_id')}/responder?aceptar=false", headers=headers_auth)
                                            st.rerun()
                                elif estatus_a == "aceptada":
                                    st.success("🤝 ¡Son Amigos! (Chat directo ilimitado habilitado)")

                                msg_dm = st.text_input("Mensaje privado:", key=f"dm_in_{p.get('id')}")
                                if st.button("Enviar Mensaje", key=f"btn_dm_{p.get('id')}"):
                                    r_dm = requests.post(f"{API_URL}/comunidad/dm", headers=headers_auth, json={"destinatario_id": p.get("id"), "contenido": msg_dm})
                                    if r_dm.status_code == 200:
                                        st.success("Mensaje enviado.")
                                    else:
                                        st.error(r_dm.json().get("detail", "Límite alcanzado."))

                                if st.checkbox("Ver conversación previa", key=f"chk_conv_{p.get('id')}"):
                                    r_c = requests.get(f"{API_URL}/comunidad/conversacion/{p.get('id')}", headers=headers_auth)
                                    if r_c.status_code == 200:
                                        for cm in r_c.json().get("mensajes", []):
                                            rem = "Tú" if cm.get("remitente_id") != p.get("id") else p.get("apodo")
                                            st.write(f"**{rem}:** {cm.get('contenido')}")
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_muro:
            st.markdown("### 💬 Muro de Desahogo y Esperanza")
            
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
                            })
                            st.success("Publicación realizada.")
                            st.rerun()
            else:
                st.caption("ℹ️ El Plan Gratis permite leer testimonios. Para publicar tus propias reflexiones, activa el Plan Comunicador.")

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
            
            res_muro = requests.get(url_muro, headers=headers_auth)
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
                        <div class="post-card" style="border-left: 5px solid {borde_color};">
                            <span style="font-size:12px; font-weight:bold; color:{THEME_COLORS['text_secondary']};">[{tag_nombre}] {post.get('autor')}</span>
                            <p style="margin-top:6px; font-size:15px; color:{THEME_COLORS['text_primary']};">{post.get('contenido')}</p>
                        </div>
                    """, unsafe_allow_html=True)

        with tab_reuniones:
            st.markdown("### 👥 Reunidos para Compartir (Salas de Círculos)")
            if st.session_state.user_plan == "gratis":
                st.warning("🔒 Debes pertenecer al Plan Comunicador o Amigo de Todos para adquirir tu sala y conversar en reunión con tus amigos.")
            else:
                st.success("✨ Tienes acceso a salas sincrónicas para convocar y dialogar con tus círculos de apoyo.")

        with tab_buzon:
            st.markdown("### 📬 Buzón y Tickets de Soporte")
            cat = st.selectbox("Categoría:", ["Falla técnica", "Duda de facturación/plan", "Sugerencia", "Consulta general"])
            asu = st.text_input("Asunto:")
            det = st.text_area("Mensaje detallado:")
            if st.button("Enviar al Administrador"):
                requests.post(f"{API_URL}/buzon/ticket", headers=headers_auth, json={"categoria": cat, "asunto": asu, "mensaje": det})
                st.success("Ticket registrado correctamente.")

    # 4. PLANES Y CONCILIACIÓN DE PAGOS PROTEGIDA
    elif menu == "Planes y Suscripción":
        tab_p, tab_c, tab_pago_guiado = st.tabs(["Planes Oficiales", "Canjear y Compartir Referido", "Coordinar Pago Privado con Admin"])

        with tab_p:
            c1, c2, c3 = st.columns(3)
            c1.markdown("### 🌿 Gratis\n- $0\n- 1 Avatar activo\n- 25 chats semanales\n- Comunidad en modo lectura")
            c2.markdown("### ⭐ Comunicador\n- $5 USD / 30 días\n- 3 Avatares activos\n- 100 chats semanales\n- Muro y salas activas\n- Envío de solicitudes de amistad")
            c3.markdown("### 👑 Amigo de Todos\n- $10 USD / 40 días\n- 10 Avatares activos\n- Chats ilimitados\n- Acceso total sin restricciones")

        with tab_c:
            st.markdown("### 🎟️ Canjear Cupón Promocional")
            cod = st.text_input("Introduce tu Código de Cupón (Ej: SL-VERDE-4821):")
            if st.button("Canjear Cupón"):
                r = requests.post(f"{API_URL}/cupones/canjear", headers=headers_auth, json={"codigo": cod.strip()})
                if r.status_code == 200:
                    st.success(r.json().get("message"))
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Cupón inexistente, expirado o previamente utilizado."))

            st.markdown("---")
            st.markdown("### 📢 Comparte tu Enlace y Gana Recompensas")
            try:
                res_me = requests.get(f"{API_URL}/usuario/mi-perfil", headers=headers_auth)
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
                        })
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
                    })
                    if r_ped.status_code == 200:
                        st.success("Solicitud enviada. El Administrador te suministrará los datos por este chat.")
                        st.rerun()

            st.markdown("#### Conversación Privada y Cupones Entregados")
            try:
                r_my_p = requests.get(f"{API_URL}/pagos/mis-mensajes", headers=headers_auth)
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
        tab_cupones_adm, tab_pagos_adm, tab_afiliados_adm, tab_metricas_adm, tab_mantenimiento_adm = st.tabs([
            "Generar Cupones", "Bandeja de Pagos", "Afiliados y Recompensas", "Métricas Globales", "Mantenimiento y Respaldo"
        ])

        with tab_cupones_adm:
            st.markdown("### Emisión de Cupones de Activación (Válidos por 30 minutos)")
            color = st.selectbox("Color del Cupón:", ["verde", "azul", "rojo", "morado"])
            if st.button("Generar Código"):
                r = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": color})
                if r.status_code == 200:
                    d = r.json()
                    st.success(f"Código: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Días: {d.get('duracion_dias')}")

        with tab_pagos_adm:
            st.markdown("### Bandeja de Conciliación de Pagos")
            try:
                r_conv = requests.get(f"{API_URL}/admin/pagos/conversaciones", headers=headers_auth)
                if r_conv.status_code == 200:
                    usuarios = r_conv.json().get("usuarios_con_pago", [])
                    if not usuarios:
                        st.info("No hay pagos pendientes de revisión.")
                    for u in usuarios:
                        with st.expander(f"Usuario: {u.get('apodo')} ({u.get('correo')}) - Plan: {u.get('plan')}"):
                            r_hist = requests.get(f"{API_URL}/admin/pagos/usuario/{u.get('id')}", headers=headers_auth)
                            if r_hist.status_code == 200:
                                for h in r_hist.json().get("mensajes", []):
                                    st.caption(f"{'Usuario' if h.get('emisor_rol') == 'user' else 'Admin'}: {h.get('mensaje')}")
                            
                            st.caption("💡 *Plantilla rápida para enviar datos Pago Móvil BDV:*")
                            if st.button("📋 Pegar Coordenadas BDV", key=f"bdv_{u.get('id')}"):
                                texto_bdv = "Datos BDV: Banco de Venezuela (0102) | Tel: 04128014962 | CI: 84608666 | Monto al cambio BCV del día según plan."
                                requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"para_usuario_id": u.get("id"), "mensaje": texto_bdv})
                                st.success("Coordenadas enviadas.")
                                st.rerun()

                            resp_admin = st.text_area(f"Responder o entregar cupón a {u.get('apodo')}:", key=f"adm_resp_{u.get('id')}")
                            if st.button("Enviar Respuesta", key=f"btn_adm_resp_{u.get('id')}"):
                                requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"para_usuario_id": u.get("id"), "mensaje": resp_admin})
                                st.success("Respuesta enviada.")
                                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_afiliados_adm:
            st.markdown("### 👥 Auditoría de Referidos y Programa de Recompensas")
            try:
                r_af = requests.get(f"{API_URL}/admin/afiliados", headers=headers_auth)
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
                                        })
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
                                        })
                                        if r_rew.status_code == 200:
                                            st.success(r_rew.json().get("message"))
                                            st.rerun()
                                else:
                                    st.caption(f"Progreso Gran Meta: {a.get('total_referidos')}/100 referidos")
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_metricas_adm:
            try:
                r_m = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth)
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
                    r_bk = requests.get(f"{API_URL}/admin/backup", headers=headers_auth)
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
                    r_cron = requests.post(f"{API_URL}/cron/mantenimiento", headers={"X-Cron-Key": CRON_SECRET_KEY})
                    if r_cron.status_code == 200:
                        d_res = r_cron.json()
                        st.success(f"Mantenimiento ejecutado: {d_res.get('chats_semanales_reseteados')} chats reseteados, {d_res.get('planes_vencidos_revertidos')} planes expirados y {d_res.get('mensajes_directos_purgados')} DMs purgados.")
                    else:
                        st.error("Error al disparar mantenimiento.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
