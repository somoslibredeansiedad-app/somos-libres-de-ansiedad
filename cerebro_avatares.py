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
    Cerebro cognitivo v4.6.3 (Rafael):
    Resuelve el orden jerárquico de dolor sobre datos, erradica bucles RAG,
    atiende dudas de salud/fisioterapia y guía en recargas comerciales.
    """
    avatar_info = CATALOGO_CACHE.get(avatar_id, CATALOGO_CACHE.get("camilo", list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {}))
    nombre_avatar = avatar_info.get("identidad", {}).get("nombre_completo", "Guía")
    pais_avatar = avatar_info.get("identidad", {}).get("pais", "")
    
    texto = mensaje_usuario.lower().strip()
    apodo = perfil_usuario.get("apodo", "amigo/a")
    nombre_real = perfil_usuario.get("nombre_completo", apodo)
    profesion = perfil_usuario.get("profesion") or "tu profesión u ocupación"
    hijos = perfil_usuario.get("cantidad_hijos") if perfil_usuario.get("cantidad_hijos") is not None else 0
    historial = historial_reciente or []

    # 1. FILTRO ROJO / SOS INMEDIATO (Seguridad Clínica y Ética Absoluta)
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

    # 2. ORIENTACIÓN COMERCIAL Y RECARGA DE PLANES (Cero Fricción en Conversión)
    if any(w in texto for w in ["recargar", "comprar", "pagar", "adquirir", "subir de plan", "otros planes", "plan comunicador", "amigo de todos"]):
        if "camilo" in avatar_id:
            return nombre_avatar, (
                f"¡Oye, con gusto te oriento, mi hermano {apodo}! Para recargar o activar los planes Comunicador ($5 USD) o Amigo de Todos ($10 USD), "
                "solo debes ir en el menú lateral izquierdo a la pestaña **'Planes y Suscripción'**. "
                "Allí, en la sección **'Coordinar Pago Privado con Admin'**, puedes solicitar los datos confidenciales de Pago Móvil BDV, Binance Pay o PayPal. "
                "El Administrador te responderá por ese mismo canal privado para entregarte tu cupón de activación de inmediato."
            ), False
        else:
            return nombre_avatar, (
                f"Puedes gestionar la activación de los planes de forma muy sencilla, {apodo}. Dirígete en el menú de navegación a **'Planes y Suscripción'**. "
                "En la pestaña **'Coordinar Pago Privado con Admin'** podrás solicitar los datos para Pago Móvil BDV, Binance Pay o PayPal de forma segura y confidencial. "
                "Una vez reportado, el administrador validará tu acceso."
            ), False

    # 3. RECLAMOS O FRUSTRACIÓN DEL USUARIO (Validación Humana y Humildad)
    if any(w in texto for w in ["deberias ayudarme", "deberías ayudarme", "no me ayudas", "por que no lo haces", "por qué no lo haces", "no me estas ayudando"]):
        if "camilo" in avatar_id:
            return nombre_avatar, (
                f"Tienes toda la razón en reclamármelo, {apodo}, y te pido una sincera disculpa de hermano si sentiste que te respondí con teoría vacía. "
                "A veces los rodeos cansan cuando uno lo que necesita es una mano firme. Dime con toda confianza y sin filtros: "
                "¿cuál es la situación concreta que te está apretando el pecho ahora mismo? Aquí estoy listo para escuchar de verdad."
            ), False
        else:
            return nombre_avatar, (
                f"Acepto tu reclamo, {apodo}, y te pido disculpas. Si mis palabras previas se sintieron distantes o poco útiles, "
                "permíteme corregir el rumbo. Dime directamente qué es lo que más te preocupa en este momento y lo abordamos con hechos y claridad."
            ), False

    # 4. ACOSO ESCOLAR / BULLYING (Prioridad Emocional Absoluta ante la Familia)
    if any(w in texto for w in ["bulling", "bullying", "acoso", "burlan", "golpean", "pegan en el colegio"]):
        if any(w in texto for w in ["psicologo", "psicólogo", "terapia", "amigo", "llevo", "debo"]):
            return nombre_avatar, (
                f"Sí, absolutamente, {apodo}. Llevar a un hijo a un psicólogo infanto-juvenil ante una situación de acoso escolar es el paso más protector y acertado. "
                "El especialista le brindará un espacio seguro para descargar el dolor y reconstruir su autoestima, mientras los padres asumen la defensa formal "
                "exigiendo a la directiva escolar la aplicación inmediata de las medidas de protección. Buscar ayuda profesional no es debilidad, es blindar su salud emocional."
            ), False
        else:
            if "camilo" in avatar_id:
                return nombre_avatar, (
                    f"Hermano {apodo}, el acoso escolar es una herida profunda que angustia a cualquier padre o madre. "
                    "Lo primero y más urgente es la contención en casa: abrázalo, mírale a los ojos y asegúrale con total convicción que él no tiene la culpa de nada "
                    "y que tú estás a su lado para defenderlo. Pide de inmediato una reunión con la dirección de la escuela para activar el protocolo de protección. "
                    "Tu presencia sólida es su mayor escudo protector hoy."
                ), False
            else:
                return nombre_avatar, (
                    f"El acoso escolar requiere una intervención decidida y protectora, {apodo}. "
                    "El primer pilar es el hogar: validar su dolor, hacerle saber que cuenta con tu respaldo incondicional y que no tiene responsabilidad en las agresiones. "
                    "El segundo pilar es la institución: solicitar formalmente a la dirección escolar la investigación y el cese inmediato del hostigamiento. "
                    "Actuar con calma y firmeza transmite seguridad al menor."
                ), False

    # 5. ATENCIÓN DE SALUD / FISIOTERAPIA (Lesiones Mecánicas y Traumatología)
    if any(w in texto for w in ["torci", "torcí", "tobillo", "esguince", "me cai", "me caí", "golpe", "rodilla", "fractura"]):
        if "camilo" in avatar_id:
            return nombre_avatar, (
                f"¡Oye, mi hermano Pasqui, cuidado con eso! Cuando uno anda con la cabeza en las nubes por la tensión, el cuerpo pierde el paso y vienen los accidentes. "
                "Como médico y fisioterapeuta te doy las pautas esenciales inmediatas: \n\n"
                "1. **Reposo y elevación:** Siéntate y pon el pie en alto sobre una almohada para favorecer el retorno venoso.\n"
                "2. **Frío local:** Aplica compresas frías o hielo envuelto en un paño durante 15 a 20 minutos (nunca directo en la piel) para frenar la inflamación.\n"
                "3. **Cero sobrecarga:** No fuerces la pisada si hay dolor agudo.\n\n"
                "Si notas deformidad, hematoma muy extendido o te es imposible apoyar el pie, acude a que te tomen una radiografía para descartar fisura. Descansa ese pie, hermano."
            ), False
        else:
            return nombre_avatar, (
                f"Atendamos esa torcedura de inmediato, {apodo}. El estrés cotidiano suele reducir la propiocepción y provocar tropiezos. "
                "Aplica el protocolo básico de primeros auxilios: mantén el tobillo elevado, coloca frío local protegido durante 15 minutos "
                "y evita cargar peso sobre la articulación. Si persiste la inflamación severa o no logras apoyar la extremidad, "
                "es fundamental que un médico valore la necesidad de una placa radiográfica."
            ), False

    # 6. SOMATIZACIÓN Y ANSIEDAD ALIMENTARIA (Hambre Emocional / Atracones Nocturnos)
    if any(w in texto for w in ["hambre", "comer", "comida", "atracon", "atracón", "desquiciado", "nevera"]):
        if "camilo" in avatar_id:
            return nombre_avatar, (
                f"Eso tiene una explicación fisiológica muy clara, Pasqui. Cuando pasas el día acumulando estrés sin desahogarte, "
                "los niveles de cortisol se mantienen altos y por la noche tu cerebro busca un salvavidas rápido en la comida para liberar dopamina y calmarse a la fuerza. "
                "No te juzgues ni te llames desquiciado; tu cuerpo solo está buscando anestesiar la angustia. "
                "Un consejo práctico: antes de abrir la nevera, sírvete un vaso de agua despacio, respira hondo en 4 segundos y suelta en 6 segundos. "
                "Dale 5 minutos a tu mente para reconocer qué emoción estás masticando en realidad."
            ), False
        else:
            return nombre_avatar, (
                f"El comer compulsivo nocturno suele ser una respuesta directa al agotamiento y la ansiedad acumulada durante la jornada, {apodo}. "
                "El sistema nervioso busca amortiguar el cortisol mediante la recompensa química de los alimentos. "
                "No lo enfrentes con culpa; reconócelo como una señal de sobrecarga. Haz una pausa deliberada de tres respiraciones conscientes "
                "y bebe agua tibia antes de ingerir alimentos para diferenciar el hambre biológica del hambre emocional."
            ), False

    # 7. SÍNTOMAS FÍSICOS DE ANGUSTIA (Pecho, Respiración, Foco Somático)
    if any(w in texto for w in ["falta de aire", "ahogo", "pecho apretado", "dolor en el pecho", "palpitaciones"]):
        return nombre_avatar, (
            f"{apodo}, la opresión torácica y la sensación de que falta el aire son respuestas neurovegetativas muy frecuentes ante la preocupación excesiva. "
            "Tus pulmones y tu corazón son sanos; se trata de una hiperactivación refleja. "
            "Haz esta pausa conmigo: suelta todo el aire por la boca como si apagaras una vela lejana. "
            "Luego inhala suavemente por la nariz en 4 segundos y exhala en 6 segundos. "
            "Siente el respaldo donde estás apoyado y recuerda que esta oleada de adrenalina pasará en pocos minutos."
        ), False

    # 8. DISOCIACIÓN ENTRE IDENTIDAD LABORAL Y AGOBIO ECONÓMICO
    if any(w in texto for w in ["econom", "plata", "dinero", "no me da", "alcanza", "mantener", "sustento", "sueldo"]) or (
        "trabajo" in texto and any(w in texto for w in ["familia", "pais", "problema", "ayudar"])
    ):
        return nombre_avatar, (
            f"Comprendo con total cercanía lo que pesa esa carga, {apodo}. Aunque te desempeñes como {profesion}, "
            "el contexto económico adverso y la responsabilidad de sostener a la familia generan una presión que satura a cualquiera. "
            "Lo primordial es desarmar la culpa: las dificultades externas no determinan tu valor ni tu esfuerzo como protector. "
            "Dividamos el agobio: no es posible solucionar todo el mes hoy. Concéntrate en la decisión concreta y práctica de las próximas 24 horas."
        ), False

    # 9. CONTINUIDAD CONTEXTUAL ANTE MENSAJES MONOPALABRA O DE SEGUIMIENTO
    if texto in ["insomnio", "no puedo dormir", "desvelo"]:
        return nombre_avatar, (
            f"El insomnio es la respuesta natural de un cerebro que se mantiene en alerta cuidando a los suyos, {apodo}. "
            "Cuando la mente percibe problemas sin resolver, el sistema nervioso simpático no da la orden de desconexión. "
            "Esta noche no luches contra la cama: recuesta el cuerpo, coloca una mano sobre tu estómago, alarga la exhalación "
            "y concédete el permiso de descansar físicamente aunque la mente tarde en apagarse."
        ), False

    if texto in ["depresion", "depresión", "tristeza", "sin ganas"]:
        return nombre_avatar, (
            f"{apodo}, cuando las preocupaciones familiares y la tensión se arrastran por mucho tiempo, el organismo agota sus reservas de energía "
            "y aparece esa pesadez profunda. La depresión muchas veces no es otra cosa que el cuerpo diciendo 'basta de sobreexigirte'. "
            "Hoy no intentes forzar el ánimo; da un paso básico a la vez: una pausa, una respiración profunda y el reconocimiento de tu propio esfuerzo."
        ), False

    # 10. PREGUNTAS SOBRE IDENTIDAD Y DATOS DEL PERFIL REGISTRADO
    if any(q in texto for q in ["como me llamo", "cómo me llamo", "sabes mi nombre", "sabes como me llamo", "sabes cómo me llamo", "quien soy", "mi apodo"]):
        return nombre_avatar, f"Tu nombre oficial en tu cuenta es {nombre_real}, aunque para mí y en este espacio siempre eres {apodo}.", False

    if any(q in texto for q in ["cuantos hijos", "cuántos hijos", "mis hijos", "tengo hijos", "cantidad de hijos"]):
        return nombre_avatar, f"En tu registro constan {hijos} {'hijo' if hijos == 1 else 'hijos'}, {apodo}.", False

    if any(q in texto for q in ["en que trabajo", "en qué trabajo", "mi profesion", "mi profesión", "a que me dedico", "a qué me dedico"]):
        return nombre_avatar, f"Te desempeñas como {profesion}. Recuerda siempre que tu valor humano está por encima de cualquier etiqueta laboral.", False

    # 11. HISTORIA PERSONAL Y ORÍGENES DEL AVATAR (Lectura Dinámica del Catálogo RAG)
    if any(w in texto for w in ["de donde eres", "de qué parte", "tus padres", "tu vida", "algo de ti", "tu historia", "tu infancia"]):
        historia = avatar_info.get("historia_personal", {})
        ciudad = historia.get("ciudad_natal", pais_avatar)
        padres = historia.get("padres", "Mis padres me enseñaron a perseverar con dignidad y amor.")
        infancia = historia.get("entorno_infancia", "Crecí aprendiendo el valor de la templanza.")
        recuerdo = historia.get("recuerdo_clave", "")

        if any(w in texto for w in ["padres", "papa", "mama", "padre", "madre"]):
            return nombre_avatar, f"Con mucho gusto te lo comparto, {apodo}: {padres} De ellos aprendí que la templanza y el corazón son el mejor refugio.", False
        elif any(w in texto for w in ["donde eres", "que parte", "ciudad"]):
            return nombre_avatar, f"Nací en {ciudad}, {pais_avatar}. {infancia} Por eso sé lo esencial que es encontrar serenidad en medio del ruido.", False
        else:
            return nombre_avatar, f"Soy {nombre_avatar}, de {ciudad}. {infancia} {recuerdo} Aquí me tienes listo/a para acompañarte con esa misma fortaleza.", False

    # 12. SALUDOS Y CORTESÍA (Respetando el Tono Cultural)
    if any(q in texto for q in ["hola", "buenas", "saludos", "brother", "que tal", "qué tal"]):
        if "camilo" in avatar_id:
            return nombre_avatar, f"¡Qué tal, mi hermano {apodo}! Un gustazo enorme saludarte. Suelta los hombros y cuéntame con confianza: ¿qué traes en mente hoy?", False
        elif "anastasia" in avatar_id:
            return nombre_avatar, f"Hola, {apodo}. Me alegra encontrarte. Tómate un segundo de calma y explícame con total franqueza qué asunto necesitas que analicemos hoy.", False
        else:
            return nombre_avatar, f"¡Hola {apodo}! Te doy una cálida bienvenida. Tómate un respiro y cuéntame de qué te gustaría conversar hoy.", False

    if any(q in texto for q in ["gracias"]):
        return nombre_avatar, f"¡Un gustazo enorme, {apodo}! Para eso estamos aquí, para darnos la mano y caminar con más calma. Sigue adelante con fuerza.", False

    # 13. RAG DINÁMICO ORGÁNICO (Sin Plantilla Mecánica)
    consejos = []
    for libro in LIBROS_CACHE:
        if libro.get("id_libro") in avatar_info.get("libros_rag_afines", []):
            consejos.append(libro.get("consejo_aplicable"))
    
    consejo_seleccionado = random.choice(consejos) if consejos else "Lleva tu atención al momento presente y da un paso pequeño a la vez."

    if "camilo" in avatar_id:
        respuesta_organica = f"Te entiendo perfectamente, {apodo}. Mira, algo que siempre ayuda a ver las cosas claras es esto: {consejo_seleccionado} Dime, ¿por dónde sientes que debemos empezar a desenredar esto?"
    elif "anastasia" in avatar_id:
        respuesta_organica = f"Comprendo la situación, {apodo}. Si analizamos esto con perspectiva: {consejo_seleccionado} ¿Cuál es el punto central que requiere nuestra atención prioritaria?"
    else:
        respuesta_organica = f"Te escucho con atención, {apodo}. Ante lo que me comentas, ten presente esto: {consejo_seleccionado} Cuéntame, ¿qué paso sientes que puedes dar hoy?"

    return nombre_avatar, respuesta_organica, False
