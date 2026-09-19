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

st.set_page_config(page_title="Somos Libres de Ansiedad", page_icon="🌿", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {THEME_COLORS['background']}; color: {THEME_COLORS['text_primary']}; }}
    h1, h2, h3, h4, h5, h6, p, label, span {{ color: {THEME_COLORS['text_primary']} !important; }}
    
    /* Sidebar con colores institucionales claros */
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
        padding: 18px;
        border-radius: 12px;
        color: #1E4D3B;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        margin-bottom: 18px;
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
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "https://somos-libres-de-ansiedad-1.onrender.com/api")

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

ref_url = st.query_params.get("ref", "")

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
        
        # Validación de 2FA solo para el Administrador Juan Carlos
        preg_secreta = None
        if correo_log.strip().lower() == "somos.libredeansiedad@gmail.com":
            st.info("🔒 Cuenta Maestra Detectada: Se requiere confirmación de seguridad.")
            preg_secreta = st.text_input("Pregunta secreta: ¿Cuál es la palabra clave de resguardo?", type="password", key="log_admin_sec")

        if st.button("Ingresar a mi espacio"):
            try:
                payload_log = {"correo": correo_log.strip(), "password": pass_log}
                if preg_secreta:
                    payload_log["pregunta_secreta"] = preg_secreta.strip()

                res = requests.post(f"{API_URL}/auth/login", json=payload_log)
                if res.status_code == 200:
                    d = res.json()
                    st.session_state.authenticated = True
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
        t1 = st.checkbox("Acepto Términos de Servicio y Privacidad. (*)")
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
                        st.success("¡Registro completado! Ya puedes Iniciar Sesión.")
                    else:
                        st.error(res.json().get("detail", "Error al registrarse."))
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

# --- PANTALLA PRINCIPAL ---
else:
    headers_auth = {"Authorization": f"Bearer {st.session_state.token}"}
    
    if st.session_state.avatar_activo:
        banner_msg = f"Tu guía activo es {st.session_state.avatar_activo.get('nombre')}. Puedes consultar en 'Chat con Avatar'."
    else:
        banner_msg = "Selecciona tu avatar guía para iniciar tu acompañamiento reflexivo."

    st.markdown(f"""
        <div class="welcome-banner">
            <h2>🌟 Espacio Activo de {st.session_state.user_apodo}</h2>
            <p>{banner_msg}</p>
        </div>
    """, unsafe_allow_html=True)

    opciones = ["Seleccionar Avatar", "Chat con Avatar", "Red Social y Comunidad", "Planes y Suscripción"]
    if st.session_state.user_role == "admin":
        opciones.append("Panel de Administración")

    menu = st.sidebar.selectbox("Navegación", opciones)
    st.sidebar.markdown(f"**Plan:** <span style='color:#4E8A72; font-weight:bold;'>{st.session_state.user_plan.upper()}</span>", unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.avatar_activo = None
        st.session_state.token = None
        st.rerun()

    # 1. SELECCIONAR AVATAR
    if menu == "Seleccionar Avatar":
        st.subheader("🛠️ Catálogo Oficial de Guías")
        if st.session_state.user_plan == "gratis":
            st.info("ℹ️ Tu **Plan Gratis** te permite vincular **1 Avatar activo** y disfrutar de **25 chats reflexivos semanales**.")

        try:
            res = requests.get(f"{API_URL}/avatares/catalogo", headers=headers_auth)
            avatares = res.json().get("avatares", []) if res.status_code == 200 else []
        except Exception:
            avatares = []

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
                            st.success(f"Has seleccionado a {av.get('nombre')}. Ve a la pestaña 'Chat con Avatar'.")
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Límite de avatares alcanzado para tu plan."))
                    except Exception as e:
                        st.error(f"Error: {e}")

    # 2. CHAT CON AVATAR
    elif menu == "Chat con Avatar":
        if not st.session_state.avatar_activo:
            st.warning("Selecciona un guía primero en la pestaña 'Seleccionar Avatar'.")
        else:
            av = st.session_state.avatar_activo
            col_f, col_t = st.columns([1, 4])
            with col_f:
                mostrar_imagen(av, ancho=80)
            with col_t:
                st.subheader(f"Conversando con {av.get('nombre')}")
                st.caption(f"{av.get('bandera')} {av.get('tono')}")

            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": av.get("disparador_inicial", "Hola, estoy aquí para acompañarte.")}]

            # Render de mensajes con ícono sereno de planta o avatar, nunca un robot
            for m in st.session_state.messages:
                avatar_icono = "🌿" if m["role"] == "assistant" else "👤"
                with st.chat_message(m["role"], avatar=avatar_icono):
                    st.markdown(m["content"])

            # Entrada integrada de voz y texto
            col_audio, col_arch = st.columns(2)
            with col_audio:
                audio_mic = st.audio_input("🎙️ Grabar nota de voz corta:")
            with col_arch:
                audio_file = st.file_uploader("📁 O adjuntar archivo de audio:", type=["wav", "mp3"])

            if audio_mic or audio_file:
                st.caption("Audio listo para ser procesado.")

            if user_text := st.chat_input("Escribe tu pensamiento o inquietud..."):
                st.session_state.messages.append({"role": "user", "content": user_text})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_text)

                try:
                    payload = {"avatar_id": av.get("id"), "message": user_text, "is_audio": False, "audio_duracion_segundos": 0}
                    r = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload)
                    if r.status_code == 200:
                        ans = r.json().get("respuesta")
                        chats_rest = r.json().get("chats_restantes")
                        st.session_state.messages.append({"role": "assistant", "content": ans})
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
                    st.write(f"**Nombre:** {mi_p.get('nombre_completo')} | **Apodo:** {mi_p.get('apodo')}")
                    st.write(f"**Edad:** {mi_p.get('edad')} años | **Sexo:** {mi_p.get('sexo') or 'No especificado'}")
                    st.write(f"**Código de Referido:** `{mi_p.get('codigo_referido')}`")
                    
                    st.markdown("---")
                    st.markdown("#### Actualizar Datos de Perfil")
                    nueva_prof = st.text_input("Profesión u Oficio:", value=mi_p.get("profesion") or "")
                    nuevo_estado = st.selectbox("Situación Sentimental:", ["Prefiero no decir", "Soltero/a", "En pareja / Casado/a", "Divorciado/a", "Viudo/a"], index=0)
                    nuevos_hijos = st.number_input("Hijos:", min_value=0, max_value=10, value=mi_p.get("cantidad_hijos") or 0)
                    nueva_bio = st.text_area("Biografía / Pensamiento de Serenidad:", value=mi_p.get("biografia") or "")
                    
                    if st.button("Guardar Cambios de Perfil"):
                        r_up = requests.put(f"{API_URL}/usuario/mi-perfil", headers=headers_auth, json={
                            "profesion": nueva_prof,
                            "situacion_sentimental": None if nuevo_estado == "Prefiero no decir" else nuevo_estado,
                            "cantidad_hijos": int(nuevos_hijos),
                            "biografia": nueva_bio
                        })
                        if r_up.status_code == 200:
                            st.success("Perfil actualizado con éxito.")
                            st.rerun()
            except Exception as e:
                st.error(f"Error cargando perfil: {e}")

        with tab_amigos:
            st.markdown("### 👥 Miembros de la Comunidad y Amistades")
            st.caption("Haz amigos para poder conversar sin límite de mensajes directos, incluso en el Plan Gratis.")
            try:
                res_perf = requests.get(f"{API_URL}/comunidad/perfiles", headers=headers_auth)
                if res_perf.status_code == 200:
                    for p in res_perf.json().get("perfiles", []):
                        with st.expander(f"👤 {p.get('apodo')} ({p.get('edad')} años) - {p.get('profesion')}"):
                            st.write(f"**Biografía:** {p.get('biografia')}")
                            st.caption(f"Estado sentimental: {p.get('situacion_sentimental')}")
                            
                            # Estado de la amistad
                            estatus_a = p.get("amistad_estatus")
                            if estatus_a == "ninguna":
                                if st.button(f"Enviar Solicitud de Amistad", key=f"sol_{p.get('id')}"):
                                    requests.post(f"{API_URL}/comunidad/amistad/solicitar", headers=headers_auth, json={"usuario_id": p.get("id")})
                                    st.success("Solicitud enviada.")
                                    st.rerun()
                            elif estatus_a == "pendiente":
                                if p.get("soy_solicitante"):
                                    st.info("⏳ Solicitud enviada (Esperando respuesta).")
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
                                st.success("🤝 ¡Son Amigos! (Chat ilimitado activo)")

                            # Módulo de Chat Directo
                            msg_dm = st.text_input("Mensaje privado:", key=f"dm_input_{p.get('id')}")
                            if st.button("Enviar Mensaje", key=f"btn_send_dm_{p.get('id')}"):
                                r_dm = requests.post(f"{API_URL}/comunidad/dm", headers=headers_auth, json={"destinatario_id": p.get("id"), "contenido": msg_dm})
                                if r_dm.status_code == 200:
                                    st.success("Mensaje enviado.")
                                else:
                                    st.error(r_dm.json().get("detail", "Límite de mensajes alcanzado."))

                            # Ver historial privado
                            if st.checkbox("Ver conversación", key=f"chk_conv_{p.get('id')}"):
                                r_c = requests.get(f"{API_URL}/comunidad/conversacion/{p.get('id')}", headers=headers_auth)
                                if r_c.status_code == 200:
                                    for cm in r_c.json().get("mensajes", []):
                                        remitente = "Tú" if cm.get("remitente_id") != p.get("id") else p.get("apodo")
                                        st.write(f"**{remitente}:** {cm.get('contenido')}")
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_muro:
            st.markdown("### 💬 Muro de Desahogo y Esperanza")
            if st.session_state.user_plan != "gratis":
                post_txt = st.text_area("Comparte una reflexión con la comunidad:")
                anon = st.checkbox("Publicar de forma anónima")
                if st.button("Publicar en el Muro"):
                    requests.post(f"{API_URL}/muro", headers=headers_auth, json={"contenido": post_txt, "is_anonimo": anon})
                    st.success("Publicación compartida.")
                    st.rerun()
            else:
                st.caption("ℹ️ El Plan Gratis permite leer los testimonios del muro. Pasa a Plan Comunicador para publicar tus reflexiones.")

            res_muro = requests.get(f"{API_URL}/muro", headers=headers_auth)
            if res_muro.status_code == 200:
                for post in res_muro.json().get("posts", []):
                    st.info(f"**{post.get('autor')}**: {post.get('contenido')}")

        with tab_reuniones:
            st.markdown("### 👥 Reunidos para Compartir (Salas de Círculos)")
            if st.session_state.user_plan == "gratis":
                st.warning("🔒 Para adquirir y moderar tu propia sala sincrónica con tus amigos debes contar con el Plan Comunicador o Amigo de Todos.")
            else:
                st.success("✨ Tienes acceso a salas sincrónicas para conversar en grupo y convocar a tus amigos.")

        with tab_buzon:
            st.markdown("### 📬 Buzón y Tickets de Soporte")
            cat = st.selectbox("Categoría:", ["Falla técnica", "Duda de facturación/plan", "Sugerencia", "Consulta general"])
            asu = st.text_input("Asunto:")
            det = st.text_area("Detalla tu consulta:")
            if st.button("Enviar al Administrador"):
                requests.post(f"{API_URL}/buzon/ticket", headers=headers_auth, json={"categoria": cat, "asunto": asu, "mensaje": det})
                st.success("Ticket registrado correctamente.")

    # 4. PLANES Y SUSCRIPCIÓN (PAGOS SEGUROS VÍA CHAT CON ADMIN)
    elif menu == "Planes y Suscripción":
        tab_p, tab_c, tab_chat_pago = st.tabs(["Planes Oficiales", "Canjear Cupón", "Coordinar Pago con Administrador"])
        
        with tab_p:
            c1, c2, c3 = st.columns(3)
            c1.markdown("### 🌿 Gratis\n- $0\n- 1 Avatar activo\n- 25 chats semanales\n- 3 audios (10s)")
            c2.markdown("### ⭐ Comunicador\n- $5 USD / 30 días\n- 3 Avatares activos\n- 100 chats semanales\n- 10 audios (30s)\n- Salas y muro activo")
            c3.markdown("### 👑 Amigo de Todos\n- $10 USD / 40 días\n- 10 Avatares activos\n- Chats ilimitados\n- Audios ilimitados (60s)\n- Acceso total")

        with tab_c:
            cod = st.text_input("Introduce tu Código de Cupón (Ej: SL-VERDE-4821):")
            if st.button("Canjear Cupón"):
                r = requests.post(f"{API_URL}/cupones/canjear", headers=headers_auth, json={"codigo": cod.strip()})
                if r.status_code == 200:
                    st.success(r.json().get("message"))
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Cupón inexistente, expirado o previamente utilizado."))

        with tab_chat_pago:
            st.markdown("### 💬 Chat de Pago y Conciliación con el Administrador")
            st.caption("Por tu seguridad, no exponemos datos bancarios públicos. Solicita aquí las coordenadas del método de tu preferencia (Pago Móvil, Binance Pay o PayPal), envía tu número de comprobante y recibirás tu cupón de activación.")
            
            # Historial de conversación de pagos
            try:
                r_pchat = requests.get(f"{API_URL}/pagos/mis-mensajes", headers=headers_auth)
                if r_pchat.status_code == 200:
                    for mp in r_pchat.json().get("mensajes", []):
                        emisor = "Tú" if mp.get("emisor_rol") == "user" else "🌟 Administrador (Juan Carlos)"
                        st.markdown(f"**{emisor}:** {mp.get('mensaje')}")
            except Exception as e:
                st.error(f"Error cargando chat: {e}")

            st.markdown("---")
            mensaje_pago = st.text_area("Escribe tu consulta o envía tu número de referencia / comprobante:")
            if st.button("Enviar al Administrador"):
                if mensaje_pago.strip():
                    r_send = requests.post(f"{API_URL}/pagos/enviar-mensaje", headers=headers_auth, json={"mensaje": mensaje_pago.strip()})
                    if r_send.status_code == 200:
                        st.success("Mensaje enviado. El Administrador te responderá a la brevedad.")
                        st.rerun()

    # 5. PANEL ADMIN (JUAN CARLOS)
    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel Maestro (Admin - Juan Carlos)")
        
        tab_adm_cupones, tab_adm_pagos, tab_adm_metricas = st.tabs(["Generar Cupones", "Conciliación de Pagos", "Métricas Globales"])
        
        with tab_adm_cupones:
            st.markdown("### Emisión de Cupones de Activación (Válidos por 30 minutos)")
            color = st.selectbox("Tipo / Color del Cupón:", ["verde", "azul", "rojo", "morado"])
            if st.button("Generar Código de Cupón"):
                r = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": color})
                if r.status_code == 200:
                    d = r.json()
                    st.success(f"Código: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Duración: {d.get('duracion_dias')} días")

        with tab_adm_pagos:
            st.markdown("### Bandeja de Mensajes de Conciliación de Pagos")
            try:
                r_conv = requests.get(f"{API_URL}/admin/pagos/conversaciones", headers=headers_auth)
                if r_conv.status_code == 200:
                    usuarios_pago = r_conv.json().get("usuarios_con_pago", [])
                    if not usuarios_pago:
                        st.info("No hay solicitudes de pago pendientes.")
                    for up in usuarios_pago:
                        with st.expander(f"Usuario: {up.get('apodo')} ({up.get('correo')}) - Plan actual: {up.get('plan')}"):
                            # Ver mensajes de este usuario
                            r_usr_msg = requests.get(f"{API_URL}/pagos/mis-mensajes", headers=headers_auth) # Se cargan en contexto
                            resp_pago = st.text_area(f"Responder con datos de pago o código de cupón a {up.get('apodo')}:", key=f"resp_pago_{up.get('id')}")
                            if st.button("Enviar Respuesta y Datos", key=f"btn_pago_{up.get('id')}"):
                                requests.post(f"{API_URL}/admin/pagos/responder", headers=headers_auth, json={"mensaje": resp_pago, "para_usuario_id": up.get("id")})
                                st.success("Respuesta enviada al usuario.")
                                st.rerun()
            except Exception as e:
                st.error(f"Error cargando conciliaciones: {e}")

        with tab_adm_metricas:
            try:
                r_adm = requests.get(f"{API_URL}/admin/usuarios", headers=headers_auth)
                if r_adm.status_code == 200:
                    met = r_adm.json().get("metricas", {})
                    st.metric("Total Usuarios Registrados", met.get("total_registrados", 0))
                    st.metric("Registrados en las últimas 24 horas", met.get("registros_ultimas_24h", 0))
            except Exception as e:
                st.error(f"Error al obtener métricas: {e}")
