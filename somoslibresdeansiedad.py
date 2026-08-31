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
    "Está bien hacer una pausa. El descanso también es parte del camino."
]

class UserPlanStatus(BaseModel):
    user_id: str
    plan_actual: str  # 'gratis', 'comunicador', 'amigo_todos'
    fecha_expiracion: Optional[datetime] = None
    tiempo_acumulado_interaccion_horas: float = 0.0
    referidos_totales: int = 0
    referidos_vip_compraron: int = 0

class PlanesEngine:
    def __init__(self):
        self.usuarios_planes: Dict[str, UserPlanStatus] = {}

planes_engine = PlanesEngine()

AVATARS_DRIVE_FOLDER_ID = "1tyIBnoptE0RUt-DDv8wqhlJO_1Dqff5g"

class AvatarConfig(BaseModel):
    avatar_id: str
    nombre: str
    personalidad: str
    pais_usuario: str
    plan_usuario: str

class AvatarEngine:
    def __init__(self):
        self.folder_id = AVATARS_DRIVE_FOLDER_ID

    def procesar_respuesta_avatar(self, mensaje_usuario: str, avatar: AvatarConfig) -> str:
        return (
            f"Te escucho con atención y respeto. Entiendo perfectamente cuando me compartes lo que sientes. "
            f"Respira hondo, no tienes que cargar con todo al mismo tiempo. Estoy aquí para acompañarte paso a paso, con calma y sin juicios."
        )

avatar_engine = AvatarEngine()

class AdminLoginRequest(BaseModel):
    correo: EmailStr
    nombre_dueno: str

class NotificacionSistema(BaseModel):
    tipo: str
    descripcion: str
    timestamp: datetime

class AdminEngine:
    def __init__(self):
        self.notificaciones_activas: List[NotificacionSistema] = []
        self.sesion_admin_activa: bool = False

    def registrar_evento_notificacion(self, tipo_evento: str, detalle: str):
        evento = NotificacionSistema(tipo=tipo_evento, descripcion=detalle, timestamp=datetime.now())
        self.notificaciones_activas.append(evento)

admin_engine = AdminEngine()

class UserMessage(BaseModel):
    user_id: str
    message: str
    plan_nivel: str = "gratis"

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
                "4. Exhala despacio por la boca... 1, 2, 3, 4."
            )
    return None

@app.post("/api/auth/register", summary="Registro de usuario")
def registrar_usuario(data: UserRegister):
    if not data.terms_accepted or not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Debes aceptar los términos y el descargo de responsabilidad.")
    admin_engine.registrar_evento_notificacion("registro", f"Nuevo usuario: {data.apodo}")
    return {"status": "success", "message": f"¡Bienvenido/a {data.apodo}!", "codigo_generado": "ABC123"}

@app.post("/api/auth/login", summary="Acceso de usuarios")
def acceder_usuario(data: UserLogin):
    pensamiento_del_dia = random.choice(PENSAMIENTOS_BIENVENIDA)
    admin_engine.registrar_evento_notificacion("login", f"Ingreso: {data.correo}")
    
    # Si es el administrador global, otorgar de una vez plan 'amigo_todos'
    if data.correo == "somos.libredeansiedad@gmail.com":
        return {"status": "success", "message": "Acceso concedido.", "bienvenida_avatar": pensamiento_del_dia, "plan_actual": "amigo_todos"}
    
    return {"status": "success", "message": "Acceso concedido.", "bienvenida_avatar": pensamiento_del_dia, "plan_actual": "gratis"}

@app.post("/api/chat", summary="Chat con Avatar")
def chat_con_avatar(data: UserMessage):
    respuesta_emergencia = evaluar_capa_emergencia(data.message)
    if respuesta_emergencia:
        return {"status": "crisis detected", "response": respuesta_emergencia, "source": "Emergency_Protocol"}
    
    avatar_config = AvatarConfig(avatar_id="av_1", nombre="Guía de Apoyo", personalidad="Resiliente y empático", pais_usuario="Venezuela", plan_usuario=data.plan_nivel)
    respuesta_avatar = avatar_engine.procesar_respuesta_avatar(data.message, avatar_config)
    return {"status": "success", "response": respuesta_avatar, "source": f"Avatar_Engine_{data.plan_nivel}"}
