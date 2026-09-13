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
        st.markdown(f"<div style='width:{ancho}px; height:{ancho}px; background:#C2EAD9; display:flex; align-items:center; justify-content:center; border-radius:8px;'>👤</div>", unsafe_allow_html=True)

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
        if st.button("Ingresar a mi espacio"):
            try:
                res = requests.post(f"{API_URL}/auth/login", json={"correo": correo_log.strip(), "password": pass_log})
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
                    st.error("Credenciales incorrectas.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)
        codigo_ref = st.text_input("Código de Referido (opcional)", value=ref_url)
        
        t1 = st.checkbox("Acepto Términos de Servicio y Privacidad. (*)")
        t2 = st.checkbox("Acepto que este programa es una herramienta educativa no médica. (*)")
        if st.button("Registrarme"):
            if not t1 or not t2 or not nombre or not apodo or not correo_reg or not pass_reg:
                st.warning("Completa los campos obligatorios marcados con (*).")
            else:
                try:
                    payload = {"nombre_completo": nombre.strip(), "apodo": apodo.strip(), "correo": correo_reg.strip(), "password": pass_reg, "edad": int(edad), "codigo_referido": codigo_ref.strip() or None, "terms_accepted": t1, "disclaimer_accepted": t2}
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
                    if res.status_code == 201:
                        st.success("¡Registro completado! Inicia sesión.")
                    else:
                        st.error(res.json().get("detail", "Error al registrarse."))
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

# --- PANTALLA PRINCIPAL ---
else:
    headers_auth = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Banner dinámico
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

    opciones = ["Seleccionar Avatar", "Chat con Avatar", "Comunidad y Red de Apoyo", "Planes y Suscripción"]
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
                            st.success(f"Has seleccionado a {av.get('nombre')}. Pasa al chat.")
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Límite de avatares alcanzado."))
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
                st.session_state.messages = [{"role": "assistant", "content": av.get("disparador_inicial", "Hola, ¿en qué puedo ayudarte hoy?")}]

            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])

            # Opciones de audio: en vivo o archivo subido
            with st.expander("🎙️ Opciones de Nota de Voz"):
                audio_mic = st.audio_input("Grabar en vivo:")
                audio_file = st.file_uploader("O adjuntar audio (.wav, .mp3):", type=["wav", "mp3"])

            if user_text := st.chat_input("Escribe lo que sientes..."):
                st.session_state.messages.append({"role": "user", "content": user_text})
                with st.chat_message("user"):
                    st.markdown(user_text)

                try:
                    payload = {"avatar_id": av.get("id"), "message": user_text, "is_audio": False, "audio_duracion_segundos": 0}
                    r = requests.post(f"{API_URL}/chat", headers=headers_auth, json=payload)
                    if r.status_code == 200:
                        ans = r.json().get("respuesta")
                        chats_rest = r.json().get("chats_restantes")
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                        with st.chat_message("assistant"):
                            st.markdown(ans)
                            st.caption(f"Mensajes restantes: {chats_rest}")
                    else:
                        st.error(r.json().get("detail", "Error al procesar mensaje."))
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # 3. COMUNIDAD Y RED DE APOYO
    elif menu == "Comunidad y Red de Apoyo":
        tab_perfiles, tab_muro, tab_reuniones, tab_buzon = st.tabs(["Perfiles Comunitarios", "Muro de Desahogo", "Reuniones", "Buzón"])

        with tab_perfiles:
            st.markdown("### 👥 Miembros de la Comunidad")
            try:
                res_perf = requests.get(f"{API_URL}/comunidad/perfiles", headers=headers_auth)
                if res_perf.status_code == 200:
                    for p in res_perf.json().get("perfiles", []):
                        with st.expander(f"👤 {p.get('apodo')} ({p.get('edad')} años) - {p.get('profesion')}"):
                            st.write(p.get("biografia"))
                            msg_dm = st.text_input("Enviar mensaje directo:", key=f"dm_txt_{p.get('id')}")
                            if st.button("Enviar", key=f"btn_dm_{p.get('id')}"):
                                r_dm = requests.post(f"{API_URL}/comunidad/dm", headers=headers_auth, json={"destinatario_id": p.get("id"), "contenido": msg_dm})
                                if r_dm.status_code == 200:
                                    st.success("Mensaje privado enviado.")
                                else:
                                    st.error(r_dm.json().get("detail", "Límite diario alcanzado."))
            except Exception as e:
                st.error(f"Error: {e}")

        with tab_muro:
            st.markdown("### 💬 Muro de Desahogo")
            if st.session_state.user_plan != "gratis":
                post_txt = st.text_area("Comparte una reflexión:")
                anon = st.checkbox("Publicar como anónimo")
                if st.button("Publicar en Muro"):
                    requests.post(f"{API_URL}/muro", headers=headers_auth, json={"contenido": post_txt, "is_anonimo": anon})
                    st.rerun()
            else:
                st.caption("ℹ️ Plan Gratis en modo lectura. Pasa a Comunicador para publicar.")

            res_muro = requests.get(f"{API_URL}/muro", headers=headers_auth)
            if res_muro.status_code == 200:
                for post in res_muro.json().get("posts", []):
                    st.info(f"**{post.get('autor')}**: {post.get('contenido')}")

        with tab_reuniones:
            st.markdown("### 👥 Reunidos para Compartir")
            st.info("Salas sincrónicas para apoyo mutuo entre usuarios según los límites de tu plan.")

        with tab_buzon:
            st.markdown("### 📬 Buzón y Tickets")
            cat = st.selectbox("Categoría:", ["Falla técnica", "Duda de facturación/plan", "Sugerencia", "Consulta general"])
            asu = st.text_input("Asunto:")
            det = st.text_area("Mensaje:")
            if st.button("Enviar Ticket"):
                requests.post(f"{API_URL}/buzon/ticket", headers=headers_auth, json={"categoria": cat, "asunto": asu, "mensaje": det})
                st.success("Ticket enviado.")

    # 4. PLANES Y SUSCRIPCIÓN
    elif menu == "Planes y Suscripción":
        tab_p, tab_c, tab_m = st.tabs(["Planes Oficiales", "Canjear Cupón", "Métodos de Pago"])
        with tab_p:
            c1, c2, c3 = st.columns(3)
            c1.markdown("### 🌿 Gratis\n- $0\n- 1 Avatar\n- 25 chats/sem")
            c2.markdown("### ⭐ Comunicador\n- $5 USD / 30 días\n- 3 Avatares\n- 100 chats/sem")
            c3.markdown("### 👑 Amigo de Todos\n- $10 USD / 40 días\n- 10 Avatares\n- Ilimitado")

        with tab_c:
            cod = st.text_input("Código de Cupón (Ej: SL-VERDE-1234):")
            if st.button("Canjear"):
                r = requests.post(f"{API_URL}/cupones/canjear", headers=headers_auth, json={"codigo": cod.strip()})
                if r.status_code == 200:
                    st.success(r.json().get("message"))
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Cupón inválido."))

        with tab_m:
            st.markdown("### Datos para Recepción de Pagos")
            st.markdown("""
            * **Pago Móvil (Venezuela):**
              * Banco: Banco Nacional de Crédito (BNC) / Mercantil
              * Teléfono: 0414-XXXXXXX
              * C.I.: V-XXXXXXXX
            * **Binance Pay:**
              * Pay ID: 123456789
              * Moneda: USDT
            * **PayPal:**
              * Correo: somos.libredeansiedad@gmail.com
            """)
            st.caption("Luego de pagar, envía el capture y número de referencia por el Buzón de Soporte.")

    # 5. PANEL ADMIN (JUAN CARLOS)
    elif menu == "Panel de Administración" and st.session_state.user_role == "admin":
        st.subheader("🔒 Panel Maestro (Admin - Juan Carlos)")
        st.markdown("### Emisión de Cupones (Válidos por 30 minutos)")
        color = st.selectbox("Color del Cupón:", ["verde", "azul", "rojo", "morado"])
        if st.button("Generar Código"):
            r = requests.post(f"{API_URL}/admin/cupones", headers=headers_auth, json={"tipo": color})
            if r.status_code == 200:
                d = r.json()
                st.success(f"Código: `{d.get('codigo')}` | Plan: {d.get('tipo_plan')} | Días: {d.get('duracion_dias')}")
