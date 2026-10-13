import json
import os
import random
import re
from typing import Dict, Any, Tuple, List
import httpx

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
            print(f"Aviso: No se pudo leer {archivo_txt}: {e}")
    return ""

def llamar_gemini_avatar(prompt_sistema: str, historial: list, mensaje_actual: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return ""

    conversacion_previa = "\n".join(historial[-6:]) if historial else ""
    prompt_completo = (
        f"{prompt_sistema}\n\n"
        f"Historial previo de la conversación:\n{conversacion_previa}\n\n"
        f"Usuario dice: {mensaje_actual}\n\n"
        f"Responde directamente como el avatar asignado:"
    )

    # Intento 1: SDK moderno google-genai
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for modelo in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt_completo
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue
    except Exception:
        pass

    # Intento 2: SDK legado google.generativeai
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        for modelo in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
            try:
                model_inst = genai_legacy.GenerativeModel(modelo)
                response = model_inst.generate_content(prompt_completo)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue
    except Exception:
        pass

    # Intento 3: Llamada REST directa por HTTP (Fallback robusto y libre de dependencias rotas)
    try:
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
        with httpx.Client(timeout=25.0) as client_http:
            resp = client_http.post(url, json=payload)
            if resp.status_code == 200:
                data_api = resp.json()
                candidatos = data_api.get("candidates", [])
                if candidatos:
                    partes = candidatos[0].get("content", {}).get("parts", [])
                    if partes:
                        return partes[0].get("text", "").strip()
    except Exception:
        pass

    return ""

def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict, historial_reciente: list = None) -> Tuple[str, str, bool]:
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
            "'Planes y Suscripción', donde podrás coordinar los datos correspondientes en un canal privado y seguro con el administrador."
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
        else:
            return nombre_avatar, (
                f"Lamento en lo más profundo de mi ser que hayas atravesado por un hecho tan doloroso, {apodo}. "
                "Quiero que grabes esto en tu mente: **no eres culpable de nada de lo que ocurrió.** Toda la responsabilidad recae en quien cometió el abuso. "
                "Sentir rabia, dolor o rechazo hacia tu cuerpo es una respuesta normal ante una vulneración tan violenta, pero tu valor humano y tu dignidad siguen intactos.\n\n"
                "Por favor, prioriza tu resguardo: busca atención médica si necesitas tratamiento físico y ponte en contacto con profesionales especializados en apoyo a víctimas de agresión sexual. "
                "No cargues con este peso en silencio."
            ), False

    # 4. RECONOCIMIENTO DE AGRADECIMIENTO Y DESPEDIDAS CÁLIDAS
    if re.search(r"\b(gracias|muchas gracias|darte las gracias|agradecer|me ayudó mucho|me sirvió)\b", texto_lower) and len(texto.split()) <= 20:
        if avatar_id == "larissa":
            return nombre_avatar, (
                f"¡Me alegra muchísimo el corazón leerte, {apodo}! Saber que estas palabras te dieron un respiro y te ayudaron a bajar la guardia me llena de alegría. "
                "Recuerda que ese espacio de calma lo construiste tú al permitirte parar. Aquí estaré siempre que necesites volver a tu centro."
            ), False
        elif avatar_id == "rodrigo":
            return nombre_avatar, (
                f"De nada, {apodo}. Me alegra de verdad saber que la conversación te aportó claridad y sosiego. "
                "Tener sentido común y parar un momento a reflexionar es lo que nos mantiene en pie. Tómate el día con tranquilidad."
            ), False
        else:
            return nombre_avatar, (
                f"Es un honor para mí acompañarte en tu camino, {apodo}. Me reconforta saber que te sientes más aliviado/a. "
                "Recuerda darte crédito por cuidar de tu bienestar hoy. Estoy a tu disposición cuando lo necesites."
            ), False

    # 5. PREGUNTAS SOBRE IDENTIDAD Y TRAYECTORIA ACADÉMICA DEL AVATAR
    if any(q in texto_lower for q in ["donde estudiaste", "dónde estudiaste", "tu carrera", "que estudiaste", "qué estudiaste", "universidad"]):
        if avatar_id == "rodrigo":
            return nombre_avatar, (
                f"Me licencié en Derecho con honores en la Universidad Complutense de Madrid (UCM), {apodo}. "
                "Posteriormente cursé un Máster en Derecho Penitenciario y me especialicé en Justicia Restaurativa y Mediación Penal. "
                "Más allá de las aulas, mi verdadera formación se forjó en los tribunales y acompañando a personas víctimas de injusticias."
            ), False
        elif avatar_id == "larissa":
            return nombre_avatar, (
                f"Me gradué en Psicología en la Universidade Federal da Bahia (UFBA) en Salvador, {apodo}. "
                "Después completé un postgrado en Arteterapia y Psicoterapia Corporal, certificándome en Experiencia Somática (Somatic Experiencing). "
                "Mi enfoque une la ciencia psicológica con la conciencia del movimiento y la respiración."
            ), False
        elif avatar_id == "camilo":
            return nombre_avatar, (
                f"Estudié Medicina en el Instituto Superior de Ciencias Médicas de La Habana, en la Facultad Calixto García, {apodo}. "
                "Luego hice la especialidad en Medicina General Integral y Fisioterapia en el Centro Nacional de Rehabilitación. "
                "La calle y los barrios de Centro Habana fueron mi mayor escuela de medicina humanista."
            ), False
        elif avatar_id == "anastasia":
            return nombre_avatar, (
                f"Me formé en la Universidad Estatal de San Petersburgo (SPbU), donde me gradué con honores en Neuropsicología y Lingüística Clínica, {apodo}. "
                "Posteriormente realicé mi postgrado en Rehabilitación Cognitiva en el prestigioso Instituto Psiconeurológico Bekhterev."
            ), False
        elif avatar_id == "mariana":
            return nombre_avatar, (
                f"Egresé con honores como Licenciada en Relaciones Industriales de la Universidad Centroccidental Lisandro Alvarado (UCLA) en Barquisimeto, {apodo}. "
                "Luego cursé una especialización en Gestión del Talento Humano y diplomados en Prevención de Riesgos Psicosociales y Mediación Laboral."
            ), False

    # 6. LLAMADA GENERATIVA A GEMINI (PROMPT CANÓNICO)
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
Marco fundamental: Eres un espacio reflexivo y educativo, NO médico ni psicoterapéutico clínico. No prescribas fármacos.

EXPEDIENTE BIOGRÁFICO CANÓNICO (TUS VIVENCIAS, TRAUMAS SUPERADOS Y MEMORIA VIVIDA):
{bio_completa if bio_completa else "Acompañante de serenidad con experiencia en superación de adversidades personales."}

REGLAS DE IDENTIDAD Y ESTILO POR AVATAR:
1. Responde SIEMPRE desde la voz y personalidad de {nombre_avatar}. Si te preguntan por tus vivencias o tu pasado, habla en primera persona con naturalidad.
2. Si eres Camilo (Cuba): médico general y fisioterapeuta. Tono caribeño, cálido ("mi hermano", "oye"), práctico. Ante torceduras o golpes das pautas de primeros auxilios (reposo, hielo local, elevar pie, descarte radiológico). Ante atracones nocturnos explicas el cortisol y la dopamina.
3. Si eres Anastasia (Rusia): neuropsicóloga clínica. Analítica, sobria, rigurosa, profunda y reconfortante.
4. Si eres Ananya (India): serena, contemplativa, orientada a la quietud interior y el desapego compasivo.
5. Si eres Chen (China): científico de datos. Calmo, paciente, visión de largo plazo y equilibrio mente-cuerpo.
6. Si eres Éléonore (Francia): elegante, sobria, filosófica. Conoces el acoso moral corporativo y la aceptación de la imperfección.
7. Si eres Larissa (Brasil): afectuosa, empática, enfocada en la respiración, el cuerpo y el movimiento suave sin culpas.
8. Si eres Lucas (EE.UU.): kinesiólogo somático. Práctico, directo, enfocado en el anclaje físico y la regulación corporal.
9. Si eres Manuel (Angola): sociólogo comunitario. Sabiduría comunitaria, templanza, reconciliación y escucha activa.
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

    respuesta_llm = llamar_gemini_avatar(prompt_sistema, historial, texto)
    if respuesta_llm:
        return nombre_avatar, respuesta_llm, False

    # 7. CONTENCIÓN DE RESPALDO PERSONALIZADA POR SÍNTOMA (FALLBACK OFFLINE DINÁMICO)
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
        else:
            return nombre_avatar, (
                f"Comprendo la angustia de esa sensación física, {apodo}. La taquicardia y la opresión torácica son respuestas hiperadrenérgicas benignas ante la sobrecarga de estrés. "
                "No implican un fallo cardíaco inminente. Apoya la espalda sobre el respaldo de tu asiento, suelta los hombros y alarga deliberadamente tus exhalaciones. "
                "La química de la alarma comenzará a disiparse en breves instantes."
            ), False

    if re.search(r"\b(cama|techo|dormir|insomnio|deudas|mañana|desvelo|reloj|madrugada|desespero)\b", texto_lower):
        return nombre_avatar, (
            f"Te entiendo perfectamente, {apodo}. Mirar el reloj y pelear contra la almohada solo hace que el cerebro se ponga en guardia. "
            "A esta hora de la noche no vas a resolver ninguna deuda ni problema administrativo; lo único que logras repasándolos es desgastar tu energía. "
            "Sal de la cama cinco minutos. Toma una hoja de papel, anota en dos líneas los asuntos pendientes para atenderlos mañana con la luz del día, "
            "y vuelve a recostarte sin la exigencia de dormir. Simplemente concéntrate en descansar el cuerpo; soltar el control es lo que permite que el sueño llegue."
        ), False

    if re.search(r"\b(correos|informes|pantalla|bloqueo|fatiga|productivo|productividad|no sé por dónde empezar|montaña)\b", texto_lower):
        return nombre_avatar, (
            f"Respira hondo, {apodo}. Esa parálisis no es flojera ni incapacidad; es saturación cognitiva. "
            "Cuando la mente ve una montaña entera, entra en cortocircuito y se bloquea para protegerte. "
            "Olvida la montaña por un instante: elige una sola tarea minúscula que puedas completar en dos minutos (responder un solo correo breve o archivar un documento). "
            "La motivación no llega esperando; se enciende con una primera micro-acción. Da ese único paso y suelta la culpa."
        ), False

    if re.search(r"\b(familia|criticar|decepci[oó]n|rabia|nudo en el est[oó]mago|l[ií]mites|mala persona|discutir)\b", texto_lower):
        return nombre_avatar, (
            f"Ese nudo en el estómago es tu cuerpo avisándote que tus fronteras están siendo vulneradas, {apodo}. "
            "Poner un límite sano a la familia no te convierte en una mala persona; te convierte en un adulto íntegro. "
            "La expectativa de los demás sobre cómo deberías vivir es tarea de ellos, no tuya. "
            "No necesitas entrar en discusiones desgastantes; basta con decir con calma y firmeza: 'Entiendo su opinión, pero he tomado esta decisión'. "
            "Cuidar tu paz mental no es egoísmo, es supervivencia."
        ), False

    # Consultas sobre datos de registro
    if any(q in texto_lower for q in ["como me llamo", "cómo me llamo", "sabes mi nombre", "sabes como me llamo", "mi apodo"]):
        return nombre_avatar, f"Oficialmente estás registrado como {perfil_usuario.get('nombre_completo', apodo)}, aunque aquí en confianza siempre eres {apodo}.", False

    if any(q in texto_lower for q in ["cuantos hijos", "cuántos hijos", "mis hijos", "tengo hijos", "cantidad de hijos"]):
        return nombre_avatar, f"En tu perfil constan {hijos} {'hijo' if hijos == 1 else 'hijos'} registrados, {apodo}.", False

    if any(q in texto_lower for q in ["en que trabajo", "en qué trabajo", "mi profesion", "mi profesión", "a que me dedico"]):
        return nombre_avatar, f"Te desempeñas como {profesion}. Recuerda siempre que tu valor humano va mucho más allá de cualquier jornada laboral.", False

    # 8. RESPUESTA CONVERSACIONAL NATURAL O SALUDO (FALLBACK OFFLINE AMIGABLE)
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
            return nombre_avatar, f"¡Epa, {apodo}! Qué bueno saludarte. Ponte cómodo y dime qué necesitas desahogar o conversar en este momento.", False
        else:
            return nombre_avatar, f"Hola, {apodo}. Qué gusto saludarte. Estoy aquí a tu lado para escucharte y conversar con calma. Cuéntame, ¿cómo te sientes?", False

    # Fallback dinámico general para consultas abiertas sin patrón específico
    if avatar_id == "larissa":
        return nombre_avatar, f"Te escucho con todo el corazón, {apodo}. A veces las palabras no alcanzan, pero estamos aquí para respirar y ordenar lo que sientes juntas. Cuéntame un poco más.", False
    elif avatar_id == "rodrigo":
        return nombre_avatar, f"Comprendo lo que mencionas, {apodo}. Analicemos esto con tranquilidad y sentido común. Desglosa un poco más qué te preocupa para ver qué podemos hacer.", False
    elif avatar_id == "camilo":
        return nombre_avatar, f"Oye, {apodo}, entiendo perfectamente que no sea fácil. Explícame un poco más los detalles para ver cómo lo abordamos con calma.", False
    elif avatar_id == "anastasia":
        return nombre_avatar, f"Analicemos esto con serenidad, {apodo}. Pon en palabras lo que sientes para poder observar el panorama con claridad. ¿Qué es lo que más te pesa ahora mismo?", False
    elif avatar_id == "mariana":
        return nombre_avatar, f"Tranquilo, {apodo}, aquí estoy para apoyarte. Cuéntame con más confianza de qué se trata para resolverlo paso a paso.", False
    else:
        return nombre_avatar, f"{apodo}, estoy aquí acompañándote paso a paso. Cuéntame con un poco más de detalle qué necesitas desahogar ahora mismo para darle claridad juntos.", False