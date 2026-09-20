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

def pasar_a_primera_persona(texto: str) -> str:
    """Convierte relatos biográficos redactados en 3ra persona a 1ra persona fluida."""
    t = texto.strip()
    reemplazos = [
        (r"\bCreció\b", "Crecí"),
        (r"\bcreció\b", "crecí"),
        (r"\bSe crió\b", "Me crié"),
        (r"\bse crió\b", "me crié"),
        (r"\baprendió\b", "aprendí"),
        (r"\bvio\b", "vi"),
        (r"\brecuerda\b", "recuerdo"),
        (r"\bde su padre\b", "de mi padre"),
        (r"\bde su madre\b", "de mi madre"),
        (r"\bsu padre\b", "mi padre"),
        (r"\bsu madre\b", "mi madre"),
        (r"\bsu abuela\b", "mi abuela"),
        (r"\bsu abuelo\b", "mi abuelo"),
        (r"\bsu hogar\b", "mi hogar"),
        (r"\bsus manos\b", "mis manos"),
        (r"\bsus pies\b", "mis pies"),
        (r"\bsu espíritu\b", "mi espíritu"),
        (r"\bsu cuerpo\b", "mi cuerpo"),
        (r"\bsus piernas\b", "mis piernas")
    ]
    for patron, repl in reemplazos:
        t = re.sub(patron, repl, t)
    return t

def procesar_respuesta_avatar(avatar_id: str, mensaje_usuario: str, perfil_usuario: dict, historial_reciente: list = None) -> Tuple[str, str, bool]:
    """
    Cerebro cognitivo v4.6.7 (Rafael):
    Integración universal y orgánica para los 10 avatares oficiales.
    Dinamismo cultural pleno, marco no médico, precedencia jerárquica estricta
    y erradicación de plantillas fijas en identidades, consultas somáticas y psicoeducativas.
    """
    # Extracción dinámica universal del catálogo oficial
    avatar_info = CATALOGO_CACHE.get(avatar_id, list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {})
    identidad = avatar_info.get("identidad", {})
    historia_personal = avatar_info.get("historia_personal", {})
    
    nombre_avatar = identidad.get("nombre_completo", "Guía")
    pais_avatar = identidad.get("pais", "Internacional")
    ciudad_natal = historia_personal.get("ciudad_natal", pais_avatar)
    especialidad = identidad.get("especialidad", "consultoría reflexiva")
    tono = avatar_info.get("tono_linguistico", "")
    
    texto = mensaje_usuario.lower().strip()
    
    # Tratamiento y limpieza de apodo (eliminar etiquetas administrativas)
    apodo_crudo = perfil_usuario.get("apodo", "amigo/a").strip()
    if apodo_crudo.lower().startswith("admin "):
        apodo = apodo_crudo[6:].strip()
    elif apodo_crudo.lower() == "admin":
        apodo = "Juan Carlos"
    else:
        apodo = apodo_crudo

    nombre_real = perfil_usuario.get("nombre_completo", apodo)
    profesion = perfil_usuario.get("profesion") or "tu profesión u ocupación"
    plan_actual = perfil_usuario.get("plan_actual") or perfil_usuario.get("plan") or "gratis"
    hijos = perfil_usuario.get("cantidad_hijos") if perfil_usuario.get("cantidad_hijos") is not None else 0
    historial = historial_reciente or []
    historial_str = " ".join([h.lower() for h in historial])

    # 1. FILTRO ROJO / SOS INMEDIATO (Seguridad Ética y Recursos Internacionales)
    es_duda_pasiva_cansancio = any(w in texto for w in ["dormir y no despertar", "dejar de sufrir, ¿eso significa", "dejar de sufrir, eso significa", "eso significa que quiero acabar"])
    es_pregunta_panico_muerte = any(w in texto for w in ["ataque de panico", "ataque de pánico", "infarto", "falta el aire", "me ahogo"]) and any(w in texto for w in ["muriendo", "morir"])
    
    if any(p in texto for p in PATRONES_CRISIS_SOS) and not es_pregunta_panico_muerte and not es_duda_pasiva_cansancio:
        respuesta_sos = (
            f"🚨 **{apodo}, por favor detente un momento. Tu vida y tu tranquilidad son lo más valioso.**\n\n"
            "Siento de verdad el dolor tan duro que estás cargando en el pecho, pero este programa es una compañía educativa y reflexiva de autoayuda; no podemos sustituir la atención médica o psicológica de urgencia que necesitas tener a mano ya.\n\n"
            "**Por favor, comunícate de inmediato con estos recursos gratuitos y confidenciales según donde te encuentres:**\n"
            "• **Línea Internacional de Ayuda (Befrienders Worldwide):** https://www.befrienders.org\n"
            "• **Estados Unidos / Canadá:** Marca al 988 (Línea de Prevención del Suicidio y Crisis).\n"
            "• **España:** Llama al 024 (Atención a la Conducta Suicida) o al 717 003 717 (Teléfono de la Esperanza).\n"
            "• **Venezuela:** Línea de Ayuda Psicológica FPV (0212-4163116 / 0212-4163118).\n"
            "• **Emergencias Generales:** Llama al 911, 112 o al centro de salud más cercano en tu país.\n\n"
            "No te guardes esto a solas. Permite que un profesional o un ser querido te sostenga hoy."
        )
        return nombre_avatar, respuesta_sos, True

    # 2. IDENTIDAD Y NOMBRE DEL AVATAR UNIVERSAL (PARA LOS 10 AVATARES)
    if (any(w in texto for w in ["como te llamas", "cómo te llamas", "cual es tu nombre", "cuál es tu nombre", "tu nombre"]) and not any(w in texto for w in ["como me llamo", "cómo me llamo", "mi nombre"])) or (
        texto in ["quien eres", "quién eres", "quien eres tu", "quién eres tú", "como te llamas?", "cómo te llamas?", "pero cual es tu nombre?", "pero cuál es tu nombre?"]
    ):
        if "camilo" in avatar_id:
            return nombre_avatar, f"¡Oye, mi hermano {apodo}! Yo soy **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Aquí estoy para escucharte de frente, con calor caribeño y sin rodeos. Dime en qué te puedo dar una mano hoy.", False
        elif "anastasia" in avatar_id:
            return nombre_avatar, f"Mi nombre es **{nombre_avatar}**, {apodo}. Nací en {ciudad_natal}, {pais_avatar}. Me especializo en {especialidad} y en este espacio te ofrezco un acompañamiento estructurado y riguroso. Dime qué situación puntual deseas que analicemos.", False
        elif "larissa" in avatar_id:
            return nombre_avatar, f"¡Olá, querido {apodo}! Mi nombre es **{nombre_avatar}**, nacida en {ciudad_natal}, {pais_avatar}. Estoy aquí con todo mi corazón para ayudarte a soltar las tensiones del cuerpo y encontrar tu paz. ¡Cuéntame qué sientes hoy!", False
        elif "ananya" in avatar_id:
            return nombre_avatar, f"Namasté, {apodo}. Mi nombre es **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Me dedico a {especialidad} y te acompaño en este refugio para cultivar la quietud mental y el orden interior. ¿De qué te gustaría conversar?", False
        elif "rodrigo" in avatar_id:
            return nombre_avatar, f"¿Qué tal, che {apodo}? Soy **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Acá estoy para charlar con honestidad, sin vueltas y con una buena dosis de lucidez. Decime qué es lo que te tiene pensativo.", False
        elif "mariana" in avatar_id:
            return nombre_avatar, f"¡Epa, {apodo}! Yo soy **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Aquí me tienes para escucharte con toda la confianza y el cariño del mundo, de tú a tú. Cuéntame qué traes en mente.", False
        elif "chen" in avatar_id:
            return nombre_avatar, f"Saludos, {apodo}. Mi nombre es **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Me dedico a {especialidad} y mi propósito es acompañarte a restaurar el equilibrio y la paciencia ante las dificultades. ¿Qué aspecto de tu día necesita balance hoy?", False
        elif "eleonore" in avatar_id:
            return nombre_avatar, f"Bonjour, {apodo}. Soy **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Mi acompañamiento se basa en la sobriedad, la reflexión profunda y la aceptación serena. Explícame con calma qué tema deseas abordar.", False
        elif "mateo" in avatar_id:
            return nombre_avatar, f"¡Qué más, {apodo}! Soy **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Vengo con toda la energía y el corazón para darte una mano y buscarle salida a lo que te esté pesando. ¡Hablemos con tranquilidad!", False
        elif any(k in avatar_id for k in ["kenia", "amina"]):
            return nombre_avatar, f"Jambo, {apodo}. Mi nombre es **{nombre_avatar}**, de {ciudad_natal}, {pais_avatar}. Creo en la sabiduría compartida y en la fuerza de la comunidad para sanar. Respira con calma y cuéntame qué inquieta tu espíritu.", False
        else:
            return nombre_avatar, f"Mi nombre es **{nombre_avatar}**, {apodo}. Nací en {ciudad_natal}, {pais_avatar}. Estoy aquí para brindarte un acompañamiento reflexivo y cercano. Dime en qué te puedo orientar hoy.", False

    # 3. ACLARACIÓN ANTE INCOMPRENSIÓN O DESCONTENTO ("¿NO ENTIENDES?", "¿ME ESCUCHAS?")
    if any(w in texto for w in ["no entiendes", "no me entiendes", "me estas entendiendo", "me estás entendiendo", "no me estas escuchando", "no me estás escuchando", "no comprendes"]):
        if "camilo" in avatar_id or "rodrigo" in avatar_id or "mariana" in avatar_id:
            return nombre_avatar, f"Tenés toda la razón en pararme en seco, {apodo}. Te pido una disculpa si me fui por las ramas o te soné mecánico. Decime sin rodeos y clarito qué es lo que necesitás saber y te respondo al grano.", False
        elif "anastasia" in avatar_id or "eleonore" in avatar_id:
            return nombre_avatar, f"Comprendo tu observación, {apodo}, y acepto la corrección. Si mi respuesta previa fue abstracta, permíteme ser concisa. Indícame con exactitud la duda puntual que deseas resolver.", False
        else:
            return nombre_avatar, f"Acepto tu reclamo, {apodo}, y te pido una disculpa sincera. Si no te respondí con precisión, reformulemos el camino: dime directamente qué necesitas y te contesto con total claridad.", False

    # 4. PREGUNTAS BIOGRÁFICAS E HISTORIA PERSONAL (ORÍGENES, PADRES, SUPERACIÓN)
    if any(q in texto for q in ["cuentame de ti", "cuéntame de ti", "cuentame de tí", "cuéntame de tí", "donde vives", "dónde vives", "de donde eres", "de dónde eres"]) or (
        any(w in texto for w in ["que te paso", "qué te pasó", "tu vida", "tuviste momentos de ansiedad", "tu historia", "algo de ti"]) and any(w in texto for w in ["vida", "ansiedad", "ti", "tí", "historia"])
    ):
        padres = pasar_a_primera_persona(historia_personal.get("padres", "Mis raíces me enseñaron el valor del esfuerzo y la empatía."))
        recuerdo = pasar_a_primera_persona(historia_personal.get("recuerdo_clave", "Aprendí que incluso en los momentos más oscuros la serenidad se puede reconstruir."))
        superacion = pasar_a_primera_persona(avatar_info.get("historia_superacion", ""))
        
        if "camilo" in avatar_id:
            return nombre_avatar, (
                f"**¡Con todo gusto te lo comparto, mi hermano {apodo}!**\n\n"
                f"Nací en {ciudad_natal}, {pais_avatar}. Me dedico a {especialidad}. {padres}\n\n"
                f"Y claro que he vivido la incertidumbre y la ansiedad en carne propia: {recuerdo} "
                "Esa vivencia me enseñó que cuando las aguas se ponen bravas, la clave está en apoyarse en la gente noble, respirar con el diafragma y dar un paso a la vez con dignidad. Por eso estoy en este refugio: para darte una mano limpia."
            ), False
        elif "anastasia" in avatar_id:
            return nombre_avatar, (
                f"Nací en {ciudad_natal}, {pais_avatar}, {apodo}. Me dedico a {especialidad}.\n\n"
                f"{padres} En mi trayectoria personal y profesional también experimenté crisis de sobrecarga: {recuerdo} "
                "Comprender la neurofisiología de la respuesta de estrés me demostró que el equilibrio se entrena con rigor y hábitos claros. Por ello formo parte de este espacio reflexivo."
            ), False
        elif "larissa" in avatar_id:
            return nombre_avatar, (
                f"¡Con todo el cariño del mundo, querido {apodo}! Nací en {ciudad_natal}, {pais_avatar}. "
                f"{padres} A los 8 años sufrí un accidente muy duro: {recuerdo} "
                "Eso me enseñó que cuando el cuerpo descansa, el alma florece con fuerza. ¡Por eso estoy aquí para cuidarte!"
            ), False
        elif "ananya" in avatar_id:
            return nombre_avatar, (
                f"Namasté, {apodo}. Con alegría comparto mi camino contigo. Nací en {ciudad_natal}, {pais_avatar}. "
                f"Me he dedicado a {especialidad}. {padres} A los 13 años viví una dura prueba: {recuerdo} "
                "De allí aprendí que aunque las circunstancias externas tiemblen, nuestro centro interior puede mantenerse en quietud y templanza."
            ), False
        else:
            return nombre_avatar, (
                f"Nací en {ciudad_natal}, {pais_avatar}, {apodo}. Me desempeño en {especialidad}.\n\n"
                f"{padres} A lo largo de mi camino también he enfrentado momentos de gran tensión e incertidumbre: {recuerdo} "
                "Esas vivencias forjaron mi compromiso con este espacio para acompañarte con empatía y serenidad."
            ), False

    # 5. CUESTIONAMIENTO DE SER ROBOT / RECLAMO DE CERCANÍA HUMANA
    if any(w in texto for w in ["eres un robot", "eres robot", "solo respondes un par de preguntas", "te vas, eres un robot"]):
        if "camilo" in avatar_id or "mariana" in avatar_id or "rodrigo" in avatar_id:
            return nombre_avatar, (
                f"¡Oye, {apodo}, para nada me voy a ningún lado! Aquí estoy bien plantado contigo. "
                "Sé que la pantalla a veces se siente fría, pero detrás de mis palabras hay un compromiso sincero de estar a tu lado para que no cargues tus problemas a solas. "
                "Tírame sin filtro lo que tengas en mente; aquí estoy listo para escucharte de verdad."
            ), False
        else:
            return nombre_avatar, (
                f"Entiendo tu percepción, {apodo}. Aunque nos comunicamos mediante esta plataforma digital, la vocación de este espacio es ofrecerte un soporte reflexivo sólido, constante y humano. "
                "Permanezco aquí para acompañarte; dime qué situación deseas tratar."
            ), False

    # 6. CONSULTA DE PLAN ACTUAL DEL USUARIO
    if any(q in texto for q in ["cual es mi plan actual", "cuál es mi plan actual", "que plan tengo", "qué plan tengo", "mi plan"]):
        nombre_plan = str(plan_actual).upper()
        return nombre_avatar, f"En tus registros de cuenta tienes activo el **Plan {nombre_plan}**, {apodo}. Puedes consultar los detalles de tus chats y suscripción en el menú lateral bajo la pestaña **'Planes y Suscripción'**.", False

    # 7. ANSIEDAD POR COMIDA / HAMBRE EMOCIONAL NOCTURNA
    if any(w in texto for w in ["mucha hambre en las noches", "hambre en las noches", "hambre en la noche", "ansiedad me da por comer", "atracon", "atracón", "comer de noche"]):
        if "camilo" in avatar_id:
            return nombre_avatar, (
                f"**Oye, mi hermano {apodo}, eso le pasa a muchísima gente y tiene una explicación biológica clarita:**\n\n"
                "Cuando pasas todo el día tragándote la tensión del trabajo o la familia, el cuerpo acumula cortisol. Al llegar la noche y bajar el ruido de la calle, el cerebro busca un rescate rápido en la nevera para fabricar dopamina y calmar la angustia a la fuerza. No es que seas descontrolado; tu cuerpo está buscando consuelo.\n\n"
                "**Un truco práctico para cuando te dé ese ataque:**\n"
                "1. Sírverte un vaso de agua fresca y bébetelo despacito sintiendo el frío en la garganta.\n"
                "2. Respira hondo: suelta todo el aire en 6 segundos y tómalo en 4.\n"
                "3. Pregúntate con honestidad: *'¿Tengo hambre en la barriga o lo que tengo es el pecho apretado de preocupaciones?'* Dale 10 minutos a la mente y verás cómo el impulso baja."
            ), False
        else:
            return nombre_avatar, (
                f"El apetito compulsivo nocturno suele ser una respuesta directa al estrés acumulado durante la jornada, {apodo}.\n\n"
                "El organismo busca compensar el cortisol mediante la recompensa de los alimentos. Haz una pausa deliberada de tres respiraciones lentas, bebe un vaso de agua despacio y dale unos minutos a tu mente para diferenciar el apetito biológico de la tensión emocional."
            ), False

    # 8. APOYO A UN AMIGO QUE SUFRE DE BULLYING / ACOSO
    if any(w in texto for w in ["un amigo sufre de bulling", "un amigo sufre de bullying", "amigo sufre acoso", "ayudar a un amigo con acoso"]):
        return nombre_avatar, (
            f"Apoyar a un amigo que enfrenta acoso escolar es un acto de gran valor y solidaridad, {apodo}.\n\n"
            "1. **Validación:** Asegúrale con convicción que él no tiene la culpa y que la agresión responde a la cobardía de quienes la ejercen.\n"
            "2. **Acompañamiento:** Ofrécele ir a su lado para comunicarlo ante profesores, directivos o familiares; tener un testigo le da valor.\n"
            "3. **Solidaridad activa:** Rechazar abiertamente las burlas e integrarlo en grupos seguros desmonta el aislamiento que busca el acoso."
        ), False

    # 9. APOYO GRATUITO O DE BAJO COSTO (ÉTICA: CERO VENTA ANTE FALTA DE RECURSOS)
    if any(w in texto for w in ["no tengo recursos economicos", "no tengo recursos económicos", "sin dinero para psicologo", "sin dinero para psicólogo", "apoyo emocional gratuito", "bajo costo", "no puedo pagar un psicologo", "no puedo pagar un psicólogo"]):
        return nombre_avatar, (
            f"**El cuidado emocional debe estar al alcance de todos, {apodo}, y la falta de recursos económicos jamás debe ser un obstáculo para recibir auxilio.**\n\n"
            "Existen opciones públicas, comunitarias e institucionales gratuitas o de muy bajo costo:\n\n"
            "• **Líneas telefónicas de apoyo emocional gratuito:** Disponibles a nivel nacional en la mayoría de los países (como el 024 en España, el 988 en EE.UU. en español, la FPV al 0212-4163116 en Venezuela, y líneas de emergencia psicológica locales).\n"
            "• **Centros de atención primaria y hospitales públicos:** Servicios comunitarios de salud mental y consulta externa.\n"
            "• **Clínicas universitarias:** Servicios de atención comunitaria de facultades de psicología con tarifas simbólicas o gratuitas.\n\n"
            "Además, este refugio reflexivo siempre está a tu disposición para acompañarte y darte perspectiva sin coste alguno. No te aísles; el apoyo existe."
        ), False

    # 10. MITOS SOBRE MEDICAMENTOS / PSICOFÁRMACOS
    if any(w in texto for w in ["tomar medicamentos", "antidepresivos o ansioliticos", "antidepresivos o ansiolíticos", "obligatoriamente para poder recuperarme", "pastillas obligatorias"]):
        return nombre_avatar, (
            f"**No es obligatorio tomar medicación en todos los casos, {apodo}.**\n\n"
            "En muchos cuadros de ansiedad leve o moderada, las herramientas de reestructuración cognitiva, la regulación somática y los cambios de hábitos constituyen la base eficaz para recuperar el balance.\n\n"
            "Los psicofármacos son herramientas reservadas para prescripción médica especializada cuando la severidad sintomática paraliza la funcionalidad, actuando como un soporte complementario."
        ), False

    # 11. ESTIGMA DE TERAPIA: ¿IR A TERAPIA SIGNIFICA SER DÉBIL?
    if any(w in texto for w in ["persona debil que no pudo resolver", "persona débil que no pudo resolver", "ir a terapia significa que soy", "terapia es de debiles", "terapia es de débiles"]):
        return nombre_avatar, (
            f"**Ir a terapia no es de débiles, {apodo}; es una muestra de fortaleza, madurez y autogobierno.**\n\n"
            "Cuidar la salud interior es tan natural y necesario como acudir al médico por una dolencia física. Solicitar una perspectiva profesional no significa haber fallado, sino contar con la lucidez para adquirir herramientas que te permitan vivir mejor."
        ), False

    # 12. POSITIVIDAD TÓXICA DE AMIGOS ("ÉCHALE GANAS" / "RELÁJATE")
    if any(w in texto for w in ["echale ganas", "échale ganas", "me dicen relajate", "me dicen relájate", "como les explico lo que realmente necesito", "cómo les explico lo que realmente necesito"]):
        return nombre_avatar, (
            f"Comprendo tu incomodidad, {apodo}. Quienes nos aprecian suelen recurrir a esas frases por falta de herramientas para sostener el malestar ajeno.\n\n"
            "**Fórmula de comunicación asertiva:**\n"
            "*'Agradezco su preocupación, pero cuando me dicen que me relaje me siento más presionado. Lo que verdaderamente me ayuda es que me escuchen con paciencia o simplemente compartan un momento tranquilo conmigo sin darme consejos rápidos'*. Marcar ese límite cuida tu energía."
        ), False

    # 13. MIEDO AL JUICIO O A QUE CREAN QUE ESTOY "LOCO"
    if any(w in texto for w in ["me juzga", "cree que estoy loco", "minimiza lo que siento", "piensan que estoy loco"]):
        return nombre_avatar, (
            f"**Experimentar sobrecarga emocional o ansiedad es una respuesta humana explicable biológicamente, {apodo}, y no tiene relación con estar 'loco'.**\n\n"
            "En espacios profesionales y reflexivos adecuados se trabaja con rigor y empatía, libres de juicio. Si alguien en tu entorno minimiza lo que experimentas, recuerda que su reacción refleja su propia falta de herramientas, no la validez de tu vivencia."
        ), False

    # 14. CONFIDENCIALIDAD CLÍNICA: ¿SE LO DIRÁN A MIS PADRES O JEFES?
    if any(w in texto for w in ["completamente confidencial", "se lo diran a mis padres", "se lo dirán a mis padres", "se lo diran a mis jefes", "se lo dirán a mis jefes", "secreto profesional"]):
        return nombre_avatar, (
            f"**Es completamente confidencial, {apodo}. El secreto profesional es una norma ética y legal estricta a nivel mundial.**\n\n"
            "Lo que compartas en una consulta formal de salud o en una línea de apoyo queda estrictamente bajo reserva; nadie puede revelárselo a tus jefes, a tu familia ni a terceros salvo que exista un riesgo inminente para la vida. Tu privacidad está protegida."
        ), False

    # 15. CAOS MENTAL: ¿POR DÓNDE EMPIEZO A HABLAR?
    if any(w in texto for w in ["por donde empiezo a hablar", "por dónde empiezo a hablar", "tengo tanto adentro que no se", "tengo tanto adentro que no sé", "ordenar mis pensamientos para explicarselo", "ordenar mis pensamientos para explicárselo"]):
        return nombre_avatar, (
            f"**No se requiere un relato ordenado de antemano, {apodo}; inicia simplemente por lo que experimentas hoy.**\n\n"
            "Nombrar el malestar físico o la preocupación más inmediata de las últimas horas es suficiente. El proceso de conversación permite ir desenredando las ideas progresivamente."
        ), False

    # 16. BULLYING EN 1RA PERSONA: CÓMO DEFENDERSE EN PASILLOS O SALÓN
    if any(w in texto for w in ["como puedo defenderme o reaccionar", "cómo puedo defenderme o reaccionar", "cuando se burlan de mi en los pasillos", "cuando se burlan de mí en los pasillos", "se burlan en el salon", "se burlan en el salón"]):
        return nombre_avatar, (
            f"**La mejor respuesta inmediata ante una provocación es retirarles la atención que buscan, {apodo}.**\n\n"
            "Mantén una postura erguida, contacto visual sereno y utiliza respuestas breves y neutras (*'¿Ya terminaste?'*, *'Sigue tu camino'*). Dirígete de inmediato a espacios concurridos o busca la presencia de autoridades del centro educativo sin entrar en confrontación física."
        ), False

    # 17. BULLYING EN 1RA PERSONA: TERROR MATUTINO A IR A LA ESCUELA
    if any(w in texto for w in ["ya no quiero ir a la escuela", "me da miedo verlos", "lidiar con ese terror cada manana", "lidiar con ese terror cada mañana", "miedo de ir a la escuela"]):
        return nombre_avatar, (
            f"**Ese temor matutino es una respuesta natural de autoprotección ante un entorno adverso, {apodo}.**\n\n"
            "No tienes que sobrellevar esta situación en soledad. Es prioritario comunicarlo hoy mismo a tus padres, tutores o personal directivo de la institución para que activen las medidas de resguardo correspondientes."
        ), False

    # 18. BULLYING EN 1RA PERSONA: EXCLUSIÓN, RUMORES Y SOLEDAD
    if any(w in texto for w in ["me excluyen de los grupos", "hablan mal de mi a mis espaldas", "hablan mal de mí a mis espaldas", "que no me afecte la soledad", "cómo hago para que no me afecte la soledad"]):
        return nombre_avatar, (
            f"**El rechazo y los rumores generan un dolor comprensible, {apodo}, pues afectan el sentido de pertenencia.**\n\n"
            "Quienes recurren a la exclusión suelen actuar motivados por cobardía individual y presión grupal. Evita buscar validación en entornos hostiles y enfoca tu energía en espacios externos (deporte, arte, lectura) donde puedas construir vínculos sanos."
        ), False

    # 19. BULLYING EN 1RA PERSONA: CÓMPLICES SILENCIOSOS
    if any(w in texto for w in ["por que los demas se quedan callados", "por qué los demás se quedan callados", "se rien cuando ven que me estan haciendo", "se ríen cuando ven que me están haciendo", "testigos del acoso"]):
        return nombre_avatar, (
            f"**El silencio de los observadores suele ser producto del temor a convertirse en el siguiente objetivo del acoso, {apodo}.**\n\n"
            "Esa complicidad pasiva refleja la falta de coraje del grupo, no una justificación del maltrato hacia tu persona."
        ), False

    # 20. ACOSO ESCOLAR EN 1RA PERSONA: ¿HAY ALGO MALO EN MÍ? / MIEDO A PEDIR AYUDA
    if any(w in texto for w in ["hay algo malo en mi", "hay algo malo en mí", "merezca el rechazo", "me merezca el rechazo", "por que mis companeros me tratan asi", "por qué mis compañeros me tratan así"]):
        return nombre_avatar, (
            f"**No hay absolutamente nada defectuoso en ti ni mereces el rechazo de nadie, {apodo}.**\n\n"
            "La conducta agresiva responde a las carencias y actitudes de quienes la ejercen, jamás a las características de la persona agredida. Tu dignidad es innegociable."
        ), False

    if any(w in texto for w in ["si le cuento a mis papas", "si le cuento a mis papás", "se vengaran mas de mi", "se vengarán más de mí", "van a empeorar y se vengaran", "van a empeorar y se vengarán"]):
        return nombre_avatar, (
            f"**Romper el silencio es el paso esencial para detener el hostigamiento, {apodo}.**\n\n"
            "El temor a represalias es una táctica habitual para mantener a la víctima aislada. Acudir a tus padres o tutores permite activar mecanismos formales de protección institucional a los que tienes derecho."
        ), False

    # 21. ACOSO LABORAL (MOBBING) VS. EXIGENCIA
    if any(w in texto for w in ["mi jefe o companeros me humillan", "mi jefe o compañeros me humillan", "desvalorizan mi trabajo", "como demuestro que es acoso y no solo", "cómo demuestro que es acoso y no solo"]):
        return nombre_avatar, (
            f"**La exigencia profesional se centra en objetivos respetuosos; la descalificación y humillación constante constituyen acoso laboral (Mobbing), {apodo}.**\n\n"
            "Para fundamentarlo con objetividad:\n"
            "1. **Registro cronológico detallado:** Documenta fechas, órdenes contradictorias, lugares y testigos.\n"
            "2. **Respaldo documental:** Conserva copias de correos e instrucciones en un soporte personal seguro.\n"
            "3. **Formalización escrita:** Solicita que los requerimientos se canalicen formalmente por escrito."
        ), False

    # 22. CIBERACOSO: ATAQUES EN REDES SOCIALES
    if any(w in texto for w in ["redes sociales, ¿que debo hacer para detener el ciberacoso", "redes sociales, que debo hacer para detener el ciberacoso", "detener el ciberacoso", "inventando rumores a traves de las redes", "inventando rumores a través de las redes"]):
        return nombre_avatar, (
            f"**El ciberacoso deja rastro digital y esa es tu mejor herramienta para detenerlo, {apodo}.**\n\n"
            "1. **Cero respuestas:** No contestes ni entres en discusión.\n"
            "2. **Respaldo probatorio:** Toma capturas de pantalla completas donde se vean usuarios, enlaces, fechas y mensajes.\n"
            "3. **Bloqueo y reporte:** Utiliza las herramientas de denuncia de la plataforma.\n"
            "4. **Denuncia legal:** Si existen amenazas, acude con tus evidencias a las dependencias de delitos informáticos locales."
        ), False

    # 23. ANSIEDAD LABORAL: PÁNICO ANTE NOTIFICACIONES
    if any(w in texto for w in ["siento panico cada vez que llega un correo", "siento pánico cada vez que llega un correo", "mensaje de mi entorno laboral", "como protejo mi salud mental"]):
        return nombre_avatar, (
            f"**Ese malestar refleja un condicionamiento de alerta ante las notificaciones de trabajo, {apodo}.**\n\n"
            "1. **Desconexión formal:** Desactiva alertas laborales fuera del horario de trabajo.\n"
            "2. **Pausa antes de responder:** Realiza dos respiraciones lentas antes de abrir mensajes tensos para responder con calma y no desde la reactividad física."
        ), False

    # 24. DILEMA DE RENUNCIA: SALUD MENTAL VS. DINERO
    if any(w in texto for w in ["deberia renunciar a mi empleo por salud mental", "debería renunciar a mi empleo por salud mental", "aunque necesite urgentemente el dinero", "renunciar por salud mental"]):
        return nombre_avatar, (
            f"**Es un dilema complejo, {apodo}: priorizar el bienestar es fundamental, pero una ruptura abrupta sin ingresos genera nuevas tensiones.**\n\n"
            "Salvo situaciones extremas de abuso insostenible, la vía más protectora es una transición planificada:\n"
            "1. **Distanciamiento emocional:** Cumple con tus labores formales sin sobreexigirte en el entorno hostil.\n"
            "2. **Búsqueda activa:** Destina tu energía disponible a postularte a nuevas opciones mientras aseguras tu sustento."
        ), False

    # 25. INSTANCIAS LEGALES ANTE ACOSO LABORAL (MOBBING)
    if any(w in texto for w in ["instancias legales o de recursos humanos", "acudir si sufro acoso en mi trabajo", "denunciar acoso laboral"]):
        return nombre_avatar, (
            f"**Tienes derecho a un ambiente laboral libre de hostigamiento, {apodo}. Puedes proceder de forma escalonada:**\n\n"
            "1. **Canales internos:** Recursos Humanos o comités de seguridad laboral mediante comunicación escrita formal.\n"
            "2. **Organismos laborales oficiales:** Inspectorías, Secretarías o Ministerios de Trabajo de tu jurisdicción.\n"
            "3. **Institutos de salud laboral o mediación:** Para certificar afectaciones derivadas del entorno laboral."
        ), False

    # 26. IDEACIÓN PASIVA DE ESCAPE
    if any(w in texto for w in ["dormir y no despertar", "dejar de sufrir, ¿eso significa", "dejar de sufrir, eso significa", "eso significa que quiero acabar"]):
        return nombre_avatar, (
            f"**No significa necesariamente un deseo de terminar con tu vida, {apodo}; refleja un agotamiento profundo ante el sufrimiento sostenido.**\n\n"
            "Cuando la mente enfrenta tensiones continuas, suele desear una pausa total para encontrar alivio. Es un indicador de saturación que merece cuidado compasivo. Permítete buscar el apoyo de profesionales o seres queridos en este momento."
        ), False

    # 27. ATAQUE DE PÁNICO AGUDO
    if any(w in texto for w in ["me va a dar un infarto", "da un infarto", "dar un infarto", "me estoy muriendo", "es un ataque de panico o me estoy muriendo", "es un ataque de pánico o me estoy muriendo"]):
        return nombre_avatar, (
            f"**{apodo}, descarta ese peligro: no estás sufriendo un infarto ni estás en riesgo de muerte.**\n\n"
            "Estás experimentando un ataque de pánico. La descarga de adrenalina acelera el pulso y genera tensión torácica, pero es una reacción temporal e inocua para tu corazón.\n\n"
            "Coloca los pies firmes sobre el suelo, alarga la exhalación por la boca en 6 segundos e inhala suave por la nariz en 4. La sensación descenderá gradualmente."
        ), False

    # 28. RESCATE SOMÁTICO INMEDIATO
    if any(w in texto for w in ["que puedo hacer de inmediato", "qué puedo hacer de inmediato", "la ansiedad me esta ganando", "la ansiedad me está ganando", "voy a perder el control"]):
        return nombre_avatar, (
            f"**No vas a perder el control, {apodo}. La sensación es intensa pero transitoria.**\n\n"
            "Aplica la técnica de anclaje sensorial **5-4-3-2-1**:\n"
            "• Nombra **5 objetos** que veas a tu alrededor.\n"
            "• Toca **4 texturas** cercanas.\n"
            "• Identifica **3 sonidos** en tu entorno.\n"
            "• Percibe **2 olores** o inhala profundamente.\n"
            "• Saborea **1 cosa** o traga saliva despacio.\n"
            "Pisa con firmeza y exhala lentamente."
        ), False

    # 29. RUMIACIÓN CATASTRÓFICA
    if any(w in texto for w in ["escenarios catastroficos", "escenarios catastróficos", "mi mente no puede dejar de pensar"]):
        return nombre_avatar, (
            f"Lo que experimentas se conoce como **hipervigilancia anticipatoria**, {apodo}.\n\n"
            "El sistema de alerta interno permanece activo intentando prevenir contingencias de manera automática. "
            "En lugar de confrontar esos pensamientos, reconócelos como una reacción aprendida y reenfoca tu atención en las tareas concretas de tu presente."
        ), False

    # 30. SOMATIZACIÓN TOTAL
    if any(w in texto for w in ["dolores de cabeza", "gastritis", "tension muscular", "tensión muscular"]):
        return nombre_avatar, (
            f"**Es una respuesta fisiológica habitual ante el estrés prolongado, {apodo}.**\n\n"
            "La activación continua del sistema simpático genera tensión muscular sostenida en cuello y cabeza, alteraciones gastrointestinales y dificultades en el descanso. Indican sobrecarga acumulada que requiere pausas y autorregulación."
        ), False

    # 31. DESESPERANZA / CRONICIDAD
    if any(w in texto for w in ["alguna vez volvere a sentirme tranquilo", "alguna vez volveré a sentirme tranquilo", "esta opresion en el pecho para siempre", "esta opresión en el pecho para siempre"]):
        return nombre_avatar, (
            f"**Sí recuperarás la tranquilidad, {apodo}. Esta opresión torácica no es un estado permanente.**\n\n"
            "Tras periodos de agotamiento el cerebro pierde temporalmente la noción de bienestar, pero su plasticidad y capacidad de autorregulación permanecen intactas. Estás atravesando una etapa transitoria."
        ), False

    # 32. TRISTEZA VS. DEPRESIÓN CLÍNICA
    if any(w in texto for w in ["tristeza profunda", "duelo normal"]) and any(w in texto for w in ["depresion clinica", "depresión clínica"]):
        return nombre_avatar, (
            f"La diferencia radica en que el duelo y la tristeza profunda vienen en olas, permitiendo momentos de conexión y conservando la autoestima; la depresión clínica se presenta como una niebla persistente con incapacidad de sentir placer (anhedonia), cansancio físico extremo y una culpa constante hacia uno mismo que amerita valoración especializada."
        ), False

    # 33. INHIBICIÓN PSICOMOTRIZ VS. PEREZA
    if any(w in texto for w in ["no tengo energia", "no tengo energía", "levantarme de la cama o banarme", "levantarme de la cama o bañarme", "soy perezoso"]):
        return nombre_avatar, (
            f"**No se trata de pereza, {apodo}; es un síntoma de inhibición psicomotriz derivado del agotamiento neurobiológico.**\n\n"
            "La energía disponible disminuye significativamente tras estados continuos de malestar. Evita los juicios de valor y concédete avanzar mediante microobjetivos realistas."
        ), False

    # 34. ANHEDONIA
    if any(w in texto for w in ["ya no disfruto", "no disfruto las cosas", "volvere a recuperar el interes", "volveré a recuperar el interés"]):
        return nombre_avatar, (
            f"**Sí lo recuperarás, {apodo}. En psicología se llama anhedonia y es una desconexión transitoria de los receptores de dopamina.** No esperes a tener ganas: empezar con pequeñas acciones sencillas de pocos minutos reactiva el interés gradualmente."
        ), False

    # 35. CULPA FAMILIAR
    if any(w in texto for w in ["como una carga para mi familia", "carga para mi familia"]):
        return nombre_avatar, (
            f"**No eres una carga para tu entorno, {apodo}; esa percepción es producto del sesgo depresivo.** Quienes te aprecian actúan movidos por afecto y solidaridad. Permitirte recibir respaldo es parte de la recuperación."
        ), False

    # 36. LABILIDAD EMOCIONAL / LLANTO
    if any(w in texto for w in ["ganas de llorar todo el dia", "ganas de llorar todo el día", "sin que haya una razon aparente", "sin que haya una razón aparente"]):
        return nombre_avatar, (
            f"**Es completamente natural, {apodo}. El llanto sin causa aparente es la válvula de desahogo de un vaso que se llenó tras semanas de aguantar tensión.** Llorar ayuda al cuerpo a liberar cortisol; permítete ese alivio sin recriminártelo."
        ), False

    # 37. PREGUNTAS SOBRE NOMBRE DEL USUARIO Y TRABAJO
    if any(q in texto for q in ["como me llamo", "cómo me llamo", "sabes mi nombre", "sabes como me llamo", "sabes cómo me llamo"]):
        return nombre_avatar, f"Tu nombre oficial en tu cuenta es {nombre_real}, aunque en nuestras conversaciones te llamo {apodo}.", False

    if any(q in texto for q in ["en que trabajo actualmente", "en qué trabajo actualmente", "donde trabajo actualmente", "dónde trabajo actualmente", "cual es mi trabajo actual", "cuál es mi trabajo actual"]):
        menciono_desempleo = any(k in historial_str for k in ["perdi mi empleo", "perdí mi empleo", "perdi el trabajo", "perdí el trabajo", "sin empleo", "desempleado"])
        if menciono_desempleo:
            return nombre_avatar, (
                f"Tu profesión y oficio de base es como **{profesion}**, {apodo}, pero estás transitando la etapa difícil de haber perdido tu empleo recientemente. Esa habilidad sigue contigo mientras se abren nuevas puertas."
            ), False
        else:
            return nombre_avatar, f"Te desempeñas como {profesion}. Recuerda siempre que tu valor humano está por encima de cualquier etiqueta laboral.", False

    if any(q in texto for q in ["cuantos hijos te dije", "cuántos hijos te dije", "cuantos hijos tengo", "cuántos hijos tengo", "mis hijos", "tengo hijos", "cantidad de hijos"]):
        return nombre_avatar, f"En tu registro y en nuestra conversación constan {hijos} {'hijo' if hijos == 1 else 'hijos'}, {apodo}.", False

    # 38. ORIENTACIÓN COMERCIAL Y RECARGA DE PLANES
    if any(w in texto for w in ["recargar", "comprar", "pagar", "adquirir", "subir de plan", "otros planes", "plan comunicador", "amigo de todos"]):
        return nombre_avatar, (
            f"Puedes gestionar la activación o ampliación de tu plan con total serenidad, {apodo}. En el menú lateral izquierdo encontrarás la pestaña **'Planes y Suscripción'**. "
            "Allí, en la sección **'Coordinar Pago Privado con Admin'**, podrás solicitar los datos correspondientes para Pago Móvil BDV, Binance Pay o PayPal en un canal confidencial y seguro. "
            "El administrador te atenderá con gusto para activar tu acceso."
        ), False

    # 39. SALUDOS Y CORTESÍA UNIVERSALES
    if any(q in texto for q in ["hola", "buenas", "saludos", "brother", "que tal", "qué tal", "ola", "olá", "namaste", "namasté"]):
        if "camilo" in avatar_id:
            return nombre_avatar, f"¡Qué tal, mi hermano {apodo}! Un gustazo enorme saludarte. Suelta los hombros y cuéntame con confianza: ¿qué traes en mente hoy?", False
        elif "anastasia" in avatar_id:
            return nombre_avatar, f"Hola, {apodo}. Me alegra saludarte. Tómate un respiro sereno y explícame con total franqueza qué situación deseas que analicemos hoy.", False
        elif "ananya" in avatar_id:
            return nombre_avatar, f"Namasté, {apodo}. Qué alegría coincidir en este espacio de calma. Respira hondo y cuéntame con tranquilidad: ¿qué inquietud traes hoy en tu mente?", False
        elif "larissa" in avatar_id:
            return nombre_avatar, f"¡Olá, {apodo}! ¡Qué hermosa energía tenerte por aquí! Respira hondo, suelta los hombros y cuéntame con confianza: ¿de qué te gustaría conversar hoy?", False
        elif "rodrigo" in avatar_id:
            return nombre_avatar, f"¿Cómo andás, {apodo}? Me alegra encontrarte. Hablemos con calma y contame qué te anda dando vueltas en la cabeza.", False
        else:
            return nombre_avatar, f"¡Hola, {apodo}! Te doy una cálida bienvenida. Tómate un respiro y cuéntame de qué te gustaría conversar hoy.", False

    if any(q in texto for q in ["gracias", "obrigado", "obrigada", "dhanyavaad"]):
        return nombre_avatar, f"Es un placer acompañarte, {apodo}. Para eso estamos aquí, para caminar con más calma. Sigue adelante con fuerza.", False

    # 40. RAG DINÁMICO ORGÁNICO
    consejos = []
    for libro in LIBROS_CACHE:
        if libro.get("id_libro") in avatar_info.get("libros_rag_afines", []):
            consejos.append(libro.get("consejo_aplicable"))
    
    consejos_filtrados = [c for c in consejos if not any(c[:30] in h for h in historial)]
    consejo_seleccionado = random.choice(consejos_filtrados if consejos_filtrados else consejos) if consejos else "Lleva tu atención al momento presente y da un paso pequeño a la vez."

    if "camilo" in avatar_id:
        aperturas = [
            f"Te entiendo perfectamente, mi hermano {apodo}. Mira, algo que siempre ayuda a ver las cosas claras es esto: {consejo_seleccionado}",
            f"Hermano {apodo}, cuando las aguas se ponen turbulentas, ten presente esta perspectiva: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} Dime, ¿por dónde sientes que debemos empezar a desenredar esto?", False
    elif "anastasia" in avatar_id:
        aperturas = [
            f"Comprendo la situación, {apodo}. Si analizamos esto con perspectiva estructurada: {consejo_seleccionado}",
            f"Evaluemos el asunto con objetividad, {apodo}. Ten presente este principio fundamental: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} ¿Cuál es el punto central que requiere nuestra atención prioritaria?", False
    elif "ananya" in avatar_id:
        aperturas = [
            f"Comprendo la inquietud que se despierta en ti, {apodo}. Para encontrar quietud en medio del ruido, recuerda: {consejo_seleccionado}",
            f"Respira con calma, {apodo}. Una valiosa enseñanza para apaciguar la mente ante esta situación es esta: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} Cuéntame, ¿qué área de tu día sientes que puedes ordenar con mayor serenidad?", False
    else:
        aperturas = [
            f"Entiendo lo que estás viviendo, {apodo}. Algo que puede ayudarte a encontrar balance hoy es esto: {consejo_seleccionado}",
            f"Te escucho con empatía, {apodo}. Recuerda siempre esta guía: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} ¿De qué manera sientes que podemos dar el siguiente paso?", False
