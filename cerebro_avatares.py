import json
import os
import random
from typing import Dict, Any, Tuple

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
    return avatar_id in CATALOGO_CACHE

def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict) -> Tuple[str, str, bool]:
    """
    Cerebro cognitivo: Evalúa la intención, estado somático, crisis SOS
    y contexto del usuario para responder con identidad cultural y RAG.
    Retorna: (nombre_avatar, respuesta, es_crisis)
    """
    avatar_info = CATALOGO_CACHE[avatar_id]
    nombre_avatar = avatar_info["identidad"]["nombre_completo"]
    pais_avatar = avatar_info["identidad"]["pais"]
    
    texto = mensaje_usuario.lower().strip()
    apodo = perfil_usuario.get("apodo", "amigo/a")
    nombre_real = perfil_usuario.get("nombre_completo", apodo)
    hijos = perfil_usuario.get("cantidad_hijos") or 0
    profesion = perfil_usuario.get("profesion") or "tu labor diaria"
    estado = perfil_usuario.get("situacion_sentimental") or "tu vida actual"
    biografia = perfil_usuario.get("biografia") or ""

    # 1. FILTRO ROJO / SOS PRIORITARIO
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

    # 2. PRIORIDADES SITUACIONALES DE DOLOR Y ANGUSTIA
    if any(w in texto for w in ["bulling", "bullying", "acoso", "se burlan", "pegan en el colegio"]):
        respuesta = (
            f"Hermano {apodo}, el acoso escolar hacia un hijo es una de las cosas que más golpea y angustia el corazón. "
            "Lo primero y más vital: abrázalo, hazle saber con certeza absoluta que él no tiene la culpa de nada y que estás a su lado. "
            "Pide de inmediato una reunión con la directiva escolar para exigir un protocolo claro de protección. "
            "Tu presencia firme y protectora es su mayor refugio hoy. Respira hondo, no estás solo para defenderlo."
        )
    elif any(w in texto for w in ["pecho", "dolor en el pecho", "me duele el pecho", "barriga", "estomago"]):
        respuesta = (
            f"{apodo}, cuando la mente se llena de tensión, el cuerpo es el primero en manifestarlo: el pecho se aprieta y el estómago se anuda. "
            "Pon una mano en tu pecho ahora mismo. Inhala despacio en 4 segundos y exhala en 6 segundos como si soplaras una vela. "
            "Si el dolor es punzante o persiste, ve a revisarte con un médico para tu total tranquilidad; pero si viene de la angustia, tu cuerpo solo te pide que pares el ruido mental un minuto."
        )
    elif any(w in texto for w in ["economico", "dinero", "alimentar", "deudas", "plata", "comer"]):
        respuesta = (
            f"Sé lo que pesa tener que llevar el sustento a casa y alimentar a la familia, {apodo}. "
            "Cuando los problemas económicos nos invaden, la mente salta al peor escenario futuro y nos paraliza. "
            "Vamos a dividirlo: no puedes resolver todo el mes hoy, enfócate únicamente en la acción práctica que puedes dar en las próximas 24 horas. Paso a paso."
        )
    
    # 3. TRASFONDO PERSONAL E HISTORIA DEL AVATAR
    elif any(w in texto for w in ["de donde eres", "que parte de cuba", "tus padres", "algo de ti", "tu vida"]):
        if "camilo" in avatar_id:
            respuesta = (
                f"¡Oye, con gusto te cuento, {apodo}! Nací y me crié en Santiago de Cuba, entre el calor de la gente, el sonido del son tradicional y el mar Caribe. "
                "Mis padres me enseñaron que ante la escasez y las tormentas, lo último que se pierde es la dignidad y la sonrisa para tenderle la mano al hermano. Por eso estoy aquí para ti."
            )
        else:
            respuesta = f"Soy {nombre_avatar}, vengo de {pais_avatar}. En mi tierra aprendí que la calma y la perseverancia son las herramientas más nobles para salir adelante."

    # 4. MEMORIA RELACIONAL DEL USUARIO
    elif any(q in texto for q in ["casado", "soltero", "mi estado", "situacion sentimental"]):
        respuesta = f"En tus datos registraste estar: {estado}. Sea cual sea tu estado, lo esencial es el diálogo y la paz con la que vivas tu día a día."
    elif any(q in texto for q in ["nombre completo", "como me llamo completo"]):
        respuesta = f"Tu nombre oficial es {nombre_real}, aunque para mí siempre eres {apodo}."
    elif any(q in texto for q in ["cuantos hijos", "mis hijos", "tengo hijos"]):
        respuesta = f"Tienes {hijos} {'hijo' if hijos == 1 else 'hijos'} registrados, {apodo}."
    elif any(q in texto for q in ["trabajo", "profesion", "dedico"]):
        respuesta = f"Te desempeñas como {profesion}. Recuerda que eres mucho más valioso que la carga laboral que llevas encima."
    elif any(q in texto for q in ["hola", "buenas", "saludos"]):
        respuesta = f"¡Hola {apodo}! Me alegra escucharte. Tómate un respiro, cuéntame qué asunto tienes entre manos y lo vemos juntos."
    elif any(q in texto for q in ["gracias"]):
        respuesta = f"¡Un gustazo enorme, {apodo}! Aquí estamos para darnos la mano como hermanos. Sigue adelante con fuerza."
    else:
        # 5. RAG ADAPTATIVO CON LIBROS AFINES
        consejos = []
        for libro in LIBROS_CACHE:
            if libro.get("id_libro") in avatar_info.get("libros_rag_afines", []):
                consejos.append(libro.get("consejo_aplicable"))
        consejo_base = random.choice(consejos) if consejos else "Toma una respiración pausada y regresa al presente."
        respuesta = f"Te comprendo, {apodo}. Oye esto con atención: {consejo_base} Dime, ¿qué es lo primero que sientes que debes atender?"

    return nombre_avatar, respuesta, False
