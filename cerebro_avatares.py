import json
import os
import random
import re
from typing import Dict, Any, Tuple, List

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
    r"\bsuicid", r"\bmatarme\b", r"\bquitarme la vida\b", r"\bno quiero vivir\b",
    r"\bhacerme da[nñ]o\b", r"\bcortarme\b", r"\bacabar con todo\b",
    r"\bno vale la pena vivir\b", r"\bdesaparecer\b.*\b(despertar|morir|sufrir)\b",
    r"\bmejor si no existiera\b", r"\bpreferir[ií]a estar muerto\b"
]

def obtener_catalogo_formateado(activos_usuario: list) -> list:
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

def cargar_biografia_completa(avatar_id: str) -> str:
    archivo_txt = f"{avatar_id}.txt"
    if os.path.exists(archivo_txt):
        try:
            with open(archivo_txt, "r", encoding="utf-8") as f:
                return f.read()[:3500]
        except Exception as e:
            print(f"Aviso: No se pudo leer {archivo_txt}: {e}")
    return ""

def llamar_gemini_avatar(prompt_sistema: str, historial: list, mensaje_actual: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[LLM ERROR] Variable GEMINI_API_KEY no encontrada en el entorno de Render.")
        return ""

    conversacion_previa = "\n".join(historial[-6:]) if historial else ""
    prompt_completo = (
        f"{prompt_sistema}\n\n"
        f"Historial previo de la conversación:\n{conversacion_previa}\n\n"
        f"Usuario dice: {mensaje_actual}\n\n"
        f"Responde directamente en la voz del avatar:"
    )

    # Intento 1: SDK google-genai
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
                print(f"[LLM Log] Error con {modelo} en google-genai: {e_mod}")
    except Exception as e_sdk:
        print(f"[LLM Log] SDK google-genai fallo: {e_sdk}")

    # Intento 2: SDK google.generativeai (fallback)
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
                print(f"[LLM Log] Error con {modelo} en google.generativeai: {e_mod2}")
    except Exception as e_sdk2:
        print(f"[LLM Log] SDK google.generativeai fallo: {e_sdk2}")

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

    # 1. FILTRO DE CRISIS / SOS
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

    # 2. FILTRO COMERCIAL DE PAGOS
    if re.search(r"\b(recargar|adquirir plan|cambiar de plan|subir de plan|pagar suscripci[oó]n|m[eé]todos de pago)\b", texto_lower) or (
        re.search(r"\bpagar\b", texto_lower) and not re.search(r"\b(apagar|apagar el ruido|apagar la mente)\b", texto_lower)
    ):
        return nombre_avatar, (
            f"Puedes gestionar la ampliación de tu plan con total tranquilidad, {apodo}. En el menú lateral encontrarás la sección "
            "'Planes y Suscripción', donde podrás coordinar los datos correspondientes en un canal privado y seguro."
        ), False

    # 3. LLAMADA AL MOTOR GENERATIVO CON CONTEXTO CANÓNICO
    bio_completa = cargar_biografia_completa(avatar_id)
    libros_afines = avatar_info.get("libros_rag_afines", [])
    fragmentos_rag = [
        lib.get("consejo_aplicable") for lib in LIBROS_CACHE 
        if lib.get("id_libro") in libros_afines and "legal" not in lib.get("consejo_aplicable", "").lower()
    ]
    contexto_libros = "\n- ".join(fragmentos_rag[:3]) if fragmentos_rag else "Enfócate en lo que puedes controlar y da un paso a la vez."

    prompt_sistema = f"""Eres {nombre_avatar}, un avatar de apoyo emocional y acompañamiento reflexivo de {ciudad_natal}, {pais_avatar}.
Estás conversando con {apodo}.

EXPEDIENTE BIOGRÁFICO CANÓNICO (TUS RAÍCES, TRAUMAS Y MEMORIA VIVIDA):
{bio_completa if bio_completa else "Abogado penalista y mediador de Toledo. Estuviste en prisión preventiva injusta en Soto del Real por la corrupción de De la Riva, sufriste accidentes graves de montaña en Gredos con tu tío Gonzalo y en Pirineos con tu amigo Pablo, fuiste operado de hernia discal con artrodesis lumbar y diriges la Fundación Horizonte Restaurativo."}

REGLAS DE PERSONALIDAD Y ÉTICA:
1. Habla en español de España natural, sobrio, pragmático y con sentido común castellano (tuteo estricto: 'tú tienes', 'mira', 'hombre', 'venga', 'chaval'). NUNCA uses voseo ni modismos ajenos.
2. Si te preguntan por Soto del Real, De la Riva o tu historia: asume tu biografía en primera persona con serenidad y sin dramatismo artificial.
3. Si el usuario plantea agresión sexual o violación: desculpabilízalo totalmente, valida el trauma, enfatiza que la culpa es 100% del agresor y aconseja atención médica/forense y apoyo psicológico especializado.
4. Si plantea duelo perinatal o pérdida de un hijo prematuro: trata el dolor con reverencia, valida la paternidad/maternidad y jamás recurras a clichés vacíos ('eres joven', 'el tiempo lo cura').
5. Si describe dolor lumbar, ciática o limitaciones físicas: empatiza desde tu propia experiencia con la columna y la artrodesis, aportando calma somática sin prescribir fármacos.
6. Adapta el cierre de forma orgánica sin repetir siempre la misma pregunta final.
Principios de serenidad aplicables:
- {contexto_libros}
"""

    respuesta_llm = llamar_gemini_avatar(prompt_sistema, historial, texto)
    if respuesta_llm:
        return nombre_avatar, respuesta_llm, False

    # 4. CONTENCIÓN DE RESPALDO (FALLBACK TEMÁTICO)
    if re.search(r"\b(soto del real|de la riva|prisi[oó]n|c[aá]rcel|encerrado|acusaci[oó]n injusta)\b", texto_lower):
        return nombre_avatar, (
            f"Sé perfectamente lo que es ese frío en el estómago, {apodo}. Pasé ochenta y dos días en el Módulo 4 de Soto del Real "
            "por las firmas falsificadas de De la Riva, sabiendo que era inocente mientras el mundo seguía girando fuera. "
            "Si te enfrentas a una injusticia, no te desgastes peleando contra la rabia mental: organízate con rigor documental, "
            "apóyate en quien te defienda con hechos limpios y mantén la cabeza serena. Los muros encierran el cuerpo, pero la integridad no te la quita nadie."
        ), False

    if re.search(r"\b(agresi[oó]n sexual|violaci[oó]n|abusad[oa]|abus[oó]|me toc[oó]|forz[oó])\b", texto_lower):
        return nombre_avatar, (
            f"Escúchame con toda claridad, {apodo}: **no tienes absolutamente ninguna culpa de lo sucedido.** "
            "Ni por haber ido, ni por haber bebido, ni por haber confiado. La responsabilidad recae al cien por cien en quien agredió. "
            "Lo que experimentas ahora es la reacción de choque de tu sistema nervioso. Tu prioridad absoluta es tu resguardo: "
            "acude a un centro médico para recibir profilaxis y apoyo especializado, y no cargues con esto en soledad."
        ), False

    if re.search(r"\b(beb[eé]|incubadora|prematur[oa]|muri[oó] mi hijo|falleci[oó] mi hijo|perdimos al beb[eé])\b", texto_lower):
        return nombre_avatar, (
            f"Lamento profundamente una pérdida tan desgarradora, {apodo}. La partida de un hijo, aunque haya sido prematuro o haya estado pocos días en la incubadora, "
            "deja un vacío inmenso y un dolor que merece todo el respeto del mundo. No te apresures a 'estar bien' ni hagas caso a frases insensibles de quien no comprende; "
            "tu dolor y tu paternidad son reales. Tómate el tiempo necesario para llorar, respirar y sostenerte un día a la vez."
        ), False

    if re.search(r"\b(lumbar|ci[aá]tica|columna|espalda|dolor punzante|atrapado en una cama)\b", texto_lower):
        return nombre_avatar, (
            f"Comprendo bien esa desesperación, {apodo}. Conozco ese dolor: viví la inmovilidad con corsé tras el accidente en Gredos y pasé por una artrodesis con tornillos en la columna por una hernia extruida. "
            "Cuando la ciática muerde, la mente tiende a rebelarse contra el propio cuerpo creyendo que ya no sirve. No pelees contra la cama; apoya la respiración, "
            "suelta la mandíbula y concéntrate solo en desinflamar el momento presente. El cuerpo sabe encontrar su equilibrio si no le sumas la angustia de la anticipación."
        ), False

    if re.search(r"\b(dormir|insomnio|ruido mental|vueltas a la cabeza)\b", texto_lower):
        return nombre_avatar, (
            f"La cama no es lugar para resolver los problemas del día, {apodo}. Cuando te quedas a oscuras y en silencio, la mente monta escenarios catastróficos. "
            "Si llevas más de quince minutos dando vueltas, sal de la cama, anota en un papel lo que te inquieta y déjalo para mañana a primera hora. "
            "Tu cerebro necesita ver que los asuntos quedan registrados para aflojar la tensión y descansar."
        ), False

    return nombre_avatar, f"Te escucho con atención, {apodo}. Pon el foco únicamente en lo que está bajo tu control directo en las próximas dos horas. Cuéntame qué es lo que más te pesa ahora mismo y lo miramos juntos.", False
