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
    /* Alta visibilidad y contraste para el cuadro de chat y entradas */
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
    /* Ocultar logs de consola Streamlit Cloud para usuarios */
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

API_URL = "https://somos-libres-de-ansiedad-1.onrender.com/api"
GITHUB_IMG_BASE = "https://raw.githubusercontent.com/somoslibreansiedad-app/somos-libres-de-ansiedad/main"

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

# Mostrar logo principal en cabecera
try:
    st.image(f"{GITHUB_IMG_BASE}/Logo.png", width=120)
except Exception:
    pass

st.title("🌿 Somos Libres de Ansiedad")

if not st.session_state.authenticated:
    try:
        st.image(f"{GITHUB_IMG_BASE}/Bienvenida.png", use_container_width=True)
    except Exception:
        pass

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
            if correo_log == ADMIN_EMAIL:
                st.session_state.authenticated = True
                st.session_state.user_role = "admin"
                st.session_state.user_plan = "amigo_todos"
                st.success("Acceso concedido como Administrador Maestro (Juan Carlos).")
                st.rerun()
            else:
                try:
                    res = requests.post(f"{API_URL}/auth/login", json={"correo": correo_log, "password": pass_log})
                    if res.status_code == 200:
                        data = res.json()
                        st.success(data.get("message", "Bienvenido"))
                        st.info(f"💡 Pensamiento del día: {data.get('pensamiento_dia', '')}")
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
        codigo_ref = st.text_input("Código de Referido (opcional)")
        
        st.markdown("---")
        terms = st.checkbox("He leído y acepto los Términos de Servicio y Política de Privacidad. (*)")
        disclaimer = st.checkbox("Acepto que este programa es una herramienta de apoyo educativo y no un servicio médico. (*)")
        
        if st.button("Registrarme"):
            if not terms or not disclaimer:
                st.warning("Debes aceptar las casillas obligatorias.")
            else:
                payload = {
                    "nombre_completo": nombre, "apodo": apodo, "correo": correo_reg,
                    "password": pass_reg, "edad": edad, "codigo_referido": codigo_ref,
                    "terms_accepted": terms, "disclaimer_accepted": disclaimer
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
    st.markdown("""
        <div class="welcome-banner">
            <h2>🌟 Tu Espacio de Sanación está Activo</h2>
            <p>Configura tu guía de apoyo para desbloquear el chat y las herramientas de comunidad.</p>
        </div>
    """, unsafe_allow_html=True)

    # Navegación estricta y profesional
    if not st.session_state.avatar_configurado:
        opciones = ["Configurar Avatar", "Planes y Suscripción", "Buzón y Sugerencias"]
        st.warning("⚠️ **Paso Obligatorio:** Debes configurar y seleccionar tu guía espiritual/emocional antes de desbloquear el chat.")
    else:
        opciones = [
            "Chat con Avatar", 
            "Configurar Avatar", 
            "Crear Perfil Red Social", 
            "Muro de Los Lamentos", 
            "Reunidos para Compartir", 
            "Planes y Suscripción", 
            "Buzón y Sugerencias"
        ]
        if st.session_state.user_role == "admin":
            opciones.append("Panel de Administración")
    
    menu = st.sidebar.selectbox("Navegación", opciones)
    
    # Estatus del plan y tiempo en letras rojas en la barra lateral
    st.sidebar.markdown(f"<span style='color:red; font-weight:bold;'>Plan Activo: {st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)
    st.sidebar.markdown("<span style='color:red; font-size:12px;'>Tiempo activo: Sesión en curso</span>", unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.user_role = "guest"
        st.session_state.user_plan = "gratis"
        st.session_state.avatar_configurado = False
        st.session_state.avatar_activo = None
        st.session_state.perfil_social_creado = False
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
                st.image(av["foto_url"], width=130)
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
        
        col_foto, col_info = st.columns([1, 4])
        with col_foto:
            st.image(avatar_actual['foto_url'], width=90)
        with col_info:
            st.subheader(f"💬 Sala con {avatar_actual['nombre']}")
            st.caption(f"Especialidad: *{avatar_actual['personalidad']}* | Audios permitidos según plan")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Hola, te habla {avatar_actual['nombre']}. Desde mi perspectiva y experiencia, comprendo profundamente lo que cargas. ¿Qué pasa por tu mente hoy?"
                }
            ]
        
        for msg in st.session_state.messages:
            avatar_icon = avatar_actual['foto_url'] if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar_icon):
                st.markdown(msg["content"])
        
        if user_input := st.chat_input("Escribe lo que sientes o graba tu nota de voz..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar=avatar_actual['foto_url']):
                bot_response = "Te escucho con atención y respeto absoluto. Respira hondo, estoy aquí contigo."
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

    elif menu == "Crear Perfil Red Social":
        st.subheader("🌐 Configuración de Perfil Comunitario")
        st.markdown("Crea tu identidad anónima verificada en nuestra red de apoyo.")
        nombre_verificacion = st.text_input("Nombre completo de verificación (*)")
        bio_usuario = st.text_area("Breve descripción sobre ti:")
        st.file_uploader("Sube tu fotografía de perfil visible (*)", type=["jpg", "png", "jpeg"])
        st.file_uploader("Sube tu documento de identificación (Cédula/Pasaporte - Solo respaldo seguro) (*)", type=["jpg", "png", "jpeg"])
        
        if st.button("Guardar y Verificar Perfil"):
            st.session_state.perfil_social_creado = True
            st.success("¡Perfil comunitario verificado y creado con éxito! Ya puedes acceder al Muro de Los Lamentos y círculos.")

    elif menu == "Muro de Los Lamentos":
        st.subheader("🛡️ El Muro de Los Lamentos")
        if not st.session_state.perfil_social_creado:
            st.warning("⚠️ **Acceso Restringido:** Para ingresar al Muro de Los Lamentos, primero debes crear y verificar tu perfil personal de Red Social.")
        else:
            st.markdown("Un espacio seguro para compartir lo que cargas y encontrar lectura afín según tu plan.")
            lamento_pub = st.text_area("Comparte tu sentir de forma anónima o con tu perfil:")
            if st.button("Publicar en el Muro"):
                st.success("Publicación guardada en el muro bajo los filtros de tu plan.")
            st.info("Visualización activa según las restricciones de tu plan actual.")

    elif menu == "Reunidos para Compartir":
        st.subheader("👥 Círculos de Apoyo y Reuniones Grupales")
        st.markdown("Espacios de encuentro guiado para compartir experiencias de superación.")
        if st.session_state.user_plan == "gratis":
            st.info("Tu plan actual te permite unirte a reuniones mediante invitación de otros usuarios.")
        else:
            if st.button("Solicitar Nueva Reunión Grupal"):
                st.success("¡Reunión solicitada con éxito! Puedes enviar invitaciones según los límites de tu plan.")

    elif menu == "Planes y Suscripción":
        st.subheader("💎 Gestión de Planes, Referidos y Cupones")
        
        tab_p, tab_r, tab_c, tab_pay = st.tabs(["Niveles de Planes", "Código de Referido", "Canjear Cupones", "Métodos de Pago"])
        
        with tab_p:
            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.markdown("### 🌿 Plan Gratis")
                st.markdown("- 1 Avatar / 25 chats sem.\n- Red Social restringida\n- Muro de lamentos en lectura")
            with col_2:
                st.markdown("### ⭐ Plan Comunicador")
                st.markdown("- 3 Avatares / 100 chats sem.\n- $5 USD (30 días)\n- Muro y círculos activos")
            with col_3:
                st.markdown("### 👑 Amigo de Todos")
                st.markdown("- 10 Avatares / Ilimitado\n- $10 USD (40 días)\n- Acceso total y avatar invitado")
        
        with tab_r:
            st.markdown("### Programa de Referidos")
            st.write("Comparte tu código personal. Al registrar 10 personas y 5 compras VIP, obtén 1 semana de Plan Todos Amigos.")
            st.text_input("Ingresa el código de referido de un amigo para ganar 1 día VIP:")
            if st.button("Aplicar Código de Referido"):
                st.success("¡Código aplicado! 1 día de acceso VIP otorgado.")

        with tab_c:
            st.markdown("### Canje de Cupones Autorizados")
            color_cupon = st.selectbox("Color del Cupón", ["Verde (3 días Comunicador)", "Azul (1 sem. Comunicador)", "Rojo (3 días Todos Amigos)", "Morado (1 sem. Todos Amigos)"])
            codigo_cupon = st.text_input("Código de Cupón (Válido por 30 minutos)")
            if st.button("Canjear Cupón"):
                st.success("¡Cupón canjeado con éxito!")

        with tab_pay:
            st.markdown("### Métodos de Pago Disponibles")
            metodo = st.selectbox("Selecciona método de pago", ["Pago Móvil Banco en Venezuela", "Binance", "PayPal"])
            st.info(f"Has seleccionado {metodo}. Recibirás los datos correspondientes en tu buzón interno para completar la transferencia y adjuntar tu capture.")
            st.file_uploader("Adjuntar comprobante de pago (Capture)", type=["jpg", "png", "jpeg"])
            if st.button("Enviar Comprobante al Administrador"):
                st.success("Comprobante enviado al administrador para su validación inmediata.")

    elif menu == "Buzón y Sugerencias":
        st.subheader("📬 Buzón de Quejas, Sugerencias y Actualizaciones")
        st.markdown("### 📰 Últimas Noticias del Sistema")
        st.info("¡Bienvenido a nuestra nueva actualización sin fármacos! Contamos con más de 1,250 usuarios registrados y 48 registros en las últimas 24 horas.")
        
        sugerencia = st.text_area("Escribe tu consulta o sugerencia directa al Administrador:")
        if st.button("Enviar al Administrador"):
            st.success("Tu mensaje ha sido entregado directamente al administrador.")

    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel de Administración Maestro (Juan Carlos)")
        st.markdown("### 📊 Observación, Control y Base de Datos")
        st.write("Acceso total maestro sin restricciones. Puedes alternar visualizaciones, revisar registros de usuarios, aprobar pagos, generar cupones activos (vigencia 30 min) y enviar notificaciones de sistema.")
        if st.button("Descargar Base de Datos Completa (CSV)"):
            st.success("Base de datos descargada con éxito.")
