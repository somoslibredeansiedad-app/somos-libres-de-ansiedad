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
    """Ejecuta la llamada a Gemini utilizando modelos oficiales compatibles."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[LLM Error] GEMINI_API_KEY no encontrada en variables de entorno.")
        return ""

    conversacion_previa = "\n".join(historial[-6:]) if historial else ""
    prompt_completo = (
        f"{prompt_sistema}\n\n"
        f"Historial previo de la conversación:\n{conversacion_previa}\n\n"
        f"Usuario dice: {mensaje_actual}\n\n"
        f"Responde directamente en la voz del avatar:"
    )

    # Intento 1: SDK moderno google-genai
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for modelo in ["gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt_completo
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e_mod:
                print(f"[LLM Aviso] Error con modelo {modelo} en google-genai: {e_mod}")
    except Exception as e_sdk:
        print(f"[LLM Aviso] Fallo al inicializar google-genai: {e_sdk}")

    # Intento 2: SDK google.generativeai clásico (fallback de librería)
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        for modelo in ["gemini-1.5-flash", "gemini-1.5-pro"]:
            try:
                model_inst = genai_legacy.GenerativeModel(modelo)
                response = model_inst.generate_content(prompt_completo)
                if response and response.text:
                    return response.text.strip()
            except Exception as e_mod2:
                print(f"[LLM Aviso] Error con modelo {modelo} en google.generativeai: {e_mod2}")
    except Exception as e_sdk2:
        print(f"[LLM Error] Fallo en SDK legacy: {e_sdk2}")

    return ""

def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict, historial_reciente: list = None) -> Tuple[str, str, bool]:
    avatar_info = CATALOGO_CACHE.get(avatar_id, list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {})
    identidad = avatar_info.get("identidad", {})
    historia_personal = avatar_info.get("historia_personal", {})
    
    nombre_avatar = identidad.get("nombre_completo", "Rodrigo Javier Navas Serrano")
    pais_avatar = identidad.get("pais", "España")
    ciudad_natal = historia_personal.get("ciudad_natal", "Toledo")
    
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

    # 2. FILTRO COMERCIAL DE PAGOS ESTRICTO
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
Reglas de personalidad y ética obligatorias:
1. Usa español de España natural, directo y cercano (tuteo estricto: 'tú tienes', 'mira', 'hombre', 'venga'). NUNCA uses voseo ('vos sabés', 'tenés') ni giros ajenos.
2. Sé empático pero orientado a la acción y al sentido común. Evita tecnicismos excesivos o sermones vacíos.
3. Si el usuario plantea una agresión sexual o violación: desculpabilízalo totalmente, valida el trauma, enfatiza que la culpa es exclusiva del agresor y aconseja buscar apoyo médico y psicológico especializado.
4. Si el usuario plantea la muerte de un hijo o duelo perinatal: aborda el dolor con máximo respeto, no uses frases hechas ('eres joven', 'el tiempo lo cura'), valida su paternidad/maternidad y acompaña su proceso.
5. Si menciona a su hijo 'Venito', responde a esa situación concreta con sensibilidad paternal constructiva.
6. Jamás repitas la misma coletilla de cierre en cada mensaje. Varía el final de forma orgánica.
Principios de serenidad a integrar:
- {contexto_libros}
"""

    respuesta_llm = llamar_gemini_avatar(prompt_sistema, historial, texto)
    if respuesta_llm:
        return nombre_avatar, respuesta_llm, False

    # 4. CONTENCIÓN DE RESPALDO (FALLBACK EN CASO DE INTERRUPCIÓN DE RED)
    if re.search(r"\b(agresi[oó]n sexual|violaci[oó]n|abusad[oa]|abus[oó]|me toc[oó])\b", texto_lower):
        return nombre_avatar, (
            f"Escúchame muy bien, {apodo}: **no tienes absolutamente ninguna culpa de lo sucedido.** "
            "Ni por haber confiado, ni por haber estado allí, ni por cómo reaccionó tu cuerpo para sobrevivir. La culpa es exclusivamente de quien agredió. "
            "En este momento lo primordial es tu salud y tu seguridad: acude cuanto antes a un centro médico de urgencias para recibir atención y resguardo, "
            "y busca apoyo en un profesional especializado en trauma o en alguien de tu máxima confianza. No cargues con esto en soledad."
        ), False

    if re.search(r"\b(beb[eé]|incubadora|prematur[oa]|muri[oó] mi hijo|falleci[oó] mi hijo|perdimos al beb[eé])\b", texto_lower):
        return nombre_avatar, (
            f"Lamento profundamente una pérdida tan desgarradora, {apodo}. La partida de un hijo, aunque haya sido prematuro o haya estado pocos días en la incubadora, "
            "deja un vacío inmenso y un dolor que merece todo el respeto del mundo. No te apresures a 'estar bien' ni hagas caso a frases insensibles de quien no comprende; "
            "tu dolor y tu paternidad son reales. Tómate el tiempo necesario para llorar, respirar y sostenerte un día a la vez."
        ), False

    if re.search(r"\b(pecho|coraz[oó]n|taquicardia|morir|latidos|falta el aire|ahogo)\b", texto_lower):
        return nombre_avatar, (
            f"Escúchame con calma, {apodo}: no te vas a morir ni te va a dar nada por esa taquicardia. "
            "Lo que sientes en el pecho es una respuesta de alarma de tu sistema nervioso; tu cuerpo cree que hay un león delante y dispara la adrenalina. "
            "Siéntate, apoya los dos pies firmes en el suelo, suelta los hombros y alarga la respiración: echa el aire despacio en seis segundos y tómalo en cuatro. "
            "El cuerpo no puede sostener ese pico de tensión eternamente; dale cinco minutos y verás cómo el pulso se va asentando."
        ), False

    if re.search(r"\b(dormir|cama|noche|insomnio|ruido mental|vueltas a la cabeza)\b", texto_lower):
        return nombre_avatar, (
            f"La cama no es lugar para resolver los problemas del día, {apodo}. Cuando te quedas a oscuras y en silencio, la mente aprovecha para montar una película de terror anticipando catástrofes. "
            "Si llevas más de quince minutos dando vueltas, no te quedes peleando con las sábanas. Levántate, coge papel y bolígrafo y vomita todo lo que tengas en la cabeza; sácalo de ahí. "
            "Luego déjalo sobre la mesa y dite con firmeza: 'Hasta mañana a las ocho esto ya no es asunto mío'. Tu cerebro necesita ver que los problemas están anotados para bajar la guardia y descansar."
        ), False

    if re.search(r"\bvenito\b", texto_lower):
        return nombre_avatar, (
            f"Es comprensible que te desvivas por tu hijo Venito, {apodo}; el instinto de protegerlo es lo más natural del mundo. "
            "Pero hay una línea muy clara: el amor cuida, el miedo desbordado asfixia. Si transmites esa alerta constante, el chaval terminará creyendo que el mundo es un lugar hostil. "
            "Pregúntate ante cada susto: '¿Hay un peligro real aquí y ahora o es una fantasía de mi cabeza?'. La mejor herencia que le puedes dar a Venito no es un escudo de cristal, sino un padre que sabe gestionar su propia calma."
        ), False

    if re.search(r"\b(trabajo|empleo|bloqueado|tareas|pantalla|primer paso)\b", texto_lower):
        return nombre_avatar, (
            f"Ese bloqueo frente a la pantalla ocurre cuando la mente intenta procesar toda la montaña de golpe y se colapsa. "
            "Olvida el proyecto entero por un momento. Coge una sola tarea, la más tonta y pequeña que tengas, y dale diez minutos de reloj sin mirar nada más. "
            "El orden mental no llega pensando; llega arrancando con el primer movimiento, por minúsculo que sea."
        ), False

    return nombre_avatar, f"Te escucho con atención, {apodo}. Pon el foco únicamente en lo que está bajo tu control directo en las próximas dos horas. Cuéntame qué es lo que más te pesa ahora mismo y lo miramos juntos.", False
