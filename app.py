import streamlit as st
import requests
import os

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
    .stButton button {{
        background-color: {THEME_COLORS['secondary']} !important;
        color: #FFFFFF !important;
        border-radius: 8px;
    }}
    </style>
""", unsafe_allow_html=True)

API_URL = "https://somos-libres-de-ansiedad-1.onrender.com/api"

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "somos.libredeansiedad@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")

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

st.title("🌿 Somos Libres de Ansiedad")

if not st.session_state.authenticated:
    st.markdown("""
        <div class="welcome-banner">
            <h2>✨ ¡Bienvenido a tu Refugio Seguro! ✨</h2>
            <p>Un espacio confidencial, anónimo y guiado por expertos para recuperar tu calma interior.</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
        correo_log = st.text_input("Correo Electrónico", key="log_correo")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        if st.button("Ingresar"):
            if correo_log == ADMIN_EMAIL and pass_log == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.user_role = "admin"
                st.session_state.user_plan = "amigo_todos"
                st.success("Acceso concedido como Administrador.")
                st.rerun()
            else:
                try:
                    res = requests.post(f"{API_URL}/auth/login", json={"correo": correo_log, "password": pass_log})
                    if res.status_code == 200:
                        data = res.json()
                        st.success(data.get("message", "Bienvenido"))
                        st.session_state.authenticated = True
                        st.session_state.user_role = "user"
                        st.session_state.user_plan = data.get("plan_actual", "gratis")
                        st.rerun()
                    else:
                        st.error("Correo o contraseña incorrectos.")
                except Exception as e:
                    st.error(f"Error de conexión con el servidor: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)
        
        st.markdown("---")
        terms = st.checkbox("He leído y acepto los Términos de Servicio y Política de Privacidad. (*)")
        disclaimer = st.checkbox("Acepto que este programa es una herramienta de apoyo educativo y no un servicio médico. (*)")
        
        if st.button("Registrarme"):
            if not terms or not disclaimer:
                st.warning("Debes aceptar las casillas obligatorias.")
            else:
                payload = {
                    "nombre_completo": nombre, "apodo": apodo, "correo": correo_reg,
                    "password": pass_reg, "edad": edad, "terms_accepted": terms,
                    "disclaimer_accepted": disclaimer
                }
                try:
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
                    if res.status_code == 200:
                        st.success(res.json()["message"])
                    else:
                        st.error(res.json().get("detail", "Error en el registro."))
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

else:
    # Mensaje de bienvenida llamativo tras iniciar sesión
    st.markdown("""
        <div class="welcome-banner">
            <h2>🌟 Tu Espacio de Sanación está Activo</h2>
            <p>Configura tu guía de apoyo para comenzar la sesión de acompañamiento.</p>
        </div>
    """, unsafe_allow_html=True)

    # Definir opciones de navegación según si el avatar está configurado o no
    if not st.session_state.avatar_configurado:
        opciones = ["Configurar Avatar"]
        st.warning("⚠️ **Paso Obligatorio:** Debes configurar y seleccionar tu guía espiritual/emocional antes de desbloquear el chat.")
    else:
        opciones = ["Chat con Avatar", "Configurar Avatar", "Muro de Los Lamentos", "Biblioteca"]
        if st.session_state.user_role == "admin":
            opciones.append("Panel de Administración")
    
    menu = st.sidebar.selectbox("Navegación", opciones)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.user_role = "guest"
        st.session_state.user_plan = "gratis"
        st.session_state.avatar_configurado = False
        st.session_state.avatar_activo = None
        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()

    if menu == "Configurar Avatar":
        st.subheader("🛠️ Selección y Personalización de tu Guía")
        st.markdown("Elige al especialista que mejor se adapte a tu momento actual:")
        
        try:
            res = requests.get(f"{API_URL}/avatares/catalogo")
            avatares = res.json().get("avatares", []) if res.status_code == 200 else []
        except Exception:
            avatares = []

        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for idx, av in enumerate(avatares):
            with cols[idx % 3]:
                st.image(av["foto_url"], width=120)
                st.markdown(f"**{av['nombre']}** ({av['edad']} años)")
                st.markdown(f"🌍 **País:** {av['nacionalidad']}")
                st.markdown(f"💡 **Enfoque:** {av['personalidad']}")
                if st.button(f"Seleccionar a {av['nombre']}", key=f"btn_{idx}"):
                    st.session_state.avatar_activo = av
                    st.session_state.avatar_configurado = True
                    if "messages" in st.session_state:
                        del st.session_state.messages
                    st.success(f"¡Has seleccionado a {av['nombre']} como tu guía!")
                    st.rerun()

    elif menu == "Chat con Avatar" and st.session_state.avatar_configurado:
        avatar_actual = st.session_state.avatar_activo
        st.subheader(f"💬 Sala de Apoyo Emocional con {avatar_actual['nombre']}")
        st.caption(f"Plan: **{st.session_state.get('user_plan', 'GRATIS').upper()}** | Especialista: *{avatar_actual['personalidad']}*")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Hola, soy {avatar_actual['nombre']}. He leído detenidamente mi guía de vida y estoy aquí para escucharte y apoyarte desde nuestra biblioteca de recursos. ¿Qué pasa por tu mente hoy?"
                }
            ]
        
        for msg in st.session_state.messages:
            avatar_icon = "🌿" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar_icon):
                st.markdown(msg["content"])
        
        if user_input := st.chat_input("Escribe lo que sientes en este momento..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar="🌿"):
                bot_response = "Te escucho con atención. Respira hondo, estoy aquí contigo."
                try:
                    res = requests.post(f"{API_URL}/chat", json={
                        "user_id": "user_demo",
                        "message": user_input,
                        "plan_nivel": st.session_state.get('user_plan', 'gratis'),
                        "avatar_id": avatar_actual['avatar_id'],
                        "avatar_nombre": avatar_actual['nombre']
                    })
                    if res.status_code == 200:
                        data = res.json()
                        bot_response = data.get("response", bot_response)
                except Exception:
                    pass
                
                st.markdown(bot_response)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_response})

    elif menu == "Muro de Los Lamentos":
        st.subheader("🛡️ El Muro de Los Lamentos")
        st.markdown("Un espacio seguro para compartir lo que cargas y encontrar lectura afín según tu plan.")
        st.info("Espacio comunitario protegido activo.")

    elif menu == "Biblioteca":
        st.subheader("📚 Biblioteca Documental y Recursos")
        st.markdown("Explora lecturas y guías validadas para la gestión de la ansiedad.")

    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel de Administración Maestro")
        st.markdown("### 📊 Actividad del Sistema")
        st.write("Modo supervisor activado con acceso total.")
