import streamlit as st
import requests

# Configuración de la página
st.set_page_config(
    page_title="Somos Libres de Ansiedad",
    page_icon="🌿",
    layout="centered"
)

# URL del backend en la nube (Render)
API_URL = "https://somos-libres-de-ansiedad-1.onrender.com/api"

st.title("🌿 Somos Libres de Ansiedad")
st.markdown("Tu refugio seguro, anónimo y guiado por expertos.")

# Menú lateral de navegación
menu = st.sidebar.selectbox("Navegación", ["Acceso / Registro", "Chat con Avatar", "Muro de Los Lamentos", "Panel de Administración"])

if menu == "Acceso / Registro":
    st.subheader("Bienvenido a tu Espacio Seguro")
    
    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
        correo_log = st.text_input("Correo Electrónico", key="log_correo")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        if st.button("Ingresar"):
            try:
                res = requests.post(f"{API_URL}/auth/login", json={"correo": correo_log, "password": pass_log})
                if res.status_code == 200:
                    data = res.json()
                    st.success(data["message"])
                    st.info(f"💡 **Pensamiento del día:** {data['bienvenida_avatar']}")
                    st.session_state["logged_in"] = True
                    st.session_state["user_plan"] = data["plan_actual"]
                else:
                    st.error("Credenciales inválidas.")
            except Exception as e:
                st.error(f"No se pudo conectar con el servidor: {e}")

    with tab_register:
        nombre = st.text_input("Nombre Completo (*)")
        apodo = st.text_input("Apodo (*)")
        correo_reg = st.text_input("Correo Electrónico (*)", key="reg_correo")
        pass_reg = st.text_input("Contraseña (*)", type="password", key="reg_pass")
        edad = st.number_input("Edad (*)", min_value=12, max_value=100, value=25)
        
        st.markdown("---")
        st.markdown("*Campos opcionales (¿?): Esta información se utiliza exclusivamente para personalizar tu experiencia en la plataforma y no condiciona el acceso al servicio.*")
        sexo = st.text_input("Sexo (Opcional)")
        profesion = st.text_input(" Profesión (Opcional)")
        orientacion = st.text_input("Orientación sexual (Opcional)")
        sentimental = st.text_input("Situación sentimental (Opcional)")
        hijos = st.number_input("Cantidad de hijos", min_value=0, value=0)
        referido = st.text_input("Código de Referido (Opcional)")
        
        st.markdown("---")
        terms = st.checkbox("«He leído y acepto los Términos de Servicio y la Política de Privacidad.» (*)")
        disclaimer = st.checkbox("«Acepto que este programa es una herramienta de apoyo informativo/educativo y no un servicio médico o terapéutico.» (*)")
        
        if st.button("Registrarme"):
            if not terms or not disclaimer:
                st.warning("Debes aceptar las casillas obligatorias exigidas por la auditoría legal.")
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

elif menu == "Chat con Avatar":
    st.subheader("💬 Sala de Apoyo Emocional")
    plan_usuario = st.session_state.get("user_plan", "gratis")
    st.caption(f"Plan activo: {plan_usuario.upper()}")
    
    mensaje_usuario = st.text_area("¿Qué pasa por tu mente en este momento?")
    
    if st.button("Enviar mensaje"):
        if mensaje_usuario.strip():
            try:
                res = requests.post(f"{API_URL}/chat", json={
                    "user_id": "user_demo",
                    "message": mensaje_usuario,
                    "plan_nivel": plan_usuario
                })
                if res.status_code == 200:
                    data = res.json()
                    if data["status"] == "crisis detected":
                        st.error(data["response"])
                    else:
                        st.success(data["response"])
            except Exception as e:
                st.error(f"Error al conectar con el Avatar: {e}")
        else:
            st.warning("Por favor escribe un mensaje.")

elif menu == "Muro de Los Lamentos":
    st.subheader("🛡️ El Muro de Los Lamentos")
    st.markdown("Un espacio seguro para compartir lo que cargas y encontrar lectura afín según tu plan.")
    st.info("Próximamente disponible en esta vista interactiva.")

elif menu == "Panel de Administración":
    st.subheader("🔒 Acceso de Superusuario (Juan Carlos)")
    admin_correo = st.text_input("Correo Oficial", value="somos.libredeansiedad@gmail.com")
    admin_nombre = st.text_input("Nombre del Dueño", value="Juan Carlos")
    
    if st.button("Acceder al Panel Maestro"):
        try:
            res = requests.post(f"{API_URL}/admin/login", json={"correo": admin_correo, "nombre_dueno": admin_nombre})
            if res.status_code == 200:
                st.success(res.json()["mensaje"])
                st.markdown("### 📊 Alertas y Actividad Reciente")
                st.write("Modo invisible activado con éxito.")
            else:
                st.error("Credenciales maestras inválidas.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")
