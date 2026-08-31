from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="Somos Libres de Ansiedad Core API",
    version="2.1.0",
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

# Catálogo oficial de Avatares vinculado a Google Drive (1tyIBnoptE0RUt-DDv8wqhlJO_1Dqff5g)
CATALOGO_AVATARES = [
    {
        "avatar_id": "av_valeria",
        "nombre": "Valeria Sofía",
        "edad": 34,
        "nacionalidad": "Venezuela",
        "personalidad": "Empática y Cálida",
        "foto_url": "https://drive.google.com/uc?id=1tyIBnoptE0RUt-DDv8wqhlJO_1Dqff5g",
        "descripcion": "Especialista en contención emocional y respiración consciente."
    },
    {
        "avatar_id": "av_mateo",
        "nombre": "Mateo Alejandro",
        "edad": 38,
        "nacionalidad": "Argentina",
        "personalidad": "Resiliente y Motivacional",
        "foto_url": "https://drive.google.com/uc?id=1tyIBnoptE0RUt-DDv8wqhlJO_1Dqff5g",
        "descripcion": "Enfocado en reestructuración cognitiva y superación de crisis."
    },
    {
        "avatar_id": "av_elena",
        "nombre": "Elena Rincón",
        "edad": 42,
        "nacionalidad": "España",
        "personalidad": "Escucha Activa y Serena",
        "foto_url": "https://drive.google.com/uc?id=1tyIBnoptE0RUt-DDv8wqhlJO_1Dqff5g",
        "descripcion": "Guía experta en meditación profunda y anclaje al presente."
    }
]

class AvatarConfig(BaseModel):
    avatar_id: str
    nombre: str
    personalidad: str
    pais_usuario: str
    plan_usuario: str

class AvatarEngine:
    def obtener_catalogo(self) -> List[dict]:
        return CATALOGO_AVATARES

    def procesar_respuesta_avatar(self, mensaje_usuario: str, avatar_nombre: str) -> str:
        return (
            f"Te escucho con atención y respeto. Entiendo perfectamente cuando me compartes '{mensaje_usuario}'. "
            f"Respira hondo, no tienes que cargar con todo al mismo tiempo. Estoy aquí para acompañarte paso a paso, con calma y sin juicios."
        )

avatar_engine = AvatarEngine()

class UserMessage(BaseModel):
    user_id: str
    message: str
    plan_nivel: str = "gratis"
    avatar_nombre: str = "Valeria Sofía"

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
    return {"status": "success", "message": f"¡Bienvenido/a {data.apodo}!", "codigo_generado": "ABC123"}

@app.post("/api/auth/login", summary="Acceso de usuarios")
def acceder_usuario(data: UserLogin):
    pensamiento_del_dia = random.choice(PENSAMIENTOS_BIENVENIDA)
    if data.correo == "somos.libredeansiedad@gmail.com":
        return {"status": "success", "message": "Acceso concedido.", "bienvenida_avatar": pensamiento_del_dia, "plan_actual": "amigo_todos"}
    return {"status": "success", "message": "Acceso concedido.", "bienvenida_avatar": pensamiento_del_dia, "plan_actual": "gratis"}

@app.get("/api/avatares/catalogo", summary="Obtener lista de avatares")
def obtener_avatares():
    return {"avatares": avatar_engine.obtener_catalogo()}

@app.post("/api/chat", summary="Chat con Avatar")
def chat_con_avatar(data: UserMessage):
    respuesta_emergencia = evaluar_capa_emergencia(data.message)
    if respuesta_emergencia:
        return {"status": "crisis detected", "response": respuesta_emergencia, "source": "Emergency_Protocol"}
    
    respuesta_avatar = avatar_engine.procesar_respuesta_avatar(data.message, data.avatar_nombre)
    return {"status": "success", "response": respuesta_avatar, "source": f"Avatar_Engine_{data.plan_nivel}"}
