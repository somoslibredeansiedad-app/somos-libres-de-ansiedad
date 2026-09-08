from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import random
import os

app = FastAPI(
    title="Somos Libres de Ansiedad Core API",
    version="2.2.0",
    description="Backend definitivo y unificado para el ecosistema Somos Libres de Ansiedad con soporte local en GitHub."
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

# Catálogo dinámico basado en la carpeta 'avatares/' de GitHub
# Puedes ajustar la URL base según tu usuario y repositorio exacto en GitHub
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPOSITORIO/main/avatares"

AVATARES_CONFIG = [
    {
        "avatar_id": "ananya",
        "nombre": "Ananya Priya Sharma Iyer",
        "edad": 32,
        "nacionalidad": "India",
        "personalidad": "Holística y Compasiva",
        "archivo_base": "Ananya Priya Sharma Iyer"
    },
    {
        "avatar_id": "anastasia",
        "nombre": "Anastasia Yurievna Volkova",
        "edad": 36,
        "nacionalidad": "Rusia",
        "personalidad": "Analítica y Resiliente",
        "archivo_base": "Anastasia Yurievna Volkova"
    },
    {
        "avatar_id": "camilo",
        "nombre": "Camilo Ernesto Valdés Portuondo",
        "edad": 40,
        "nacionalidad": "Cuba",
        "personalidad": "Cercano y Motivacional",
        "archivo_base": "Camilo Ernesto Valdés Portuondo"
    },
    {
        "avatar_id": "chen",
        "nombre": "Chen Wei-Ming",
        "edad": 35,
        "nacionalidad": "Taiwán",
        "personalidad": "Sereno y Metódico",
        "archivo_base": "Chen Wei-Ming"
    },
    {
        "avatar_id": "eleonore",
        "nombre": "Éléonore Claire Dubois Laurent",
        "edad": 39,
        "nacionalidad": "Francia",
        "personalidad": "Reflexiva y Artística",
        "archivo_base": "Éléonore Claire Dubois Laurent"
    },
    {
        "avatar_id": "larissa",
        "nombre": "Larissa Beatriz Fonseca de Oliveira",
        "edad": 33,
        "nacionalidad": "Brasil",
        "personalidad": "Vital y Empática",
        "archivo_base": "Larissa Beatriz Fonseca de Oliveira"
    },
    {
        "avatar_id": "lucas",
        "nombre": "Lucas Alexander Miller",
        "edad": 37,
        "nacionalidad": "Estados Unidos",
        "personalidad": "Práctico y Directo",
        "archivo_base": "Lucas Alexander Miller"
    },
    {
        "avatar_id": "manuel",
        "nombre": "Manuel Francisco dos Santos Nzita",
        "edad": 41,
        "nacionalidad": "Angola",
        "personalidad": "Sólido y Protector",
        "archivo_base": "Manuel Francisco dos Santos Nzita"
    },
    {
        "avatar_id": "mariana",
        "nombre": "Mariana Elena Rivas Delgado",
        "edad": 34,
        "nacionalidad": "Venezuela",
        "personalidad": "Cálida y Comprensiva",
        "archivo_base": "Mariana Elena Rivas Delgado"
    },
    {
        "avatar_id": "rodrigo",
        "nombre": "Rodrigo Javier Navas Serrano",
        "edad": 38,
        "nacionalidad": "Chile",
        "personalidad": "Estratégico y Centrado",
        "archivo_base": "Rodrigo Javier Navas Serrano"
    }
]

class AvatarEngine:
    def obtener_catalogo(self) -> List[dict]:
        catalogo = []
        for av in AVATARES_CONFIG:
            # Generamos las URLs raw para la foto y el archivo de texto en GitHub
            nombre_archivo_url = av["archivo_base"].replace(" ", "%20")
            catalogo.append({
                "avatar_id": av["avatar_id"],
                "nombre": av["nombre"],
                "edad": av["edad"],
                "nacionalidad": av["nacionalidad"],
                "personalidad": av["personalidad"],
                "foto_url": f"{GITHUB_RAW_BASE}/{nombre_archivo_url}.jpg",
                "descripcion": f"Guía especializada con enfoque en {av['personalidad'].lower()}."
            })
        return catalogo

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
    avatar_nombre: str = "Mariana Elena Rivas Delgado"

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
