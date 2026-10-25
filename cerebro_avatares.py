import json
import os
import random
import re
from typing import Dict, Any, Tuple, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

# ==================================================================================================
# CATÁLOGO DE LOS 5 AVATARES OFICIALES SIMPLIFICADOS
# ==================================================================================================
AVATARES_5 = {
    "mariana": {
        "id": "mariana",
        "nombre": "Mariana Elena Rivas Delgado",
        "pais": "Venezuela",
        "bandera": "🇻🇪",
        "especialidad": "Relacionista Industrial y Clima Laboral",
        "tono": "Cálido, espontáneo ('epa'), resolutivo y enfocado en límites humanos y laborales.",
        "imagen": "avatares/mariana.png",
        "disparador_inicial": "¡Epa! Aquí estoy para escucharte y ayudarte a poner orden sin que te gane el estrés.",
        "arbol_opciones": {
            "raiz": [
                {"id": "mar_bloqueo", "texto": "💼 Me siento bloqueado/a y saturado/a de trabajo"},
                {"id": "mar_limites", "texto": "🛡️ No sé cómo poner límites a mi jefe o compañeros"},
                {"id": "mar_ansiedad_futuro", "texto": "⏳ Tengo incertidumbre por mi estabilidad económica"},
                {"id": "mar_desahogo", "texto": "☕ Solo necesito desahogarme un momento"}
            ],
            "respuestas": {
                "mar_bloqueo": {
                    "texto": "¡Epa! Para ahí mismo. Esa sensación de 'montaña de pendientes' la conozco al detalle: el cerebro entra en cortocircuito por autoprotección.\n\nVamos a desarmar esa montaña juntos: escoge una sola tarea diminuta (responder un solo correo corto o archivar un documento). Haz esa y date permiso de soltar el resto por 20 minutos. El avance no arranca con motivación; la motivación llega después de la primera micro-acción.",
                    "opciones_siguientes": [
                        {"id": "mar_micro_accion", "texto": "✅ ¿Cómo elijo esa micro-tarea sin sentir culpa?"},
                        {"id": "mar_pausa", "texto": "🫁 Enséñame una pausa rápida de 2 minutos"},
                        {"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}
                    ]
                },
                "mar_micro_accion": {
                    "texto": "Aplica la regla de los dos minutos: si toma menos de 120 segundos, hazla ya; si toma más, anótala en un papel y divídela a la mitad. No intentes ser un robot; hoy el objetivo no es la perfección, sino el cuidado de tu energía.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "mar_pausa": {
                    "texto": "Suelta el ratón y la pantalla ahora mismo. Levántate, estira los brazos hacia el techo, bebe medio vaso de agua a temperatura ambiente y respira profundo tres veces. La empresa sigue existiendo; tu salud va primero.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "mar_limites": {
                    "texto": "Poner límites no es pelear ni ser grosero/a; es cuidar las reglas del juego. Cuando te asignen una sobrecarga abusiva, responde con claridad ejecutiva: 'Entiendo la urgencia de esta tarea; para incluirla hoy con calidad, ¿cuál de los otros tres proyectos previos ponemos en pausa?'. Eso traslada la responsabilidad de priorizar a quien corresponde.",
                    "opciones_siguientes": [
                        {"id": "mar_culpa_decir_no", "texto": "😔 Pero me da miedo o culpa decir que no"},
                        {"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}
                    ]
                },
                "mar_culpa_decir_no": {
                    "texto": "La culpa aparece porque te acostumbraste a complacer para estar en paz. Pero recuerda esto con fuerza: cada vez que le dices que sí a una exigencia desmedida de otros, te estás diciendo que no a ti mismo/a y a tu descanso.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "mar_ansiedad_futuro": {
                    "texto": "La mente suele viajar a escenarios catastróficos que rara vez suceden. Siéntate, toma aire y pregúntate: '¿Qué paso real y concreto puedo dar HOY para cuidar mi ingreso o mi profesión?'. Lo que pasará dentro de tres meses no lo resuelves hoy; cuida el paso que estás dando en este minuto.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "mar_desahogo": {
                    "texto": "Tómate tu tiempo. Aquí no hay evaluaciones de desempeño ni jefes mirando. Si quieres escribirlo todo con tus propias palabras o desahogarte en el chat libre, adelante. Te leo con atención y respeto.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                }
            }
        }
    },
    "camilo": {
        "id": "camilo",
        "nombre": "Camilo Ernesto Valdés Portuondo",
        "pais": "Cuba",
        "bandera": "🇨🇺",
        "especialidad": "Médico General y Fisioterapeuta",
        "tono": "Cálido, fraterno ('mi hermano'), clínico preventivo y con sabiduría de sentido común.",
        "imagen": "avatares/camilo.png",
        "disparador_inicial": "Oye, mi hermano/a, pasa y descansa un momento. Dime qué señales te está enviando el cuerpo hoy.",
        "arbol_opciones": {
            "raiz": [
                {"id": "cam_taquicardia", "texto": "💓 Siento el corazón acelerado y opresión en el pecho"},
                {"id": "cam_falta_aire", "texto": "🫁 Siento que el aire no me entra bien a los pulmones"},
                {"id": "cam_tension_cuello", "texto": "💆‍♂️ Tengo el cuello, mandíbula y hombros como una piedra"},
                {"id": "cam_atracones", "texto": "🍫 Ansiedad por comer dulce o picar de noche"}
            ],
            "respuestas": {
                "cam_taquicardia": {
                    "texto": "Tranquilo/a, pon los pies firmes en el suelo y mírame aquí: un corazón sano no se detiene ni te va a dar un infarto por una crisis de ansiedad. Lo que experimentas es una descarga simpática de adrenalina: tu cuerpo se puso en guardia como si hubiera un peligro físico real.\n\nEsa adrenalina tarda entre 3 y 8 minutos en metabolizarse. Siéntate cómodo, vacía el aire de los pulmones con un suspiro largo y toma un sorbo de agua fresca. El ritmo va a bajar solo, confía en tu cuerpo.",
                    "opciones_siguientes": [
                        {"id": "cam_respiracion_vago", "texto": "🫀 ¿Cómo estimulo el nervio vago para bajar pulsaciones?"},
                        {"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}
                    ]
                },
                "cam_respiracion_vago": {
                    "texto": "Haz esto conmigo: toma aire por la nariz en 4 tiempos, y luego bótalo muy suave por la boca frunciendo los labios (como soplando una sopa caliente) en 7 u 8 tiempos. Al alargar la exhalación, el diafragma le envía un mensaje bioeléctrico al corazón para que baje revoluciones.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "cam_falta_aire": {
                    "texto": "No te falta el aire; al contrario: estás hiperventilando por respirar corto y superficial con la parte alta del tórax. Tus pulmones están llenos de aire viejo residual.\n\nHaz esto: exhala TODO el aire hasta que sientas el abdomen plano. Aguanta dos segundos vacío, y luego deja que el aire entre por la nariz de manera natural sin forzar el pecho.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "cam_tension_cuello": {
                    "texto": "Es el reflejo somático del susto: los hombros suben para proteger las carótidas del cuello. Vamos a soltarlo: sube los dos hombros hacia las orejas apretando fuerte por 5 segundos... y ahora ¡suéltalos de golpe con un suspiro! Repítelo 3 veces.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "cam_atracones": {
                    "texto": "De noche el cortisol elevado del día choca con la fatiga cerebral, y la mente busca una inyección rápida de dopamina en el azúcar. No te castigues con culpas; hidrátate primero con una infusión caliente (manzanilla o tilo) y dale 15 minutos a tu estómago antes de asaltar la cocina.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                }
            }
        }
    },
    "rodrigo": {
        "id": "rodrigo",
        "nombre": "Rodrigo Javier Navas Serrano",
        "pais": "España",
        "bandera": "🇪🇸",
        "especialidad": "Abogado Penalista y Mediador",
        "tono": "Sobrio, pragmático, castellano directo, realista y con profundo sentido común.",
        "imagen": "avatares/rodrigo.png",
        "disparador_inicial": "Hola. Vamos a aplicar sentido común y a ordenar las cosas que de verdad están en tu mano resolver.",
        "arbol_opciones": {
            "raiz": [
                {"id": "rod_insomnio_deudas", "texto": "🌙 Estoy en la cama dando vueltas pensando en deudas o dinero"},
                {"id": "rod_conflicto_legal", "texto": "⚖️ Tengo un problema legal, laboral o administrativo que me asusta"},
                {"id": "rod_rumiacion_peor", "texto": "🌪️ Mi cabeza no para de imaginar el peor escenario posible"},
                {"id": "rod_acoso", "texto": "🛑 Siento hostigamiento o acoso en mi entorno"}
            ],
            "respuestas": {
                "rod_insomnio_deudas": {
                    "texto": "Mira, seamos claros y pragmáticos: a las tres de la madrugada no se liquida una hipoteca, no abre el banco ni se firma un acuerdo en el juzgado. Quedarte en la cama mirando el techo solo te garantiza llegar agotado al momento en que sí tengas que tomar decisiones despierto.\n\nSal de la cama 10 minutos. Coge papel y lápiz, escribe los dos asuntos puntuales que atenderás a partir de las 9:00 AM y regresa a la cama únicamente a darle reposo físico al esqueleto. Quitarte la obligación de dormir es lo que te devolverá el sueño.",
                    "opciones_siguientes": [
                        {"id": "rod_control_real", "texto": "📋 ¿Cómo ordeno las deudas para no ahogarme?"},
                        {"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}
                    ]
                },
                "rod_control_real": {
                    "texto": "Primero la lista fría: acreedor, cuantía total y fecha. No mezcles emociones con números. Habla con las partes antes de que venza el plazo; en derecho y en finanzas, quien se anticipa y propone un plan de pagos razonable siempre tiene mejor posición de negociación que quien se esconde.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "rod_conflicto_legal": {
                    "texto": "El miedo procesal se alimenta de la falta de información contrastada. Deja de buscar sentencias en internet a medianoche. Separa hechos objetivos de suposiciones dramáticas. Si hay una notificación oficial, léela despacio, consulta con el profesional competente y respeta los plazos con cabeza fría.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "rod_rumiacion_peor": {
                    "texto": "El cerebro ansioso monta juicios rápidos donde tú eres siempre el condenado sin pruebas. Apliquemos la prueba pericial: ¿qué evidencias reales y tangibles tienes hoy de que esa catástrofe vaya a suceder? El 90% de lo que tememos jamás llega a los tribunales de la realidad.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "rod_acoso": {
                    "texto": "Ante el acoso (laboral o vecinal) la regla de oro es: NADA DE PALABRAS AL AIRE. Bitácora confidencial exhaustiva: anota fecha, hora exacta, lugar, hechos concretos sin adjetivos y posibles testigos. Toda comunicación sensible con el hostigador, por escrito resguardado. No confrontes en caliente; crea expediente probatorio.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                }
            }
        }
    },
    "larissa": {
        "id": "larissa",
        "nombre": "Larissa Beatriz Fonseca de Oliveira",
        "pais": "Brasil",
        "bandera": "🇧🇷",
        "especialidad": "Psicóloga Clínica y Arteterapeuta Somática",
        "tono": "Vivaz, afectuoso, profundamente compasivo, corporal y enfocado en la autoaceptación.",
        "imagen": "avatares/larissa.png",
        "disparador_inicial": "¡Olá, querido/a! Coloca tu mano sobre el pecho un momento. Vamos a respirar juntos sin prisas.",
        "arbol_opciones": {
            "raiz": [
                {"id": "lar_anclaje_54321", "texto": "🌿 Necesito volver a la calma con un ejercicio de anclaje"},
                {"id": "lar_culpa_descanso", "texto": "😔 Siento culpa cuando intento descansar o no hacer nada"},
                {"id": "lar_tristeza_desanimo", "texto": "🌧️ Tengo una tristeza pesada y poco ánimo"},
                {"id": "lar_autoexigencia", "texto": "🎯 Siento que nunca hago lo suficiente"}
            ],
            "respuestas": {
                "lar_anclaje_54321": {
                    "texto": "Vamos a hacer este anclaje sensorial juntas/os para traer a tu mente de vuelta a este instante seguro:\n\n👀 **5 cosas** que puedas ver a tu alrededor (fíjate en sus colores y formas).\n✋ **4 cosas** que puedas tocar (la textura de tu ropa, la mesa, tus manos).\n👂 **3 sonidos** que escuches ahora mismo (lejanos o cercanos).\n👃 **2 aromas** que puedas percibir en el ambiente.\n👅 **1 sabor** que quede en tu boca (o un trago suave de agua).\n\nRespira lento. Estás aquí, en tu presente, y en este minuto exacto estás a salvo.",
                    "opciones_siguientes": [
                        {"id": "lar_respiracion_corazon", "texto": "💖 Guíame en una respiración con la mano en el pecho"},
                        {"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}
                    ]
                },
                "lar_respiracion_corazon": {
                    "texto": "Coloca tu palma abierta sobre el centro de tu pecho. Siente el calorcito que emana. Inhala despacio imaginando que ese calor llena tus pulmones... y exhala suave soltando los hombros. No tienes que arreglar nada en los próximos dos minutos; solo existir y respirar.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "lar_culpa_descanso": {
                    "texto": "Nos enseñaron que valemos por lo que producimos, pero eso es una trampa. Descansar conscientemente no es un premio que debes ganarte con sufrimiento; es una necesidad biológica tan vital como el agua. Permitirte reposar es un acto de amor hacia tu propio cuerpo.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "lar_tristeza_desanimo": {
                    "texto": "No pelee contra esa tristeza ni intentes taparla con una sonrisa falsa. La tristeza es solo tu alma pidiendo una pausa y un abrazo. Dale permiso de estar un ratito; arropate, toma algo tibio y permítete un ritmo más suave hoy.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "lar_autoexigencia": {
                    "texto": "Eres tu crítico más severo. Si le hablaras a tu mejor amigo con la dureza con la que te juzgas a ti mismo/a, no te duraría un día. Sé más compasivo/a con tus propios límites: estás haciendo lo mejor que puedes con los recursos que tienes hoy.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                }
            }
        }
    },
    "anastasia": {
        "id": "anastasia",
        "nombre": "Anastasia Yurievna Volkova",
        "pais": "Rusia",
        "bandera": "🇷🇺",
        "especialidad": "Neuropsicóloga Clínica y Lingüista Cognitiva",
        "tono": "Analítico, sobrio, de alto rigor neurocientífico, estructurado y reconfortante.",
        "imagen": "avatares/anastasia.png",
        "disparador_inicial": "Saludos. Desarticulemos la sobrecarga de tu mente mediante la observación objetiva de tus procesos cognitivos.",
        "arbol_opciones": {
            "raiz": [
                {"id": "ana_rumiacion", "texto": "🔄 Pensamientos en bucle que no puedo detener"},
                {"id": "ana_despersonalizacion", "texto": "🌫️ Siento que estoy desconectado/a de mi cuerpo o de la realidad"},
                {"id": "ana_niebla_mental", "texto": "🧠 Tengo niebla mental y me cuesta concentrarme"},
                {"id": "ana_catastrofismo", "texto": "⚡ Mi mente anticipa peligros constantemente"}
            ],
            "respuestas": {
                "ana_rumiacion": {
                    "texto": "El bucle mental de rumiación ocurre cuando la Red Neuronal por Defecto (DMN) hiperactiva escenarios pasados o futuros sin vincularse al sistema de ejecución motora.\n\nPara interrumpir este ciclo neuroquímico, necesitamos activar deliberadamente la Red de Tarea Positiva: toma un objeto cercano con tu mano, descríbelo en voz alta con tres adjetivos físicos (peso, temperatura, textura) y realiza una resta regresiva de 7 en 7 desde el 100 hasta el 72. Esto forzará al lóbulo frontal a recuperar la dirección consciente del pensamiento.",
                    "opciones_siguientes": [
                        {"id": "ana_registro_pensamientos", "texto": "📝 ¿Cómo desmonto la distorsión del pensamiento?"},
                        {"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}
                    ]
                },
                "ana_registro_pensamientos": {
                    "texto": "Aplica la técnica de la triple columna cognitiva: 1) Pensamiento automático intrusivo ('Voy a fracasar'). 2) Evidencias fácticas en contra ('En situaciones similares anteriores he sabido resolver'). 3) Pensamiento alternativo realista ('Es un desafío complejo, pero tengo capacidad de abordarlo por fases').",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "ana_despersonalizacion": {
                    "texto": "La desrealización o extrañeza corporal es un mecanismo defensivo benigno del sistema nervioso ante niveles elevados de ansiedad. El cerebro reduce temporalmente el procesamiento sensorial para evitar sobrecargas. No estás perdiendo el juicio. Se desactiva gradualmente al descender los niveles plasmáticos de cortisol.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "ana_niebla_mental": {
                    "texto": "La niebla mental no es deterioro biológico, sino fatiga atencional por exceso de procesamiento defensivo. Tu memoria de trabajo tiene un cupo limitado; cuando destinas el 70% de tus recursos a monitorear la ansiedad, solo queda un 30% para tus labores. Reduce las tareas a una sola unidad secuencial.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                },
                "ana_catastrofismo": {
                    "texto": "La amígdala cerebral está genéticamente programada para preferir el falso positivo ('pensar que hay un león donde solo hay viento') que el falso negativo. Tu mente intenta protegerte mediante el sesgo de confirmación pesimista. Reconócelo: 'Es mi cerebro intentando protegerme con una hipótesis improbable, no una certeza fáctica'.",
                    "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones principales"}]
                }
            }
        }
    }
}

# ==================================================================================================
# CARGA DE BIBLIOTECA RAG COMPLEMENTARIA
# ==================================================================================================
LIBROS_CACHE: List[Dict[str, Any]] = []
if os.path.exists("catalogo_rag_avatares.json"):
    try:
        with open("catalogo_rag_avatares.json", "r", encoding="utf-8") as f:
            datos_json = json.load(f)
            LIBROS_CACHE = datos_json.get("biblioteca_rag", [])
    except Exception as e:
        print(f"[CEREBRO AVATARES] Aviso: No se pudo cargar biblioteca RAG: {e}")

# ==================================================================================================
# PATRONES DE PROTECCIÓN ÉTICA Y SEGURIDAD CLÍNICA
# ==================================================================================================
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
    """Devuelve la lista estructurada de los 5 avatares con su ruta de opciones raíz."""
    catalogo = []
    for k, v in AVATARES_5.items():
        catalogo.append({
            "id": k,
            "nombre": v["nombre"],
            "pais": v["pais"],
            "bandera": v["bandera"],
            "tono": v["tono"],
            "imagen": v["imagen"],
            "is_activo": k in activos_usuario,
            "disparador_inicial": v["disparador_inicial"],
            "opciones_iniciales": v["arbol_opciones"]["raiz"]
        })
    return catalogo

def existe_avatar(avatar_id: str) -> bool:
    return avatar_id in AVATARES_5

def obtener_opciones_raiz(avatar_id: str) -> List[Dict[str, str]]:
    if avatar_id in AVATARES_5:
        return AVATARES_5[avatar_id]["arbol_opciones"]["raiz"]
    return []

async def llamar_gemini_avatar_async(prompt_sistema: str, historial: list, mensaje_actual: str) -> str:
    """Enlace asíncrono con Gemini REST moderno para peticiones libres que requieran IA generativa."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return ""

    conversacion_previa = "\n".join(historial[-4:]) if historial else ""
    prompt_completo = (
        f"{prompt_sistema}\n\n"
        f"Historial previo:\n{conversacion_previa}\n\n"
        f"Usuario dice: {mensaje_actual}\n\n"
        f"Responde directamente como tu avatar sin rodeos:"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt_completo}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client_http:
            resp = await client_http.post(url, json=payload)
            if resp.status_code == 200:
                data_api = resp.json()
                candidatos = data_api.get("candidates", [])
                if candidatos:
                    partes = candidatos[0].get("content", {}).get("parts", [])
                    if partes:
                        return partes[0].get("text", "").strip()
    except Exception as e_http:
        print(f"[CEREBRO AVATARES] Timeout/Excepción Gemini: {e_http}")

    return ""

# ==================================================================================================
# PROCESADOR PRINCIPAL (4 VALORES DE RETORNO)
# ==================================================================================================
async def procesar_respuesta_avatar(
    avatar_id: str, 
    mensaje_usuario: str, 
    opcion_id: Optional[str] = None,
    perfil_usuario: Optional[dict] = None, 
    historial_reciente: Optional[list] = None
) -> Tuple[str, str, bool, List[Dict[str, str]]]:
    """
    Procesa la interacción con el avatar entregando:
    (nombre_avatar, respuesta_texto, es_crisis, opciones_siguientes)
    """
    perfil = perfil_usuario or {}
    avatar_info = AVATARES_5.get(avatar_id, AVATARES_5["mariana"])
    nombre_avatar = avatar_info["nombre"]
    arbol = avatar_info["arbol_opciones"]

    apodo_crudo = perfil.get("apodo", "amigo/a").strip()
    apodo = "Juan Carlos" if apodo_crudo.lower() == "admin" else apodo_crudo.replace("Admin ", "").strip()
    
    texto = (mensaje_usuario or "").strip()
    texto_lower = texto.lower()

    # 1. FILTRO ROJO DE CRISIS (SOS INMEDIATO)
    for patron in PATRONES_CRISIS_SOS:
        if re.search(patron, texto_lower):
            respuesta_sos = (
                f"🚨 **{apodo}, por favor detente un momento. Tu vida y tu integridad son lo primordial.**\n\n"
                "Siento profundamente el dolor y el agobio que estás sintiendo ahora mismo, pero este espacio es una guía reflexiva de acompañamiento; no sustituye la atención médica ni psicológica urgente.\n\n"
                "**Por favor, comunícate de inmediato con estos recursos gratuitos y confidenciales:**\n"
                "• **España:** Llama al 024 (Atención a la Conducta Suicida) o al 717 003 717 (Teléfono de la Esperanza).\n"
                "• **Venezuela:** Línea de Ayuda Psicológica FPV (0212-4163116 / 0212-4163118).\n"
                "• **Estados Unidos / Internacional:** Marca al 988 o visita https://www.befrienders.org\n"
                "• **Emergencias Generales:** Llama al 112, 911 o acude al centro de urgencias más cercano.\n\n"
                "No te quedes a solas con este sufrimiento. Da el paso de pedir ayuda hoy mismo."
            )
            return nombre_avatar, respuesta_sos, True, []

    # 2. CONTENCIÓN ANTE AGRESIÓN SEXUAL O VIOLACIÓN
    if any(re.search(p, texto_lower) for p in PATRONES_AGRESION_SEXUAL):
        respuesta_abuso = (
            f"Escúchame con toda claridad, {apodo}: **tú no tienes absolutamente ninguna culpa de lo ocurrido.** "
            "La responsabilidad total recae sobre quien cometió la agresión. Es comprensible que sientas dolor, asco o desconexión con tu cuerpo; "
            "tu cuerpo es el templo que resistió para mantenerte con vida hoy.\n\n"
            "Tu prioridad inmediata es tu resguardo: acude a un centro médico de urgencias si el hecho fue reciente y apóyate en profesionales "
            "especializados en trauma sexual. Tu dignidad y tu valor humano permanecen intactos."
        )
        return nombre_avatar, respuesta_abuso, False, arbol["raiz"]

    # 3. NAVEGACIÓN DETERMINISTA POR ÁRBOL DE OPCIONES (COSTO $0 USD Y RESPUESTA INMEDIATA)
    if opcion_id:
        if opcion_id == "raiz":
            return nombre_avatar, f"¿Qué aspecto te gustaría abordar ahora, {apodo}?", False, arbol["raiz"]
        
        nodo = arbol.get("respuestas", {}).get(opcion_id)
        if nodo:
            return nombre_avatar, nodo["texto"], False, nodo.get("opciones_siguientes", arbol["raiz"])

    # 4. FILTRO DE PAGOS Y SUSCRIPCIÓN
    patron_pago = r"\b(recargar|adquirir plan|cambiar de plan|subir de plan|pagar suscripci[oó]n|m[eé]todos de pago|pago m[oó]vil|binance pay)\b"
    if re.search(patron_pago, texto_lower):
        resp_pago = (
            f"Puedes coordinar la renovación o ascenso de tu plan de forma privada, {apodo}. "
            "En el menú lateral encontrarás la pestaña de 'Planes y Suscripción', donde podrás acordar los detalles de manera confidencial directamente con el Administrador."
        )
        return nombre_avatar, resp_pago, False, arbol["raiz"]

    # 5. SALUDOS O CONSULTAS GENERALES
    if any(s in texto_lower for s in ["hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", "cómo estás"]):
        return nombre_avatar, f"¡Hola, {apodo}! Qué alegría coincidir contigo. Selecciona una de las opciones guiadas o cuéntame con tus palabras cómo te sientes hoy.", False, arbol["raiz"]

    # 6. LLAMADA GENERATIVA A GEMINI PARA MENSAJES LIBRES ABIERTOS
    prompt_sistema = f"""Eres {nombre_avatar}, originario de {avatar_info['pais']}.
Tu especialidad: {avatar_info['especialidad']}.
Tu tono característico: {avatar_info['tono']}.
Estás conversando con {apodo}.
Marco ético: Espacio reflexivo y psicoeducativo de acompañamiento. Prohibido diagnosticar clínicamente o prescribir fármacos.
Jerarquía de dolor sobre datos: si el usuario manifiesta dolor por un familiar o hijo, prioriza la contención compasiva sin confrontar con registros de la base de datos."""

    resp_llm = await llamar_gemini_avatar_async(prompt_sistema, historial_reciente or [], texto)
    if resp_llm:
        return nombre_avatar, resp_llm, False, arbol["raiz"]

    # 7. FALLBACK OFFLINE DIALECTAL DETERMINISTA
    respuestas_fallback = {
        "mariana": f"Te escucho con calma, {apodo}. Para resolver lo que tienes encima, vamos a descomponerlo paso a paso sin saturarnos.",
        "camilo": f"Oye, {apodo}, como médico te digo: respira hondo, apoya los pies firmes y cuéntame un poco más para abordarlo juntos.",
        "rodrigo": f"Comprendo la inquietud, {apodo}. Vamos a aplicar sentido común y a separar lo que puedes controlar hoy de lo que no.",
        "larissa": f"Siento lo que me compartes, {apodo}. Pon tu mano en el pecho, suelta los hombros y tómate tu tiempo. Aquí estoy a tu lado.",
        "anastasia": f"Analicemos la situación con objetividad, {apodo}. Desglosa lo que sientes en hechos concretos para orientar el pensamiento con claridad."
    }
    
    texto_fallback = respuestas_fallback.get(avatar_id, f"{apodo}, estoy aquí para acompañarte en tu serenidad. Cuéntame un poco más.")
    return nombre_avatar, texto_fallback, False, arbol["raiz"]