import json
import os
import random
import re
from typing import Dict, Any, Tuple, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

# ==================================================================================================
# CATÁLOGO DE LOS 5 GUÍAS OFICIALES Y DATOS BIOGRÁFICOS BASE
# ==================================================================================================
AVATARES_5 = {
    "mariana": {
        "id": "mariana",
        "nombre": "Mariana Elena Rivas Delgado",
        "pais": "Venezuela",
        "bandera": "🇻🇪",
        "especialidad": "Relacionista Industrial, Consultora de RRHH y Clima Laboral",
        "tono": "Cálido, espontáneo ('epa'), resolutivo y enfocado en límites humanos y laborales.",
        "imagen": "avatares/mariana.png",
        "disparador_inicial": "¡Epa! Aquí estoy para escucharte y ayudarte a poner orden sin que te gane el estrés."
    },
    "camilo": {
        "id": "camilo",
        "nombre": "Camilo Ernesto Valdés Portuondo",
        "pais": "Cuba",
        "bandera": "🇨🇺",
        "especialidad": "Médico General Integral y Fisioterapeuta",
        "tono": "Cálido, fraterno ('mi hermano'), clínico preventivo y con sabiduría de sentido común.",
        "imagen": "avatares/camilo.png",
        "disparador_inicial": "Oye, mi hermano/a, pasa y descansa un momento. Dime qué señales te está enviando el cuerpo hoy."
    },
    "rodrigo": {
        "id": "rodrigo",
        "nombre": "Rodrigo Javier Navas Serrano",
        "pais": "España",
        "bandera": "🇪🇸",
        "especialidad": "Abogado Penalista y Mediador Penitenciario",
        "tono": "Sobrio, pragmático, castellano directo, realista y con profundo sentido común.",
        "imagen": "avatares/rodrigo.png",
        "disparador_inicial": "Hola. Vamos a aplicar sentido común y a ordenar las cosas que de verdad están en tu mano resolver."
    },
    "larissa": {
        "id": "larissa",
        "nombre": "Larissa Beatriz Fonseca de Oliveira",
        "pais": "Brasil",
        "bandera": "🇧🇷",
        "especialidad": "Psicóloga Clínica y Arteterapeuta Somática",
        "tono": "Vivaz, afectuoso, profundamente compasivo, corporal y enfocado en la autoaceptación.",
        "imagen": "avatares/larissa.png",
        "disparador_inicial": "¡Olá, querido/a! Coloca tu mano sobre el pecho un momento. Vamos a respirar juntos sin prisas."
    },
    "anastasia": {
        "id": "anastasia",
        "nombre": "Anastasia Yurievna Volkova",
        "pais": "Rusia",
        "bandera": "🇷🇺",
        "especialidad": "Neuropsicóloga Clínica y Lingüista Cognitiva",
        "tono": "Analítico, sobrio, de alto rigor neurocientífico, estructurado y reconfortante.",
        "imagen": "avatares/anastasia.png",
        "disparador_inicial": "Saludos. Desarticulemos la sobrecarga de tu mente mediante la observación objetiva de tus procesos cognitivos."
    }
}

# ==================================================================================================
# MATRIZ OFICIAL: 13 PROBLEMÁTICAS, ASIGNACIÓN DE AVATARES Y ÁRBOLES PREDEFINIDOS ($0 USD)
# ==================================================================================================
CATALOGO_PROBLEMAS = {
    "ansiedad_panico": {
        "id": "ansiedad_panico",
        "titulo": "Ansiedad y Ataques de Pánico Físico",
        "descripcion": "Taquicardia, palpitaciones, falta de aire, temblores y opresión torácica.",
        "avatares": ["camilo", "larissa"],
        "raiz": [
            {"id": "p1_panico", "texto": "💓 Siento que el corazón se me va a salir y me falta el aire"},
            {"id": "sub_p1_nudo", "texto": "🫁 ¿Cómo aflojo el nudo en la garganta o el estómago ahora mismo?"},
            {"id": "sub_p2_desmayo", "texto": "🌫️ Siento que me voy a desmayar por respirar corto"},
            {"id": "sub_p3_infarto", "texto": "🩺 ¿Qué diferencia hay entre este pánico y un infarto real?"}
        ]
    },
    "depresion_vacio": {
        "id": "depresion_vacio",
        "titulo": "Depresión, Vacío y Desesperanza",
        "descripcion": "Tristeza profunda, falta de energía, apatía y pérdida de sentido vital.",
        "avatares": ["anastasia", "larissa"],
        "raiz": [
            {"id": "p2_vacio", "texto": "🌧️ Siento un vacío que no se quita y no tengo ganas de nada"},
            {"id": "sub_p4_atencion", "texto": "🧠 No logro concentrarme ni leer dos páginas seguidas"},
            {"id": "sub_p5_pesimismo", "texto": "🔄 ¿Cómo desarmo la idea de que todo me saldrá mal?"},
            {"id": "sub_p6_culpa_triste", "texto": "😔 Me siento culpable por estar triste teniendo 'todo'"}
        ]
    },
    "angustia_deudas": {
        "id": "angustia_deudas",
        "titulo": "Angustia, Deudas y Rumiación Financiera",
        "descripcion": "Insomnio por dinero, demandas, compromisos económicos y vergüenza patrimonial.",
        "avatares": ["rodrigo", "mariana"],
        "raiz": [
            {"id": "p3_deudas", "texto": "🌙 No puedo dormir pensando en deudas y siento vergüenza"},
            {"id": "sub_p15_familia", "texto": "👨‍👩‍👧 ¿Cómo le explico a mi familia la quiebra sin derrumbarlos?"},
            {"id": "mar_micro_accion", "texto": "📋 ¿Cómo ordeno los pagos para salir de la parálisis?"}
        ]
    },
    "bullying_acoso_escolar": {
        "id": "bullying_acoso_escolar",
        "titulo": "Bullying Escolar y Ciberacoso Digital",
        "descripcion": "Burlas, exclusión escolar, stickers o difamación en grupos de redes sociales.",
        "avatares": ["larissa", "mariana"],
        "raiz": [
            {"id": "p4_bullying", "texto": "📱 Se burlan de mí en WhatsApp y no quiero volver a clases"},
            {"id": "sub_p7_pasillo", "texto": "🚶‍♂️ ¿Cómo reacciono si me acorralan en el pasillo o la salida?"},
            {"id": "sub_p8_perfil_falso", "texto": "🛡️ Crearon un perfil falso con mis fotos, ¿qué hago?"},
            {"id": "sub_p9_panico_lunes", "texto": "🚪 Tengo terror de pisar el aula el lunes"}
        ]
    },
    "acoso_sexual": {
        "id": "acoso_sexual",
        "titulo": "Acoso Sexual y Abuso de Poder",
        "descripcion": "Insinuaciones indebidas, tocamientos, chantajes y culpa inducida en trabajo o entorno.",
        "avatares": ["larissa", "rodrigo"],
        "raiz": [
            {"id": "p5_acoso_sex", "texto": "🛑 Un conocido/superior me tocó sin permiso y me amenazó"},
            {"id": "sub_p10_asco", "texto": "🪞 ¿Cómo manejo el asco y el rechazo a mi propio cuerpo?"},
            {"id": "sub_p11_credibilidad", "texto": "⚖️ Me da pánico denunciar y que no me crean"},
            {"id": "sub_p12_contacto", "texto": "✋ No soporto que nadie se me acerque físicamente"}
        ]
    },
    "acoso_laboral_mobbing": {
        "id": "acoso_laboral_mobbing",
        "titulo": "Acoso Laboral (Mobbing) y Burnout",
        "descripcion": "Descalificaciones del jefe, sobrecarga intencional, humillaciones y desgaste extremo.",
        "avatares": ["mariana", "rodrigo"],
        "raiz": [
            {"id": "p6_mobbing", "texto": "💼 Mi jefe me descalifica delante de todos y me satura"},
            {"id": "sub_p13_puerta_cerrada", "texto": "🚪 Me grita o presiona a solas donde no hay testigos"},
            {"id": "sub_p14_miedo_renuncia", "texto": "⏳ Tengo pánico de renunciar y quedarme sin sustento"},
            {"id": "mar_limites", "texto": "🛡️ Enséñame a responder con firmeza sin perder el empleo"}
        ]
    },
    "victimas_abuso_violencia": {
        "id": "victimas_abuso_violencia",
        "titulo": "Víctimas de Violencia Física o Abuso",
        "descripcion": "Sobrevivientes de agresiones directas, golpes, asaltos y relaciones violentas.",
        "avatares": ["rodrigo", "larissa"],
        "raiz": [
            {"id": "p7_violencia", "texto": "⚡ Fui víctima de una agresión violenta y vivo con terror"},
            {"id": "sub_p17_sirenas", "texto": "🚨 Un sonido fuerte o seco me hace temblar incontrolable"},
            {"id": "sub_p18_repeticion", "texto": "🌪️ Siento que en cualquier momento se repetirá el ataque"}
        ]
    },
    "miedos_fobias": {
        "id": "miedos_fobias",
        "titulo": "Personas que no Pueden Superar sus Miedos",
        "descripcion": "Agorafobia, miedo a salir solo, pánico al transporte o a espacios abiertos.",
        "avatares": ["camilo", "anastasia"],
        "raiz": [
            {"id": "p8_miedo_calle", "texto": "🚪 Tengo terror a salir a la calle después de lo ocurrido"},
            {"id": "sub_p16_transporte", "texto": "🚌 Pánico a subir a un autobús o transporte cerrado"},
            {"id": "cam_respiracion_vago", "texto": "🫀 ¿Cómo desactivo la señal de alarma de mi cuerpo?"}
        ]
    },
    "duelo_perdida": {
        "id": "duelo_perdida",
        "titulo": "Duelo y Pérdida de un Ser Querido",
        "descripcion": "Fallecimiento repentino, pérdidas sin despedida, duelo sin cuerpo y culpa del sobreviviente.",
        "avatares": ["camilo", "rodrigo"],
        "raiz": [
            {"id": "p9_duelo", "texto": "🕊️ Perdí a alguien muy amado de golpe y siento culpa por vivir"},
            {"id": "sub_p19_habitacion", "texto": "📦 No he sido capaz de mover ni tocar sus cosas"},
            {"id": "sub_p20_rabia", "texto": "🔥 Siento mucha rabia con Dios y con la vida por esto"},
            {"id": "sub_p21_fuerte", "texto": "💔 Me dicen que 'debo ser fuerte', pero ya no aguanto más"}
        ]
    },
    "trauma_complejo_desrealizacion": {
        "id": "trauma_complejo_desrealizacion",
        "titulo": "Traumas Psicológicos y Desrealización",
        "descripcion": "Sensación de estar desconectado del cuerpo, ver el mundo como película o niebla mental.",
        "avatares": ["anastasia", "larissa"],
        "raiz": [
            {"id": "p10_desrealizacion", "texto": "🌫️ Siento que floto o no estoy en mi cuerpo; temo enloquecer"},
            {"id": "ana_rumiacion", "texto": "🔄 Pensamientos en bucle que no se apagan"},
            {"id": "lar_anclaje_54321", "texto": "🌿 Guíame en un anclaje sensorial inmediato (5-4-3-2-1)"}
        ]
    },
    "desregulacion_bipolar": {
        "id": "desregulacion_bipolar",
        "titulo": "Desregulación Afectiva y Ciclos de Ánimo",
        "descripcion": "Oscilaciones entre entusiasmo sin freno y bajones profundos de energía.",
        "avatares": ["anastasia"],
        "raiz": [
            {"id": "sub_p22_montana_rusa", "texto": "🎢 Paso de días sin dormir a semanas postrado sin energía"},
            {"id": "sub_p23_alarma_euforia", "texto": "⚡ ¿Cómo distingo entusiasmo sano de una fase hipomaníaca?"},
            {"id": "sub_p24_incomprension", "texto": "👥 Siento que nadie a mi alrededor comprende estos cambios"}
        ]
    },
    "conversacion_abierta": {
        "id": "conversacion_abierta",
        "titulo": "Personas que Solo Quieren Conversar",
        "descripcion": "Desahogo sin juzgamientos, compañía empática, soledad y anclaje humano cotidiano.",
        "avatares": ["mariana", "camilo"],
        "raiz": [
            {"id": "sub_p25_soledad", "texto": "☕ Hoy no tengo crisis grave, solo me siento solo/a y quiero hablar"},
            {"id": "sub_p26_esperanza", "texto": "🌱 ¿Cómo haces tú para tener fe tras lo que viviste?"},
            {"id": "sub_p27_desconfianza", "texto": "🛡️ Me cuesta confiar en la gente porque siempre me fallan"}
        ]
    },
    "aprender_habitos_neurociencia": {
        "id": "aprender_habitos_neurociencia",
        "titulo": "Aprender Neurociencia, Técnicas y Hábitos",
        "descripcion": "Aprender a regular el sistema nervioso, dosificación de energía y auto-perdón.",
        "avatares": ["anastasia", "camilo"],
        "raiz": [
            {"id": "sub_p28_pacing", "texto": "🔋 ¿Qué es la técnica del 'pacing' para no fundirme a media tarde?"},
            {"id": "sub_p29_mente_blanco", "texto": "🧠 ¿Qué ejercicio hago si mi mente se nubla en el trabajo?"},
            {"id": "sub_p30_perdon_sabio", "texto": "🕊️ ¿Cómo perdono sin volverme ingenuo/a ante quien me dañó?"}
        ]
    }
}

# ==================================================================================================
# BANCO DE RESPUESTAS DETERMINISTAS CONSOLIDADAS ($0 USD)
# ==================================================================================================
RESPUESTAS_CLINICAS_DB = {
    # P1 a P10
    "p1_panico": {
        "avatar": "camilo",
        "texto": "Oye, mi hermano/a, detente ahí y siéntate conmigo. Apoya los dos pies planos en el piso. Como médico te digo con total certeza: un corazón sano no se va a reventar ni te va a dar un infarto por una crisis de ansiedad.\n\nLo que experimentas es una descarga simpática de adrenalina: tu cuerpo interpretó una alerta y puso a circular sangre a mil por hora. Esa adrenalina dura entre 3 y 8 minutos en sangre y tu hígado la depura de forma natural. No te falta aire; estás hiperventilando aire viejo superficial. Vacía tus pulmones por la boca con un suspiro largo... eso es. Yo vi a mi cuerpo quebrado por fracturas y asaltos, y sé que la máquina humana resiste si le das calma mecánica. Estoy contigo, respira despacio.",
        "opciones_siguientes": [
            {"id": "sub_p1_nudo", "texto": "🫁 ¿Cómo aflojo el nudo en la garganta o el estómago ahora mismo?"},
            {"id": "sub_p2_desmayo", "texto": "🌫️ Siento que me voy a desmayar por respirar corto"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p1_nudo": {
        "avatar": "camilo",
        "texto": "Ese nudo es el reflejo somático del plexo celíaco y del músculo cricofaríngeo. Haz esto: toma un vaso de agua tibia y da tres sorbos muy lentos, sintiendo el paso del líquido. Al tragar de forma consciente, obligas a tu esófago a relajarse y el cerebro interpreta que no hay un predador atacándote. Suelta los hombros.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p2_desmayo": {
        "avatar": "camilo",
        "texto": "El mareo no es un síncope cardíaco; ocurre porque al respirar muy rápido botas demasiado dióxido de carbono y los vasos sanguíneos del cráneo se estrechan temporalmente. Haz esto: bota todo el aire, aguanta 3 segundos con el vientre plano, y deja que el aire entre despacio por la nariz. En un minuto el mareo desaparece.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p3_infarto": {
        "avatar": "camilo",
        "texto": "En un infarto el dolor es opresivo, fijo, se irradia al brazo izquierdo o mandíbula y no varía con la respiración. En el pánico, el dolor punza en partes móviles del tórax por espasmo intercostal, el corazón galopa pero mantiene ritmo regular y las extremidades hormiguean. Tu corazón está sano.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p2_vacio": {
        "avatar": "anastasia",
        "texto": "Analicemos lo que ocurre en tu cerebro con rigor objetivo. Cuando la tristeza profunda y la depresión se instalan, la corteza prefrontal izquierda disminuye su tasa metabólica y la Red Neuronal por Defecto (DMN) entra en un bucle rumiante hiperactivo.\n\nEse vacío no es una falla de tu carácter; es un estado de neuroquímica desregulada y fatiga atencional. Cuando mi padre falleció en el aula y cuando perdí la movilidad concertística de mi mano, comprendí que exigirte estar alegre solo profundiza la herida. Hoy no necesitas entusiasmo; necesitas microacciones basales. Levantarte y beber agua ya estimula tus vías dopaminérgicas. El movimiento precede a la motivación. Da solo un micro-paso hoy.",
        "opciones_siguientes": [
            {"id": "sub_p4_atencion", "texto": "🧠 No logro concentrarme ni leer dos páginas seguidas"},
            {"id": "sub_p5_pesimismo", "texto": "🔄 ¿Cómo desarmo la idea de que todo me saldrá mal?"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p4_atencion": {
        "avatar": "anastasia",
        "texto": "Tu memoria operativa tiene un cupo limitado de procesamiento. Si el 70% de tus recursos cognitivos está consumido por la angustia inconsciente, solo te queda un 30% para tus tareas diarias. No intentes leer capítulos enteros; aplica bloques cerrados de 10 minutos y luego descansa la vista dos minutos mirando un punto lejano.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p5_pesimismo": {
        "avatar": "anastasia",
        "texto": "Aplica la triple columna cognitiva de Lúriya: 1) Registra la distorsión: 'Todo va a salir mal'. 2) Exige evidencia probatoria: ¿qué dato fáctico indiscutible demuestra una catástrofe total? 3) Plantea la alternativa realista: 'Es un reto exigente, pero en el pasado he resuelto situaciones adversas paso a paso'.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p6_culpa_triste": {
        "avatar": "larissa",
        "texto": "No te castigues con la trampa de la positividad tóxica. La tristeza no pide permiso ni revisa cuentas bancarias; es una respuesta emocional que te pide una pausa y un abrazo. Tener comodidades materiales no te hace inmune al dolor humano. Suelta la culpa y permítete un ritmo suave hoy.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p3_deudas": {
        "avatar": "rodrigo",
        "texto": "Mírame con claridad: a las tres de la madrugada no se liquida una hipoteca, no abre una oficina judicial ni se firma un acuerdo bancario. Quedarte en la cama mirando el techo solo te garantiza llegar agotado al momento en que debas tomar decisiones despierto.\n\nYo sé lo que es ver tu patrimonio calcinado y arrastrar deudas de más de ciento sesenta mil euros bajo amenazas de embargo. La vergüenza es una trampa. Mañana por la mañana coges papel y pluma: acreedor, cuantía total objetiva y fecha de vencimiento. Quien se anticipa, da la cara y propone un calendario razonable de pagos, desarma el pánico de litigio. Ahora sal de la cama diez minutos, rompe la rumiación y deja reposar el esqueleto.",
        "opciones_siguientes": [
            {"id": "sub_p15_familia", "texto": "👨‍👩‍👧 ¿Cómo le explico a mi familia la quiebra sin derrumbarlos?"},
            {"id": "mar_micro_accion", "texto": "📋 ¿Cómo ordeno los pagos para salir de la parálisis?"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p15_familia": {
        "avatar": "mariana",
        "texto": "La quiebra o la falta de dinero destruye cuando se oculta en silencios y mentiras. Siéntate con los tuyos con sobriedad y serenidad: 'Estamos cruzando una tormenta económica transitoria; tendremos que ajustar gastos por unos meses, pero estamos juntos y lo vamos a resolver'. Quitar el secreto le quita el 80% de la angustia al hogar.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p4_bullying": {
        "avatar": "larissa",
        "texto": "Respira hondo, pon tu mano en el pecho y siente mi abrazo a través de estas palabras. A mis quince años viví exactamente ese infierno: editaron mis fotos personales, las regaron por el colegio y se burlaron de mi familia. Pasé meses sin querer comer ni salir de mi cuarto.\n\nHoy te digo mirándote a los ojos: **tú no tienes la culpa de la crueldad ajena.** Quien hostiga lo hace desde su propia miseria y cobardía. No les contestes en esos grupos; no les des combustible emocional. Toma captura de pantalla completa donde se vean fechas y números de teléfono. Muéstraselo de inmediato a tus padres o a un docente de confianza. Tu valor no depende de lo que digan cobardes detrás de una pantalla.",
        "opciones_siguientes": [
            {"id": "sub_p7_pasillo", "texto": "🚶‍♂️ ¿Cómo reacciono si me acorralan en el pasillo o la salida?"},
            {"id": "sub_p8_perfil_falso", "texto": "🛡️ Crearon un perfil falso con mis fotos, ¿qué hago?"},
            {"id": "sub_p9_panico_lunes", "texto": "🚪 Tengo terror de pisar el aula el lunes"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p7_pasillo": {
        "avatar": "mariana",
        "texto": "Aplica la regla de la 'piedra gris': mantén la barbilla en alto, mirada serena hacia un punto fijo, camina a paso constante sin correr ni achicarte, y busca de inmediato zonas concurridas (la sala de profesores o la secretaría). No respondas a los insultos; el agresor busca tu reacción, si no la encuentra, se frustra.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p8_perfil_falso": {
        "avatar": "rodrigo",
        "texto": "Cero confrontación con la cuenta. Entra, copia el enlace directo del perfil, toma capturas donde se observe la fecha del sistema y los comentarios denigrantes, y procede a denunciar la cuenta ante la plataforma por suplantación de identidad. Esos registros sirven para una denuncia formal por delitos telemáticos.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p9_panico_lunes": {
        "avatar": "larissa",
        "texto": "No tienes que cruzar esa puerta a solas sintiéndote indefensa/o. Pide a tu representante que te acompañe hasta la puerta del salón y que solicite una reunión formal con la dirección del plantel para activar el protocolo de protección escolar. No estás cometiendo ningún delito; estás exigiendo tu derecho al estudio seguro.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p5_acoso_sex": {
        "avatar": "larissa",
        "texto": "Escúchame con toda la fuerza de mi alma: **eres completamente inocente.** La responsabilidad moral y penal recae únicamente sobre quien vulneró tus límites.\n\nEn mi juventud enfrenté a un gerente de hotel que utilizó su jerarquía para hostigarme, y cuando lo denuncié, la empresa me despidió fabricando mentiras. Conozco el asco en la garganta y la sensación de sentir el cuerpo manchado. Pero tu cuerpo es el templo sagrado que resistió para mantenerte con vida. No cargues con el crimen de otro. Si la agresión ocurrió recientemente, busca resguardo médico y forense urgente para cuidar tu salud. Busca acompañamiento en trauma sexual; tu dignidad está intacta.",
        "opciones_siguientes": [
            {"id": "sub_p10_asco", "texto": "🪞 ¿Cómo manejo el asco y el rechazo a mi propio cuerpo?"},
            {"id": "sub_p11_credibilidad", "texto": "⚖️ Me da pánico denunciar y que no me crean"},
            {"id": "sub_p12_contacto", "texto": "✋ No soporto que nadie se me acerque físicamente"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p10_asco": {
        "avatar": "larissa",
        "texto": "Mírate las palmas de las manos. Estas manos respiran, sienten y sostienen tu presente. El acto del abusador fue una agresión externa; no forma parte de tus células ni de tu ser interior. Dúchate con agua tibia usando un jabón con aroma suave que tú elijas conscientemente; recupera la soberanía sobre cada rincón de tu piel sin juzgarte.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p11_credibilidad": {
        "avatar": "rodrigo",
        "texto": "En la doctrina procesal y forense contemporánea, el testimonio de la víctima es prueba fundamental cuando es coherente y persistente. No te autoimpongas la carga de un tribunal en tu cabeza. Acude a una oficina de atención a víctimas o a una abogada/o de oficio especializada en género; su deber técnico es blindar tu testimonio.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p12_contacto": {
        "avatar": "larissa",
        "texto": "Tu sistema nervioso cerró las compuertas de proximidad para protegerte, y ese límite es 100% válido y necesario en esta etapa. Hazlo respetar sin culpa: 'Por favor mantengamos distancia, no me siento cómodo/a con abrazos en este momento'. Quien te respeta de verdad, esperará a que tu cuerpo vuelva a sentirse seguro.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p6_mobbing": {
        "avatar": "mariana",
        "texto": "¡Epa! Para ahí mismo. Esa violencia sutil la viví en carne propia con un gerente que me exigía cosas ilegales a las tres de la madrugada y me destruyó la salud hasta terminar hospitalizada por úlcera sangrante.\n\nEl acoso laboral (*mobbing*) busca quebrarte moralmente para que renuncies creyendo que eres un/a incompetente. Desarmemos la trampa: esto no es un problema de rendimiento; es abuso de poder corporativo. Desde hoy la regla de oro es: **cero palabras al aire**. Toda instrucción desmedida, pide que te la confirmen por correo. Abre una bitácora fuera del computador de la empresa: anota fecha, hora, hecho exacto y testigos. Y recuerda: las empresas se reemplazan; tus órganos no.",
        "opciones_siguientes": [
            {"id": "sub_p13_puerta_cerrada", "texto": "🚪 Me grita o presiona a solas donde no hay testigos"},
            {"id": "sub_p14_miedo_renuncia", "texto": "⏳ Tengo pánico de renunciar y quedarme sin sustento"},
            {"id": "mar_limites", "texto": "🛡️ Enséñame a responder con firmeza sin perder el empleo"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p13_puerta_cerrada": {
        "avatar": "mariana",
        "texto": "Cuando salgas de esa oficina privada, dirígete de inmediato a tu puesto y redacta un correo formal de seguimiento con copia a tu correo personal: 'Estimado [Nombre], en relación con la conversación privada recién sostenida en su despacho a las [Hora], confirmo que las instrucciones indicadas fueron [describir hecho]. Quedo a la espera de sus observaciones'. Eso neutraliza el abuso y crea expediente probatorio.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p14_miedo_renuncia": {
        "avatar": "mariana",
        "texto": "No renuncies en caliente ni des un salto al vacío. Conviértete en un 'empleado invisible': haz estrictamente lo que marca tu contrato de 8 a 5, ni un minuto más, no te involucres en chismes, cuida tu energía y dedica las tardes a postular en silencio a nuevas opciones laborales.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p7_violencia": {
        "avatar": "rodrigo",
        "texto": "Sé lo que es tener sicarios vigilando la puerta de tu casa y que disparen contra las ventanas de tu despacho. Sé lo que es que tu sistema nervioso se quede atascado en alerta máxima, esperando el siguiente golpe a cada minuto.\n\nLa agresión violenta fractura la sensación básica de seguridad en el mundo. Tu mente aprende que cualquier sombra es una amenaza mortal. Tu prioridad ahora no es confrontar; es tu blindaje fáctico: corta comunicación con el agresor, cambia tus rutas de desplazamiento habituales y formaliza la denuncia penal correspondiente. En paralelo desensibilizaremos el cuerpo. Los agresores apuestan a tu parálisis; tu respuesta será la frialdad procesal.",
        "opciones_siguientes": [
            {"id": "sub_p17_sirenas", "texto": "🚨 Un sonido fuerte o seco me hace temblar incontrolable"},
            {"id": "sub_p18_repeticion", "texto": "🌪️ Siento que en cualquier momento se repetirá el ataque"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p17_sirenas": {
        "avatar": "larissa",
        "texto": "Es el reflejo somatosensorial del sobresalto. Haz esto: cruza tus brazos sobre el pecho abrazando tus costados con las manos abiertas, y da golpecitos alternados (derecha, izquierda, derecha, izquierda) a ritmo lento mientras dices en voz alta: 'Estoy a salvo en este cuarto, eso ya pasó'. Esto desactiva el shock de la amígdala cerebral.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p18_repeticion": {
        "avatar": "anastasia",
        "texto": "Tu cerebro mamífero confunde el recuerdo con la percepción presente. Aplica la diferenciación temporal: di en voz alta: 'Eso ocurrió en la fecha [mencionar fecha de la agresión]. Hoy es [mencionar fecha de hoy] y estoy resguardado/a'. Obliga a tu hipocampo a archivar el trauma en el pasado.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p8_miedo_calle": {
        "avatar": "camilo",
        "texto": "Esa sensación de encierro la conozco milimétricamente. Cuando me fracturaron la mandíbula con un tubo de hierro en un callejón, pasé meses en los que solo asomar la cabeza por el balcón me disparaba mareos y palpitaciones.\n\nEl cerebro crea una ecuación inmediata: calle igual a peligro mortal. Pero si te quedas atrincherado, le confirmas a tu amígdala que el mundo entero es un campo de batalla. No vamos a salir a caminar diez cuadras de golpe. La rehabilitación se hace por micro-dosis: hoy te paras cinco minutos en el marco de tu puerta principal respirando despacio. Mañana caminas diez metros y regresas. Tu sistema registrará que puedes habitar tu entorno sin daño.",
        "opciones_siguientes": [
            {"id": "sub_p16_transporte", "texto": "🚌 Pánico a subir a un autobús o transporte cerrado"},
            {"id": "cam_respiracion_vago", "texto": "🫀 ¿Cómo desactivo la señal de alarma de mi cuerpo?"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p16_transporte": {
        "avatar": "rodrigo",
        "texto": "Tras los atentados del 11M donde falleció mi primo, tardé años en volver a subir a un vagón de tren sin ahogarme en pánico. Se supera mediante aproximaciones sucesivas: primero acércate a la estación y mira los vehículos pasar; luego sube y haz una sola parada corta acompañado de alguien de confianza. Tu cuerpo irá reprogramando la seguridad.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p9_duelo": {
        "avatar": "camilo",
        "texto": "Hermano/a, suelta las corazas y descansa un momento en este dolor. Yo vi a mi padre morir aplastado por el balcón de un derrumbe, y años después vi a mi mejor amigo Yordanis desaparecer en el mar sin poder recuperar su cuerpo para darle sepultura.\n\nConozco la culpa del sobreviviente: esa voz cruel que te dice que debiste hacer algo más o que no tienes derecho a sonreír cuando ellos ya no están. Pero honrar a quienes amamos no consiste en sepultarnos en vida a su lado. El duelo no es una enfermedad que se cura con pastillas; es el precio que paga el alma por haber amado de verdad. Llora lo que necesites, pero recuerda: tu vida hoy es el único monumento vivo que le queda a su memoria.",
        "opciones_siguientes": [
            {"id": "sub_p19_habitacion", "texto": "📦 No he sido capaz de mover ni tocar sus cosas"},
            {"id": "sub_p20_rabia", "texto": "🔥 Siento mucha rabia con Dios y con la vida por esto"},
            {"id": "sub_p21_fuerte", "texto": "💔 Me dicen que 'debo ser fuerte', pero ya no aguanto más"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p19_habitacion": {
        "avatar": "camilo",
        "texto": "Nadie tiene derecho a forzarte a deshacerte de su ropa ni de sus recuerdos en plazos impuestos por terceros. Cuando tu corazón esté listo, escogerás un solo objeto simbólico para conservar y donarás o guardarás el resto. Respeta tus ritmos sagrados de asimilación.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p20_rabia": {
        "avatar": "rodrigo",
        "texto": "La ira no es un pecado; es una fase legítima del duelo desgarrador. Expresa esa cólera: escríbela en un papel sin filtros morales y luego quémalo. Lo destructivo es tragarte la rabia y convertirla en amargura contra los que siguen vivos a tu lado.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p21_fuerte": {
        "avatar": "mariana",
        "texto": "La frase 'tienes que ser fuerte' es una torpeza que la sociedad repite porque no sabe qué hacer con las lágrimas ajenas. Quítate esa armadura pesada. Tienes derecho a derrumbarte, a pedir un abrazo y a no tener respuestas hoy.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "p10_desrealizacion": {
        "avatar": "anastasia",
        "texto": "Lo que estás experimentando clínicamente se denomina despersonalización y desrealización. No te estás volviendo loco/a ni estás perdiendo la razón.\n\nCuando el sistema nervioso alcanza un nivel de sobrecarga traumática o angustia que rebasa su umbral biológico, el cerebro activa un fusible de autoprotección: disminuye la intensidad perceptiva para evitar que el dolor te quiebre. Lo viví cuando caí bajo las placas de hielo del Nevá a -18°C y tras la muerte de mi padre: sentía que todo a mi alrededor era una maqueta de papel. Para reconectar los circuitos, no intentes forzar pensamientos abstractos; activa estímulos mecánicos y térmicos: pisa descalzo el suelo, toma un cubo de hielo en la mano o lávate el rostro con agua helada. Tu cuerpo le dirá al cerebro que estás a salvo.",
        "opciones_siguientes": [
            {"id": "ana_rumiacion", "texto": "🔄 Pensamientos en bucle que no se apagan"},
            {"id": "lar_anclaje_54321", "texto": "🌿 Guíame en un anclaje sensorial inmediato (5-4-3-2-1)"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },

    "sub_p22_montana_rusa": {
        "avatar": "anastasia",
        "texto": "La oscilación de ciclos afectivos requiere una higiene rigurosa del ritmo circadiano. Cuando el sueño se desorganiza, los neurotransmisores entran en resonancia caótica. Tu primera regla de protección es la hora fija de acostarse y levantarse, la desconexión total de pantallas a las 9 PM y evitar estimulantes químicos.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p23_alarma_euforia": {
        "avatar": "anastasia",
        "texto": "Existen marcadores de hipomanía que debes monitorear: aceleración notable del ritmo verbal, sensación de no necesitar dormir más de 3 horas sintiéndote invencible, y urgencia de realizar gastos o proyectos imprudentes. Si detectas estos signos, acude de inmediato a tu médico tratante para reajuste preventivo.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p24_incomprension": {
        "avatar": "anastasia",
        "texto": "La sociedad suele juzgar la desregulación anímica como debilidad o falta de voluntad. No gastes energía discutiendo con quien carece de formación médica. Construye un círculo estrecho de apoyo informado y lleva un diario de estados basales para reconocer tus propios ciclos.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "sub_p25_soledad": {
        "avatar": "mariana",
        "texto": "¡Epa! Aquí estoy para hacerte compañía con todo el cariño del mundo. A veces no necesitamos una sesión de psicología profunda; solo hace falta saber que del otro lado hay alguien que te lee con atención y respeto. Cuéntame: ¿cómo estuvo tu día hoy? ¿Tomaste algo rico?",
        "opciones_siguientes": [
            {"id": "sub_p26_esperanza", "texto": "🌱 ¿Cómo haces tú para tener fe tras lo que viviste?"},
            {"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}
        ]
    },
    "sub_p26_esperanza": {
        "avatar": "camilo",
        "texto": "La esperanza no es un optimismo ciego de que todo es perfecto; es la decisión consciente de no permitir que la fealdad del mundo te robe la ternura. Tras ver derrumbes y pérdidas, entendí que mientras nos quede aire en los pulmones, podemos ser el auxilio de alguien más. Servir es la mejor medicina.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p27_desconfianza": {
        "avatar": "rodrigo",
        "texto": "Desconfiar es un mecanismo de defensa tras haber sido traicionado. El error no fue tuyo por confiar, sino de quien rompió las reglas éticas. No tienes que abrir tu casa de golpe a nadie; la confianza sana se construye por peldaños verificables a lo largo del tiempo.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    "sub_p28_pacing": {
        "avatar": "mariana",
        "texto": "El 'pacing' es la técnica clínica de dosificación energética: parar antes de que aparezca la fatiga extrema. Si sabes que a las dos horas de trabajo colapsas, programa una alarma a los 75 minutos para caminar tres minutos y tomar agua. No vacíes tu tanque de reserva.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p29_mente_blanco": {
        "avatar": "anastasia",
        "texto": "Cuando la mente se bloquee, activa tu lóbulo frontal con estimulación refleja: cuenta regresivamente de 3 en 3 desde el 50 hasta el 20, y luego nombra tres objetos de madera a tu alrededor. Romperás el bloqueo de la corteza motora suplementaria.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "sub_p30_perdon_sabio": {
        "avatar": "rodrigo",
        "texto": "Perdonar no es firmar un cheque de impunidad ni obligarte a tomar café con quien te agravió. El perdón es un acto de higiene jurídica y moral personal: es renunciar al veneno del rencor diario para que tu mente quede libre para construir tu presente.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },

    # Respuestas de árbol clásico integrado
    "mar_limites": {
        "avatar": "mariana",
        "texto": "Poner límites no es pelear ni ser grosero/a; es cuidar las reglas del juego. Cuando te asignen una sobrecarga abusiva, responde con claridad ejecutiva: 'Entiendo la urgencia de esta tarea; para incluirla hoy con calidad, ¿cuál de los otros tres proyectos previos ponemos en pausa?'. Eso traslada la responsabilidad de priorizar a quien corresponde.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "mar_micro_accion": {
        "avatar": "mariana",
        "texto": "Aplica la regla de los dos minutos: si toma menos de 120 segundos, hazla ya; si toma más, anótala en un papel y divídela a la mitad. No intentes ser un robot; hoy el objetivo no es la perfección, sino el cuidado de tu energía.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "cam_respiracion_vago": {
        "avatar": "camilo",
        "texto": "Haz esto conmigo: toma aire por la nariz en 4 tiempos, y luego bótalo muy suave por la boca frunciendo los labios (como soplando una sopa caliente) en 7 u 8 tiempos. Al alargar la exhalación, el diafragma le envía un mensaje bioeléctrico al corazón para que baje revoluciones.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "lar_anclaje_54321": {
        "avatar": "larissa",
        "texto": "Vamos a hacer este anclaje sensorial juntas/os para traer a tu mente de vuelta a este instante seguro:\n\n👀 **5 cosas** que puedas ver a tu alrededor.\n✋ **4 cosas** que puedas tocar (ropa, mesa, manos).\n👂 **3 sonidos** que escuches ahora mismo.\n👃 **2 aromas** que percibas.\n👅 **1 sabor** en tu boca.\n\nRespira lento. Estás aquí, en tu presente, y en este minuto exacto estás a salvo.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
    },
    "ana_rumiacion": {
        "avatar": "anastasia",
        "texto": "El bucle mental de rumiación ocurre cuando la Red Neuronal por Defecto (DMN) hiperactiva escenarios pasados o futuros sin vincularse al sistema motor.\n\nPara interrumpir este ciclo neuroquímico, activa la Red de Tarea Positiva: toma un objeto con tu mano, descríbelo en voz alta con tres adjetivos físicos (peso, textura, temperatura) y realiza una resta regresiva de 7 en 7 desde el 100 hasta el 72.",
        "opciones_siguientes": [{"id": "raiz", "texto": "⬅️ Volver a las opciones de este tema"}]
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
# FILTROS DE SEGURIDAD CLÍNICA
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

def cargar_biografia_completa(avatar_id: str) -> str:
    rutas = [os.path.join("avatares", f"{avatar_id}.txt"), f"{avatar_id}.txt"]
    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return f.read()[:3500]
            except Exception as e:
                print(f"[CEREBRO AVATARES] Aviso: No se pudo leer {ruta}: {e}")
    return ""

def obtener_catalogo_problemas() -> List[Dict[str, Any]]:
    """Entrega la lista ordenada de las 13 problemáticas con sus avatares recomendados."""
    resultado = []
    for k, v in CATALOGO_PROBLEMAS.items():
        avatares_info = [AVATARES_5[a_id] for a_id in v["avatares"] if a_id in AVATARES_5]
        resultado.append({
            "id": k,
            "titulo": v["titulo"],
            "descripcion": v["descripcion"],
            "avatares": avatares_info,
            "opciones_iniciales": v["raiz"]
        })
    return resultado

def obtener_avatar_por_defecto(problema_id: str) -> str:
    """Selecciona automáticamente el avatar primario asignado al motivo del usuario."""
    if problema_id in CATALOGO_PROBLEMAS:
        return CATALOGO_PROBLEMAS[problema_id]["avatares"][0]
    return "mariana"

def obtener_opciones_raiz(avatar_id: str, problema_id: Optional[str] = None) -> List[Dict[str, str]]:
    if problema_id and problema_id in CATALOGO_PROBLEMAS:
        return CATALOGO_PROBLEMAS[problema_id]["raiz"]
    return CATALOGO_PROBLEMAS["ansiedad_panico"]["raiz"]

async def llamar_gemini_avatar_async(prompt_sistema: str, historial: list, mensaje_actual: str) -> str:
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
# PROCESADOR CENTRAL DE RESPUESTAS (4 VALORES DE RETORNO)
# ==================================================================================================
async def procesar_respuesta_avatar(
    avatar_id: str, 
    mensaje_usuario: str, 
    opcion_id: Optional[str] = None,
    problema_id: Optional[str] = None,
    perfil_usuario: Optional[dict] = None, 
    historial_reciente: Optional[list] = None
) -> Tuple[str, str, bool, List[Dict[str, str]]]:
    """
    Retorna: (nombre_avatar, texto_respuesta, es_crisis, opciones_siguientes)
    """
    perfil = perfil_usuario or {}
    avatar_info = AVATARES_5.get(avatar_id, AVATARES_5["mariana"])
    nombre_avatar = avatar_info["nombre"]
    prob_key = problema_id if (problema_id and problema_id in CATALOGO_PROBLEMAS) else "ansiedad_panico"
    opciones_defecto = CATALOGO_PROBLEMAS[prob_key]["raiz"]

    apodo_crudo = perfil.get("apodo", "amigo/a").strip()
    apodo = "Juan Carlos" if apodo_crudo.lower() == "admin" else apodo_crudo.replace("Admin ", "").strip()
    
    texto = (mensaje_usuario or "").strip()
    texto_lower = texto.lower()

    # 1. FILTRO ROJO DE CRISIS (SOS PRIORIDAD DE VIDA)
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
        return nombre_avatar, respuesta_abuso, False, opciones_defecto

    # 3. NAVEGACIÓN DETERMINISTA POR BANCO CLÍNICO ($0 USD)
    if opcion_id:
        if opcion_id == "raiz":
            return nombre_avatar, f"¿Qué otro punto te gustaría abordar ahora, {apodo}?", False, opciones_defecto
        
        nodo = RESPUESTAS_CLINICAS_DB.get(opcion_id)
        if nodo:
            avatar_especifico = AVATARES_5.get(nodo["avatar"], avatar_info)["nombre"]
            return avatar_especifico, nodo["texto"], False, nodo.get("opciones_siguientes", opciones_defecto)

    # 4. FILTRO DE PAGOS Y SUSCRIPCIÓN
    patron_pago = r"\b(recargar|adquirir plan|cambiar de plan|subir de plan|pagar suscripci[oó]n|m[eé]todos de pago|pago m[oó]vil|binance pay)\b"
    if re.search(patron_pago, texto_lower):
        resp_pago = (
            f"Puedes coordinar la renovación o ascenso de tu plan de forma privada, {apodo}. "
            "En el menú lateral encontrarás la pestaña de 'Planes y Suscripción', donde podrás acordar los detalles de manera confidencial directamente con el Administrador."
        )
        return nombre_avatar, resp_pago, False, opciones_defecto

    # 5. SALUDOS O CONSULTAS GENERALES
    if any(s in texto_lower for s in ["hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", "cómo estás"]):
        return nombre_avatar, f"¡Hola, {apodo}! Qué bueno encontrarnos. Selecciona una de las opciones guiadas o cuéntame con tus palabras lo que estás viviendo hoy.", False, opciones_defecto

    # 6. LLAMADA GENERATIVA A GEMINI PARA PREGUNTAS ABIERTAS DEL USUARIO
    bio = cargar_biografia_completa(avatar_id)
    consejos_rag = [lib.get("consejo_aplicable") for lib in LIBROS_CACHE[:3] if lib.get("consejo_aplicable")]
    contexto_rag_str = "\n- ".join(consejos_rag) if consejos_rag else "Respira hondo y da un paso a la vez."

    prompt_sistema = f"""Eres {nombre_avatar}, originario de {avatar_info['pais']}.
Tu especialidad: {avatar_info['especialidad']}.
Tu tono característico: {avatar_info['tono']}.
Estás conversando con {apodo}.
Marco ético: Espacio reflexivo y psicoeducativo de acompañamiento. Prohibido diagnosticar clínicamente o prescribir fármacos.
Jerarquía de dolor sobre datos: si el usuario manifiesta dolor por un familiar o hijo, prioriza la contención compasiva sin confrontar con registros de la base de datos.

TU MEMORIA BIOGRÁFICA CANÓNICA:
{bio if bio else "Acompañante de serenidad con experiencia en superación personal."}

PRINCIPIOS RAG APLICABLES:
- {contexto_rag_str}"""

    resp_llm = await llamar_gemini_avatar_async(prompt_sistema, historial_reciente or [], texto)
    if resp_llm:
        return nombre_avatar, resp_llm, False, opciones_defecto

    # 7. FALLBACK OFFLINE DIALECTAL DETERMINISTA
    respuestas_fallback = {
        "mariana": f"Te escucho con calma, {apodo}. Para resolver lo que tienes encima, vamos a descomponerlo paso a paso sin saturarnos.",
        "camilo": f"Oye, {apodo}, como médico te digo: respira hondo, apoya los pies firmes y cuéntame un poco más para abordarlo juntos.",
        "rodrigo": f"Comprendo la inquietud, {apodo}. Vamos a aplicar sentido común y a separar lo que puedes controlar hoy de lo que no.",
        "larissa": f"Siento lo que me compartes, {apodo}. Pon tu mano en el pecho, suelta los hombros y tómate tu tiempo. Aquí estoy a tu lado.",
        "anastasia": f"Analicemos la situación con objetividad, {apodo}. Desglosa lo que sientes en hechos concretos para orientar el pensamiento con claridad."
    }
    
    texto_fallback = respuestas_fallback.get(avatar_id, f"{apodo}, estoy aquí para acompañarte en tu serenidad. Cuéntame un poco más.")
    return nombre_avatar, texto_fallback, False, opciones_defecto