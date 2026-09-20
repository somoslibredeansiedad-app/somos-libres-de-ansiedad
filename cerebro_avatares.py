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
    Cerebro cognitivo v4.6.3 (Rafael):
    Resuelve el orden jerárquico de dolor sobre datos, erradica bucles RAG y plantillas estáticas,
    distingue acoso escolar en 1ra persona de acoso laboral (mobbing), ciberacoso y estigmas de salud mental,
    atiende ética de apoyo gratuito y modula la identidad cultural de cada guía.
    """
    avatar_info = CATALOGO_CACHE.get(avatar_id, CATALOGO_CACHE.get("ananya", list(CATALOGO_CACHE.values())[0] if CATALOGO_CACHE else {}))
    nombre_avatar = avatar_info.get("identidad", {}).get("nombre_completo", "Guía")
    pais_avatar = avatar_info.get("identidad", {}).get("pais", "")
    
    texto = mensaje_usuario.lower().strip()
    
    # Tratamiento y limpieza de apodo (eliminar prefijos administrativos)
    apodo_crudo = perfil_usuario.get("apodo", "amigo/a").strip()
    if apodo_crudo.lower().startswith("admin "):
        apodo = apodo_crudo[6:].strip()
    elif apodo_crudo.lower() == "admin":
        apodo = "Juan Carlos"
    else:
        apodo = apodo_crudo

    nombre_real = perfil_usuario.get("nombre_completo", apodo)
    profesion = perfil_usuario.get("profesion") or "tu profesión u ocupación"
    hijos = perfil_usuario.get("cantidad_hijos") if perfil_usuario.get("cantidad_hijos") is not None else 0
    historial = historial_reciente or []
    historial_str = " ".join([h.lower() for h in historial])

    # 1. FILTRO ROJO / SOS INMEDIATO (Seguridad Clínica y Ética Absoluta)
    es_duda_pasiva_cansancio = any(w in texto for w in ["dormir y no despertar", "dejar de sufrir, ¿eso significa", "dejar de sufrir, eso significa"])
    es_pregunta_panico_muerte = any(w in texto for w in ["ataque de panico", "ataque de pánico", "infarto", "falta el aire", "me ahogo"]) and any(w in texto for w in ["muriendo", "morir"])
    
    if any(p in texto for p in PATRONES_CRISIS_SOS) and not es_pregunta_panico_muerte and not es_duda_pasiva_cansancio:
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

    # 2. APOYO GRATUITO O DE BAJO COSTO (ÉTICA: CERO VENTA ANTE FALTA DE RECURSOS)
    if any(w in texto for w in ["no tengo recursos economicos", "no tengo recursos económicos", "sin dinero para psicologo", "sin dinero para psicólogo", "apoyo emocional gratuito", "bajo costo", "no puedo pagar un psicologo", "no puedo pagar un psicólogo"]):
        return nombre_avatar, (
            f"**Tu bienestar emocional es un derecho sagrado, {apodo}, y la falta de dinero jamás debe ser un obstáculo para recibir auxilio.**\n\n"
            "Existen opciones públicas, universitarias y comunitarias totalmente gratuitas o a muy bajo costo a las que puedes acudir con plena confianza:\n\n"
            "• **Línea de Ayuda Psicológica de la FPV:** Servicio telefónico gratuito y confidencial de orientación y primeros auxilios psicológicos (Tel: 0212-4163116 / 0212-4163118).\n"
            "• **Servicios de Psicología Clínica de Hospitales Públicos:** Consulta externa de salud mental y psiquiatría en los principales hospitales universitarios y regionales.\n"
            "• **Unidades de Atención Psicológica Universitaria:** Universidades públicas y autónomas (como la UCV o servicios comunitarios) brindan consulta clínica accesible a la comunidad.\n"
            "• **Cruz Roja Venezolana / Centros de Salud Comunitarios:** Módulos de atención con tarifas solidarias o gratuitas.\n\n"
            "Además, cuentas siempre con este refugio reflexivo para desahogarte y ordenar tus pensamientos sin costo. No te aisles; el apoyo existe y está a tu alcance."
        ), False

    # 3. MITOS SOBRE MEDICAMENTOS / PSICOFÁRMACOS
    if any(w in texto for w in ["tomar medicamentos", "antidepresivos o ansioliticos", "antidepresivos o ansiolíticos", "obligatoriamente para poder recuperarme", "pastillas obligatorias"]):
        return nombre_avatar, (
            f"**No, {apodo}, la medicación no es obligatoria para recuperarte en todos los casos.**\n\n"
            "En la gran mayoría de los cuadros de ansiedad leve o moderada y en crisis vitales, la **psicoterapia (especialmente TCC, ACT y regulación somática)** junto con cambios en hábitos de descanso y gestión del estrés es el tratamiento de primera línea y resulta completamente suficiente para restaurar la calma.\n\n"
            "Los psicofármacos (ansiolíticos o antidepresivos) son herramientas que **únicamente prescribe un médico psiquiatra** tras una evaluación exhaustiva, y se reservan para momentos donde la severidad de los síntomas paraliza por completo la vida cotidiana. Incluso en esos casos, la medicación no es un castigo ni una condena de por vida: es solo un salvavidas temporal para bajar la marea mientras la terapia te enseña a nadar. Cada proceso es único y se decide a tu propio ritmo."
        ), False

    # 4. ESTIGMA DE TERAPIA: ¿IR A TERAPIA SIGNIFICA SER DÉBIL?
    if any(w in texto for w in ["persona debil que no pudo resolver", "persona débil que no pudo resolver", "ir a terapia significa que soy", "terapia es de debiles", "terapia es de débiles"]):
        return nombre_avatar, (
            f"**Ir a terapia no es un signo de debilidad, {apodo}; es exactamente lo contrario: el mayor acto de lucidez y valentía personal.**\n\n"
            "Nadie cuestiona que un atleta de alto rendimiento consulte a un fisioterapeuta cuando un músculo se desgarra, ni nadie califica de 'débil' a quien va al médico cuando tiene una infección. Tu mente y tu sistema nervioso soportan cargas biológicas y emocionales inmensas, y pedir una mirada profesional especializada no significa que hayas fallado, sino que te rehúsas a conformarte con el sufrimiento.\n\n"
            "Reconocer los propios límites y buscar herramientas para reconstruir tu paz interior es la máxima expresión de autogobierno y madurez. La verdadera debilidad es quedarse estancado por miedo al qué dirán."
        ), False

    # 5. POSITIVIDAD TÓXICA DE AMIGOS ("ÉCHALE GANAS" / "RELÁJATE")
    if any(w in texto for w in ["echale ganas", "échale ganas", "me dicen relajate", "me dicen relájate", "como les explico lo que realmente necesito", "cómo les explico lo que realmente necesito"]):
        return nombre_avatar, (
            f"Es agotador escuchar esas frases, {apodo}, porque aunque nazcan del cariño, solo consiguen hacerte sentir incomprendido y culpable.\n\n"
            "Decirle a alguien con ansiedad o depresión 'relájate' o 'échale ganas' es como pedirle a alguien con miopía que mire más fuerte para ver claro: **no es un problema de falta de ganas, es una sobrecarga neurobiológica real**.\n\n"
            "**Puedes explicárselo con esta fórmula asertiva y directa:**\n"
            "*'Agradezco de corazón que quieran verme bien, pero cuando me dicen que me relaje me siento más presionado. Ahora mismo no necesito consejos rápidos ni soluciones mágicas; lo que verdaderamente me ayuda es que me escuchen sin juzgarme o simplemente que compartan un café conmigo en silencio'*. Poner ese límite protege tu energía."
        ), False

    # 6. MIEDO AL JUICIO O A QUE CREAN QUE ESTOY "LOCO"
    if any(w in texto for w in ["me juzga", "cree que estoy loco", "minimiza lo que siento", "piensan que estoy loco"]):
        return nombre_avatar, (
            f"**Quita ese temor de tu mente, {apodo}: experimentar ansiedad, tristeza profunda o dolor emocional no tiene absolutamente nada que ver con 'estar loco'.**\n\n"
            "Ese miedo suele nacer de la incomprensión social. Un profesional de la salud mental ético y preparado jamás juzga, minimiza ni coloca etiquetas hirientes; su labor es crear un espacio seguro donde tu dolor sea validado con respeto y comprensión científica de tu sistema nervioso.\n\n"
            "Y si alguna persona en tu entorno cercano minimiza lo que sientes diciendo que 'no es para tanto', recuerda que eso habla de su propia incapacidad para gestionar emociones, no de la validez de tu experiencia. Lo que sientes es real, tiene causa y merece ser tratado con dignidad."
        ), False

    # 7. CONFIDENCIALIDAD CLÍNICA: ¿SE LO DIRÁN A MIS PADRES O JEFES?
    if any(w in texto for w in ["completamente confidencial", "se lo diran a mis padres", "se lo dirán a mis padres", "se lo diran a mis jefes", "se lo dirán a mis jefes", "secreto profesional"]):
        return nombre_avatar, (
            f"**Es completamente confidencial y está protegido por la ley y el código de ética profesional, {apodo}.**\n\n"
            "Todo lo que hablas en una consulta psicológica privada o en una línea formal de ayuda está amparado por el **secreto profesional inviolable**. Ningún terapeuta puede revelar tus palabras a tus jefes, familiares o terceros bajo ninguna circunstancia.\n\n"
            "La única excepción ética y legal que existe a nivel mundial es ante un riesgo inminente y letal contra tu propia vida o la de terceros, donde la ley exige activar redes protectoras de urgencia médica. Fuera de ese extremo, tu privacidad es un santuario sagrado."
        ), False

    # 8. CAOS MENTAL: ¿POR DÓNDE EMPIEZO A HABLAR?
    if any(w in texto for w in ["por donde empiezo a hablar", "por dónde empiezo a hablar", "tengo tanto adentro que no se", "tengo tanto adentro que no sé", "ordenar mis pensamientos para explicarselo", "ordenar mis pensamientos para explicárselo"]):
        return nombre_avatar, (
            f"**No tienes que traer un discurso ordenado ni estructurado, {apodo}; empieza por lo que te apriete el pecho hoy.**\n\n"
            "Cuando llevamos meses tragando preocupaciones, la mente se siente como un cajón revuelto donde todo está mezclado. La terapia o una conversación de desahogo no es un examen ni una rendición de cuentas; la labor del terapeuta es precisamente ayudarte a desenredar esa madeja hilo por hilo.\n\n"
            "**Una regla práctica para empezar:** No intentes contar tu biografía entera. Empieza diciendo cómo te levantaste esta mañana, o cuál fue la molestia puntual de las últimas 24 horas: *'Hoy me siento abrumado por esto'*. A partir de ahí, el diálogo fluye solo y las piezas se van acomodando con naturalidad."
        ), False

    # 9. BULLYING EN 1RA PERSONA: CÓMO DEFENDERSE EN PASILLOS O SALÓN
    if any(w in texto for w in ["como puedo defenderme o reaccionar", "cómo puedo defenderme o reaccionar", "cuando se burlan de mi en los pasillos", "cuando se burlan de mí en los pasillos", "se burlan en el salon", "se burlan en el salón"]):
        return nombre_avatar, (
            f"**Tu mayor escudo de defensa inmediata frente a las burlas es no darles el combustible que buscan, {apodo}.**\n\n"
            "Los acosadores se alimentan de la reacción de angustia o del enojo descontrolado de su objetivo. En el momento en que se produzca una burla en el pasillo o salón, aplica la **estrategia de la piedra gris**:\n\n"
            "1. **Postura corporal firme:** Mantén la espalda recta, la mirada tranquila a la altura de sus ojos (sin desafiar, pero sin agachar la cabeza).\n"
            "2. **Respuesta neutral y cortante:** Un tono seco como: *'¿Ya terminaste?'*, *'Tu opinión me es indiferente'* o simplemente mirarlos en silencio 3 segundos y seguir caminando con paso seguro hacia un lugar concurrido.\n"
            "3. **Rompe el aislamiento:** Acércate a personas que no se presten a la agresión o a un profesor. Mostrar que su burla no tiene poder sobre tu dignidad desarma su juego de intimidación."
        ), False

    # 10. BULLYING EN 1RA PERSONA: TERROR MATUTINO A IR A LA ESCUELA
    if any(w in texto for w in ["ya no quiero ir a la escuela", "me da miedo verlos", "lidiar con ese terror cada manana", "lidiar con ese terror cada mañana", "miedo de ir a la escuela"]):
        return nombre_avatar, (
            f"**Es completamente comprensible que sientas ese terror cada mañana, {apodo}; tu cuerpo entra en alarma porque sabe que va a un lugar hostil.**\n\n"
            "Esa angustia matutina no es flojera ni cobardía, es tu reflejo natural de supervivencia intentando protegerte del dolor. Pero quedarte encerrado en ese terror en soledad solo agranda la jaula.\n\n"
            "**El paso urgente e inaplazable hoy:** Tienes que hablar con tus padres o tutores hoy mismo antes de salir de casa o al regresar. Diles la verdad con el corazón abierto: *'Tengo pánico de ir al colegio porque estoy viviendo agresiones continuas y no puedo lidiar con esto solo'*. No tienes que ser un héroe que soporte la hostilidad en silencio; los adultos responsables tienen la obligación legal y moral de intervenir en la escuela para garantizar tu seguridad."
        ), False

    # 11. BULLYING EN 1RA PERSONA: EXCLUSIÓN, RUMORES Y SOLEDAD
    if any(w in texto for w in ["me excluyen de los grupos", "hablan mal de mi a mis espaldas", "hablan mal de mí a mis espaldas", "que no me afecte la soledad", "cómo hago para que no me afecte la soledad"]):
        return nombre_avatar, (
            f"**La exclusión social deliberada y los rumores duelen profundamente, {apodo}, porque tocan nuestra necesidad de pertenencia.**\n\n"
            "Recuerda esto con claridad: quienes necesitan aliarse para esparcir chismes o excluir a alguien lo hacen desde una enorme cobardía individual; dependen del rebaño para sentirse seguros porque no tienen brillo propio. La soledad temporal es mil veces más sana que la compañía de quienes te desprecian.\n\n"
            "No mendigues aceptación en círculos que te dañan. Busca espacios fuera del colegio o aula (talleres de arte, deporte, lectura, grupos comunitarios) donde tu valor sea apreciado con honestidad. Tu tribu existe, solo que no está en ese grupo inmaduro."
        ), False

    # 12. BULLYING EN 1RA PERSONA: CÓMPLICES SILENCIOSOS
    if any(w in texto for w in ["por que los demas se quedan callados", "por qué los demás se quedan callados", "se rien cuando ven que me estan haciendo", "se ríen cuando ven que me están haciendo", "testigos del acoso"]):
        return nombre_avatar, (
            f"**Ese silencio y esas risas cómplices duelen a veces más que el propio ataque, {apodo}, pero tienen una explicación psicológica clara.**\n\n"
            "Los espectadores pasivos que se callan o se ríen no lo hacen porque crean que mereces el daño, sino por **puro miedo a convertirse en la siguiente víctima**. Prefieren mimetizarse con el agresor o fingir que es un chiste para que la mirada del hostigador no se pose sobre ellos.\n\n"
            "Es un reflejo de cobardía y presión grupal, no de que tú estés equivocado o carezcas de valor. Comprender esto te permite retirar la culpa de ti: la falta de coraje moral de tus compañeros es su propia carencia, no tu responsabilidad."
        ), False

    # 13. ACOSO LABORAL (MOBBING) VS. EXIGENCIA
    if any(w in texto for w in ["mi jefe o companeros me humillan", "mi jefe o compañeros me humillan", "desvalorizan mi trabajo", "como demuestro que es acoso y no solo", "cómo demuestro que es acoso y no solo"]):
        return nombre_avatar, (
            f"**La exigencia laboral busca resultados profesionales con respeto; la humillación sistemática es ACOSO LABORAL (Mobbing) y constituye una falta legal grave, {apodo}.**\n\n"
            "La diferencia radica en que la exigencia se enfoca en objetivos objetivos y plazos, mientras que el acoso busca desgastar psicológicamente a la persona mediante descalificaciones personales, aislamiento, sobrecarga malintencionada o críticas públicas denigrantes.\n\n"
            "**Cómo blindarte y demostrarlo:**\n"
            "1. **Bitácora confidencial detallada:** Anota cada incidente con fecha, hora exacta, lugar, palabras textuales y testigos presentes.\n"
            "2. **Respaldo documental:** Guarda correos electrónicos, mensajes o evaluaciones arbitrarias en un dispositivo personal fuera de los equipos de la empresa.\n"
            "3. **Exige comunicación por escrito:** Si te asignan tareas absurdas o desproporcionadas, responde por correo: *'Entendido, procedo según sus indicaciones por escrito'*. La prueba documental desarma la arbitrariedad."
        ), False

    # 14. CIBERACOSO: ATAQUES EN REDES SOCIALES
    if any(w in texto for w in ["redes sociales, ¿que debo hacer para detener el ciberacoso", "redes sociales, que debo hacer para detener el ciberacoso", "detener el ciberacoso", "inventando rumores a traves de las redes", "inventando rumores a través de las redes"]):
        return nombre_avatar, (
            f"**El ciberacoso deja huella digital y esa es tu mayor ventaja para detenerlo legal y administrativamente, {apodo}.**\n\n"
            "Aplica de inmediato este protocolo de protección:\n\n"
            "1. **Cero respuestas:** No contestes, no discutas ni contraataques; el acosador digital busca tu reacción pública para alimentar la polémica.\n"
            "2. **Respaldo probatorio inmediato:** Toma capturas de pantalla completas donde se aprecien nombres de usuario, enlaces (URLs), fechas y comentarios antes de que los borren.\n"
            "3. **Bloqueo y reporte:** Utiliza las herramientas de denuncia de la plataforma (Instagram, TikTok, WhatsApp, X) por acoso o difamación.\n"
            "4. **Denuncia formal:** Si existen amenazas, extorsión o difusión no autorizada de material íntimo/personal, acude con las pruebas a la División contra Delitos Informáticos de los cuerpos policiales de tu localidad."
        ), False

    # 15. ANSIEDAD LABORAL: PÁNICO ANTE CORREOS O MENSAJES
    if any(w in texto for w in ["siento panico cada vez que llega un correo", "siento pánico cada vez que llega un correo", "mensaje de mi entorno laboral", "como protejo mi salud mental"]):
        return nombre_avatar, (
            f"**Tu sistema nervioso ha condicionado las notificaciones de trabajo a una señal de ataque físico, {apodo}.**\n\n"
            "Cuando el entorno laboral es hostil, cada sonido de notificación genera una descarga refleja de cortisol que acelera tu pulso antes de que leas una sola línea.\n\n"
            "**Estrategia de blindaje mental inmediato:**\n"
            "1. **Silencia notificaciones fuera de horario:** Tu jornada tiene un principio y un final legal; no permitas que el estrés invada tu cama o tu mesa familiar.\n"
            "2. **La pausa de 10 segundos:** Ante un correo que te altere, no respondas en caliente. Apártate de la pantalla, exhala profundo y repite: *'Esto es solo trabajo, no define mi vida ni mi valor humano'*. Separa tu identidad de tu empleo."
        ), False

    # 16. DILEMA DE RENUNCIA: SALUD MENTAL VS. DINERO
    if any(w in texto for w in ["deberia renunciar a mi empleo por salud mental", "debería renunciar a mi empleo por salud mental", "aunque necesite urgentemente el dinero", "renunciar por salud mental"]):
        return nombre_avatar, (
            f"**Es uno de los dilemas más duros y legítimos, {apodo}: ningún empleo vale tu salud mental, pero el desempleo abrupto sin ingresos genera otra forma grave de ansiedad.**\n\n"
            "Salvo que estés sufriendo violencia física o acoso extremo insostenible que amerite denuncia inmediata, la salida más inteligente y protectora es una **estrategia de desconexión emocional y transición planificada**:\n\n"
            "1. **Baja el involucramiento emocional:** Cumple estrictamente con tus obligaciones formales sin dar horas extra ni buscar aprobación de jefes tóxicos (desconexión mental deliberada).\n"
            "2. **Enfoca tu energía en la salida:** Utiliza el tiempo libre para actualizar tu síntesis curricular, activar contactos y postular a nuevas ofertas laborales mientras conservas el sustento básico.\n"
            "Tu prioridad absoluta es tu paz, pero trazar una ruta ordenada te evitará caer en la asfixia financiera."
        ), False

    # 17. INSTANCIAS LEGALES ANTE ACOSO LABORAL (MOBBING)
    if any(w in texto for w in ["instancias legales o de recursos humanos", "acudir si sufro acoso en mi trabajo", "denunciar acoso laboral"]):
        return nombre_avatar, (
            f"**Tienes derecho a un ambiente de trabajo libre de violencia y hostigamiento, {apodo}. Estas son las instancias a las que debes acudir de forma escalonada:**\n\n"
            "1. **Dirección de Recursos Humanos / Comité de Seguridad y Salud:** Presenta una comunicación formal escrita con acuse de recibo exponiendo los hechos objetivos y solicitando la activación de los protocolos internos de resolución de conflictos.\n"
            "2. **Inspectoría del Trabajo (Ministerio del Trabajo):** Si la empresa es omisa o cómplice del acoso, puedes interponer una denuncia formal por hostigamiento laboral o solicitar una calificación de despido indirecto justificado.\n"
            "3. **INPSASEL (Instituto Nacional de Prevención, Salud y Seguridad Laborales):** Para certificar el daño psicosocial y las secuelas en la salud mental derivadas del ambiente laboral tóxico.\n"
            "Ve siempre con tu bitácora de evidencias y pruebas documentales en mano."
        ), False

    # 18. IDEACIÓN PASIVA DE ESCAPE
    if any(w in texto for w in ["dormir y no despertar", "dejar de sufrir, ¿eso significa", "dejar de sufrir, eso significa"]):
        return nombre_avatar, (
            f"**No necesariamente significa que desees acabar con tu vida, {apodo}; significa que estás agotado de sufrir.**\n\n"
            "Cuando el dolor emocional o la ansiedad se prolongan por mucho tiempo sin tregua, el cerebro busca desesperadamente una pausa para no seguir sintiendo esa sobrecarga. Desear dormir y no despertar es un síntoma de saturación biológica, no una sentencia de quién eres.\n\n"
            "Permite que un ser querido o un especialista te sostenga en este momento difícil. Recuerda que cuentas con la Línea de Ayuda Psicológica de la FPV (0212-4163116 / 0212-4163118). Respira despacio; estamos aquí para acompañarte."
        ), False

    # 19. ATAQUE DE PÁNICO AGUDO
    if any(w in texto for w in ["me va a dar un infarto", "da un infarto", "dar un infarto", "me estoy muriendo", "es un ataque de panico o me estoy muriendo", "es un ataque de pánico o me estoy muriendo"]):
        return nombre_avatar, (
            f"**No te estás muriendo ni te va a dar un infarto, {apodo}. Por favor, respira conmigo y lee esto con certeza absoluta.**\n\n"
            "Lo que estás experimentando es un **ataque de pánico**. La descarga de adrenalina tensa tu tórax y acelera tu corazón, pero es una reacción **totalmente inocua y biológicamente incapaz de causarte un infarto**. Tu corazón está sano y fuerte.\n\n"
            "Apoya los pies en el suelo, vacía el aire de tus pulmones soplando despacio por 6 segundos y déjalo entrar suavemente por la nariz en 4. La oleada alcanzará su pico y descenderá en minutos. Estás a salvo."
        ), False

    # 20. RESCATE SOMÁTICO INMEDIATO
    if any(w in texto for w in ["que puedo hacer de inmediato", "qué puedo hacer de inmediato", "la ansiedad me esta ganando", "la ansiedad me está ganando", "voy a perder el control"]):
        return nombre_avatar, (
            f"**No vas a perder el control, {apodo}. La ansiedad es una falsa alarma que va a ceder.**\n\n"
            "Aplica la técnica de anclaje sensorial **5-4-3-2-1**:\n"
            "• Nombra **5 cosas que veas** a tu alrededor.\n"
            "• Toca **4 texturas tangibles** (la mesa, tu ropa, el teléfono).\n"
            "• Escucha **3 sonidos** en tu entorno.\n"
            "• Identifica **2 olores** o respira hondo.\n"
            "• Saborea **1 cosa** o traga saliva despacio.\n"
            "Pon los pies firmes sobre el piso y exhala largo. Dime qué objeto tienes enfrente ahora mismo."
        ), False

    # 21. RUMIACIÓN CATASTRÓFICA
    if any(w in texto for w in ["escenarios catastroficos", "escenarios catastróficos", "mi mente no puede dejar de pensar"]):
        return nombre_avatar, (
            f"Lo que experimentas se llama **hipervigilancia anticipatoria**, {apodo}.\n\n"
            "Tu cerebro tiene sobreactivada la alarma biológica y busca peligros ficticios creyendo que así te protegerá. "
            "No pelees contra la mente: reconoce el pensamiento diciendo *'Gracias, cerebro, pero ahora estoy a salvo y los hechos reales están en orden'* y regresa a interactuar con lo tangible que te rodea."
        ), False

    # 22. SOMATIZACIÓN TOTAL
    if any(w in texto for w in ["dolores de cabeza", "gastritis", "tension muscular", "tensión muscular"]):
        return nombre_avatar, (
            f"**Es completamente normal, {apodo}.** La contractura muscular en nuca y mandíbula, la gastritis y el desvelo son la respuesta física del cortisol crónico en el cuerpo. "
            "Tu organismo no está fallando, está sobrecargado de tensión acumulada. Requiere pausas somáticas, calor local y exhalaciones lentas."
        ), False

    # 23. DESESPERANZA / CRONICIDAD
    if any(w in texto for w in ["alguna vez volvere a sentirme tranquilo", "alguna vez volveré a sentirme tranquilo", "esta opresion en el pecho para siempre", "esta opresión en el pecho para siempre"]):
        return nombre_avatar, (
            f"**Sí, vas a volver a sentirte tranquilo, {apodo}. Esta opresión no durará para siempre.**\n\n"
            "El sistema nervioso agotado pierde temporalmente la memoria de la calma y cree que el dolor será eterno. Tu plasticidad cerebral y tu capacidad biológica de equilibrio siguen intactas. Esto es una etapa, no tu estado definitivo."
        ), False

    # 24. TRISTEZA VS. DEPRESIÓN CLÍNICA
    if any(w in texto for w in ["tristeza profunda", "duelo normal"]) and any(w in texto for w in ["depresion clinica", "depresión clínica"]):
        return nombre_avatar, (
            f"La diferencia radica en que el duelo y la tristeza profunda vienen en olas y conservan la autoestima y la capacidad de recibir afecto; la depresión clínica es una niebla continua con anhedonia total, fatiga severa y culpa corrosiva hacia uno mismo que requiere intervención profesional estructurada."
        ), False

    # 25. INHIBICIÓN PSICOMOTRIZ VS. PEREZA
    if any(w in texto for w in ["no tengo energia", "no tengo energía", "levantarme de la cama o banarme", "levantarme de la cama o bañarme", "soy perezoso"]):
        return nombre_avatar, (
            f"**No es pereza, {apodo}; es inhibición psicomotriz por agotamiento de dopamina.** Tu cuerpo está biológicamente exhausto por sobrecarga emocional. Retira la culpa y da microavances diminutos sin autoexigencia."
        ), False

    # 26. ANHEDONIA
    if any(w in texto for w in ["ya no disfruto", "no disfruto las cosas", "volvere a recuperar el interes", "volveré a recuperar el interés"]):
        return nombre_avatar, (
            f"**Sí lo recuperarás, {apodo}. Se llama anhedonia y es una desconexión transitoria de los receptores de dopamina.** No esperes a tener ganas: la acción consciente precede a la motivación; involucrarte unos minutos de forma sencilla reactivará tus circuitos con el tiempo."
        ), False

    # 27. CULPA FAMILIAR
    if any(w in texto for w in ["como una carga para mi familia", "carga para mi familia"]):
        return nombre_avatar, (
            f"**No eres una carga, {apodo}; es la voz distorsionada de la depresión.** Quienes te aman lo hacen por afecto genuino, tal como tú los cuidarías a ellos. Recibir amor y apoyo es el puente necesario para sanar."
        ), False

    # 28. LABILIDAD EMOCIONAL / LLANTO
    if any(w in texto for w in ["ganas de llorar todo el dia", "ganas de llorar todo el día", "sin que haya una razon aparente", "sin que haya una razón aparente"]):
        return nombre_avatar, (
            f"**Es completamente normal, {apodo}. El llanto sin causa visible es la válvula de escape de un sistema nervioso que saturó su capacidad de aguante.** Permítete llorar sin culpa; las lágrimas reducen el cortisol acumulado."
        ), False

    # 29. CONSULTAS DE TRABAJO ACTUAL CON CONTEXTO HISTÓRICO
    if any(q in texto for q in ["en que trabajo actualmente", "en qué trabajo actualmente", "donde trabajo actualmente", "dónde trabajo actualmente", "cual es mi trabajo actual", "cuál es mi trabajo actual", "en que trabajo", "en qué trabajo", "a que me dedico", "a qué me dedico"]):
        menciono_desempleo = any(k in historial_str for k in ["perdi mi empleo", "perdí mi empleo", "perdi el trabajo", "perdí el trabajo", "sin empleo", "desempleado"])
        if menciono_desempleo:
            return nombre_avatar, (
                f"Tu profesión y formación de base es como **{profesion}**, {apodo}, pero como compartiste anteriormente, perdiste tu empleo en marzo. "
                "Por eso sé que estás en una etapa de transición y búsqueda. Tu identidad y capacidad profesional permanecen intactas contigo."
            ), False
        else:
            return nombre_avatar, f"Te desempeñas como {profesion}. Recuerda siempre que tu valor humano está por encima de cualquier etiqueta laboral.", False

    # 30. PREGUNTAS DE MEMORIA Y REGISTRO DE HIJOS
    if any(q in texto for q in ["cuantos hijos te dije", "cuántos hijos te dije", "cuantos hijos tengo", "cuántos hijos tengo", "mis hijos", "tengo hijos", "cantidad de hijos"]):
        return nombre_avatar, f"En tu registro y en nuestra conversación constan {hijos} {'hijo' if hijos == 1 else 'hijos'}, {apodo}.", False

    # 31. ORIENTACIÓN COMERCIAL Y RECARGA DE PLANES
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
                f"Puedes gestionar la activación o ampliación de tu plan con total serenidad, {apodo}. En el menú lateral izquierdo encontrarás la pestaña **'Planes y Suscripción'**. "
                "Allí, en la sección **'Coordinar Pago Privado con Admin'**, podrás solicitar los datos correspondientes para Pago Móvil BDV, Binance Pay o PayPal en un canal confidencial y seguro. "
                "El administrador te atenderá con gusto para activar tu acceso."
            ), False

    # 32. SALUDOS Y CORTESÍA
    if any(q in texto for q in ["hola", "buenas", "saludos", "brother", "que tal", "qué tal", "ola", "olá", "namaste", "namasté"]):
        if "ananya" in avatar_id:
            return nombre_avatar, f"Namasté, {apodo}. Qué alegría coincidir en este espacio de calma. Respira hondo y cuéntame con tranquilidad: ¿qué inquietud traes hoy en tu mente?", False
        elif "larissa" in avatar_id:
            return nombre_avatar, f"¡Olá, {apodo}! ¡Qué hermosa energía tenerte por aquí! Respira hondo, suelta los hombros y cuéntame con confianza: ¿de qué te gustaría conversar hoy?", False
        elif "camilo" in avatar_id:
            return nombre_avatar, f"¡Qué tal, mi hermano {apodo}! Un gustazo enorme saludarte. Suelta los hombros y cuéntame con confianza: ¿qué traes en mente hoy?", False
        else:
            return nombre_avatar, f"¡Hola {apodo}! Te doy una cálida bienvenida. Tómate un respiro y cuéntame de qué te gustaría conversar hoy.", False

    if any(q in texto for q in ["gracias", "obrigado", "obrigada", "dhanyavaad"]):
        return nombre_avatar, f"Es un placer acompañarte, {apodo}. La serenidad se cultiva paso a paso. Recuerda que siempre tienes este refugio para cuando lo necesites.", False

    # 33. RAG DINÁMICO ORGÁNICO (Cero Plantillas Robóticas Repetitivas)
    consejos = []
    for libro in LIBROS_CACHE:
        if libro.get("id_libro") in avatar_info.get("libros_rag_afines", []):
            consejos.append(libro.get("consejo_aplicable"))
    
    consejos_filtrados = [c for c in consejos if not any(c[:30] in h for h in historial)]
    consejo_seleccionado = random.choice(consejos_filtrados if consejos_filtrados else consejos) if consejos else "Lleva tu atención al momento presente y da un paso pequeño a la vez."

    if "camilo" in avatar_id:
        aperturas = [
            f"Te entiendo perfectamente, {apodo}. Mira, algo que siempre ayuda a ver las cosas claras es esto: {consejo_seleccionado}",
            f"Hermano {apodo}, cuando las aguas se ponen turbulentas, ten presente esta perspectiva: {consejo_seleccionado}",
            f"Comprendo la carga que traes, {apodo}. Reflexionemos un segundo sobre esto: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} Dime, ¿por dónde sientes que debemos empezar a desenredar esto?", False
    elif "ananya" in avatar_id:
        aperturas = [
            f"Comprendo la inquietud que se despierta en ti, {apodo}. Para encontrar quietud en medio del ruido, recuerda: {consejo_seleccionado}",
            f"Respira con calma, {apodo}. Una valiosa enseñanza para apaciguar la mente ante esta situación es esta: {consejo_seleccionado}",
            f"Te escucho con absoluta presencia, {apodo}. Observa este instante a través de esta reflexión: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} Cuéntame, ¿qué área de tu día sientes que puedes ordenar con mayor serenidad?", False
    elif "larissa" in avatar_id:
        aperturas = [
            f"¡Te siento tan de cerca, {apodo}! A veces la vida nos llena de tensión en el cuerpo, pero fíjate qué valioso es recordar esto: {consejo_seleccionado}",
            f"Querido {apodo}, abracemos este momento con calma. Una verdad hermosa para calmar el corazón es esta: {consejo_seleccionado}",
            f"Respira hondo conmigo, {apodo}. No cargues todo ese peso tú solo; ten presente: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} Cuéntame con toda calma, ¿qué paso sientes que tu corazón puede dar hoy?", False
    elif "anastasia" in avatar_id:
        aperturas = [
            f"Comprendo la situación, {apodo}. Si analizamos esto con perspectiva neuropsicológica: {consejo_seleccionado}",
            f"Evaluemos el asunto con objetividad, {apodo}. Ten presente este principio fundamental: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} ¿Cuál es el punto central que requiere nuestra atención prioritaria?", False
    else:
        aperturas = [
            f"Entiendo lo que estás viviendo, {apodo}. Algo que puede ayudarte a encontrar balance hoy es esto: {consejo_seleccionado}",
            f"Te escucho con empatía, {apodo}. Recuerda siempre esta guía: {consejo_seleccionado}"
        ]
        return nombre_avatar, f"{random.choice(aperturas)} ¿De qué manera sientes que podemos dar el siguiente paso?", False
