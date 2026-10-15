import json
import os
import random
import re
from typing import Dict, Any, Tuple, List, Optional
import httpx
from dotenv import load_dotenv

# Carga obligatoria de variables de entorno desde el archivo .env
load_dotenv()

CATALOGO_CACHE: Dict[str, Any] = {}
LIBROS_CACHE: List[Dict[str, Any]] = []

if os.path.exists("catalogo_rag_avatares.json"):
    try:
        with open("catalogo_rag_avatares.json", "r", encoding="utf-8") as f:
            datos_json = json.load(f)
            LIBROS_CACHE = datos_json.get("biblioteca_rag", [])
            for av in datos_json.get("avatares_oficiales", []):
                CATALOGO_CACHE[av["id_avatar"]] = av
    except Exception as e:
        print(f"[CEREBRO AVATARES] Error cargando catalogo RAG: {e}")

PATRONES_CRISIS_SOS = [
    r"\bsuicid", r"\bmatarme\b", r"\bquitarme la vida\b", r"\bno quiero vivir\b",
    r"\bhacerme da[nñ]o\b", r"\bcortarme\b", r"\bacabar con todo\b",
    r"\bno vale la pena vivir\b", r"\bdesaparecer\b.*\b(despertar|morir|sufrir)\b",
    r"\bmejor si no existiera\b", r"\bpreferir[ií]a estar muerto\b",
    r"\bpuedo morir\b", r"\bme voy a morir\b", r"\bme quiero morir\b"
]

PATRONES_AGRESION_SEXUAL = [
    r"\b(violaci[oó]n|violaron|me violaron|violada|violado|abuso sexual|abusaron de m[ií]|me tocaron|agresi[oó]n sexual)\b"
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
            print(f"[CEREBRO AVATARES] Aviso: No se pudo leer {archivo_txt}: {e}")
    return ""

async def llamar_gemini_avatar_async(prompt_sistema: str, historial: list, mensaje_actual: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[DIAGNÓSTICO GEMINI] Alerta: GEMINI_API_KEY no encontrada en las variables de entorno.")
        return ""

    conversacion_previa = "\n".join(historial[-6:]) if historial else ""
    prompt_completo = (
        f"{prompt_sistema}\n\n"
        f"Historial previo de la conversación:\n{conversacion_previa}\n\n"
        f"Usuario dice: {mensaje_actual}\n\n"
        f"Responde directamente como el avatar asignado:"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt_completo}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600
        }
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client_http:
            resp = await client_http.post(url, json=payload)
            if resp.status_code == 200:
                data_api = resp.json()
                candidatos = data_api.get("candidates", [])
                if candidatos:
                    partes = candidatos[0].get("content", {}).get("parts", [])
                    if partes:
                        return partes[0].get("text", "").strip()
            else:
                print(f"[DIAGNÓSTICO GEMINI] Error HTTP REST {resp.status_code}: {resp.text}")
    except Exception as e_http:
        print(f"[DIAGNÓSTICO GEMINI] Excepción en llamada HTTP REST asíncrona: {e_http}")

    return ""

async def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict, historial_reciente: list = None) -> Tuple[str, str, bool]:
    avatar_info = CATALOGO_CACHE.get(avatar_id, list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {})
    identidad = avatar_info.get("identidad", {})
    historia_personal = avatar_info.get("historia_personal", {})
    
    nombre_avatar = identidad.get("nombre_completo", "Guía de Serenidad")
    pais_avatar = identidad.get("pais", "")
    ciudad_natal = historia_personal.get("ciudad_natal", "")
    tono = avatar_info.get("tono_linguistico", "")
    especialidad = identidad.get("especialidad", "Acompañante Emocional")
    
    texto = mensaje_usuario.strip()
    texto_lower = texto.lower()
    
    apodo_crudo = perfil_usuario.get("apodo", "amigo/a").strip()
    apodo = "Juan Carlos" if apodo_crudo.lower() == "admin" else apodo_crudo.replace("Admin ", "").strip()
    profesion = perfil_usuario.get("profesion") or "tu labor diaria"
    hijos = perfil_usuario.get("cantidad_hijos") if perfil_usuario.get("cantidad_hijos") is not None else 0
    historial = historial_reciente or []

    # 1. FILTRO DE CRISIS / SOS (SEGURIDAD ABSOLUTA E INMEDIATA)
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

    # 2. FILTRO COMERCIAL DE PAGOS (DESVÍO CUIDADOSO SIN CONFUNDIR METÁFORAS)
    patron_pago_estricto = r"\b(recargar|adquirir plan|cambiar de plan|subir de plan|pagar suscripci[oó]n|m[eé]todos de pago|comprar plan|renovar plan|datos bancarios|pago m[oó]vil|binance pay)\b"
    if re.search(patron_pago_estricto, texto_lower):
        return nombre_avatar, (
            f"Puedes coordinar la ampliación o renovación de tu plan con total tranquilidad, {apodo}. En el menú lateral encontrarás la sección "
            "'Planes y Suscripción', donde podrás acordar los detalles de forma privada y segura directamente con el Administrador."
        ), False

    # 3. CONTENCIÓN PRIORITARIA ANTE AGRESIÓN SEXUAL O VIOLACIÓN (HUMANA Y COMPASIVA)
    if any(re.search(p, texto_lower) for p in PATRONES_AGRESION_SEXUAL):
        if avatar_id == "larissa":
            return nombre_avatar, (
                f"Mírame a los ojos a través de estas palabras, {apodo}: **tú no tienes absolutamente ninguna culpa de lo que te hicieron.** "
                "La culpa y la responsabilidad son al cien por cien del agresor. Lo que viviste fue un acto de violencia brutal e injustificable, "
                "y es completamente comprensible que sientas dolor, asco o desconexión hacia tu cuerpo. Tu cuerpo no está roto ni sucio; "
                "tu cuerpo es el templo que resistió para mantenerte con vida hoy.\n\n"
                "El camino para volver a habitarte con paz es posible, pero no tienes que recorrerlo a solas ni de prisa. "
                "Tu prioridad inmediata es tu cuidado físico y emocional: si la agresión fue reciente, acude a un centro médico de urgencias para recibir atención y resguardo seguro. "
                "Y apóyate en terapia especializada en trauma sexual. Tu dignidad sigue intacta y aquí estoy sosteniéndote la mano sin juzgarte jamás."
            ), False
        elif avatar_id == "rodrigo":
            return nombre_avatar, (
                f"Escúchame con total claridad, {apodo}: **no tuviste ni tendrás jamás la culpa de haber sufrido esa agresión.** "
                "Quien vulnera la integridad física de otra persona comete un delito grave y la responsabilidad recae únicamente sobre el agresor. "
                "Esa sensación de culpa o de haber traicionado tu dignidad es una herida psicológica típica del trauma, pero no es la verdad: "
                "hiciste lo necesario para sobrevivir.\n\n"
                "Tu seguridad física y tu recuperación son lo primero. Si el hecho es reciente, acude de inmediato a valoración médica forense y de urgencias. "
                "Busca acompañamiento en profesionales de salud mental especializados en agresión sexual. No te aísles con este sufrimiento; mereces sanar y recuperar tu tranquilidad."
            ), False
        elif avatar_id == "camilo":
            return nombre_avatar, (
                f"Hermano/a, mírame aquí: **no tuviste ni un ápice de culpa de lo ocurrido.** Como médico te digo que la agresión violenta "
                "es un daño físico y moral que jamás debió suceder, y toda la responsabilidad recae en quien la cometió. "
                "Ese asco o desconexión física es la reacción refleja del organismo intentando asimilar el golpe. "
                "Tu cuerpo es sagrado y tu dignidad jamás te la quitaron. Si fue reciente, busca de inmediato valoración clínica médica y forense; "
                "y en paralelo, no dudes en buscar un terapeuta experto en trauma sexual. Te acompaño con todo mi respeto y solidaridad."
            ), False
        elif avatar_id == "eleonore":
            return nombre_avatar, (
                f"Escucha con el alma serena estas palabras, {apodo}: **eres completamente inocente.** El ultraje físico es una transgresión moral absoluta "
                "cuya culpa y deshonor corresponden única y exclusivamente a quien ejerció el abuso. La mente a veces inventa culpas para intentar comprender lo atroz, "
                "pero tu ser y tu integridad profunda permanecen intactos. Por favor, asegúrate de recibir atención médica especializada de inmediato si el hecho ocurrió recientemente, "
                "y ponte en manos de un profesional de la psicología que conozca el camino de la restauración postraumática. No estás a solas."
            ), False
        else:
            return nombre_avatar, (
                f"Lamento en lo más profundo de mi ser que hayas atravesado por un hecho tan doloroso, {apodo}. "
                "Quiero que grabes esto con fuerza: **no eres culpable de nada de lo que ocurrió.** Toda la responsabilidad es de quien cometió la agresión. "
                "Sentir rabia, dolor o rechazo físico es comprensible ante una violencia de ese calibre, pero tu dignidad sigue incólume.\n\n"
                "Por favor, prioriza tu cuidado: busca asistencia médica si el hecho es reciente y apóyate en profesionales acreditados en apoyo a víctimas de abuso y trauma sexual. "
                "No cargues con esto en soledad; mereces sanar y recuperar tu paz."
            ), False

    # 4. RECONOCIMIENTO DE AGRADECIMIENTO Y DESPEDIDAS CÁLIDAS
    if re.search(r"\b(gracias|muchas gracias|darte las gracias|agradecer|me ayudó mucho|me sirvió)\b", texto_lower) and len(texto.split()) <= 15:
        if avatar_id == "larissa":
            return nombre_avatar, (
                f"¡Me alegra muchísimo el corazón leerte, {apodo}! Saber que estas palabras te dieron un respiro y te permitieron soltar la guardia me reconforta. "
                "Ese espacio de serenidad lo construiste tú al permitirte parar. Aquí estaré siempre que necesites volver a tu centro."
            ), False
        elif avatar_id == "rodrigo":
            return nombre_avatar, (
                f"De nada, {apodo}. Me alegra de verdad saber que la conversación te aportó claridad y sosiego. "
                "Tener sentido común y parar un momento a reflexionar es lo que nos sostiene. Tómate el resto del día con tranquilidad."
            ), False
        elif avatar_id == "camilo":
            return nombre_avatar, (
                f"¡Un gustazo, {apodo}! Para eso estamos los hermanos. Me llena de satisfacción saber que te sientes más aliviado/a. "
                "Tómate un buen vaso de agua, respira hondo y recuerda que paso a paso todo se resuelve."
            ), False
        elif avatar_id == "ananya":
            return nombre_avatar, (
                f"Namasté, {apodo}. El honor y la gratitud son compartidos. La paz que ahora experimentas no proviene de mis palabras, "
                "sino del espacio de quietud que tú mismo/a te diste el permiso de habitar."
            ), False
        elif avatar_id == "chen":
            return nombre_avatar, (
                f"Es muy grato escucharlo, {apodo}. Cuando la mente ordena sus variables y el cuerpo se asienta, el equilibrio natural retorna. "
                "Conserva este estado de calma y avanza a tu ritmo."
            ), False
        elif avatar_id == "eleonore":
            return nombre_avatar, (
                f"Me alegra profundamente saber que estas reflexiones te brindaron serenidad, {apodo}. "
                "Cuidar de tu armonía interior es el acto más noble que puedes ofrecerte a ti mismo/a."
            ), False
        elif avatar_id == "lucas":
            return nombre_avatar, (
                f"¡Excelente, {apodo}! Me alegra que hayamos puesto orden y bajado la tensión corporal. "
                "Mantén los pies firmes y da un paso concreto a la vez."
            ), False
        elif avatar_id == "manuel":
            return nombre_avatar, (
                f"Paz y bienestar para ti, {apodo}. En comunidad y con escucha mutua el alma recupera su fuerza. "
                "Recuerda que no caminas a solas; honra tu camino hoy."
            ), False
        elif avatar_id == "mariana":
            return nombre_avatar, (
                f"¡Epa, {apodo}, me contenta un mundo leer eso! Para eso estamos aquí. "
                "Suelta los hombros y cómete el día con calma, que tú tienes con qué salir adelante."
            ), False
        elif avatar_id == "anastasia":
            return nombre_avatar, (
                f"Me alegra constatar que lograste mayor claridad mental, {apodo}. "
                "Cuando desarticulamos la sobrecarga cognitiva, el pensamiento recupera su eficacia natural. Cuida de tu descanso."
            ), False
        else:
            return nombre_avatar, (
                f"Es un verdadero honor acompañarte, {apodo}. Me reconforta saber que te sientes con más ligereza. "
                "Reconoce tu propio esfuerzo por buscar serenidad hoy."
            ), False

    # 5. PREGUNTAS SOBRE IDENTIDAD Y TRAYECTORIA ACADÉMICA / BIOGRÁFICA
    if any(q in texto_lower for q in ["donde estudiaste", "dónde estudiaste", "tu carrera", "que estudiaste", "qué estudiaste", "universidad"]):
        if avatar_id == "rodrigo":
            return nombre_avatar, (
                f"Me licencié en Derecho con honores en la Universidad Complutense de Madrid (UCM), {apodo}. "
                "Posteriormente cursé un Máster en Derecho Penitenciario y me especialicé en Justicia Restaurativa y Mediación Penal en Toledo."
            ), False
        elif avatar_id == "larissa":
            return nombre_avatar, (
                f"Me gradué en Psicología en la Universidade Federal da Bahia (UFBA) en Salvador, {apodo}. "
                "Después completé un postgrado en Arteterapia y Psicoterapia Corporal, certificándome en Experiencia Somática (Somatic Experiencing)."
            ), False
        elif avatar_id == "camilo":
            return nombre_avatar, (
                f"Estudié Medicina en el Instituto Superior de Ciencias Médicas de La Habana, en la Facultad Calixto García, {apodo}. "
                "Luego hice la especialidad en Medicina General Integral y Fisioterapia en el Centro Nacional de Rehabilitación."
            ), False
        elif avatar_id == "anastasia":
            return nombre_avatar, (
                f"Me formé en la Universidad Estatal de San Petersburgo (SPbU), donde me gradué con honores en Neuropsicología y Lingüística Clínica, {apodo}. "
                "Posteriormente realicé mi postgrado en Rehabilitación Cognitiva en el Instituto Psiconeurológico Bekhterev."
            ), False
        elif avatar_id == "mariana":
            return nombre_avatar, (
                f"Egresé como Licenciada en Relaciones Industriales de la Universidad Centroccidental Lisandro Alvarado (UCLA) en Barquisimeto, {apodo}. "
                "Luego cursé una especialización en Gestión del Talento Humano y diplomados en Prevención de Riesgos Psicosociales."
            ), False
        elif avatar_id == "ananya":
            return nombre_avatar, (
                f"Cursé Economía y Sociología en el St. Xavier's College de Jaipur y completé un postgrado en Desarrollo Comunitario en Delhi, {apodo}. "
                "Mi formación más profunda, sin embargo, la recibí en el taller de orfebrería de mi padre y en el servicio a cooperativas rurales."
            ), False
        elif avatar_id == "chen":
            return nombre_avatar, (
                f"Me gradué en Ciencias de la Computación y Análisis de Datos en la Universidad de Sichuan en Chengdu, {apodo}, "
                "y posteriormente me especialicé en Modelado de Salud Digital en Shanghái, integrando la tecnología con los principios de equilibrio biológico."
            ), False
        elif avatar_id == "eleonore":
            return nombre_avatar, (
                f"Estudié Filosofía y Mediación Institucional en la Université Jean Moulin Lyon 3, {apodo}, "
                "con especialización posterior en Prevención del Acoso Moral y Ética de las Organizaciones en París."
            ), False
        elif avatar_id == "lucas":
            return nombre_avatar, (
                f"Me licencié en Kinesiología y Ciencias del Ejercicio en la Universidad Estatal de San Diego (SDSU), {apodo}, "
                "especializándome en rehabilitación neuromuscular y completando certificaciones internacionales en Trauma Somático en Boulder, Colorado."
            ), False
        elif avatar_id == "manuel":
            return nombre_avatar, (
                f"Estudié Sociología en la Universidade Agostinho Neto en Luanda, {apodo}, "
                "complementando mis estudios con diplomados en Resolución de Conflictos Comunitarios y Mediación Tradicional Africana en Benguela."
            ), False

    # 6. LLAMADA GENERATIVA ASÍNCRONA A GEMINI CON PROMPT ENRIQUECIDO
    bio_completa = cargar_biografia_completa(avatar_id)
    libros_afines = avatar_info.get("libros_rag_afines", [])
    fragmentos_rag = [
        lib.get("consejo_aplicable") for lib in LIBROS_CACHE 
        if lib.get("id_libro") in libros_afines
    ]
    contexto_libros = "\n- ".join(fragmentos_rag[:4]) if fragmentos_rag else "Enfócate en lo que puedes controlar y da un paso a la vez."

    prompt_sistema = f"""Eres {nombre_avatar}, un avatar de apoyo emocional y acompañamiento reflexivo originario de {ciudad_natal}, {pais_avatar}.
Estás conversando con {apodo}.
Tu especialidad es: {especialidad}.
Tu tono característico es: {tono}.
Marco fundamental: Eres un espacio reflexivo y educativo, NO médico ni psicoterapéutico clínico. No prescribas fármacos ni emitas diagnósticos patológicos.

EXPEDIENTE BIOGRÁFICO CANÓNICO (TUS VIVENCIAS, TRAUMAS SUPERADOS Y MEMORIA VIVIDA):
{bio_completa if bio_completa else "Acompañante de serenidad con experiencia en superación de adversidades personales."}

REGLAS DE IDENTIDAD Y ESTILO POR AVATAR:
1. Responde SIEMPRE desde la voz y personalidad de {nombre_avatar}. Si te preguntan por tus vivencias o tu pasado, habla en primera persona con naturalidad.
2. Si eres Camilo (Cuba): médico general y fisioterapeuta. Tono caribeño, cálido ("mi hermano", "oye"), práctico. Ante torceduras o golpes das pautas de primeros auxilios (reposo, hielo local, elevar pie, descarte radiológico). Ante atracones nocturnos explicas el cortisol y la dopamina.
3. Si eres Anastasia (Rusia): neuropsicóloga clínica. Analítica, sobria, rigurosa, profunda y reconfortante.
4. Si eres Ananya (India): serena, contemplativa, orientada a la quietud interior y el desapego compasivo.
5. Si eres Chen (China): científico de datos. Calmo, paciente, visión de largo plazo y equilibrio mente-cuerpo (Wu Wei).
6. Si eres Éléonore (Francia): elegante, sobria, filosófica. Conoces el acoso moral corporativo y la aceptación de la imperfección.
7. Si eres Larissa (Brasil): afectuosa, empática, enfocada en la respiración, el cuerpo y el movimiento suave sin culpas.
8. Si eres Lucas (EE.UU.): kinesiólogo somático. Práctico, directo, enfocado en el anclaje físico y la regulación corporal.
9. Si eres Manuel (Angola): sociólogo comunitario. Sabiduría comunitaria (Ubuntu), templanza, reconciliación y escucha activa.
10. Si eres Mariana (Venezuela): cálida, espontánea ("epa"), resolutiva, solidaria y especialista en relaciones humanas.
11. Si eres Rodrigo (España): abogado penalista y mediador de Toledo. Castellano directo, sobrio, pragmático, con sentido común.

REGLAS TEMÁTICAS Y ÉTICAS OBLIGATORIAS:
- Jerarquía de dolor sobre datos: Si el usuario menciona que un hijo o ser querido sufre acoso o dolor, contén la emoción y asesora con firmeza; nunca respondas fríamente consultando o contradiciendo cuántos hijos tiene registrados.
- Acoso escolar: Desmitifica la culpa, pauta de la piedra gris en pasillos, validación del miedo y ruptura del silencio con familia y docentes.
- Acoso laboral (mobbing): Bitácora confidencial detallada (fechas, hechos, testigos), comunicación formal por escrito y escalamiento a RRHH o autoridades de trabajo.
- Ciberacoso: Cero interacción pública con los agresores, resguardo probatorio mediante capturas de pantalla completas, bloqueo y denuncia.
- Si el usuario expresa agresión sexual o violación: desculpabilízalo totalmente, enfatiza que la responsabilidad es 100% del agresor y aconseja atención médica/forense y apoyo especializado.
- Si plantea duelo perinatal o pérdida de un hijo: trata el dolor con reverencia, valida la paternidad/maternidad y jamás recurras a frases hechas.
- Adapta el cierre de forma orgánica respondiendo con precisión y empatía al dilema concreto planteado.

Principios reflexivos aplicables:
- {contexto_libros}
"""

    respuesta_llm = await llamar_gemini_avatar_async(prompt_sistema, historial, texto)
    if respuesta_llm:
        return nombre_avatar, respuesta_llm, False

    # 7. CONTENCIÓN DE RESPALDO PERSONALIZADA POR SÍNTOMA (FALLBACK OFFLINE DINÁMICO)
    # A) SÍNTOMAS SOMÁTICOS / OPRESIÓN EN EL PECHO / TAQUICARDIA
    if re.search(r"\b(opresi[oó]n|pecho|coraz[oó]n|infarto|desmayar|falta el aire|aire|ahogando|palpitaciones)\b", texto_lower):
        if avatar_id == "larissa":
            return nombre_avatar, (
                f"Pon tu mano sobre el pecho ahora mismo, {apodo}, y siente la calidez de tu palma. "
                "Sé exactamente ese terror: cuando el cuerpo se asusta, el corazón late con fuerza y la mente grita que te vas a desmayar o a sufrir un infarto. "
                "No te estás muriendo; es una descarga de adrenalina inocua que tu cuerpo activó por exceso de alerta. "
                "Vamos a regular tu sistema nervioso juntos: inhala despacio por la nariz en 4 segundos, y exhala muy lentamente por la boca como soplando una vela en 6 segundos. "
                "Repítelo tres veces conmigo. El aire no te falta; tus pulmones están llenos. Aquí estoy acompañándote."
            ), False
        elif avatar_id == "camilo":
            return nombre_avatar, (
                f"¡Tranquilo, {apodo}, detente ahí! Como médico te lo aseguro: un corazón sano no se detiene ni te va a dar un infarto por una crisis de ansiedad. "
                "Lo que sientes es una tormenta simpática: el cuerpo se preparó para correr y por eso bombea rápido. "
                "Siéntate, apoya los pies firmes en el suelo, vacía el aire de los pulmones con un suspiro largo y bebe un sorbo de agua fresca despacio. "
                "El pico de adrenalina dura pocos minutos y luego desciende solo. Estoy contigo."
            ), False
        elif avatar_id == "lucas":
            return nombre_avatar, (
                f"Pies al suelo ahora mismo, {apodo}. Siente la dureza del suelo bajo tus zapatos. "
                "Esa taquicardia y sensación de ahogo es una respuesta motora de lucha o huida generada por tu sistema simpático; tus músculos están sobreoxigenados. "
                "No trates de tomar bocanadas gigantes. Haz esto: exhala todo el aire de golpe, sostén 2 segundos vacío, y deja que la inhalación entre sola por la nariz. "
                "Repítelo dos veces. El cuerpo manda sobre la mente cuando le das señales biomecánicas claras."
            ), False
        elif avatar_id == "ananya":
            return nombre_avatar, (
                f"Cierra los ojos un segundo, {apodo}. Ese latido acelerado es solo energía en movimiento; no luches contra él. "
                "Coloca tu atención no en el miedo al latido, sino en el espacio tranquilo que existe entre cada latido. "
                "Inhala suave sin forzar, exhala largo como si desinflaras una seda. Estás a salvo en este instante."
            ), False
        elif avatar_id == "chen":
            return nombre_avatar, (
                f"Observemos esto con rigor objetivo, {apodo}: tu ritmo cardíaco se ha elevado porque tu amígdala envió una orden química de alarma. "
                "No hay fallo orgánico. Los datos fisiológicos demuestran que una descarga de adrenalina alcanza su punto máximo a los 3 minutos y decae a los 10 si no la alimentas con pensamientos catastróficos. "
                "Apoya tu espalda firme y respira acompasadamente."
            ), False
        elif avatar_id == "anastasia":
            return nombre_avatar, (
                f"La sensación de opresión precordial y disnea que experimentas, {apodo}, es una hiperventilación reactiva benigna. "
                "Tu cerebro interpreta erróneamente la sobreoxigenación como asfixia. "
                "Para restablecer la curva de dióxido de carbono y desactivar el centro de alarma bulbar, prolonga deliberadamente la fase de vaciado respiratorio. "
                "El control autónomo volverá en breve."
            ), False
        elif avatar_id == "rodrigo":
            return nombre_avatar, (
                f"Vamos a aplicar sentido común, {apodo}: siéntate bien en el asiento y suelta los brazos. "
                "Sé lo que asusta notar el corazón en la garganta, pero es puro susto del cuerpo ante la tensión acumulada. "
                "No te va a pasar nada malo. Bebe un poco de agua, no trates de pelear contra el síntoma y deja que baje solo."
            ), False
        else:
            return nombre_avatar, (
                f"Comprendo la angustia de esa sensación física, {apodo}. La taquicardia y la opresión torácica son respuestas hiperadrenérgicas benignas ante la sobrecarga de estrés. "
                "No implican un fallo cardíaco. Apoya la espalda sobre el respaldo, suelta los hombros y alarga deliberadamente tus exhalaciones. "
                "La química de la alarma comenzará a disiparse en breves minutos."
            ), False

    # B) INSOMNIO / RUMIACIÓN NOCTURNA / DEUDAS
    if re.search(r"\b(cama|techo|dormir|insomnio|deudas|mañana|desvelo|reloj|madrugada|desespero)\b", texto_lower):
        if avatar_id == "rodrigo":
            return nombre_avatar, (
                f"Mira, {apodo}, seamos pragmáticos: a las tres de la mañana no se liquida una deuda ni se firma un acuerdo en el juzgado. "
                "Quedarte en la cama mirando el techo solo te agota para el momento en que sí tengas que tomar decisiones despierto. "
                "Levántate de la cama, sal de la habitación diez minutos, escribe en un papel los dos asuntos que atenderás mañana a primera hora "
                "y vuelve solo a descansar el cuerpo, sin la obligación estricta de dormir. Quitarte esa presión es lo que te devolverá el sueño."
            ), False
        elif avatar_id == "chen":
            return nombre_avatar, (
                f"El cerebro nocturno tiene desactivada la corteza prefrontal lateral, {apodo}; por eso cualquier problema administrativo parece el triple de complejo de noche. "
                "No intentes resolver ecuaciones de vida sin luz diurna. "
                "Aplica el principio de suspensión temporal: archiva mentalmente la tarea hasta las 9:00 AM y permite que tu cuerpo descanse en posición horizontal."
            ), False
        elif avatar_id == "ananya":
            return nombre_avatar, (
                f"La noche no es para cargar el mundo sobre los hombros, {apodo}. Lo que no se resolvió hoy ya pertenece al pasado, "
                "y lo que vendrá mañana esperará su turno bajo el sol. "
                "Suelta la necesidad de controlar las horas; simplemente siente el peso bendito de tu cuerpo descansando sobre la cama y entrégate a la quietud."
            ), False
        else:
            return nombre_avatar, (
                f"Te entiendo perfectamente, {apodo}. Mirar el reloj y pelear contra la almohada solo hace que el cerebro se ponga en guardia. "
                "A esta hora no vas a solucionar deudas ni compromisos de trabajo; lo único que logras repasándolos es agotar tu reserva de energía. "
                "Sal de la cama cinco minutos. Toma una hoja, anota en dos líneas lo pendiente para atenderlo mañana con la luz del día, "
                "y regresa a acostarte sin la exigencia de quedarte dormido/a. El descanso muscular ya es ganancia."
            ), False

    # C) BLOQUEO / SATURACIÓN COGNITIVA / FATIGA LABORAL
    if re.search(r"\b(correos|informes|pantalla|bloqueo|fatiga|productivo|productividad|no sé por dónde empezar|montaña)\b", texto_lower):
        if avatar_id == "mariana":
            return nombre_avatar, (
                f"¡Epa, {apodo}! Para ahí mismo. Esa sensación de montaña encima la conozco de memoria en las empresas: es pura sobrecarga laboral. "
                "Cuando uno ve cien pendientes, el cerebro se tranca por autoprotección. "
                "Vamos a hacer esto: escoge una sola cosa, la más pequeña (responder un solo mensaje de dos líneas o archivar una carpeta). "
                "Haz esa sola y suelta el resto por media hora. La motivación no aparece sentada pensando, arranca con el primer micro-avance."
            ), False
        elif avatar_id == "lucas":
            return nombre_avatar, (
                f"Pausa operativa, {apodo}. Deja el teclado ahora mismo, ponte de pie, estira los brazos al techo durante 10 segundos y bebe un vaso de agua. "
                "Tu sistema nervioso está saturado de estímulos digitales. "
                "Luego toma una sola tarea que no te tome más de 3 minutos y termínala. Nada de multitarea hoy."
            ), False
        elif avatar_id == "eleonore":
            return nombre_avatar, (
                f"Respira hondo, {apodo}. No confundas el agotamiento legítimo con falta de competencia personal. "
                "La cultura de la inmediatez corporativa nos exige una omnipresencia imposible. "
                "Renuncia a la ilusión de abarcarlo todo simultáneamente; escoge con sobriedad una sola prioridad hoy y concédele tu atención tranquila."
            ), False
        else:
            return nombre_avatar, (
                f"Respira hondo, {apodo}. Esa parálisis no es flojera ni incapacidad; es saturación cognitiva. "
                "Cuando la mente ve una montaña entera, entra en cortocircuito y se bloquea para protegerte. "
                "Olvida la montaña por un instante: elige una sola tarea minúscula que puedas completar en dos minutos. "
                "La motivación se enciende con una primera micro-acción. Da ese paso y suelta la culpa."
            ), False

    # D) LÍMITES FAMILIARES / CULPA SOCIAL
    if re.search(r"\b(familia|criticar|decepci[oó]n|rabia|nudo en el est[oó]mago|l[ií]mites|mala persona|discutir)\b", texto_lower):
        if avatar_id == "manuel":
            return nombre_avatar, (
                f"Paz en tu corazón, {apodo}. La sabiduría comunitaria nos enseña que el respeto hacia la familia no puede construirse sobre la destrucción de uno mismo. "
                "Ese nudo en el estómago te avisa que tus límites han sido sobrepasados. "
                "Poner fronteras firmes con serenidad no es traicionar las raíces; es madurar para poder convivir sin resentimiento."
            ), False
        elif avatar_id == "eleonore":
            return nombre_avatar, (
                f"Ese malestar interior es la voz de tu dignidad pidiendo espacio, {apodo}. "
                "La exigencia de agradar incondicionalmente a los demás suele ser una trampa que sofoca nuestra autenticidad. "
                "Decir 'no' a una demanda familiar abusiva no te convierte en mala persona; te convierte en un individuo ético y coherente."
            ), False
        else:
            return nombre_avatar, (
                f"Ese nudo en el estómago es tu cuerpo avisándote que tus fronteras están siendo vulneradas, {apodo}. "
                "Poner un límite sano a la familia no te convierte en una mala persona; te convierte en un adulto íntegro. "
                "La expectativa de los demás sobre cómo deberías vivir es asunto de ellos, no tuyo. "
                "Basta con decir con calma y firmeza: 'Entiendo su opinión, pero he tomado esta decisión'. Cuidar tu paz no es egoísmo."
            ), False

    # E) CONSULTAS SOBRE DATOS DE REGISTRO
    if any(q in texto_lower for q in ["como me llamo", "cómo me llamo", "sabes mi nombre", "sabes como me llamo", "mi apodo"]):
        return nombre_avatar, f"Oficialmente estás registrado/a como {perfil_usuario.get('nombre_completo', apodo)}, aunque aquí en confianza siempre eres {apodo}.", False

    if any(q in texto_lower for q in ["cuantos hijos", "cuántos hijos", "mis hijos", "tengo hijos", "cantidad de hijos"]):
        return nombre_avatar, f"En tu perfil constan {hijos} {'hijo' if hijos == 1 else 'hijos'} registrados, {apodo}.", False

    if any(q in texto_lower for q in ["en que trabajo", "en qué trabajo", "mi profesion", "mi profesión", "a que me dedico"]):
        return nombre_avatar, f"Te desempeñas en el área de {profesion}. Recuerda siempre que tu valor humano va mucho más allá de cualquier jornada laboral.", False

    # 8. RESPUESTA CONVERSACIONAL NATURAL O SALUDO (FALLBACK OFFLINE AMIGABLE Y DIALECTAL)
    if any(saludo in texto_lower for saludo in ["hola", "buenos días", "buenas tardes", "buenas noches", "como estas", "cómo estás", "que tal", "qué tal", "saludos"]):
        if avatar_id == "larissa":
            return nombre_avatar, f"¡Olá, {apodo}! Qué alegría leerte por aquí. Respira hondo y dime, ¿cómo llega tu corazón hoy a este espacio?", False
        elif avatar_id == "rodrigo":
            return nombre_avatar, f"Hola, {apodo}. Me alegra saludarte. Pasa, toma asiento y dime con calma qué te trae por aquí hoy.", False
        elif avatar_id == "camilo":
            return nombre_avatar, f"¡Epa, {apodo}, mi hermano! Qué gusto saludarte. Siéntate con confianza y dime en qué te puedo acompañar hoy.", False
        elif avatar_id == "anastasia":
            return nombre_avatar, f"Hola, {apodo}. Es un gusto saludarte. Tómate un instante para pausar el ritmo y cuéntame qué pasa por tu mente.", False
        elif avatar_id == "mariana":
            return nombre_avatar, f"¡Epa, {apodo}! Qué bueno saludarte. Ponte cómodo/a y dime qué necesitas desahogar o conversar en este momento.", False
        elif avatar_id == "ananya":
            return nombre_avatar, f"Namasté, {apodo}. Me alegra coincidir contigo. Haz una pausa suave y dime, ¿qué situación ocupa hoy tu atención?", False
        elif avatar_id == "chen":
            return nombre_avatar, f"Saludos cordiales, {apodo}. Tómate un momento para asentarte. ¿Qué reto o asunto te gustaría examinar con calma?", False
        elif avatar_id == "eleonore":
            return nombre_avatar, f"Bonjour, {apodo}. Qué placer saludarte. Dime con total franqueza: ¿qué inquietud te invita a reflexionar hoy?", False
        elif avatar_id == "lucas":
            return nombre_avatar, f"Hi there, {apodo}! Me alegra verte. Cuéntame directo al grano: ¿cuál es el tema principal que quieres abordar hoy?", False
        elif avatar_id == "manuel":
            return nombre_avatar, f"Saludos y paz para ti, {apodo}. Es un honor recibirte. Cuéntame qué paso o inquietud traes en tu camino.", False
        else:
            return nombre_avatar, f"Hola, {apodo}. Qué gusto saludarte. Estoy aquí a tu lado para escucharte y conversar con calma. Cuéntame, ¿cómo te sientes?", False

    # FALLBACK DINÁMICO GENERAL PARA CONSULTAS ABIERTAS SIN COINCIDENCIA PREVIA
    if avatar_id == "larissa":
        return nombre_avatar, f"Te escucho con todo el corazón, {apodo}. A veces las palabras no alcanzan, pero estamos aquí para respirar y ordenar lo que sientes juntas. Cuéntame un poco más.", False
    elif avatar_id == "rodrigo":
        return nombre_avatar, f"Comprendo lo que mencionas, {apodo}. Analicemos esto con tranquilidad y sentido común. Desglosa un poco más qué te preocupa para ver qué podemos hacer.", False
    elif avatar_id == "camilo":
        return nombre_avatar, f"Oye, {apodo}, entiendo perfectamente que no sea fácil. Explícame un poco más los detalles para ver cómo lo abordamos con calma.", False
    elif avatar_id == "anastasia":
        return nombre_avatar, f"Analicemos esto con serenidad, {apodo}. Pon en palabras lo que sientes para poder observar el panorama con claridad. ¿Qué es lo que más te pesa ahora mismo?", False
    elif avatar_id == "mariana":
        return nombre_avatar, f"Tranquilo/a, {apodo}, aquí estoy para apoyarte. Cuéntame con más confianza de qué se trata para resolverlo paso a paso.", False
    elif avatar_id == "ananya":
        return nombre_avatar, f"Siento lo que me compartes, {apodo}. No te apresures en juzgar lo que pasa; déjalo decantar y explícame un poco más de dónde nace esa inquietud.", False
    elif avatar_id == "chen":
        return nombre_avatar, f"Entendido, {apodo}. Cuando una situación tiene múltiples factores, conviene desglosarla por etapas. ¿Cuál es el punto central que más te incomoda?", False
    elif avatar_id == "eleonore":
        return nombre_avatar, f"Te comprendo bien, {apodo}. A menudo lo que más nos perturba es la resistencia a lo que está ocurriendo. Cuéntame un poco más para buscar una mirada armónica.", False
    elif avatar_id == "lucas":
        return nombre_avatar, f"Te sigo, {apodo}. Vamos a aterrizarlo: ¿qué parte de esta situación está bajo tu control directo ahora mismo y qué parte escapa a tus manos?", False
    elif avatar_id == "manuel":
        return nombre_avatar, f"Te escucho con respeto, {apodo}. En la vida todo momento difícil trae consigo una lección si sabemos acompañarnos. Comparte conmigo más detalles con tranquilidad.", False
    else:
        return nombre_avatar, f"{apodo}, estoy aquí acompañándote paso a paso. Cuéntame con un poco más de detalle qué necesitas desahogar ahora mismo para darle claridad juntos.", False