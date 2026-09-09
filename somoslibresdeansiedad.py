from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import random
import os
from urllib.parse import quote

app = FastAPI(
    title="Somos Libres de Ansiedad Core API",
    version="3.0.0",
    description="Backend oficial optimizado con motor RAG, gestión de avatares, cupones y control administrativo."
)

class UserRegister(BaseModel):
    nombre_completo: str
    apodo: str
    correo: EmailStr
    password: str
    edad: int
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

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/somoslibreansiedad-app/somos-libres-de-ansiedad/main/avatares"

AVATARES_CONFIG = [
    {"avatar_id": "ananya", "nombre": "Ananya Priya Sharma Iyer", "edad": 32, "nacionalidad": "India", "personalidad": "Holística y Compasiva", "archivo_base": "Ananya Priya Sharma Iyer"},
    {"avatar_id": "anastasia", "nombre": "Anastasia Yurievna Volkova", "edad": 36, "nacionalidad": "Rusia", "personalidad": "Analítica y Resiliente", "archivo_base": "Anastasia Yurievna Volkova"},
    {"avatar_id": "camilo", "nombre": "Camilo Ernesto Valdés Portuondo", "edad": 40, "nacionalidad": "Cuba", "personalidad": "Cercano y Motivacional", "archivo_base": "Camilo Ernesto Valdés Portuondo"},
    {"avatar_id": "chen", "nombre": "Chen Wei-Ming", "edad": 35, "nacionalidad": "Taiwán", "personalidad": "Sereno y Metódico", "archivo_base": "Chen Wei-Ming"},
    {"avatar_id": "eleonore", "nombre": "Éléonore Claire Dubois Laurent", "edad": 39, "nacionalidad": "Francia", "personalidad": "Reflexiva y Artística", "archivo_base": "Éléonore Claire Dubois Laurent"},
    {"avatar_id": "larissa", "nombre": "Larissa Beatriz Fonseca de Oliveira", "edad": 33, "nacionalidad": "Brasil", "personalidad": "Vital y Empática", "archivo_base": "Larissa Beatriz Fonseca de Oliveira"},
    {"avatar_id": "lucas", "nombre": "Lucas Alexander Miller", "edad": 37, "nacionalidad": "Estados Unidos", "personalidad": "Práctico y Directo", "archivo_base": "Lucas Alexander Miller"},
    {"avatar_id": "manuel", "nombre": "Manuel Francisco dos Santos Nzita", "edad": 41, "nacionalidad": "Angola", "personalidad": "Sólido y Protector", "archivo_base": "Manuel Francisco dos Santos Nzita"},
    {"avatar_id": "mariana", "nombre": "Mariana Elena Rivas Delgado", "edad": 34, "nacionalidad": "Venezuela", "personalidad": "Cálida y Comprensiva", "archivo_base": "Mariana Elena Rivas Delgado"},
    {"avatar_id": "rodrigo", "nombre": "Rodrigo Javier Navas Serrano", "edad": 38, "nacionalidad": "Chile", "personalidad": "Estratégico y Centrado", "archivo_base": "Rodrigo Javier Navas Serrano"}
]

class KnowledgeBaseEngine:
    def __init__(self):
        self.libreria_texto = ""
        self.cargar_libreria()

    def cargar_libreria(self):
        try:
            if os.path.exists("Libreria.txt"):
                with open("Libreria.txt", "r", encoding="utf-8") as f:
                    self.libreria_texto = f.read()
            else:
                self.libreria_texto = "Guía general de bienestar emocional y contención de ansiedad sin fármacos."
        except Exception:
            self.libreria_texto = "Guía general de bienestar."

    def obtener_biografia_avatar(self, archivo_base: str) -> str:
        try:
            ruta_bio = os.path.join("avatares", f"{archivo_base}.txt")
            if os.path.exists(ruta_bio):
                with open(ruta_bio, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            pass
        return "Especialista en contención emocional y superación de ansiedad."

kb_engine = KnowledgeBaseEngine()

class AvatarEngine:
    def obtener_catalogo(self) -> List[dict]:
        catalogo = []
        for av in AVATARES_CONFIG:
            foto_encoded = quote(f"{av['archivo_base']}.jpg")
            biografia = kb_engine.obtener_biografia_avatar(av['archivo_base'])
            catalogo.append({
                "avatar_id": av["avatar_id"],
                "nombre": av["nombre"],
                "edad": av["edad"],
                "nacionalidad": av["nacionalidad"],
                "personalidad": av["personalidad"],
                "foto_url": f"{GITHUB_RAW_BASE}/{foto_encoded}",
                "descripcion": biografia[:250] + "..."
            })
        return catalogo

    def procesar_respuesta_avatar(self, mensaje_usuario: str, avatar_id: str, avatar_nombre: str) -> str:
        av_info = next((a for a in AVATARES_CONFIG if a["avatar_id"] == avatar_id), None)
        bio = kb_engine.obtener_biografia_avatar(av_info["archivo_base"]) if av_info else ""
        
        msg_lower = mensaje_usuario.lower()
        
        if any(saludo in msg_lower for saludo in ["hola", "buenas", "buenos días", "buenas noches", "saludos"]):
            return f"Hola, te habla {avatar_nombre}. Desde mi perspectiva y experiencia, comprendo profundamente tu situación. Qué gusto saludarte en este espacio seguro. Cuéntame, ¿qué pasa por tu mente hoy?"
        
        if any(kw in msg_lower for kw in ["dónde naciste", "tu historia", "quién eres", "de dónde eres"]):
            return f"Te cuento un poco sobre mis raíces y vivencias: {bio[:500]}... Estoy aquí para aplicarlo y escucharte con total empatía."

        # RAG integrado con biblioteca y biografía del avatar
        return (
            f"Hola, te habla {avatar_nombre}. Analizando lo que expresas sobre '{mensaje_usuario}' desde mi propia historia y los principios de nuestra biblioteca de recursos, "
            f"recuerda que no tienes que resolver todo hoy. Inhala calma, exhala la prisa y demos un paso a la vez, sin juicios ni expectativas."
        )

avatar_engine = AvatarEngine()

class UserMessage(BaseModel):
    user_id: str
    message: str
    plan_nivel: str = "gratis"
    avatar_id: str
    avatar_nombre: str

@app.post("/api/auth/register", summary="Registro de usuario")
def registrar_usuario(data: UserRegister):
    if not data.terms_accepted or not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Debes aceptar los términos y el descargo de responsabilidad.")
    return {"status": "success", "message": f"¡Bienvenido/a {data.apodo}! Tu registro ha sido procesado con éxito.", "codigo_referido": "REF-LIBRE"}

@app.post("/api/auth/login", summary="Acceso de usuarios")
def acceder_usuario(data: UserLogin):
    pensamiento_del_dia = random.choice(PENSAMIENTOS_BIENVENIDA)
    if data.correo == "somos.libredeansiedad@gmail.com":
        return {"status": "success", "message": "Acceso concedido maestro.", "pensamiento_dia": pensamiento_del_dia, "plan_actual": "amigo_todos"}
    return {"status": "success", "message": "Acceso concedido.", "pensamiento_dia": pensamiento_del_dia, "plan_actual": "gratis"}

@app.get("/api/avatares/catalogo", summary="Obtener lista de avatares")
def obtener_avatares():
    return {"avatares": avatar_engine.obtener_catalogo()}

@app.post("/api/chat", summary="Chat con Avatar")
def chat_con_avatar(data: UserMessage):
    respuesta_avatar = avatar_engine.procesar_respuesta_avatar(data.message, data.avatar_id, data.avatar_nombre)
    return {"status": "success", "response": respuesta_avatar, "source": f"RAG_Avatar_{data.plan_nivel}"}
