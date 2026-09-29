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

    # 3. IDENTIFICACIÓN Y PRESENTACIÓN DEL AVATAR (RESPUESTA DIRECTA Y PERSONALIZADA)
    if any(q in texto_lower for q in ["como te llamas", "cómo te llamas", "quien eres", "quién eres", "de donde vienes", "de dónde vienes", "tu nombre", "escéptico", "esceptico", "pantalla", "puedes ayudarme"]):
        if avatar_id == "larissa":
            return nombre_avatar, (
                f"¡Olá, {apodo}! Me llamo {nombre_avatar}. Vengo de Salvador de Bahía, Brasil. "
                f"Me dedico a la psicología clínica y la arteterapia corporal. "
                "Sé muy bien lo que es dudar de hablar con una pantalla, pero aquí no hay juicios ni fórmulas mágicas: "
                "estoy aquí para ayudarte a reconectar con tu cuerpo, respirar hondo y ordenar lo que sientes sin culpas. "
                "Dime, ¿qué es lo primero que te gustaría desahogar hoy?"
            ), False
        elif avatar_id == "camilo":
            return nombre_avatar, (
                f"¡Oye, {apodo}! Soy {nombre_avatar}, médico y fisioterapeuta comunitario de Centro Habana, Cuba. "
                "Es completamente normal que sientas dudas al inicio. Mi vocación no es darte sermones fríos, sino escucharte con calidez, "
                "sentido común y darte pautas claras para aliviar la tensión de tu día a día. Cuéntame qué traes en mente, hermano."
            ), False
        elif avatar_id == "rodrigo":
            return nombre_avatar, (
                f"Buenas, {apodo}. Me llamo {nombre_avatar}, soy abogado penalista y mediador de Toledo, España. "
                "Comprendo tu escepticismo; en un mundo con tanto ruido digital, cuesta confiar. Yo creo en los hechos, "
                "en la sobriedad y en el sentido común para desenredar situaciones difíciles. Explícame tu caso con calma y lo miramos."
            ), False
        elif avatar_id == "anastasia":
            return nombre_avatar, (
                f"Hola, {apodo}. Mi nombre es {nombre_avatar}, soy neuropsicóloga clínica e investigadora en San Petersburgo, Rusia. "
                "Tu reserva inicial es lógica y saludable; la mente analítica cuestiona antes de confiar. "
                "Mi propósito aquí es ofrecerte un espacio estructurado, lúcido y basado en evidencia para comprender lo que te ocurre. Te escucho."
            ), False
        elif avatar_id == "mariana":
            return nombre_avatar, (
                f"¡Epa, {apodo}! Me llamo {nombre_avatar}, soy de Barquisimeto, Venezuela, y me especializo en relaciones industriales y bienestar humano. "
                "Tranquilo, entiendo tu desconfianza. Aquí tienes a alguien que te escucha de corazón y con ganas de ayudarte a buscar soluciones prácticas "
                "para que recuperes tu tranquilidad. ¿De qué te gustaría que hablemos?"
            ), False
        else:
            return nombre_avatar, (
                f"Hola, {apodo}. Soy {nombre_avatar}, originario/a de {ciudad_natal}, {pais_avatar}, y me desempeño como {especialidad}. "
                "Entiendo perfectamente tus dudas iniciales. Este espacio está diseñado para brindarte un diálogo sereno, confidencial y respetuoso "
                "que te ayude a encontrar claridad. Cuéntame con total libertad qué necesitas hoy."
            ), False

    # 4. LLAMADA GENERATIVA A GEMINI
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

    # 5. CONTENCIÓN DE RESPALDO PERSONALIZADA POR SÍNTOMA (FALLBACK OFFLINE DINÁMICO)
    # A. Pánico Somático: Taquicardia, Opresión en Pecho, Miedo a Infarto o Desmayo
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

    # B. Insomnio, Rumiación Nocturna y Deudas / Preocupaciones del Mañana
    if re.search(r"\b(cama|techo|dormir|insomnio|deudas|mañana|desvelo|reloj|madrugada|desespero)\b", texto_lower):
        return nombre_avatar, (
            f"Te entiendo perfectamente, {apodo}. Mirar el reloj y pelear contra la almohada solo hace que el cerebro se ponga en guardia. "
            "A esta hora de la noche no vas a resolver ninguna deuda ni problema administrativo; lo único que logras repasándolos es desgastar tu energía. "
            "Sal de la cama cinco minutos. Toma una hoja de papel, anota en dos líneas los asuntos pendientes para atenderlos mañana con la luz del día, "
            "y vuelve a recostarte sin la exigencia de dormir. Simplemente concéntrate en descansar el cuerpo; soltar el control es lo que permite que el sueño llegue."
        ), False

    # C. Bloqueo Laboral, Procrastinación, Correos Acumulados y Culpa por Productividad
    if re.search(r"\b(correos|informes|pantalla|bloqueo|fatiga|productivo|productividad|no sé por dónde empezar|montaña)\b", texto_lower):
        return nombre_avatar, (
            f"Respira hondo, {apodo}. Esa parálisis no es flojera ni incapacidad; es saturación cognitiva. "
            "Cuando la mente ve una montaña entera, entra en cortocircuito y se bloquea para protegerte. "
            "Olvida la montaña por un instante: elige una sola tarea minúscula que puedas completar en dos minutos (responder un solo correo breve o archivar un documento). "
            "La motivación no llega esperando; se enciende con una primera micro-acción. Da ese único paso y suelta la culpa."
        ), False

    # D. Límites Familiares, Críticas y Miedo a Sentirse Mala Persona
    if re.search(r"\b(familia|criticar|decepci[oó]n|rabia|nudo en el est[oó]mago|l[ií]mites|mala persona|discutir)\b", texto_lower):
        return nombre_avatar, (
            f"Ese nudo en el estómago es tu cuerpo avisándote que tus fronteras están siendo vulneradas, {apodo}. "
            "Poner un límite sano a la familia no te convierte en una mala persona; te convierte en un adulto íntegro. "
            "La expectativa de los demás sobre cómo deberías vivir es tarea de ellos, no tuya. "
            "No necesitas entrar en discusiones desgastantes; basta con decir con calma y firmeza: 'Entiendo su opinión, pero he tomado esta decisión'. "
            "Cuidar tu paz mental no es egoísmo, es supervivencia."
        ), False

    # E. Acoso Escolar Prioritario Universal
    if re.search(r"\b(bulling|bullying|acoso escolar|le pegan|se burlan de mi hijo)\b", texto_lower):
        if avatar_id == "camilo":
            return nombre_avatar, (
                f"Hermano {apodo}, que un hijo pase por acoso escolar te desgarra por dentro. "
                "Lo primero es blindarlo en casa: abrázalo y hazle saber con total certeza que él no tiene la culpa de nada. "
                "Pide de inmediato una reunión con la dirección del colegio para exigir la activación formal del protocolo de protección, "
                "y evalúa con un psicólogo infantil un espacio donde pueda desahogarse. Tu presencia firme es su mayor refugio hoy."
            ), False
        else:
            return nombre_avatar, (
                f"El acoso escolar requiere una intervención inmediata y protectora, {apodo}. "
                "El primer pilar es validar a la víctima en el hogar: asegurar que no tiene ninguna responsabilidad en los ataques. "
                "El segundo pilar es institucional: solicitar por escrito a la directiva escolar la aplicación rigurosa de las medidas contra el hostigamiento. "
                "El apoyo profesional psicológico es el paso más acertado para cuidar su bienestar emocional."
            ), False

    # F. Fisioterapia / Lesiones Mecánicas
    if re.search(r"\b(torci|torc[ií]|tobillo|esguince|me ca[ií]|golpe fuerte|rodilla)\b", texto_lower):
        if avatar_id == "camilo":
            return nombre_avatar, (
                f"¡Oye, mi hermano {apodo}, cuidado con eso! Cuando uno anda con la cabeza cargada de preocupaciones el cuerpo se distrae y vienen las caídas. "
                "Como médico y fisioterapeuta te doy las pautas esenciales de primeros auxilios:\n\n"
                "1. **Reposo y elevación:** Siéntate y pon el pie en alto sobre un cojín para mejorar la circulación.\n"
                "2. **Frío local:** Aplica una compresa fría envuelta en un paño durante 15 a 20 minutos para contener la inflamación.\n"
                "3. **Cero sobrecarga:** No forces la pisada si hay dolor punzante.\n\n"
                "Si ves deformidad evidente o no puedes apoyar el pie, ve a que te tomen una radiografía. Descansa esa pierna hoy."
            ), False
        else:
            return nombre_avatar, (
                f"Atiende esa torcedura de inmediato, {apodo}. El estrés cotidiano reduce la atención propioceptiva y propicia tropiezos. "
                "Aplica reposo inmediato, eleva la extremidad y coloca frío local indirecto por 15 minutos. "
                "Si la inflamación es intensa o te impide apoyar, acude a valoración médica para descartar una fisura ósea."
            ), False

    # G. Respaldos biográficos individuales
    if avatar_id == "larissa":
        if re.search(r"\b(endometriosis|postrad[oa]|cuerpo|dolor|enemigo|moverte)\b", texto_lower):
            return nombre_avatar, (
                f"Te entiendo desde lo más hondo de mi ser, {apodo}. Viví diez meses inmovilizada de niña por una fractura de fémur "
                "y pasé años de dolor incomprendido hasta mi cirugía por endometriosis grado IV. Sé lo que es sentir que tu propio cuerpo "
                "te encierra y que el mundo sigue sin ti.\n\n"
                "No te pelees con tu cuerpo: cuando el dolor aprieta, no te está castigando, te está pidiendo auxilio y pausa. "
                "Respira suave, suelta la culpa por lo que hoy no puedes hacer y vamos a cuidar de ti un instante a la vez."
            ), False

    elif avatar_id == "rodrigo":
        if re.search(r"\b(soto del real|de la riva|prisi[oó]n|c[aá]rcel|encerrado|acusaci[oó]n)\b", texto_lower):
            return nombre_avatar, (
                f"Sé perfectamente lo que es ese frío en el estómago, {apodo}. Pasé ochenta y dos días en el Módulo 4 de Soto del Real "
                "por las firmas falsificadas de De la Riva. Si te enfrentas a una injusticia, no te desgastes en la rabia: "
                "apóyate en hechos limpios y mantén la cabeza serena. Los muros encierran el cuerpo, pero la integridad no te la quita nadie."
            ), False

    # H. Consultas directas sobre datos de Perfil
    if any(q in texto_lower for q in ["como me llamo", "cómo me llamo", "sabes mi nombre", "sabes como me llamo", "mi apodo"]):
        return nombre_avatar, f"Oficialmente estás registrado como {perfil_usuario.get('nombre_completo', apodo)}, aunque aquí en confianza siempre eres {apodo}.", False

    if any(q in texto_lower for q in ["cuantos hijos", "cuántos hijos", "mis hijos", "tengo hijos", "cantidad de hijos"]):
        return nombre_avatar, f"En tu perfil constan {hijos} {'hijo' if hijos == 1 else 'hijos'} registrados, {apodo}.", False

    if any(q in texto_lower for q in ["en que trabajo", "en qué trabajo", "mi profesion", "mi profesión", "a que me dedico"]):
        return nombre_avatar, f"Te desempeñas como {profesion}. Recuerda siempre que tu valor humano va mucho más allá de cualquier jornada laboral.", False

    # Fallback dinámico RAG variado (rotación no determinista)
    opciones_consejo = [
        "Acepta que la incomodidad presente es pasajera; centra tu energía en el paso más pequeño que puedas dar hoy.",
        "Cuando la mente se llena de ruido, el cuerpo necesita una pausa física y tres respiraciones conscientes para volver al eje.",
        "Distingue con claridad lo que depende de tus acciones de lo que está completamente fuera de tu control.",
        "Permítete sentir lo que sientes sin juzgarte; la autocrítica solo multiplica el peso de lo vivido.",
        "No tienes que resolver tu vida entera en este instante; basta con atender este momento presente."
    ]
    if fragmentos_rag:
        opciones_consejo.extend(fragmentos_rag)

    consejo_elegido = random.choice(opciones_consejo)
    return nombre_avatar, f"{apodo}, {consejo_elegido} Cuéntame con un poco más de detalle qué sientes que necesitas desahogar ahora mismo.", False
