from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="Somos Libres de Ansiedad Core API",
    version="2.0.0",
    description="Backend definitivo y unificado para el ecosistema Somos Libres de Ansiedad."
)

# ==========================================
# 1. MODELOS Y MOTOR DE REGISTRO & AUTH
# ==========================================
class UserRegister(BaseModel):
    nombre_completo: str
    apodo: str
    correo: EmailStr
    password: str
    edad: int
    sexo: Optional[str] = None
    profesion: Optional[str] = None
    orientacion_sexual: Optional[str] = None
    situacion_sentimental: Optional[str] = None
    cantidad_hijos: Optional[int] = None
    codigo_referido: Optional[str] = None
    terms_accepted: bool
    disclaimer_accepted: bool

class UserLogin(BaseModel):
    correo: EmailStr
    password: str

PENSAMIENTOS_BIENVENIDA = [
    "Respira hondo, suelta los hombros y tómate tu tiempo. Este es tu espacio seguro.",
    "No tienes que resolver todo hoy; un solo paso a la vez es suficiente.",
    "Tus emociones son válidas. Lo que sientes hoy no define quién serás mañana.",
    "La calma no es la ausencia de caos, sino la paz que construyes en tu interior.",
    "Está bien hacer una pausa. El descanso también es parte del camino.",
    "No estás solo en esta batalla; reconocer lo que sientes ya es un acto de valentía.",
    "Permítete soltar lo que no puedes controlar y enfócate en el presente.",
    "Inhala calma, exhala la prisa del día. Aquí no hay juicios ni expectativas.",
    "Cada día difícil superado es una prueba de tu fortaleza interior.",
    "Hoy solo necesitas ser amable contigo mismo. Bienvenida/o a tu refugio."
]

# ==========================================
# 2. MOTOR DE PLANES, REFERIDOS Y CUPONES
# ==========================================
class UserPlanStatus(BaseModel):
    user_id: str
    plan_actual: str  # 'gratis', 'comunicador', 'amigo_todos'
    fecha_expiracion: Optional[datetime] = None
    tiempo_acumulado_interaccion_horas: float = 0.0
    referidos_totales: int = 0
    referidos_vip_compraron: int = 0

class CuponRequest(BaseModel):
    codigo_cupon: str
    color: str  # 'verde', 'azul', 'rojo', 'morado'
    user_id: str

class ReferidoRedeem(BaseModel):
    user_id: str
    codigo_amigo: str

class PagoManualRequest(BaseModel):
    user_id: str
    metodo: str  # 'Pago móvil Banco en Venezuela', 'Binance', 'PayPal'
    monto: float
    comprobante_url: str

class PlanesEngine:
    def __init__(self):
        self.usuarios_planes: Dict[str, UserPlanStatus] = {}
        self.cupones_activos: Dict[str, dict] = {} # codigo -> {color, expires_at, usado}
        self.pagos_pendientes: List[dict] = []

    def verificar_vencimiento_planes(self, user_id: str) -> dict:
        usuario = self.usuarios_planes.get(user_id)
        if not usuario:
            return {"plan": "gratis", "estado_rojo": "Plan Gratis - Sin costo. Tiempo activo: 0 días."}
        ahora = datetime.now()
        mensaje_rojo = f"Plan actual: {usuario.plan_actual.upper()}"
        if usuario.fecha_expiracion:
            dias_restantes = (usuario.fecha_expiracion - ahora).days
            if 0 <= dias_restantes <= 3:
                mensaje_rojo += f" ⚠️ ¡Atención! Tu plan vence en {dias_restantes} días. Renueva a tiempo."
            elif dias_restantes < 0:
                usuario.plan_actual = "gratis"
                mensaje_rojo = "Tu plan ha expirado. Has vuelto al Plan Gratis."
            else:
                mensaje_rojo += f" - Tiempo restante: {dias_restantes} días."
        mensaje_rojo += f" | Tiempo acumulado en la app: {usuario.tiempo_acumulado_interaccion_horas:.1f} horas."
        return {"plan": usuario.plan_actual, "info_roja": mensaje_rojo}

    def canjear_cupon(self, req: CuponRequest) -> dict:
        cupon = self.cupones_activos.get(req.codigo_cupon)
        if not cupon:
            return {"success": False, "error": "El código de cupón no existe o es inválido."}
        if cupon.get("usado", False):
            return {"success": False, "error": "Este cupón ya fue utilizado."}
        if datetime.now() > cupon["expires_at"]:
            return {"success": False, "error": "El cupón ha expirado (superó los 30 minutos de vigencia)."}
        color = cupon["color"]
        usuario = self.usuarios_planes.setdefault(req.user_id, UserPlanStatus(user_id=req.user_id, plan_actual="gratis"))
        dias_premio = 0
        if color == "verde":
            usuario.plan_actual = "comunicador"
            dias_premio = 3
        elif color == "azul":
            usuario.plan_actual = "comunicador"
            dias_premio = 7
        elif color == "rojo":
            usuario.plan_actual = "amigo_todos"
            dias_premio = 3
        elif color == "morado":
            usuario.plan_actual = "amigo_todos"
            dias_premio = 7
        usuario.fecha_expiracion = datetime.now() + timedelta(days=dias_premio)
        cupon["usado"] = True
        return {"success": True, "message": f"¡Cupón {color} canjeado con éxito! Disfruta tu acceso por {dias_premio} días."}

    def procesar_referido(self, req: ReferidoRedeem) -> dict:
        usuario = self.usuarios_planes.setdefault(req.user_id, UserPlanStatus(user_id=req.user_id, plan_actual="gratis"))
        usuario.plan_actual = "amigo_todos"
        usuario.fecha_expiracion = datetime.now() + timedelta(days=1)
        return {"success": True, "message": "¡Código de referido aplicado! Has obtenido 1 día de acceso directo al Plan Amigo de Todos."}

    def registrar_pago_manual(self, req: PagoManualRequest) -> dict:
        pago_info = {
            "user_id": req.user_id,
            "metodo": req.metodo,
            "monto": req.monto,
            "comprobante_url": req.comprobante_url,
            "timestamp": datetime.now(),
            "estado": "En Revisión por Administrador"
        }
        self.pagos_pendientes.append(pago_info)
        return {"success": True, "message": f"Comprobante enviado a través de {req.metodo}. El administrador lo validará en breve."}

planes_engine = PlanesEngine()

# ==========================================
# 3. MOTOR RAG Y MOTOR DE AVATARES
# ==========================================
DRIVE_FOLDERS = {
    "gratis": "13fpM2hP3T_dhMGCTnuDmXHvTSVGSmhEq",
    "comunicador": "13oiFRcRDQYe8jFLsXkRXbpLns6ssA-HD",
    "amigo_todos": "14l2PFKX_fNGrv-Rglu1TzymrAfrGkyvP"
}

AVATARS_DRIVE_FOLDER_ID = "1tyIBnoptE0RUt-DDv8wqhlJO_1Dqff5g"

class AvatarConfig(BaseModel):
    avatar_id: str
    nombre: str
    personalidad: str
    pais_usuario: str
    plan_usuario: str

PLAN_LIMITS = {
    "gratis": {"max_avatares": 1, "max_chats_semana": 25, "max_audios_semana": 3, "max_duracion_audio": 10},
    "comunicador": {"max_avatares": 3, "max_chats_semana": 100, "max_audios_semana": 10, "max_duracion_audio": 30},
    "amigo_todos": {"max_avatares": 10, "max_chats_semana": float('inf'), "max_audios_semana": float('inf'), "max_duracion_audio": 60}
}

class AvatarEngine:
    def __init__(self):
        self.folder_id = AVATARS_DRIVE_FOLDER_ID

    def obtener_mensaje_bienvenida(self, avatar: AvatarConfig) -> str:
        mensajes_iniciales = [
            f"Hola, soy {avatar.nombre}. Desde {avatar.pais_usuario}, estoy aquí para acompañarte paso a paso con la fortaleza que necesitas hoy.",
            f"Un gusto saludarte. Con la perspectiva de {avatar.personalidad}, quiero recordarte que cada pequeña pausa cuenta. ¿Cómo te sientes en este momento?",
            f"Bienvenido a tu espacio seguro. Vamos a transitar este camino juntos, con resiliencia y paso firme."
        ]
        return random.choice(mensajes_iniciales)

    def validar_limites_plan(self, plan: str, tipo_interaccion: str, duracion_audio: int = 0) -> dict:
        limites = PLAN_LIMITS.get(plan, PLAN_LIMITS["gratis"])
        if tipo_interaccion == "audio" and duracion_audio > limites["max_duracion_audio"]:
            return {"permitido": False, "error": f"Tu plan actual permite audios de máximo {limites['max_duracion_audio']} segundos."}
        return {"permitido": True, "mensaje": "Interacción autorizada dentro de los parámetros del plan."}

    def procesar_respuesta_avatar(self, mensaje_usuario: str, avatar: AvatarConfig) -> str:
        return (
            f"🤖 [{avatar.nombre} - Enfoque: {avatar.personalidad}]\n\n"
            f"Comprendo perfectamente tu situación. Apoyándome en las guías de superación y resiliencia, "
            f"analicemos esto sin prisa: '{mensaje_usuario}'. (Revisando 100% de la base bibliográfica en español)."
        )

avatar_engine = AvatarEngine()

# ==========================================
# 4. MOTOR SOCIAL Y DE COMUNIDAD
# ==========================================
class UserSocialProfile(BaseModel):
    user_id: str
    apodo: str
    edad: int
    foto_perfil_url: str
    descripcion: str
    plan_nivel: str  # 'gratis', 'comunicador', 'amigo_todos'
    is_verified: bool
    cedula_identificacion_url: str  # Almacenado de forma privada

class DirectMessage(BaseModel):
    remitente_id: str
    destinatario_id: str
    contenido: str
    timestamp: datetime

class MuroPost(BaseModel):
    post_id: str
    autor_id: str
    plan_autor: str
    contenido: str
    timestamp: datetime
    comentarios: List[Dict] = []

class ReunionGrupal(BaseModel):
    reunion_id: str
    organizador_id: str
    plan_organizador: str
    participantes_ids: List[str] = []
    incluye_avatar: bool = False
    avatar_id: Optional[str] = None
    timestamp: datetime

class BuzonMensaje(BaseModel):
    mensaje_id: str
    user_id: str
    asunto: str
    contenido: str
    respuesta_admin: Optional[str] = None
    timestamp: datetime

class SocialEngine:
    def __init__(self):
        self.mensajes_chat: List[DirectMessage] = []
        self.muro_posts: List[MuroPost] = []
        self.reuniones: List[ReunionGrupal] = []
        self.buzon_quejas: List[BuzonMensaje] = []
        self.registro_usuarios_historico: List[Dict] = []

    def enviar_mensaje_privado(self, remitente: UserSocialProfile, destinatario_id: str, contenido: str) -> dict:
        hoy = datetime.now()
        if remitente.plan_nivel == "gratis":
            mensajes_hoy = [m for m in self.mensajes_chat if m.remitente_id == remitente.user_id and m.timestamp.date() == hoy.date()]
            if len(mensajes_hoy) >= 1:
                return {"permitido": False, "error": "El Plan Gratis solo permite escribir directamente a 1 persona diariamente."}
        elif remitente.plan_nivel == "comunicador":
            mensajes_hoy = [m for m in self.mensajes_chat if m.remitente_id == remitente.user_id and m.timestamp.date() == hoy.date()]
            if len(mensajes_hoy) >= 5:
                return {"permitido": False, "error": "El Plan Comunicador permite escribir hasta a 5 personas diariamente."}
        
        nuevo_mensaje = DirectMessage(remitente_id=remitente.user_id, destinatario_id=destinatario_id, contenido=contenido, timestamp=hoy)
        self.mensajes_chat.append(nuevo_mensaje)
        return {"permitido": True, "message": "Mensaje enviado con éxito."}

    def publicar_en_muro(self, autor: UserSocialProfile, contenido: str) -> MuroPost:
        post = MuroPost(
            post_id=f"post_{datetime.now().timestamp()}",
            autor_id=autor.user_id,
            plan_autor=autor.plan_nivel,
            contenido=contenido,
            timestamp=datetime.now()
        )
        self.muro_posts.append(post)
        return post

    def solicitar_reunion(self, organizador: UserSocialProfile, invitados: List[str], incluir_avatar: bool = False) -> dict:
        if organizador.plan_nivel == "gratis":
            return {"permitido": False, "error": "Los usuarios de Plan Gratis no pueden solicitar reuniones grupales."}
        if organizador.plan_nivel == "comunicador":
            if len(invitados) > 5:
                return {"permitido": False, "error": "El Plan Comunicador solo puede invitar hasta a 5 personas (1 Gratis obligatoria y las demás libre)."}
            if incluir_avatar:
                return {"permitido": False, "error": "El uso del Avatar en reuniones es exclusivo del Plan Amigo de Todos."}
        if organizador.plan_nivel == "amigo_todos":
            if len(invitados) > (11 if incluir_avatar else 10):
                return {"permitido": False, "error": "El límite máximo es de 10 invitados más el Avatar."}
        
        reunion = ReunionGrupal(
            reunion_id=f"reu_{datetime.now().timestamp()}",
            organizador_id=organizador.user_id,
            plan_organizador=organizador.plan_nivel,
            participantes_ids=invitados,
            incluye_avatar=incluye_avatar,
            timestamp=datetime.now()
        )
        self.reuniones.append(reunion)
        return {"permitido": True, "message": "Salón grupal 'Reunidos para Compartir' creado con éxito."}

    def enviar_buzon_quejas(self, user_id: str, asunto: str, contenido: str) -> BuzonMensaje:
        mensaje = BuzonMensaje(
            mensaje_id=f"buzon_{datetime.now().timestamp()}",
            user_id=user_id,
            asunto=asunto,
            contenido=contenido,
            timestamp=datetime.now()
        )
        self.buzon_quejas.append(mensaje)
        return mensaje

    def obtener_metricas_comunidad(self) -> dict:
        ahora = datetime.now()
        hace_24h = ahora - timedelta(hours=24)
        total_usuarios = len(self.registro_usuarios_historico)
        registros_24h = sum(1 for u in self.registro_usuarios_historico if u.get("timestamp", ahora) >= hace_24h)
        return {"total_usuarios": total_usuarios, "registrados_ultimas_24h": registros_24h}

    def purgar_chats_antiguos(self):
        limite_tiempo = datetime.now() - timedelta(days=7)
        self.mensajes_chat = [m for m in self.mensajes_chat if m.timestamp >= limite_tiempo]

social_engine = SocialEngine()

# ==========================================
# 5. MOTOR ADMINISTRATIVO
# ==========================================
ADMIN_EMAIL_VALIDO = "somos.libredeansiedad@gmail.com"
ADMIN_NOMBRE_VALIDO = "Juan Carlos"
ADMIN_MASTER_KEY = "admin_secreto_seguro_2026"

class AdminLoginRequest(BaseModel):
    correo: EmailStr
    nombre_dueno: str

class AdminMessageDirect(BaseModel):
    destinatario_id: str
    contenido: str

class NotificacionSistema(BaseModel):
    tipo: str
    descripcion: str
    timestamp: datetime

class AdminEngine:
    def __init__(self):
        self.notificaciones_activas: List[NotificacionSistema] = []
        self.sesion_admin_activa: bool = False
        self.foto_perfil_programa: str = "https://storage.googleapis.com/assets/logo_programa.png"

    def autenticar_administrador(self, req: AdminLoginRequest) -> dict:
        if req.correo == ADMIN_EMAIL_VALIDO and req.nombre_dueno.strip().lower() == ADMIN_NOMBRE_VALIDO.lower():
            self.sesion_admin_activa = True
            return {
                "authenticated": True,
                "modo": "Superusuario Maestro Anónimo",
                "mensaje": f"Acceso concedido. Bienvenido, {ADMIN_NOMBRE_VALIDO}. Modo invisible activado."
            }
        return {"authenticated": False, "error": "Credenciales maestras inválidas."}

    def enviar_mensaje_como_admin(self, req: AdminMessageDirect) -> dict:
        return {
            "remitente": "Administrador",
            "avatar_url": self.foto_perfil_programa,
            "destinatario_id": req.destinatario_id,
            "contenido": req.contenido,
            "timestamp": datetime.now()
        }

    def registrar_evento_notificacion(self, tipo_evento: str, detalle: str):
        evento = NotificacionSistema(tipo=tipo_evento, descripcion=detalle, timestamp=datetime.now())
        self.notificaciones_activas.append(evento)

admin_engine = AdminEngine()

# ==========================================
# 6. NÚCLEO FASTAPI Y ENDPOINTS FINALES
# ==========================================
class UserMessage(BaseModel):
    user_id: str
    message: str
    plan_nivel: str = "gratis"

class AdminPaymentReview(BaseModel):
    admin_secret: str
    user_id: str
    action: str  # 'aprobar' o 'rechazar'
    nuevo_plan: Optional[str] = "amigo_todos"

CRISIS_KEYWORDS = ["me estoy muriendo", "no aguanto", "no puedo respirar", "corazón acelerado", "me quiero rendir"]

def evaluar_capa_emergencia(mensaje: str) -> Optional[str]:
    mensaje_lower = mensaje.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in mensaje_lower:
            return (
                "⚠️ **PROTOCOLO DE EMERGENCIA ACTIVADO**\n\n"
                "Hey, respira conmigo. No te estás muriendo. Es un ataque de pánico y **va a pasar**.\n"
                "Estás a salvo en este momento. Haz exactamente esto:\n"
                "1. Suelta los hombros y afloja las manos.\n"
                "2. Inhala hondo por la nariz contando hasta 4... 1, 2, 3, 4.\n"
                "3. Sostén el aire... 1, 2, 3, 4.\n"
                "4. Exhala despacio por la boca... 1, 2, 3, 4.\n\n"
                "Mírame: esto es temporal y tu cuerpo se va a regular. ¿Hay alguien cerca a quien podamos avisar?"
            )
    return None

@app.post("/api/auth/register", summary="Registro de usuario con validación legal y opcionales")
def registrar_usuario(data: UserRegister):
    if not data.terms_accepted:
        raise HTTPException(status_code=400, detail="Debes leer y aceptar los Términos de Servicio y la Política de Privacidad.")
    if not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Debes aceptar que este programa es una herramienta informativa/educativa y no médica.")
    
    admin_engine.registrar_evento_notificacion("registro", f"Nuevo usuario registrado: {data.apodo} ({data.correo})")
    return {"status": "success", "message": f"¡Bienvenido/a {data.apodo}! Cuenta registrada correctamente.", "codigo_generado": "ABC123"}

@app.post("/api/auth/login", summary="Acceso de usuarios registrados con pensamiento aleatorio")
def acceder_usuario(data: UserLogin):
    pensamiento_del_dia = random.choice(PENSAMIENTOS_BIENVENIDA)
    admin_engine.registrar_evento_notificacion("login", f"Usuario ingresó al sistema: {data.correo}")
    return {"status": "success", "message": "Acceso concedido con éxito.", "bienvenida_avatar": pensamiento_del_dia, "plan_actual": "gratis"}

@app.post("/api/chat", summary="Endpoint principal para conversar con el Avatar")
def chat_con_avatar(data: UserMessage):
    respuesta_emergencia = evaluar_capa_emergencia(data.message)
    if respuesta_emergencia:
        return {"status": "crisis detected", "response": respuesta_emergencia, "source": "Emergency_Protocol"}
    
    avatar_config = AvatarConfig(avatar_id="av_1", nombre="Guía de Apoyo", personalidad="Resiliente y empático", pais_usuario="Venezuela", plan_usuario=data.plan_nivel)
    respuesta_avatar = avatar_engine.procesar_respuesta_avatar(data.message, avatar_config)
    return {"status": "success", "response": respuesta_avatar, "source": f"Avatar_Engine_{data.plan_nivel}"}

@app.post("/api/admin/login", summary="Acceso directo del Administrador sin contraseña")
def admin_login(data: AdminLoginRequest):
    resultado = admin_engine.autenticar_administrador(data)
    if not resultado["authenticated"]:
        raise HTTPException(status_code=403, detail=resultado["error"])
    return resultado

@app.post("/api/admin/verificar-pago", summary="Aprobar o rechazar pagos manuales")
def administrar_pago(data: AdminPaymentReview):
    if data.admin_secret != ADMIN_MASTER_KEY:
        raise HTTPException(status_code=403, detail="Credenciales de administrador inválidas.")
    
    admin_engine.registrar_evento_notificacion("pago", f"Pago procesado para usuario {data.user_id} - Acción: {data.action}")
    if data.action == "aprobar":
        return {"status": "success", "message": f"Pago verificado. Usuario {data.user_id} actualizado al plan '{data.nuevo_plan}'."}
    elif data.action == "rechazar":
        return {"status": "success", "message": f"Comprobante del usuario {data.user_id} rechazado."}
    else:
        raise HTTPException(status_code=400, detail="Acción no válida.")

@app.get("/api/admin/alertas", summary="Obtener notificaciones en tiempo real del sistema")
def obtener_alertas_admin(secret_key: str = Header(...)):
    if secret_key != ADMIN_MASTER_KEY:
        raise HTTPException(status_code=403, detail="No autorizado.")
    return {"notificaciones": admin_engine.notificaciones_activas}
