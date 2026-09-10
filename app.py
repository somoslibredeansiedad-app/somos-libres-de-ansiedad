import io
import os
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

st.set_page_config(
    page_title="Somos Libres de Ansiedad",
    page_icon="🌿",
    layout="centered"
)

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {THEME_COLORS['background']};
        color: {THEME_COLORS['text_primary']};
    }}
    h1, h2, h3, h4, h5, h6, p, label, span {{
        color: {THEME_COLORS['text_primary']} !important;
    }}
    .welcome-banner {{
        background: linear-gradient(135deg, #4E8A72 0%, #A8E6CF 100%);
        padding: 20px;
        border-radius: 12px;
        color: #1E4D3B;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select, div[data-baseweb="input"] input {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        -webkit-text-fill-color: #1E4D3B !important;
        border-color: {THEME_COLORS['secondary']} !important;
    }}
    .stChatInput textarea {{
        background-color: #FFFFFF !important;
        color: #1E4D3B !important;
        -webkit-text-fill-color: #1E4D3B !important;
    }}
    .stButton button {{
        background-color: {THEME_COLORS['secondary']} !important;
        color: #FFFFFF !important;
        border-radius: 8px;
    }}
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

API_URL = "https://somos-libres-de-ansiedad-1.onrender.com/api"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "somos.libredeansiedad@gmail.com")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "guest"
if "user_plan" not in st.session_state:
    st.session_state.user_plan = "gratis"
if "avatar_configurado" not in st.session_state:
    st.session_state.avatar_configurado = False
if "avatar_activo" not in st.session_state:
    st.session_state.avatar_activo = None
if "perfil_social_creado" not in st.session_state:
    st.session_state.perfil_social_creado = False
if "token" not in st.session_state:
    st.session_state.token = None


def obtener_ruta_o_url_avatar(avatar_data: dict) -> str:
    """Resuelve la ruta local o externa de la imagen del avatar."""
    if not isinstance(avatar_data, dict):
        return ""
    
    nombre_archivo = (
        avatar_data.get("archivos", {}).get("imagen")
        or avatar_data.get("foto_url")
        or avatar_data.get("foto")
        or ""
    )
    
    if not nombre_archivo:
        return ""
    
    if nombre_archivo.startswith("http://") or nombre_archivo.startswith("https://"):
        return nombre_archivo
        
    if os.path.exists(nombre_archivo):
        return nombre_archivo
        
    ruta_en_carpeta = os.path.join("avatares", nombre_archivo)
    if os.path.exists(ruta_en_carpeta):
        return ruta_en_carpeta
        
    ruta_absoluta = os.path.join(os.path.dirname(__file__), "avatares", nombre_archivo)
    if os.path.exists(ruta_absoluta):
        return ruta_absoluta

    # Fallback con el nombre exacto de tu repositorio GitHub
    nombre_escapado = nombre_archivo.replace(" ", "%20")
    return f"https://raw.githubusercontent.com/lacontadoraia-hub/somos-libres-de-ansiedad/main/avatares/{nombre_escapado}"


def mostrar_imagen_avatar(avatar_data: dict, ancho: int = 120):
    """Renderiza la foto del avatar en pantalla o un fallback si no se ubica."""
    src = obtener_ruta_o_url_avatar(avatar_data)
    if src:
        try:
            st.image(src, width=ancho)
        except Exception:
            st.markdown(f"<div style='font-size:{ancho//2}px; text-align:center;'>👤</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:{ancho//2}px; text-align:center;'>👤</div>", unsafe_allow_html=True)


# Carga de imágenes locales
if os.path.exists("Logo.png"):
    st.image("Logo.png", width=120)

st.title("🌿 Somos Libres de Ansiedad")

if not st.session_state.authenticated:
    if os.path.exists("Bienvenida.png"):
        st.image("Bienvenida.png", use_container_width=True)

    st.markdown("""
        <div class="welcome-banner">
            <h2>✨ Tu Refugio Seguro y Sin Fármacos ✨</h2>
            <p>Un espacio confidencial guiado por expertos para recuperar tu calma interior.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab_login:
        correo_log = st.text_input("Correo Electrónico", key="log_correo")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")

        if st.button("Ingresar"):
            try:
                res = requests.post(f"{API_URL}/auth/login", json={"correo": correo_log.strip(), "password": pass_log})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.authenticated = True
                    st.session_state.user_role = data.get("role", "user")
                    st.session_state.user_plan = data.get("plan_actual", "gratis")
                    st.session_state.token = data.get("access_token")
                    st.success("¡Bienvenido/a de nuevo!")
                    st.info(f"💡 Pensamiento del día: {data.get('pensamiento_dia', '')}")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario no registrado.")
            except requests.RequestException as e:
                st.error(f"Error de conexión con el servidor API: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)

        codigo_ref = st.text_input("Código de Referido (opcional)")

        st.markdown("---")
        terms = st.checkbox("He leído y acepto los Términos de Servicio y Política de Privacidad. (*)")
        disclaimer = st.checkbox("Acepto que este programa es una herramienta de apoyo educativo y no un servicio médico. (*)")

        if st.button("Registrarme"):
            if not terms or not disclaimer:
                st.warning("Debes aceptar las casillas obligatorias.")
            elif not nombre or not apodo or not correo_reg or not pass_reg:
                st.warning("Por favor completa todos los campos obligatorios marcados con (*).")
            else:
                payload = {
                    "nombre_completo": nombre.strip(),
                    "apodo": apodo.strip(),
                    "correo": correo_reg.strip(),
                    "password": pass_reg,
                    "edad": int(edad),
                    "codigo_referido": codigo_ref.strip() if codigo_ref else None,
                    "terms_accepted": terms,
                    "disclaimer_accepted": disclaimer
                }
                try:
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
                    if res.status_code == 201:
                        st.success(res.json().get("message", "¡Registro exitoso! Ya puedes iniciar sesión."))
                    else:
                        st.error(res.json().get("detail", "Error al procesar el registro."))
                except requests.RequestException as e:
                    st.error(f"Error de conexión: {e}")

else:
    st.markdown("""
        <div class="welcome-banner">
            <h2>🌟 Tu Espacio de Sanación está Activo</h2>
            <p>Configura tu guía de apoyo para desbloquear el chat y las herramientas de comunidad.</p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.avatar_configurado:
        opciones = ["Configurar Avatar", "Planes y Suscripción", "Buzón y Sugerencias"]
        st.warning("⚠️ **Paso Obligatorio:** Selecciona tu avatar guía antes de iniciar el chat.")
    else:
        opciones = [
            "Chat con Avatar",
            "Configurar Avatar",
            "Muro de Los Lamentos",
            "Planes y Suscripción",
            "Buzón y Sugerencias"
        ]
        if st.session_state.user_role == "admin":
            opciones.append("Panel de Administración")

    menu = st.sidebar.selectbox("Navegación", opciones)

    st.sidebar.markdown(f"<span style='color:red; font-weight:bold;'>Plan Activo: {st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.user_role = "guest"
        st.session_state.user_plan = "gratis"
        st.session_state.avatar_configurado = False
        st.session_state.avatar_activo = None
        st.session_state.token = None
        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()

    headers_auth = {"Authorization": f"Bearer {st.session_state.get('token')}"}

    if menu == "Configurar Avatar":
        st.subheader("🛠️ Selección de tu Guía Especialista")
        try:
            res = requests.get(f"{API_URL}/avatares/catalogo", headers=headers_auth)
            avatares = res.json().get("avatares", []) if res.status_code == 200 else []
        except requests.RequestException:
            avatares = []

        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for idx, av in enumerate(avatares):
            with cols[idx % 3]:
                mostrar_imagen_avatar(av, ancho=130)
                st.markdown(f"**{av.get('nombre', 'Guía')}** ({av.get('edad', '')} años)")
                st.markdown(f"{av.get('bandera', '')} **País:** {av.get('nacionalidad', av.get('pais', ''))}")
                st.caption(f"💡 {av.get('especialidad', '')}")
                avatar_key = av.get('avatar_id') or av.get('id_avatar') or f"avatar_{idx}"
                if st.button("Seleccionar", key=f"btn_{avatar_key}"):
                    st.session_state.avatar_activo = av
                    st.session_state.avatar_configurado = True
                    if "messages" in st.session_state:
                        del st.session_state.messages
                    st.success(f"¡Has seleccionado a {av.get('nombre', 'tu guía')}!")
                    st.rerun()

    elif menu == "Chat con Avatar" and st.session_state.avatar_configurado:
        avatar_actual = st.session_state.avatar_activo

        col_foto, col_info = st.columns([1, 4])
        with col_foto:
            mostrar_imagen_avatar(avatar_actual, ancho=90)
        with col_info:
            st.subheader(f"💬 Sala con {avatar_actual.get('nombre', 'Guía')}")
            st.caption(f"{avatar_actual.get('bandera', '')} {avatar_actual.get('especialidad', '')}")

        avatar_src = obtener_ruta_o_url_avatar(avatar_actual)
        chat_avatar_icon = avatar_src if avatar_src.startswith("http") else "🤖"

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Hola, soy {avatar_actual.get('nombre', 'tu guía')}. Estoy aquí para acompañarte sin juicios. ¿Qué sientes en este momento?"
                }
            ]

        for msg in st.session_state.messages:
            icon = chat_avatar_icon if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=icon):
                st.markdown(msg["content"])

        if user_input := st.chat_input("Escribe lo que sientes..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar=chat_avatar_icon):
                bot_response = "Te escucho atentamente. Respira despacio; estoy procesando tu mensaje."
                try:
                    payload = {
                        "message": user_input,
                        "avatar_id": avatar_actual.get('avatar_id') or avatar_actual.get('id_avatar')
                    }
                    res = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload)
                    if res.status_code == 200:
                        bot_response = res.json().get("response", bot_response)
                    elif res.status_code == 403:
                        bot_response = "⚠️ Has alcanzado el límite de mensajes de tu plan actual. Considera renovar o canjear un cupón."
                except requests.RequestException:
                    bot_response = "Error al conectar con el asistente. Inténtalo de nuevo en unos segundos."

                st.markdown(bot_response)

            st.session_state.messages.append({"role": "assistant", "content": bot_response})

    elif menu == "Muro de Los Lamentos":
        st.subheader("🛡️ El Muro de Los Lamentos")
        st.markdown("Un espacio seguro y solidario para desahogarte y leer a otros usuarios.")

        lamento_pub = st.text_area("Comparte tu sentir de forma libre:")
        anonimo = st.checkbox("Publicar como Anónimo", value=False)

        if st.button("Publicar en el Muro"):
            if not lamento_pub.strip():
                st.warning("El mensaje no puede estar vacío.")
            else:
                try:
                    res = requests.post(
                        f"{API_URL}/muro",
                        headers=headers_auth,
                        json={"contenido": lamento_pub.strip(), "is_anonimo": anonimo}
                    )
                    if res.status_code == 201:
                        st.success("Mensaje publicado en el muro.")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Error al publicar."))
                except requests.RequestException:
                    st.error("Error de conexión al intentar publicar.")

        st.markdown("---")
        st.markdown("### Publicaciones Recientes")
        try:
            res = requests.get(f"{API_URL}/muro", headers=headers_auth)
            if res.status_code == 200:
                for post in res.json().get("posts", []):
                    st.info(f"**{post.get('autor', 'Anónimo')}**: {post.get('contenido', '')}")
            elif res.status_code == 403:
                st.warning("Tu plan actual tiene restricciones para leer el Muro. Adquiere el plan Comunicador o Amigo de Todos.")
        except requests.RequestException:
            st.error("No se pudo sincronizar el muro con el servidor.")

    elif menu == "Planes y Suscripción":
        st.subheader("💎 Gestión de Planes y Cupones")
        tab_p, tab_c = st.tabs(["Niveles de Planes", "Canjear Cupones"])

        with tab_p:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### 🌿 Gratis")
                st.markdown("- 1 Avatar\n- 25 chats/semana\n- Muro en modo lectura")
            with c2:
                st.markdown("### ⭐ Comunicador")
                st.markdown("- 3 Avatares\n- 100 chats/semana\n- Acceso completo al Muro")
            with c3:
                st.markdown("### 👑 Amigo de Todos")
                st.markdown("- 10 Avatares ilimitados\n- Sin límites de chat\n- Círculos de apoyo")

        with tab_c:
            codigo_cupon = st.text_input("Código del Cupón (ej. SL-VERDE-1234):")
            if st.button("Canjear Cupón"):
                if not codigo_cupon.strip():
                    st.warning("Ingresa un código válido.")
                else:
                    try:
                        res = requests.post(
                            f"{API_URL}/cupones/canjear",
                            headers=headers_auth,
                            json={"codigo": codigo_cupon.strip()}
                        )
                        if res.status_code == 200:
                            st.success(res.json().get("message", "¡Cupón canjeado con éxito!"))
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Cupón inválido o expirado."))
                    except requests.RequestException:
                        st.error("Error de conexión al canjear cupón.")

    elif menu == "Buzón y Sugerencias":
        st.subheader("📬 Buzón y Soporte")
        st.info("Comunidad activa en proceso de recuperación sin fármacos.")
        st.text_area("Envía tu sugerencia o duda:")
        if st.button("Enviar"):
            st.success("Mensaje recibido por el equipo.")

    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel Maestro (Admin)")
        st.markdown("### Generador de Cupones de Emergencia (30 min de validez)")
        color = st.selectbox("Tipo de Cupón:", ["verde", "azul", "rojo", "morado"])
        if st.button("Generar Cupón"):
            try:
                res = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": color})
                if res.status_code == 200:
                    d = res.json()
                    st.success(f"Código generado: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Válido: {d.get('expira_en_minutos')} minutos.")
                else:
                    st.error(res.json().get("detail", "Error al generar cupón."))
            except requests.RequestException:
                st.error("Error de conexión al generar cupón.")
