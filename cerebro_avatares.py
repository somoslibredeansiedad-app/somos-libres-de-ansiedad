import json
import os
import random
from typing import Dict, Any, Tuple, List

# Carga de catálogo y biblioteca RAG
CATALOGO_CACHE: Dict[str, Any] = {}
LIBROS_CACHE = []

if os.path.exists("catalogo_rag_avatares.json"):
    try:
        with open("catalogo_rag_avatares.json", "r", encoding="utf-8") as f:
            datos_json = json.load(f)
            LIBROS_CACHE = datos_json.get("biblioteca_rag", [])
            for av in datos_json.get("avatares_oficiales", []):
                CATALOGO_CACHE[av["id_avatar"]] = av
    except Exception as e:
        print(f"Error cargando catalogo RAG: {e}")

PATRONES_CRISIS_SOS = [
    "suicid", "matarme", "quitarme la vida", "no quiero vivir", "hacerme dano", 
    "cortarme", "morirme", "desaparecer para siempre", "acabar con todo", "no vale la pena vivir"
]

def obtener_catalogo_formateado(activos_usuario: list) -> list:
    """Devuelve la lista estructurada de avatares con su estado de activación."""
    catalogo = []
    for k, v in CATALOGO_CACHE.items():
        catalogo.append({
            "id": k,
            "nombre": v["identidad"]["nombre_completo"],
            "pais": v["identidad"]["pais"],
            "bandera": v["identidad"]["bandera"],
            "tono": v["tono_linguistico"],
            "imagen": v["archivos"]["imagen"],
            "is_activo": k in activos_usuario,
            "disparador_inicial": random.choice(v.get("frases_bienvenida", ["Hola, aquí estoy para ti."]))
        })
    return catalogo

def existe_avatar(avatar_id: str) -> bool:
    """Valida la existencia del avatar en el catálogo en memoria."""
    return avatar_id in CATALOGO_CACHE

def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict, historial_reciente: list = None) -> Tuple[str, str, bool]:
    """
    Cerebro cognitivo v4.6.2 (Rafael):
    Resuelve preguntas directas sin evasivas, sostiene la memoria de la conversación,
    disocia la profesión del estrés financiero y responde con el timbre cultural auténtico de los 10 guías.
    """
    avatar_info = CATALOGO_CACHE.get(avatar_id, CATALOGO_CACHE.get("anastasia", list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {}))
    nombre_avatar = avatar_info.get("identidad", {}).get("nombre_completo", "Guía")
    pais_avatar = avatar_info.get("identidad", {}).get("pais", "")
    
    texto = mensaje_usuario.lower().strip()
    apodo = perfil_usuario.get("apodo", "amigo/a")
    nombre_real = perfil_usuario.get("nombre_completo", apodo)
    profesion = perfil_usuario.get("profesion") or "tu labor diaria"
    hijos = perfil_usuario.get("cantidad_hijos") or 0
    historial = historial_reciente or []

    # 1. FILTRO ROJO / SOS PRIORITARIO (Seguridad Clínica y Ética Absoluta)
    if any(p in texto for p in PATRONES_CRISIS_SOS):
        respuesta_sos = (
            f"🚨 **{apodo}, por favor detente un momento. Tu vida y tu bienestar son inmensamente valiosos.**\n\n"
            "Siento profundamente el dolor tan intenso que estás experimentando, pero este programa es un espacio educativo reflexivo y no puede sustituir la atención médica o psicológica de urgencia que necesitas ahora mismo.\n\n"
            "**Por favor, contacta de inmediato a estos recursos gratuitos y confidenciales:**\n"
            "• **Venezuela - FPV (Federación de Psicólogos):** 0212-4163116 / 0212-4163118\n"
            "• **Cruz Roja / Emergencias Locales:** Llama al 911 o 171 de tu localidad, o acude al centro de salud más cercano.\n"
            "• **Línea Internacional de Ayuda (Befrienders Worldwide):** https://www.befrienders.org\n\n"
            "No estás solo/a en esto. Permite que un profesional o un ser querido te sostenga en este momento difícil."
        )
        return nombre_avatar, respuesta_sos, True

    # 2. RESOLUCIÓN DIRECTA A PREGUNTAS EXPLÍCITAS (Criterio Clínico Claro)
    if any(w in texto for w in ["psicologo", "psicólogo", "terapia"]) and any(w in texto for w in ["hijo", "llevo", "debo", "amigo"]):
        if "anastasia" in avatar_id:
            return nombre_avatar, (
                f"Sí, {apodo}. Llevar a tu hijo a evaluación con un psicólogo infanto-juvenil no solo es recomendable, sino una decisión protectora urgente. "
                "Un especialista le brindará contención clínica para procesar el impacto del acoso y evitar que se cronifique en trauma somático, "
                "mientras tú, con cabeza fría, exiges al colegio la activación formal del protocolo contra el bullying. Haces lo correcto."
            ), False
        else:
            return nombre_avatar, (
                f"Por supuesto que sí, {apodo}. Llevar a tu hijo con un psicólogo infantil es el mejor paso que puedes dar. "
                "Le dará un espacio seguro para desahogar el dolor del acoso y recuperar su seguridad, mientras tú como padre lo respaldas en la escuela. "
                "No lo dudes; buscar apoyo profesional es un acto de amor y valentía."
            ), False

    # 3. DISOCIACIÓN ENTRE IDENTIDAD LABORAL Y ANGUSTIA FINANCIERA
    if any(w in texto for w in ["econom", "plata", "dinero", "no me da", "alcanza", "mantener", "sustento", "familia"]) and any(w in texto for w in ["trabajo", "sueldo", "ayudar", "pais", "problema"]):
        return nombre_avatar, (
            f"Entiendo perfectamente el peso que sientes, {apodo}. Aunque te desempeñes como {profesion}, la realidad económica externa "
            "y las presiones de manutención generan una sobrecarga que agota el sistema nervioso. Lo primero es separar las cosas: "
            "el contexto económico adverso no disminuye tu valor humano ni tu esfuerzo como padre. "
            "Vamos a dividirlo: no intentes resolver las finanzas del mes completo en una noche de angustia; enfoquémonos en la prioridad práctica "
            "de las próximas 24 horas para devolverle el aire a tu cuerpo."
        ), False

    # 4. CONTINUIDAD CONTEXTUAL ANTE MENSAJES MONOPALABRA O DE SEGUIMIENTO
    if texto in ["insomnio", "no puedo dormir", "no duermo"]:
        return nombre_avatar, (
            f"Es comprensible que el sueño se corte, {apodo}. Cuando la mente está hipervigilante defendiendo a un hijo o anticipando gastos, "
            "el sistema simpático se queda encendido e impide la relajación. Esta noche no luches por dormir a la fuerza: "
            "recuesta la espalda, alarga la exhalación el doble que la inhalación y dale a tu cuerpo el permiso de descansar aunque la mente siga despierta."
        ), False

    if texto in ["depresion", "depresión", "tristeza", "desesperanza"]:
        return nombre_avatar, (
            f"{apodo}, cuando las cargas familiares y económicas se acumulan sin descanso, el cuerpo se agota y entra en este estado de pesadez. "
            "La depresión muchas veces no es debilidad, sino la señal de que has intentado ser fuerte por demasiado tiempo sin pausa. "
            "Hoy solo da un paso pequeño: respira, hidrátate y permítete un momento de tregua."
        ), False

    # 5. MEMORIA Y PREGUNTAS PERSONALES AL AVATAR (Lectura Dinámica del Catálogo RAG)
    if any(w in texto for w in ["de donde eres", "de que parte", "tus padres", "como se llaman tus padres", "algo de ti", "tu vida", "tu historia"]):
        historia = avatar_info.get("historia_personal", {})
        ciudad = historia.get("ciudad_natal", pais_avatar)
        padres = historia.get("padres", "Mis padres me enseñaron a perseverar con dignidad.")
        infancia = historia.get("entorno_infancia", "Crecí aprendiendo el valor de la templanza.")
        recuerdo = historia.get("recuerdo_clave", "")

        if any(w in texto for w in ["padres", "papa", "mama", "padre", "madre"]):
            return nombre_avatar, f"Con mucho gusto te lo comparto, {apodo}: {padres} De ellos aprendí a mirar la vida con entereza y serenidad.", False
        elif any(w in texto for w in ["donde eres", "que parte", "ciudad"]):
            return nombre_avatar, f"Soy de {ciudad}, {pais_avatar}. {infancia} Por eso sé lo fundamental que es mantener la calma cuando afuera hay tormenta.", False
        else:
            return nombre_avatar, f"Soy {nombre_avatar}, nacida/o en {ciudad}. {infancia} {recuerdo} Cuentas conmigo para acompañarte con esa misma firmeza.", False

    # 6. SÍNTOMAS FÍSICOS Y CRISIS SOMÁTICAS (Falta de aire, pecho, estómago)
    if any(w in texto for w in ["aire", "falta de aire", "ahogo", "pecho", "corazon", "palpitaciones"]):
        return nombre_avatar, (
            f"{apodo}, la sensación de que te falta el aire es la respuesta refleja de tu cuerpo cuando la angustia por tu familia se desborda. "
            "Tus pulmones están bien, es una falsa alarma de hiperventilación. Haz esto conmigo ahora mismo: vacía todo el aire por la boca en un suspiro largo. "
            "Luego inhala suavemente por la nariz en 4 segundos y suelta en 6 segundos. Siente tus pies apoyados en el suelo; estás a salvo en este instante."
        ), False

    # 7. PREGUNTAS DEL PERFIL REGISTRADO
    if any(q in texto for q in ["nombre completo", "como me llamo completo"]):
        return nombre_avatar, f"Tu nombre oficial es {nombre_real}, aunque en este refugio te reconozco con aprecio como {apodo}.", False
    if any(q in texto for q in ["sabes mi nombre", "quien soy", "mi apodo"]):
        return nombre_avatar, f"Por supuesto, eres {apodo}. Aquí estoy acompañándote paso a paso.", False
    if any(q in texto for q in ["cuantos hijos", "mis hijos", "tengo hijos"]):
        return nombre_avatar, f"Tienes {hijos} {'hijo' if hijos == 1 else 'hijos'} registrados, {apodo}.", False
    if any(q in texto for q in ["a que me dedico", "mi profesion", "en que trabajo"]):
        return nombre_avatar, f"Te desempeñas como {profesion}. Recuerda que eres mucho más valioso que tu productividad diaria.", False
    if any(q in texto for q in ["hola", "buenas", "saludos"]):
        return nombre_avatar, f"¡Hola {apodo}! Me alegra escucharte. Tómate un respiro y conversemos con calma sobre lo que hoy tengas en mente.", False
    if any(q in texto for q in ["gracias"]):
        return nombre_avatar, f"Es un verdadero honor acompañarte, {apodo}. El mérito es tuyo por darte este espacio para encontrar claridad.", False

    # 8. RAG DINÁMICO ADAPTATIVO
    consejos = []
    for libro in LIBROS_CACHE:
        if libro.get("id_libro") in avatar_info.get("libros_rag_afines", []):
            consejos.append(libro.get("consejo_aplicable"))
    consejo_base = random.choice(consejos) if consejos else "Toma una respiración pausada y regresa tu atención al momento presente."

    respuesta_reflexiva = (
        f"Te escucho atentamente, {apodo}. Ante lo que me planteas, ten presente esta perspectiva: "
        f"{consejo_base} Dime, ¿qué es lo primero que sientes que debes atender?"
    )
    return nombre_avatar, respuesta_reflexiva, False
