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
    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background-color: {THEME_COLORS['surface']} !important;
        color: {THEME_COLORS['text_primary']} !important;
        border-color: {THEME_COLORS['border']} !important;
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

st.title("🌿 Somos Libres de Ansiedad")
st.markdown("Tu refugio seguro, anónimo y guiado por expertos.")

if not st.session_state.authenticated:
    st.subheader("Bienvenido a tu Espacio Seguro")
    
    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
        correo_log = st.text_input("Correo Electrónico", key="log_correo")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        if st.button("Ingresar"):
            if correo_log == ADMIN_EMAIL and pass_log == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.user_role = "admin"
                st.session_state.user_plan = "premium"
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
                    st.error(f"No se pudo conectar con el servidor: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)
        
        st.markdown("---")
        st.markdown(f"<span style='color:{THEME_COLORS['text_secondary']};'>Esta información es confidencial y personaliza tu experiencia.</span>", unsafe_allow_html=True)
        sexo = st.text_input("Sexo (Opcional)")
        profesion = st.text_input("Profesión (Opcional)")
        orientacion = st.text_input("Orientación sexual (Opcional)")
        sentimental = st.text_input("Situación sentimental (Opcional)")
        hijos = st.number_input("Cantidad de hijos", min_value=0, value=0)
        referido = st.text_input("Código de Referido (Opcional)")
        
        st.markdown("---")
        terms = st.checkbox("He leído y acepto los Términos de Servicio y la Política de Privacidad. (*)")
        disclaimer = st.checkbox("Acepto que este programa es una herramienta de apoyo educativo y no un servicio médico. (*)")
        
        if st.button("Registrarme"):
            if not terms or not disclaimer:
                st.warning("Debes aceptar las casillas obligatorias.")
            else:
                payload = {
                    "nombre_completo": nombre, "apodo": apodo, "correo": correo_reg,
                    "password": pass_reg, "edad": edad, "sexo": sexo or None,
                    "profesion": profesion or None, "orientacion_sexual": orientacion or None,
                    "situacion_sentimental": sentimental or None, "cantidad_hijos": hijos,
                    "codigo_referido": referido or None, "terms_accepted": terms,
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
    opciones = ["Chat con Avatar", "Muro de Los Lamentos", "Biblioteca"]
    
    if st.session_state.user_role == "admin":
        opciones.append("Panel de Administración")
    
    menu = st.sidebar.selectbox("Navegación", opciones)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.user_role = "guest"
        st.session_state.user_plan = "gratis"
        if "messages" in st.session_state:
            del st.session_state.messages
        st.rerun()

    if menu == "Chat con Avatar":
        st.subheader("💬 Sala de Apoyo Emocional")
        st.caption(f"Plan activo: **{st.session_state.get('user_plan', 'GRATIS').upper()}**")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Hola. Estoy aquí para escucharte y acompañarte sin juzgarte. Tómate tu tiempo, ¿qué pasa por tu mente en este momento?"
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
                bot_response = "Te escucho con atención y respeto. Estoy aquí contigo, respira hondo y cuéntame un poco más."
                try:
                    res = requests.post(f"{API_URL}/chat", json={
                        "user_id": "user_demo",
                        "message": user_input,
                        "plan_nivel": st.session_state.get('user_plan', 'gratis')
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
        namespaces = st.container()
        namespaces.markdown("Explora lecturas y guías validadas para la gestión de la ansiedad.")

    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel de Administración Maestro")
        st.markdown("### 📊 Alertas y Actividad Reciente del Sistema")
        st.write("Modo supervisor activado de forma segura.")
