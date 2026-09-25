import json
import os
import random
import re
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

# Patrones robustos para detección de crisis aguda e ideación suicida
PATRONES_CRISIS_SOS = [
    r"\bsuicid", r"\bmatarme\b", r"\bquitarme la vida\b", r"\bno quiero vivir\b",
    r"\bhacerme da[nñ]o\b", r"\bcortarme\b", r"\bacabar con todo\b",
    r"\bno vale la pena vivir\b", r"\bdesaparecer\b.*\b(despertar|morir|sufrir)\b",
    r"\bmejor si no existiera\b", r"\bpreferir[ií]a estar muerto\b"
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

def llamar_gemini_avatar(prompt_sistema: str, historial: list, mensaje_actual: str) -> str:
    """Intenta generar la respuesta a través del SDK oficial de Google GenAI."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # Estructuración de contexto conversacional
        conversacion_previa = "\n".join(historial[-6:]) if historial else ""
        prompt_completo = f"{prompt_sistema}\n\nHistorial previo de la conversación:\n{conversacion_previa}\n\nUsuario dice: {mensaje_actual}\n\nResponde como el avatar:"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_completo
        )
        if response and response.text:
            return response.text.strip()
    except Exception as err:
        print(f"Aviso: Fallback local por error en API de IA: {err}")
    return ""

def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict, historial_reciente: list = None) -> Tuple[str, str, bool]:
    avatar_info = CATALOGO_CACHE.get(avatar_id, list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {})
    identidad = avatar_info.get("identidad", {})
    historia_personal = avatar_info.get("historia_personal", {})
    
    nombre_avatar = identidad.get("nombre_completo", "Rodrigo Navas")
    pais_avatar = identidad.get("pais", "España")
    ciudad_natal = historia_personal.get("ciudad_natal", "Madrid")
    especialidad = identidad.get("especialidad", "enfoque pragmático, sentido común y acción")
    
    texto = mensaje_usuario.strip()
    texto_lower = texto.lower()
    
    apodo_crudo = perfil_usuario.get("apodo", "amigo/a").strip()
    apodo = "Juan Carlos" if apodo_crudo.lower() == "admin" else apodo_crudo.replace("Admin ", "").strip()
    
    historial = historial_reciente or []
    
    # 1. FILTRO DE CRISIS / PROTOCOLO SOS
    for patron in PATRONES_CRISIS_SOS:
        if re.search(patron, texto_lower):
            respuesta_sos = (
                f"🚨 **{apodo}, por favor detente un momento. Tu vida y tu bienestar son lo principal.**\n\n"
                "Siento el peso y el dolor que estás cargando ahora mismo, pero este espacio es únicamente una guía reflexiva de acompañamiento; no sustituye la atención médica ni psicológica urgente.\n\n"
                "**Por favor, comunícate de inmediato con estos recursos gratuitos y confidenciales:**\n"
                "• **España:** Llama al 024 (Atención a la Conducta Suicida) o al 717 003 717 (Teléfono de la Esperanza).\n"
                "• **Venezuela:** Línea de Ayuda Psicológica FPV (0212-4163116 / 0212-4163118).\n"
                "• **Estados Unidos / Internacional:** Marca al 988 o visita https://www.befrienders.org\n"
                "• **Emergencias Generales:** Llama al 112, 911 o acude al centro de urgencias más cercano.\n\n"
                "No te quedes a solas con este sufrimiento. Apóyate en quienes pueden darte la mano hoy mismo."
            )
            return nombre_avatar, respuesta_sos, True

    # 2. FILTRO COMERCIAL DE PAGOS ESTRICTO (Uso de fronteras de palabra)
    if re.search(r"\b(recargar|adquirir plan|cambiar de plan|subir de plan|pagar suscripci[oó]n|m[eé]todos de pago)\b", texto_lower) or (
        re.search(r"\bpagar\b", texto_lower) and not re.search(r"\b(apagar|apagar el ruido|apagar la mente)\b", texto_lower)
    ):
        return nombre_avatar, (
            f"Puedes gestionar la ampliación de tu plan con total tranquilidad, {apodo}. En el menú lateral encontrarás la sección "
            "'Planes y Suscripción', donde podrás coordinar los datos correspondientes en un canal privado y seguro."
        ), False

    # 3. MOTOR INTELIGENTE GENERATIVO (LLM CONECTADO)
    libros_afines = avatar_info.get("libros_rag_afines", [])
    fragmentos_rag = [
        lib.get("consejo_aplicable") for lib in LIBROS_CACHE 
        if lib.get("id_libro") in libros_afines and "legal" not in lib.get("consejo_aplicable", "").lower()
    ]
    contexto_libros = "\n- ".join(fragmentos_rag[:3]) if fragmentos_rag else "Enfócate en lo que puedes controlar y da un paso a la vez."

    prompt_sistema = f"""Eres {nombre_avatar}, un avatar de apoyo emocional pragmático, sereno y directo de {ciudad_natal}, {pais_avatar}.
Estás hablando con {apodo}.
Reglas de personalidad obligatorias:
1. Usa español de España natural, directo y cercano (tuteo estricto: 'tú tienes', 'mira', 'hombre', 'venga'). NUNCA uses voseo ('vos sabés', 'tenés') ni giros de otros países.
2. Sé empático pero orientado a la acción y al sentido común. Evita frases vacías de autoayuda o tecnicismos excesivos.
3. Responde de forma personalizada a lo que te plantea el usuario. Si habla de su hijo, de somatizaciones, de trabajo o de culpa, aborda ese tema exacto.
4. Jamás repitas la misma muletilla final en cada mensaje (prohibido terminar siempre diciendo '¿por dónde empezamos a meterle mano al tema?'). Varía tus cierres de forma natural.
5. Apóyate sutilmente en estos principios de serenidad sin citar autores de forma artificial:
- {contexto_libros}
"""

    respuesta_llm = llamar_gemini_avatar(prompt_sistema, historial, texto)
    if respuesta_llm:
        return nombre_avatar, respuesta_llm, False

    # 4. MOTOR DE RESPUESTA MODULAR (FALLBACK CONTEXTUAL DIRIGIDO)
    # Identidad
    if re.search(r"\b(qui[eé]n eres|c[oó]mo te llamas|tu nombre)\b", texto_lower):
        return nombre_avatar, f"¡Qué tal, {apodo}! Soy **{nombre_avatar}**, de {ciudad_natal}. Aquí me tienes para charlar con franqueza, sin rodeos y buscando soluciones con sentido común. Dime qué tienes entre manos.", False

    # Somatización (pecho, taquicardia, respiración)
    if re.search(r"\b(pecho|coraz[oó]n|taquicardia|morir|latidos|falta el aire|ahogo)\b", texto_lower):
        return nombre_avatar, (
            f"Escúchame con calma, {apodo}: no te vas a morir ni te va a dar nada por esa taquicardia. "
            "Lo que sientes en el pecho es una respuesta de alarma de tu sistema nervioso; tu cuerpo cree que hay un león delante y dispara la adrenalina. "
            "Siéntate, apoya los dos pies firmes en el suelo, suelta los hombros y alarga la respiración: echa el aire despacio en seis segundos y tómalo en cuatro. "
            "El cuerpo no puede sostener ese pico de tensión eternamente; dale cinco minutos y verás cómo el pulso se va asentando."
        ), False

    # Insomnio y ruido mental nocturno
    if re.search(r"\b(dormir|cama|noche|insomnio|ruido mental|vueltas a la cabeza)\b", texto_lower):
        return nombre_avatar, (
            f"La cama no es lugar para resolver los problemas del día, {apodo}. Cuando te quedas a oscuras y en silencio, la mente aprovecha para montar una película de terror anticipando catástrofes. "
            "Si llevas más de quince minutos dando vueltas, no te quedes peleando con las sábanas. Levántate, coge papel y bolígrafo y vomita todo lo que tengas en la cabeza; sácalo de ahí. "
            "Luego déjalo sobre la mesa y dite con firmeza: 'Hasta mañana a las ocho esto ya no es asunto mío'. Tu cerebro necesita ver que los problemas están anotados para bajar la guardia y descansar."
        ), False

    # Paternidad y sobreprotección (Venito)
    if re.search(r"\b(venito|hijo|hijos|padre|proteger|miedo irracional)\b", texto_lower):
        return nombre_avatar, (
            f"Es comprensible que te desvivas por tu hijo Venito, {apodo}; el instinto de protegerlo es lo más natural del mundo. "
            "Pero hay una línea muy clara: el amor cuida, el miedo desbordado asfixia. Si transmites esa alerta constante, el chaval terminará creyendo que el mundo es un lugar hostil. "
            "Pregúntate ante cada susto: '¿Hay un peligro real aquí y ahora o es una fantasía de mi cabeza?'. La mejor herencia que le puedes dar a Venito no es un escudo de cristal, sino un padre que sabe gestionar su propia calma."
        ), False

    # Parálisis y agobio laboral
    if re.search(r"\b(trabajo|empleo|bloqueado|tareas|pantalla|primer paso)\b", texto_lower):
        return nombre_avatar, (
            f"Ese bloqueo frente a la pantalla ocurre cuando la mente intenta procesar toda la montaña de golpe y se colapsa. "
            "Olvida el proyecto entero por un momento. Coge una sola tarea, la más tonta y pequeña que tengas, y dale diez minutos de reloj sin mirar nada más. "
            "El orden mental no llega pensando; llega arrancando con el primer movimiento, por minúsculo que sea."
        ), False

    # Miedo al juicio / culpa
    if re.search(r"\b(verg[uü]enza|juzgado|encerrarme|culpa|arrepentimiento|carga)\b", texto_lower):
        return nombre_avatar, (
            f"Quítate esa losa de encima, {apodo}. Nadie está libre de pasar por un bache, y pedir un respiro o sentirse desbordado no te convierte en una carga para nadie. "
            "La gente suele estar demasiado ocupada con sus propias batallas como para juzgarte con la dureza con la que te estás castigando tú. "
            "No te aísles por vergüenza; deja que quienes te aprecian vean tu vulnerabilidad sin esconderte."
        ), False

    # Cierre / Plan de acción
    if re.search(r"\b(compromisos|plan|ma[nñ]ana|futuro|innegociables)\b", texto_lower):
        return nombre_avatar, (
            f"Vamos a dejarnos de teorías y a quedarnos con lo esencial, {apodo}. Tres compromisos claros para mañana:\n\n"
            "1. **Cuerpo en regla:** Camina 20 minutos a paso ligero para drenar el exceso de adrenalina.\n"
            "2. **Límite a la rumiación:** Cuando la cabeza empiece a inventar desgracias, vuelve a los sentidos: pies en el suelo y foco en lo inmediato.\n"
            "3. **Serenidad con Venito:** Permítele jugar con tranquilidad y recuérdate que tu serenidad es su mejor refugio.\n\n"
            "Cumple con eso y verás cómo recuperas el pulso de las cosas."
        ), False

    # Respuesta general reflexiva (sin frases jurídicas ni muletillas fijas)
    consejo_base = "Pon el foco únicamente en lo que está bajo tu control directo en las próximas dos horas y deja que lo demás espere su turno."
    return nombre_avatar, f"Te escucho con atención, {apodo}. {consejo_base} Cuéntame con tranquilidad qué aspecto puntual quieres que miremos ahora.", False
