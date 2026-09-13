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

API_URL = os.getenv("API_URL", "https://somos-libres-de-ansiedad-1.onrender.com/api")

# Variables de estado de sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
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

# Captura de código de referido en URL (?ref=1111111)
query_params = st.query_params
ref_url = query_params.get("ref", "")

def obtener_ruta_o_url_avatar(avatar_data: dict) -> str:
    if not isinstance(avatar_data, dict):
        return ""
    nombre_archivo = avatar_data.get("imagen") or avatar_data.get("foto") or ""
    if not nombre_archivo:
        return ""
    if nombre_archivo.startswith("http://") or nombre_archivo.startswith("https://"):
        return nombre_archivo
    ruta_en_carpeta = os.path.join("avatares", nombre_archivo)
    if os.path.exists(ruta_en_carpeta):
        return ruta_en_carpeta
    return f"https://raw.githubusercontent.com/lacontadoraia-hub/somos-libres-de-ansiedad/main/avatares/{nombre_archivo}"

def mostrar_imagen_avatar(avatar_data: dict, ancho: int = 120):
    src = obtener_ruta_o_url_avatar(avatar_data)
    if src:
        try:
            st.image(src, width=ancho)
        except Exception:
            st.markdown(f"<div style='width:{ancho}px; height:{ancho}px; background-color:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:8px; font-size:{ancho//3}px;'>👤</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='width:{ancho}px; height:{ancho}px; background-color:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:8px; font-size:{ancho//3}px;'>👤</div>", unsafe_allow_html=True)

if os.path.exists("Logo.png"):
    st.image("Logo.png", width=120)

st.title("🌿 Somos Libres de Ansiedad")

# --- PANTALLA NO AUTENTICADA (LOGIN / REGISTRO) ---
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

        if st.button("Ingresar a mi espacio"):
            try:
                res = requests.post(f"{API_URL}/auth/login", json={"correo": correo_log.strip(), "password": pass_log})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.authenticated = True
                    st.session_state.user_role = data.get("role", "user")
                    st.session_state.user_plan = data.get("plan_actual", "gratis")
                    st.session_state.user_apodo = data.get("apodo", "")
                    st.session_state.token = data.get("access_token")
                    st.success(f"¡Bienvenido/a {st.session_state.user_apodo}!")
                    st.info(f"💡 Pensamiento de calma: {data.get('pensamiento_dia', '')}")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario no registrado.")
            except requests.RequestException as e:
                st.error(f"Error de conexión con el servidor API: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*) (cómo quieres que te llamen los avatares)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)

        with st.expander("Personalizar mi experiencia (Opcional)"):
            st.caption("Campos opcionales. Esta información se utiliza exclusivamente para personalizar tu experiencia en la plataforma y no condiciona el acceso al servicio.")
            sexo = st.selectbox("Sexo", ["Prefiero no decir", "Femenino", "Masculino", "Otro"])
            profesion = st.text_input("Profesión u ocupación")
            situacion = st.selectbox("Situación sentimental", ["Prefiero no decir", "Soltero/a", "En pareja", "Casado/a", "Divorciado/a", "Viudo/a"])
            hijos = st.number_input("Cantidad de hijos", min_value=0, max_value=20, value=0)

        codigo_ref = st.text_input("Código de Referido (opcional)", value=ref_url)

        st.markdown("---")
        terms = st.checkbox("He leído y acepto los Términos de Servicio y la Política de Privacidad. (*)")
        disclaimer = st.checkbox("Acepto que este programa es una herramienta de apoyo informativo/educativo y no un servicio médico o terapéutico. (*)")

        if st.button("Registrarme"):
            if not terms or not disclaimer:
                st.warning("Debes marcar las casillas obligatorias de Términos y Descargo Médico.")
            elif not nombre or not apodo or not correo_reg or not pass_reg:
                st.warning("Por favor completa los campos obligatorios marcados con (*).")
            else:
                payload = {
                    "nombre_completo": nombre.strip(),
                    "apodo": apodo.strip(),
                    "correo": correo_reg.strip(),
                    "password": pass_reg,
                    "edad": int(edad),
                    "sexo": sexo if sexo != "Prefiero no decir" else None,
                    "profesion": profesion.strip() if profesion else None,
                    "situacion_sentimental": situacion if situacion != "Prefiero no decir" else None,
                    "cantidad_hijos": int(hijos) if hijos > 0 else 0,
                    "codigo_referido": codigo_ref.strip() if codigo_ref else None,
                    "terms_accepted": terms,
                    "disclaimer_accepted": disclaimer
                }
                try:
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
                    if res.status_code == 201:
                        st.success(res.json().get("message", "¡Registro completado! Ya puedes iniciar sesión."))
                    else:
                        st.error(res.json().get("detail", "Error al procesar el registro."))
                except requests.RequestException as e:
                    st.error(f"Error de conexión: {e}")

# --- PANTALLA AUTENTICADA ---
else:
    st.markdown(f"""
        <div class="welcome-banner">
            <h2>🌟 Espacio Activo de {st.session_state.user_apodo}</h2>
            <p>Selecciona tu avatar guía para iniciar tu acompañamiento reflexivo.</p>
        </div>
    """, unsafe_allow_html=True)

    opciones = [
        "Seleccionar Avatar",
        "Chat con Avatar",
        "Comunidad Somos Libres",
        "Planes y Suscripción"
    ]
    if st.session_state.user_role == "admin":
        opciones.append("Panel de Administración")

    menu = st.sidebar.selectbox("Navegación", opciones)
    st.sidebar.markdown(f"<span style='color:red; font-weight:bold;'>Plan Activo: {st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.user_role = "user"
        st.session_state.user_plan = "gratis"
        st.session_state.avatar_activo = None
        st.session_state.token = None
        st.query_params.clear()
        st.rerun()

    headers_auth = {"Authorization": f"Bearer {st.session_state.get('token')}"}

    # 1. SELECCIÓN DE AVATAR
    if menu == "Seleccionar Avatar":
        st.subheader("🛠️ Catálogo Oficial de Guías")
        st.caption("Selecciona el compañero con quien deseas reflexionar el día de hoy.")
        
        try:
            res = requests.get(f"{API_URL}/avatares/catalogo", headers=headers_auth)
            avatares = res.json().get("avatares", []) if res.status_code == 200 else []
        except requests.RequestException:
            avatares = []

        col1, col2 = st.columns(2)
        cols = [col1, col2]

        for idx, av in enumerate(avatares):
            with cols[idx % 2]:
                mostrar_imagen_avatar(av, ancho=140)
                st.markdown(f"### {av.get('bandera', '')} {av.get('nombre')}")
                st.markdown(f"**Origen:** {av.get('pais')} | **Enfoque:** {av.get('tono')}")
                
                btn_txt = "Seleccionar este Guía" if not av.get("is_activo") else "Continuar Conversando"
                if st.button(btn_txt, key=f"sel_{av.get('id')}"):
                    try:
                        res_act = requests.post(
                            f"{API_URL}/avatares/seleccionar",
                            headers=headers_auth,
                            json={"avatar_id": av.get("id")}
                        )
                        if res_act.status_code == 200:
                            st.session_state.avatar_activo = av
                            st.success(f"Has seleccionado a {av.get('nombre')}. Ve a la pestaña 'Chat con Avatar'.")
                        else:
                            st.error(res_act.json().get("detail", "Límite de avatares alcanzado para tu plan."))
                    except requests.RequestException:
                        st.error("Error al conectar con la API.")

    # 2. CHAT CON AVATAR
    elif menu == "Chat con Avatar":
        if not st.session_state.avatar_activo:
            st.warning("⚠️ Primero debes ir a 'Seleccionar Avatar' para elegir a tu guía.")
        else:
            avatar_actual = st.session_state.avatar_activo

            col_foto, col_info = st.columns([1, 4])
            with col_foto:
                mostrar_imagen_avatar(avatar_actual, ancho=80)
            with col_info:
                st.subheader(f"💬 Conversando con {avatar_actual.get('nombre')}")
                st.caption(f"{avatar_actual.get('bandera')} {avatar_actual.get('tono')}")

            avatar_src = obtener_ruta_o_url_avatar(avatar_actual)
            chat_avatar_icon = avatar_src if avatar_src.startswith("http") else "🌿"

            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": avatar_actual.get("disparador_inicial", "Respira hondo y tómate tu tiempo. ¿De qué te gustaría hablar hoy?")
                    }
                ]

            for msg in st.session_state.messages:
                icon = chat_avatar_icon if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=icon):
                    st.markdown(msg["content"])

            # Entrada de audio integrada en vivo
            audio_val = st.audio_input("🎙️ Enviar nota de voz corta")
            if audio_val is not None:
                st.info("Nota de voz grabada. Procesando mensaje...")

            if user_input := st.chat_input("Escribe lo que sientes..."):
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_input)

                with st.chat_message("assistant", avatar=chat_avatar_icon):
                    bot_response = "Te escucho con serenidad..."
                    try:
                        payload = {
                            "avatar_id": avatar_actual.get("id"),
                            "message": user_input,
                            "is_audio": False,
                            "audio_duracion_segundos": 0
                        }
                        res = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload)
                        if res.status_code == 200:
                            data = res.json()
                            bot_response = data.get("respuesta", bot_response)
                            st.caption(f"Mensajes restantes de tu plan: {data.get('chats_restantes')}")
                        elif res.status_code == 403:
                            bot_response = "⚠️ Has alcanzado el límite semanal de mensajes para tu plan. Considera actualizar a Comunicador o Amigo de Todos."
                    except requests.RequestException:
                        bot_response = "Error de conexión con el servidor."

                    st.markdown(bot_response)

                st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # 3. COMUNIDAD Y RED DE APOYO
    elif menu == "Comunidad Somos Libres":
        st.subheader("🌐 Espacio Comunitario")
        sub_tab = st.radio("Sección:", ["Muro de Desahogo", "Reunidos para Compartir", "Buzón de Sugerencias"], horizontal=True)

        if sub_tab == "Muro de Desahogo":
            st.markdown("### 💬 Muro de Desahogo y Esperanza")
            if st.session_state.user_plan != "gratis":
                contenido_post = st.text_area("Comparte una reflexión o desahogo:")
                anon = st.checkbox("Publicar de forma anónima")
                if st.button("Publicar en el Muro"):
                    try:
                        res = requests.post(f"{API_URL}/muro", headers=headers_auth, json={"contenido": contenido_post, "is_anonimo": anon})
                        if res.status_code == 201:
                            st.success("Publicado correctamente.")
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Error al publicar."))
                    except requests.RequestException:
                        st.error("Error al conectar con la API.")
            else:
                st.caption("ℹ️ El Plan Gratis permite leer el muro. Para publicar comentarios y crear hilos, activa el Plan Comunicador.")

            st.markdown("---")
            try:
                res = requests.get(f"{API_URL}/muro", headers=headers_auth)
                if res.status_code == 200:
                    for post in res.json().get("posts", []):
                        st.info(f"**{post.get('autor')}** ({post.get('fecha')[:10]}): {post.get('contenido')}")
            except requests.RequestException:
                st.error("No se pudo cargar el muro.")

        elif sub_tab == "Reunidos para Compartir":
            st.markdown("### 👥 Círculos de Ayuda y Encuentro")
            st.info("Salas de conversación sincrónicas para apoyo mutuo entre miembros y moderación guiada.")
            st.markdown("- **Plan Gratis:** Acceso por invitación recibida.")
            st.markdown("- **Plan Comunicador:** 1 reunión semanal (hasta 5 participantes).")
            st.markdown("- **Plan Amigo de Todos:** 3 reuniones semanales (hasta 10 participantes + Avatar guía invitado).")

        elif sub_tab == "Buzón de Sugerencias":
            st.markdown("### 📬 Buzón y Tickets de Soporte")
            tab_enviar, tab_historial = st.tabs(["Enviar Solicitud", "Mis Solicitudes"])

            with tab_enviar:
                cat = st.selectbox("Categoría:", ["Falla técnica", "Duda de facturación/plan", "Sugerencia", "Consulta general"])
                asu = st.text_input("Asunto:")
                msg = st.text_area("Detalla tu consulta:")
                if st.button("Enviar al Administrador"):
                    try:
                        payload = {"categoria": cat, "asunto": asu, "mensaje": msg}
                        res = requests.post(f"{API_URL}/buzon/ticket", headers=headers_auth, json=payload)
                        if res.status_code == 200:
                            st.success("Ticket enviado con éxito.")
                        else:
                            st.error("Error al procesar el ticket.")
                    except requests.RequestException:
                        st.error("Error de conexión.")

            with tab_historial:
                try:
                    res = requests.get(f"{API_URL}/buzon/mis-tickets", headers=headers_auth)
                    if res.status_code == 200:
                        tickets = res.json().get("tickets", [])
                        if not tickets:
                            st.caption("No tienes tickets enviados.")
                        for t in tickets:
                            with st.expander(f"[{t.get('estatus')}] {t.get('asunto')}"):
                                st.write(f"**Mensaje:** {t.get('mensaje')}")
                                if t.get('respuesta_admin'):
                                    st.success(f"**Respuesta del Administrador:** {t.get('respuesta_admin')}")
                                else:
                                    st.caption("Aún sin respuesta.")
                except requests.RequestException:
                    st.error("Error al obtener tickets.")

    # 4. PLANES Y CUPONES
    elif menu == "Planes y Suscripción":
        st.subheader("💎 Opciones de Suscripción y Cupones")
        tab_niveles, tab_cupon, tab_pago = st.tabs(["Planes Oficiales", "Canjear Cupón", "Métodos de Pago"])

        with tab_niveles:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### 🌿 Gratis\n- $0\n- 1 Avatar activo\n- 25 chats semanales\n- 3 audios (10s)")
            with c2:
                st.markdown("### ⭐ Comunicador\n- $5 USD / 30 días\n- 3 Avatares activos\n- 100 chats semanales\n- 10 audios (30s)")
            with c3:
                st.markdown("### 👑 Amigo de Todos\n- $10 USD / 40 días\n- 10 Avatares activos\n- Chats ilimitados\n- Audios ilimitados (60s)")

        with tab_cupon:
            cod_cup = st.text_input("Introduce tu Código de Cupón:")
            if st.button("Canjear Cupón"):
                try:
                    res = requests.post(f"{API_URL}/cupones/canjear", headers=headers_auth, json={"codigo": cod_cup.strip()})
                    if res.status_code == 200:
                        st.success(res.json().get("message"))
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Cupón inválido o expirado."))
                except requests.RequestException:
                    st.error("Error de conexión.")

        with tab_pago:
            st.markdown("### Canales Oficiales de Recepción de Fondos")
            st.markdown("- **Pago Móvil (Venezuela):** Banco BNC o Mercantil.")
            st.markdown("- **Binance Pay:** USDT.")
            st.markdown("- **PayPal.**")
            st.info("Envía tu comprobante con el número de referencia a través del Buzón de Soporte seleccionando la categoría 'Duda de facturación/plan'.")

    # 5. PANEL DE ADMINISTRADOR (EXCLUSIVO JUAN CARLOS)
    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel Maestro de Gestión")
        
        tab_metrics, tab_gen_cup = st.tabs(["Auditoría de Usuarios", "Emisión de Cupones"])

        with tab_metrics:
            try:
                res = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth)
                if res.status_code == 200:
                    data = res.json()
                    m = data.get("metricas", {})
                    c1, c2 = st.columns(2)
                    c1.metric("Total Usuarios Registrados", m.get("total_registrados", 0))
                    c2.metric("Nuevos en últimas 24h", m.get("registros_ultimas_24h", 0))
                    
                    st.markdown("#### Lista de Miembros")
                    st.dataframe(data.get("usuarios", []))
            except requests.RequestException:
                st.error("Error al sincronizar con el panel de administración.")

        with tab_gen_cup:
            tipo_cup = st.selectbox("Selecciona Color / Tipo de Cupón:", ["verde", "azul", "rojo", "morado"])
            if st.button("Generar Cupón de Acceso"):
                try:
                    res = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": tipo_cup})
                    if res.status_code == 200:
                        d = res.json()
                        st.success(f"Código: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Días: {d.get('duracion_dias')} | Validez: {d.get('validez_minutos')} min.")
                    else:
                        st.error(res.json().get("detail", "Error al generar cupón."))
                except requests.RequestException:
                    st.error("Error al conectar con la API.")
