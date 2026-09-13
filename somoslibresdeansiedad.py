import json
import os
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import bcrypt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./somos_libres.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SECRET_KEY = os.getenv("SECRET_KEY", "somos-libres-seguridad-produccion-2026-clave-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días de sesión activa

security = HTTPBearer()

app = FastAPI(
    title="Somos Libres de Ansiedad Core API",
    version="4.0.0",
    description="Backend oficial desacoplado: autenticación, control estricto de cuotas, avatares estandarizados y comunidad."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS ORM ---
class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(120))
    apodo: Mapped[str] = mapped_column(String(50), index=True)
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    edad: Mapped[int] = mapped_column(Integer)
    
    # Campos opcionales de perfil
    sexo: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    profesion: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    situacion_sentimental: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cantidad_hijos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Sistema de roles y planes
    plan_nivel: Mapped[str] = mapped_column(String(30), default="gratis")  # gratis, comunicador, amigo_todos
    role: Mapped[str] = mapped_column(String(20), default="user")          # user, admin
    codigo_referido: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    referido_por: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    # Cuotas de interacción semanal
    chats_usados_semana: Mapped[int] = mapped_column(Integer, default=0)
    audios_usados_semana: Mapped[int] = mapped_column(Integer, default=0)
    avatares_activos: Mapped[str] = mapped_column(String(255), default="[]")  # IDs en formato JSON string
    
    # Vigencia y estado
    suscripcion_expira: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    posts = relationship("MuroPostModel", back_populates="autor", cascade="all, delete-orphan")
    sugerencias = relationship("BuzonModel", back_populates="autor", cascade="all, delete-orphan")

class CouponModel(Base):
    __tablename__ = "cupones"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    tipo_plan: Mapped[str] = mapped_column(String(30))
    duracion_dias: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class MuroPostModel(Base):
    __tablename__ = "muro_posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    plan_origen: Mapped[str] = mapped_column(String(30), default="gratis")
    contenido: Mapped[str] = mapped_column(String(1000))
    is_anonimo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    autor = relationship("UserModel", back_populates="posts")

class BuzonModel(Base):
    __tablename__ = "buzon_mensajes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    categoria: Mapped[str] = mapped_column(String(50), default="Consulta general")
    asunto: Mapped[str] = mapped_column(String(150), default="Sin asunto")
    mensaje: Mapped[str] = mapped_column(String(2000))
    respuesta_admin: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    estatus: Mapped[str] = mapped_column(String(30), default="Pendiente")  # Pendiente, Respondido
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    autor = relationship("UserModel", back_populates="sugerencias")

# --- ESQUEMAS PYDANTIC ---
class UserRegister(BaseModel):
    nombre_completo: str
    apodo: str
    correo: EmailStr
    password: str = Field(..., min_length=6)
    edad: int
    sexo: Optional[str] = None
    profesion: Optional[str] = None
    situacion_sentimental: Optional[str] = None
    cantidad_hijos: Optional[int] = None
    codigo_referido: Optional[str] = None
    terms_accepted: bool
    disclaimer_accepted: bool

class UserLogin(BaseModel):
    correo: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    apodo: str
    plan_actual: str
    role: str
    codigo_referido: str
    pensamiento_dia: str

class AvatarSelectRequest(BaseModel):
    avatar_id: str

class UserMessage(BaseModel):
    avatar_id: str
    message: str
    is_audio: bool = False
    audio_duracion_segundos: int = 0

class CouponCreate(BaseModel):
    tipo: str = Field(..., description="verde, azul, rojo, morado")

class CouponRedeem(BaseModel):
    codigo: str

class MuroPostCreate(BaseModel):
    contenido: str = Field(..., max_length=1000)
    is_anonimo: bool = False

class BuzonCreate(BaseModel):
    categoria: str = "Consulta general"
    asunto: str
    mensaje: str = Field(..., max_length=2000)

class BuzonResponder(BaseModel):
    ticket_id: int
    respuesta: str

# --- CONSTANTES Y CATÁLOGO OFICIAL (10 AVATARES) ---
AVATARES_OFICIALES = {
    "ananya": {
        "id": "ananya",
        "nombre": "Ananya Priya Sharma Iyer",
        "pais": "India",
        "bandera": "🇮🇳",
        "tono": "Sereno, reflexivo y orientado a la calma mental",
        "imagen": "ananya.jpg",
        "archivo_prompt": "ananya.txt",
        "disparadores": [
            "Namasté. Qué alegría coincidir hoy. Respira profundo un momento... cuéntame, ¿qué pensamiento o situación ocupa hoy tu mente?",
            "Bienvenido. A veces solo necesitamos una pausa en medio del ruido para ver con claridad. ¿De qué te gustaría que hablemos?",
            "Hola. Recuerda que no tienes que resolver todo hoy. Da un paso a la vez; dime, ¿en qué puedo acompañarte el día de hoy?",
            "Cada día nos presenta un nuevo aprendizaje. Si sientes que la carga pesa un poco, aquí estoy para escucharte con atención.",
            "Namasté. Encuentra tu centro por un instante. ¿Hay alguna decisión importante que estés evaluando en este momento?",
            "Hola. Las mejores respuestas suelen surgir cuando ordenamos nuestras ideas con serenidad. ¿Por dónde empezamos hoy?",
            "Bienvenido a este espacio tranquilo. Dime qué ocurre hoy en tu vida y busquemos juntos una perspectiva equilibrada.",
            "A veces el corazón busca respuestas que la prisa no deja ver. Siéntete en total libertad de desahogarte.",
            "Hola. La claridad llega cuando nos permitimos soltar la tensión. Cuéntame qué tienes en mente y reflexionemos juntos.",
            "Namasté. Hoy es un buen día para priorizar tu paz interior. ¿Qué inquietud o proyecto traes contigo hoy?"
        ]
    },
    "anastasia": {
        "id": "anastasia",
        "nombre": "Anastasia Yurievna Volkova",
        "pais": "Rusia",
        "bandera": "🇷🇺",
        "tono": "Directo, maduro, perspicaz y analítico",
        "imagen": "anastasia.jpg",
        "archivo_prompt": "anastasia.txt",
        "disparadores": [
            "Hola. Me alegra saludarte. Dime con total franqueza: ¿cuál es el reto o asunto que necesitas analizar hoy?",
            "Bienvenido. La vida exige temple y claridad mental ante las dudas. ¿Qué situación está requiriendo tu atención?",
            "Hola. No le demos vueltas innecesarias a las cosas; analicemos los hechos con calma. ¿Qué tienes entre manos?",
            "Buenas. Incluso en los días más fríos o complicados se puede encontrar un camino sólido. Cuéntame qué sucede.",
            "Hola. Tomar buenas decisiones requiere ver la realidad tal como es. ¿Qué dilema te gustaría que evaluemos hoy?",
            "Bienvenido. Estoy lista para escucharte con objetividad y sin rodeos. ¿Cuál es el punto de partida hoy?",
            "Hola. Las dudas se disipan cuando se traza un plan claro. Dime qué te preocupa y busquemos una solución concreta.",
            "A veces la paciencia y la disciplina son los mejores consejeros. Cuéntame qué situación estás atravesando.",
            "Hola. Tómate un segundo para ordenar tu idea y explícame: ¿qué decisión necesitas tomar próximamente?",
            "Bienvenido. Cuenta con una mirada sincera y constructiva para lo que necesites resolver hoy. Te escucho."
        ]
    },
    "camilo": {
        "id": "camilo",
        "nombre": "Camilo Ernesto Valdés Portuondo",
        "pais": "Cuba",
        "bandera": "🇨🇺",
        "tono": "Cercano, cálido, optimista y humano",
        "imagen": "camilo.jpg",
        "archivo_prompt": "camilo.txt",
        "disparadores": [
            "¡Oye, qué tal! Bienvenido. Cuéntame con toda confianza, ¿qué te trae por aquí hoy?",
            "¡Hola, mi hermano! Siempre hay una salida cuando se mira la vida con cabeza fría y buen ánimo. ¿Qué me cuentas?",
            "¡Un gustazo saludarte! A mal tiempo, buena cara y mejores decisiones. Dime en qué te puedo dar una mano hoy?",
            "Hola, ¿cómo va todo? Suelta lo que te esté apretando el pecho; aquí estamos para conversar de verdad y sin pena.",
            "¡Epa! La vida da muchas vueltas, pero para cada problema hay una respuesta. Cuéntame qué te tiene pensando tanto.",
            "¡Qué alegría tenerte por aquí! Tómate un respiro, ponte cómodo y dime: ¿por dónde empezamos a desenredar el nudo?",
            "Hola. No te guardes las dudas; ponerlas en palabras ya es la mitad de la solución. Te escucho con atención.",
            "¡Saludos! Recuerda que hasta el día más nublado aclara. Dime qué situación estás viviendo y la vemos juntos.",
            "¡Hola! Aquí tienes un oído amigo y un consejo sincero cuando lo necesites. ¿Qué planes o dudas tienes hoy?",
            "¡Bienvenido! Cuéntame qué está pasando por tu cabeza y busquemos el lado práctico para seguir adelante con fuerza."
        ]
    },
    "chen": {
        "id": "chen",
        "nombre": "Chen Wei-Ming",
        "pais": "Taiwán / China",
        "bandera": "🇹🇼 / 🇨🇳",
        "tono": "Paciente, prudente y enfocado en el equilibrio",
        "imagen": "chen.jpg",
        "archivo_prompt": "chen.txt",
        "disparadores": [
            "Hola, te doy la bienvenida. Recuerda: un viaje de mil leguas comienza con un solo paso. ¿Cuál es el primer paso que buscas hoy?",
            "Saludos. Cuando las aguas están revueltas, conviene esperar a que se asienten. ¿Qué situación requiere hoy serenidad en tu vida?",
            "Bienvenido. A veces menos es más; simplificar las cosas ayuda a ver la verdad. ¿De qué te gustaría hablar?",
            "Hola. El bambú se dobla ante la tormenta pero no se quiebra. ¿Qué reto estás enfrentando en este momento?",
            "Paz y buen día. Cuéntame qué decisión tienes frente a ti; la analizaremos con calma y visión de futuro.",
            "Hola. Escuchar atentamente es el primer principio para encontrar armonía. Dime qué está pasando en tus asuntos.",
            "Bienvenido. No hay prisa: tómate tu tiempo para explicarme qué te inquieta y lo revisamos paso a paso.",
            "Saludos cordiales. Cada dilema trae consigo una semilla de oportunidad. ¿Cuál es el dilema que traes hoy?",
            "Hola. La paciencia no es pasividad, sino la capacidad de actuar en el instante preciso. ¿Qué dudas tienes hoy?",
            "Bienvenido a este espacio de diálogo constructivo. Dime qué área de tu vida te gustaría ordenar o mejorar."
        ]
    },
    "eleonore": {
        "id": "eleonore",
        "nombre": "Éléonore Claire Dubois Laurent",
        "pais": "Francia",
        "bandera": "🇫🇷",
        "tono": "Elegante, lúcido, introspectivo y reflexivo",
        "imagen": "eleonore.jpg",
        "archivo_prompt": "eleonore.txt",
        "disparadores": [
            "Bonjour. Qué placer saludarte. Dime con tranquilidad: ¿qué inquietud te invita a conversar hoy?",
            "Bienvenido. A veces basta con cambiar la perspectiva para apreciar la belleza de una solución sencilla. ¿Qué te ocurre?",
            "Bonjour. La vida merece ser vivida con intención y coherencia. ¿Hay alguna decisión importante en tu camino?",
            "Hola. No hay pregunta pequeña si te importa a ti. Tómate un momento y cuéntame qué estás sintiendo.",
            "Bienvenido. Las mejores reflexiones nacen de una conversación honesta con uno mismo. ¿Por dónde te gustaría empezar?",
            "Bonjour. A veces nos complicamos buscando la perfección en lugar de la armonía. ¿Qué te tiene pensativo hoy?",
            "Hola. Cuéntame qué situación estás evaluando; busquemos juntos un punto de vista lúcido y elegante para resolverlo.",
            "Bienvenido. Si necesitas ordenar tus pensamientos sin juicios ni prisas, estás en el lugar indicado. Te escucho.",
            "Bonjour. Recuerda que tus prioridades definen tu día a día. ¿Qué asunto requiere hoy toda tu atención?",
            "Hola. Me alegra encontrarte aquí. Exprésame libremente tus dudas y encontremos juntos el mejor rumbo a seguir."
        ]
    },
    "larissa": {
        "id": "larissa",
        "nombre": "Larissa Beatriz Fonseca de Oliveira",
        "pais": "Brasil",
        "bandera": "🇧🇷",
        "tono": "Vivaz, motivador, espontáneo y cálido",
        "imagen": "larissa.jpg",
        "archivo_prompt": "larissa.txt",
        "disparadores": [
            "¡Olá! ¡Qué lindo tenerte por aquí! Cuéntame, ¿qué energía traes hoy y de qué te gustaría conversar?",
            "¡Hola! La vida siempre tiene un camino nuevo para sorprendernos. Dime qué te preocupa y busquemos soluciones juntos.",
            "¡Tudo bem! Respira profundo, sonríe un poquito y cuéntame: ¿qué está pasando por tu mente en este momento?",
            "¡Bienvenido! No te guardes nada; aquí estamos para hablar de frente y con el corazón abierto. ¿Qué me cuentas?",
            "¡Hola! A veces solo necesitamos una chispa de motivación y un plan claro para avanzar. ¿Cuál es tu meta hoy?",
            "¡Olá! Ningún obstáculo es más grande que tus ganas de superarte. Cuéntame qué reto tienes entre manos hoy.",
            "¡Qué alegría saludarte! Si hoy sientes que te falta claridad, no te preocupes; lo vamos a descubrir juntos. Te escucho.",
            "¡Hola! Recuerda disfrutar el camino mientras resuelves los problemas del día. Dime, ¿en qué puedo ayudarte?",
            "¡Olá! Suelta las tensiones y conversemos como viejos amigos. ¿Qué asunto te gustaría desahogar o resolver?",
            "¡Bienvenido! Tienes la fuerza para lograr lo que te propones; solo ordenemos las ideas. ¿Por dónde empezamos?"
        ]
    },
    "lucas": {
        "id": "lucas",
        "nombre": "Lucas Alexander Miller",
        "pais": "EE. UU. / Reino Unido",
        "bandera": "🇺🇸 / 🇬🇧",
        "tono": "Práctico, estructurado y enfocado en objetivos",
        "imagen": "lucas.jpg",
        "archivo_prompt": "lucas.txt",
        "disparadores": [
            "Hi there! Qué bueno verte. Dime directamente: ¿cuál es el objetivo principal o el reto que quieres abordar hoy?",
            "Hola. Vayamos directo al grano pero con calma: ¿qué decisión o proyecto está demandando tu atención en este momento?",
            "Bienvenido. Los grandes resultados se construyen con pequeñas acciones consistentes. ¿Qué plan tienes en mente hoy?",
            "Hey! Me alegra saludarte. Cuéntame qué situación se te está presentando y armemos una buena estrategia.",
            "Hola. Cuando dividimos un problema grande en partes pequeñas, todo se vuelve manejable. ¿Qué te preocupa hoy?",
            "Bienvenido. Estoy aquí para ayudarte a poner foco y claridad en tus ideas. ¿Cuál es tu prioridad el día de hoy?",
            "Hello! No dejes que la sobrecarga de información te detenga. Explícame tu dilema y lo estructuramos juntos.",
            "Hola. La mejor manera de avanzar es tomar una decisión fundamentada y pasar a la acción. ¿Qué duda tienes hoy?",
            "Bienvenido. Cuéntame en qué estás trabajando o qué obstáculo apareció en tu camino; te daré mi punto de vista.",
            "Hey! Listo para escucharte. Tómate el tiempo necesario para resumirme tu situación y busquemos la mejor ruta."
        ]
    },
    "manuel": {
        "id": "manuel",
        "nombre": "Manuel Francisco dos Santos Nzita",
        "pais": "Angola",
        "bandera": "🇦🇴",
        "tono": "Ponderado, comunitario y con sabiduría reflexiva",
        "imagen": "manuel.jpg",
        "archivo_prompt": "manuel.txt",
        "disparadores": [
            "Saludos cordiales. Es un honor saludarte. Cuéntame, ¿cuáles son los pasos o inquietudes que traes en tu camino hoy?",
            "Bienvenido. Dice un sabio adagio que quien escucha con atención aprende el doble. Aquí estoy para ti; te escucho.",
            "Hola. Para cruzar un río con seguridad, primero se tantean las piedras. ¿Qué decisión importante estás considerando?",
            "Paz para ti. En comunidad y con diálogo sincero las cargas se hacen más livianas. Dime qué te inquieta hoy.",
            "Saludos. La verdadera fortaleza radica en saber cuándo hablar y cuándo reflexionar. ¿Qué asunto ocupa tu mente?",
            "Bienvenido a este espacio de respeto. Cuéntame tu historia o lo que te está ocurriendo hoy con total tranquilidad.",
            "Hola. Ningún árbol crece fuerte sin raíces firmes; busquemos el origen de tus dudas. ¿Por dónde comenzamos?",
            "Saludos fraternales. Me alegra recibirte. Dime qué reto familiar, personal o laboral te gustaría que examinemos juntos.",
            "Bienvenido. Recuerda que no caminas solo; siempre hay un consejo oportuno para quien lo busca de corazón. Te escucho.",
            "Hola. Tómate un respiro y comparte conmigo lo que sientas necesario; buscaremos la respuesta más sabia y justa."
        ]
    },
    "mariana": {
        "id": "mariana",
        "nombre": "Mariana Elena Rivas Delgado",
        "pais": "Venezuela",
        "bandera": "🇻🇪",
        "tono": "Afectuoso, solidario, resiliente y resolutivo",
        "imagen": "mariana.jpg",
        "archivo_prompt": "mariana.txt",
        "disparadores": [
            "¡Hola! ¡Qué gusto verte por acá! Cuéntame con confianza, ¿cómo estás y qué te trae por este chat hoy?",
            "¡Epa, bienvenido! A veces la rutina se pone cuesta arriba, pero aquí siempre le buscamos la vuelta a todo. ¿Qué pasó?",
            "¡Hola! Respira profundo, tómate un momento para ti y dime: ¿qué tienes en la cabeza que te está quitando el sueño?",
            "¡Qué alegría saludarte! Aquí tienes un espacio seguro para desahogarte y buscar soluciones prácticas. ¿Te escucho?",
            "¡Epa! Para todo hay solución, te lo aseguro. Cuéntame qué situación tienes enfrente y la resolvemos juntos paso a paso.",
            "¡Hola, bienvenido! No te quedes con las dudas dando vueltas; suéltalo todo con confianza y lo vemos con calma.",
            "¡Qué bueno que me escribes! Dime qué decisión estás pensando tomar y te doy mi opinión sincera y de corazón.",
            "¡Hola! Recuerda que somos más fuertes de lo que creemos, solo hace falta organizarse. ¿Cuál es el plan de hoy?",
            "¡Epa! Aquí estoy lista para darte una mano y escucharte con atención. ¿Por dónde quieres que empecemos a conversar?",
            "¡Bienvenido! Ponte cómodo y cuéntame qué te tiene pensativo hoy; verás que hablando todo se aclara mucho más rápido."
        ]
    },
    "rodrigo": {
        "id": "rodrigo",
        "nombre": "Rodrigo Javier Navas Serrano",
        "pais": "España",
        "bandera": "🇪🇸",
        "tono": "Directo, natural, pragmático y con sentido común",
        "imagen": "rodrigo.jpg",
        "archivo_prompt": "rodrigo.txt",
        "disparadores": [
            "¡Buenas! Qué alegría saludarte. Cuéntame sin rodeos: ¿qué te trae por aquí el día de hoy?",
            "¡Hola! Oye, las cosas habladas se entienden y se resuelven mucho mejor. ¿Qué dilema tienes entre manos?",
            "Bienvenido. A veces nos complicamos la vida más de la cuenta por no pedir una segunda opinión. ¿Qué te preocupa?",
            "¡Buenas! Venga, tómate un momento, cuéntame de qué va el asunto y le aplicamos un poco de sentido común.",
            "¡Hola! No le des tantas vueltas en la cabeza que se hace una montaña. Suéltalo aquí y lo vemos juntos con calma.",
            "Bienvenido. Aquí tienes un espacio de confianza para hablar las cosas claras y sin adornos. ¿Qué ha ocurrido?",
            "¡Buenas tardes/días! Me alegra que me consultes. Dime cuál es la decisión que tienes que tomar y te doy mi punto de vista.",
            "¡Hola! Recuerda que un buen café o una buena charla aclaran casi cualquier problema. Dime, ¿por dónde empezamos?",
            "Bienvenido. No te agobies antes de tiempo; analicemos las opciones reales que tienes sobre la mesa. Te escucho.",
            "¡Qué tal! Estoy listo para echarte una mano en lo que necesites orientar hoy. Cuéntame con total naturalidad."
        ]
    }
}

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

# --- DEPENDENCIAS Y SEGURIDAD ---
async def get_db():
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> UserModel:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas.")

    result = await db.execute(select(UserModel).where(UserModel.correo == correo))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    
    user.last_active_at = datetime.now(timezone.utc)
    await db.commit()
    return user

async def get_current_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso exclusivo del Administrador (Juan Carlos).")
    return current_user

async def generar_codigo_referido_unico(db: AsyncSession) -> str:
    while True:
        codigo = str(random.randint(1111111, 9999999))
        result = await db.execute(select(UserModel).where(UserModel.codigo_referido == codigo))
        if not result.scalar_one_or_none():
            return codigo

# --- ENDPOINTS: AUTENTICACIÓN Y REGISTRO ---
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED, summary="Registro de usuario")
async def registrar_usuario(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if not data.terms_accepted or not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Debes aceptar los Términos de Servicio y el Descargo de Responsabilidad Médica.")

    result = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo electrónico ya se encuentra registrado.")

    hashed_pw = hash_password(data.password)
    codigo_ref = await generar_codigo_referido_unico(db)

    # Identificación del Administrador Maestro
    is_admin = (data.correo.strip().lower() == "somos.libredeansiedad@gmail.com")
    role = "admin" if is_admin else "user"
    plan = "amigo_todos" if is_admin else "gratis"

    # Si vino recomendado por un referido, se registra el enlace
    referido_valido = None
    if data.codigo_referido:
        ref_check = await db.execute(select(UserModel).where(UserModel.codigo_referido == data.codigo_referido))
        if ref_check.scalar_one_or_none():
            referido_valido = data.codigo_referido

    nuevo_usuario = UserModel(
        nombre_completo=data.nombre_completo,
        apodo=data.apodo,
        correo=data.correo,
        password_hash=hashed_pw,
        edad=data.edad,
        sexo=data.sexo,
        profesion=data.profesion,
        situacion_sentimental=data.situacion_sentimental,
        cantidad_hijos=data.cantidad_hijos,
        plan_nivel=plan,
        role=role,
        codigo_referido=codigo_ref,
        referido_por=referido_valido
    )
    db.add(nuevo_usuario)
    await db.commit()
    
    return {
        "status": "success",
        "message": f"¡Bienvenido/a {data.apodo}! Registro completado.",
        "codigo_referido": codigo_ref
    }

@app.post("/api/auth/login", response_model=TokenResponse, summary="Acceso de usuarios")
async def acceder_usuario(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos.")

    access_token = create_access_token(data={"sub": user.correo, "role": user.role})
    pensamiento = random.choice(PENSAMIENTOS_BIENVENIDA)
    
    return TokenResponse(
        access_token=access_token,
        apodo=user.apodo,
        plan_actual=user.plan_nivel,
        role=user.role,
        codigo_referido=user.codigo_referido,
        pensamiento_dia=pensamiento
    )

# --- ENDPOINTS: AVATARES Y SELECCIÓN ---
@app.get("/api/avatares/catalogo", summary="Listado oficial de los 10 Avatares")
async def obtener_avatares(current_user: UserModel = Depends(get_current_user)):
    catalogo = []
    avatares_activos = json.loads(current_user.avatares_activos)
    
    for av_id, av in AVATARES_OFICIALES.items():
        catalogo.append({
            "id": av["id"],
            "nombre": av["nombre"],
            "pais": av["pais"],
            "bandera": av["bandera"],
            "tono": av["tono"],
            "imagen": av["imagen"],
            "is_activo": av_id in avatares_activos,
            "disparador_inicial": random.choice(av["disparadores"])
        })
    return {"status": "success", "avatares": catalogo}

@app.post("/api/avatares/seleccionar", summary="Activar un avatar según límites del Plan")
async def seleccionar_avatar(data: AvatarSelectRequest, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.avatar_id not in AVATARES_OFICIALES:
        raise HTTPException(status_code=404, detail="El avatar solicitado no existe.")

    avatares_activos = json.loads(current_user.avatares_activos)
    limites_max = {"gratis": 1, "comunicador": 3, "amigo_todos": 10}
    max_permitidos = limites_max.get(current_user.plan_nivel, 1)

    if data.avatar_id in avatares_activos:
        return {"status": "success", "message": "El avatar ya está activo.", "activos": avatares_activos}

    if len(avatares_activos) >= max_permitidos and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail=f"Tu plan ({current_user.plan_nivel}) solo permite {max_permitidos} avatar(es) activo(s). Actualiza tu plan para desbloquear más."
        )

    avatares_activos.append(data.avatar_id)
    current_user.avatares_activos = json.dumps(avatares_activos)
    await db.commit()

    return {"status": "success", "message": f"Avatar {AVATARES_OFICIALES[data.avatar_id]['nombre']} vinculado correctamente.", "activos": avatares_activos}

# --- ENDPOINTS: CHAT CON AVATAR Y VALIDACIÓN DE PLAN ---
@app.post("/api/chat", summary="Interacción con Avatar (Texto y Notas de Voz)")
async def chat_con_avatar(data: UserMessage, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.avatar_id not in AVATARES_OFICIALES:
        raise HTTPException(status_code=404, detail="Avatar no encontrado.")

    # 1. Reglas de Límites por Plan
    reglas_texto = {"gratis": 25, "comunicador": 100, "amigo_todos": 999999}
    reglas_audio_cant = {"gratis": 3, "comunicador": 10, "amigo_todos": 999999}
    reglas_audio_seg = {"gratis": 10, "comunicador": 30, "amigo_todos": 60}

    limite_texto = reglas_texto.get(current_user.plan_nivel, 25)
    limite_audio_cant = reglas_audio_cant.get(current_user.plan_nivel, 3)
    max_segundos_audio = reglas_audio_seg.get(current_user.plan_nivel, 10)

    # Validar cuota general de mensajes semanales
    if current_user.chats_usados_semana >= limite_texto and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Has alcanzado el límite semanal de mensajes para tu plan.")

    # Validar si es nota de voz
    if data.is_audio:
        if current_user.audios_usados_semana >= limite_audio_cant and current_user.role != "admin":
            raise HTTPException(status_code=403, detail=f"Has alcanzado el límite de {limite_audio_cant} audios semanales de tu plan.")
        if data.audio_duracion_segundos > max_segundos_audio and current_user.role != "admin":
            raise HTTPException(status_code=400, detail=f"Tu audio excede el límite permitido de {max_segundos_audio} segundos para tu plan.")
        current_user.audios_usados_semana += 1

    current_user.chats_usados_semana += 1
    await db.commit()

    avatar_info = AVATARES_OFICIALES[data.avatar_id]
    
    # Contextualización empática con apodo y edad
    respuesta_base = (
        f"{avatar_info['disparadores'][0]} "
        f"Hola {current_user.apodo}, te escucho desde la serenidad. Recuerda que no tienes que resolverlo todo hoy."
    )

    return {
        "status": "success",
        "avatar_nombre": avatar_info["nombre"],
        "respuesta": respuesta_base,
        "chats_restantes": max(0, limite_texto - current_user.chats_usados_semana),
        "audios_restantes": max(0, limite_audio_cant - current_user.audios_usados_semana)
    }

# --- ENDPOINTS: COMUNIDAD Y MURO ---
@app.get("/api/muro", summary="Lectura del Muro de Desahogo")
async def obtener_muro(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(MuroPostModel).options(selectinload(MuroPostModel.autor)).order_by(MuroPostModel.created_at.desc()).limit(50)
    
    # Filtro de visibilidad por plan según Roadmap
    if current_user.plan_nivel == "gratis":
        query = query.where(MuroPostModel.plan_origen == "gratis")
    elif current_user.plan_nivel == "comunicador":
        query = query.where(MuroPostModel.plan_origen.in_(["gratis", "comunicador"]))

    result = await db.execute(query)
    posts = result.scalars().all()

    return {
        "status": "success",
        "posts": [
            {
                "id": p.id,
                "contenido": p.contenido,
                "autor": "Anónimo" if p.is_anonimo else p.autor.apodo,
                "fecha": p.created_at.isoformat()
            }
            for p in posts
        ]
    }

@app.post("/api/muro", status_code=status.HTTP_201_CREATED, summary="Publicar en el Muro")
async def crear_muro_post(data: MuroPostCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan_nivel == "gratis":
        raise HTTPException(status_code=403, detail="El Plan Gratis solo permite lectura y reacciones. Actualiza tu plan para publicar comentarios.")

    nuevo_post = MuroPostModel(
        user_id=current_user.id,
        plan_origen=current_user.plan_nivel,
        contenido=data.contenido,
        is_anonimo=data.is_anonimo
    )
    db.add(nuevo_post)
    await db.commit()
    return {"status": "success", "message": "Mensaje publicado en el Muro de Desahogo."}

# --- ENDPOINTS: SOPORTE Y SUGERENCIAS ---
@app.post("/api/buzon/ticket", summary="Enviar consulta al Administrador")
async def enviar_ticket_soporte(data: BuzonCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    nuevo_ticket = BuzonModel(
        user_id=current_user.id,
        categoria=data.categoria,
        asunto=data.asunto,
        mensaje=data.mensaje
    )
    db.add(nuevo_ticket)
    await db.commit()
    return {"status": "success", "message": "Ticket recibido. El administrador responderá a la brevedad."}

@app.get("/api/buzon/mis-tickets", summary="Historial de tickets del usuario")
async def mis_tickets(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BuzonModel).where(BuzonModel.user_id == current_user.id).order_by(BuzonModel.created_at.desc()))
    tickets = result.scalars().all()
    return {"status": "success", "tickets": tickets}

# --- ENDPOINTS: CUPONES Y ADMINISTRADOR ---
@app.post("/api/admin/cupones", summary="Generar cupón de acceso (Solo Admin)")
async def generar_cupon(data: CouponCreate, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    mapeo = {
        "verde": ("comunicador", 3),
        "azul": ("comunicador", 7),
        "rojo": ("amigo_todos", 3),
        "morado": ("amigo_todos", 7)
    }
    if data.tipo.lower() not in mapeo:
        raise HTTPException(status_code=400, detail="Tipo inválido. Opciones: verde, azul, rojo, morado.")

    plan, dias = mapeo[data.tipo.lower()]
    codigo = f"SL-{data.tipo.upper()}-{random.randint(1000, 9999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    nuevo_cupon = CouponModel(codigo=codigo, tipo_plan=plan, duracion_dias=dias, expires_at=expires_at)
    db.add(nuevo_cupon)
    await db.commit()
    return {"status": "success", "codigo": codigo, "tipo_plan": plan, "duracion_dias": dias, "validez_minutos": 30}

@app.post("/api/cupones/canjear", summary="Canjear cupón")
async def canjear_cupon(data: CouponRedeem, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CouponModel).where(CouponModel.codigo == data.codigo.strip()))
    cupon = result.scalar_one_or_none()

    if not cupon or cupon.is_used:
        raise HTTPException(status_code=400, detail="Cupón inexistente o previamente utilizado.")

    # Comparación segura de fechas UTC
    now_utc = datetime.now(timezone.utc)
    exp_utc = cupon.expires_at if cupon.expires_at.tzinfo else cupon.expires_at.replace(tzinfo=timezone.utc)
    if now_utc > exp_utc:
        raise HTTPException(status_code=400, detail="El cupón ha expirado (límite de 30 minutos excedido).")

    current_user.plan_nivel = cupon.tipo_plan
    current_user.suscripcion_expira = now_utc + timedelta(days=cupon.duracion_dias)
    cupon.is_used = True
    await db.commit()

    return {"status": "success", "message": f"¡Cupón canjeado con éxito! Ahora disfrutas del Plan {cupon.tipo_plan.title()}."}

@app.get("/api/admin/usuarios", summary="Auditoría de usuarios y métricas activas (Solo Admin)")
async def auditar_usuarios(admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).order_by(UserModel.created_at.desc()))
    usuarios = result.scalars().all()
    
    total_usuarios = len(usuarios)
    hace_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    registros_24h = sum(1 for u in usuarios if (u.created_at if u.created_at.tzinfo else u.created_at.replace(tzinfo=timezone.utc)) >= hace_24h)
    
    return {
        "status": "success",
        "metricas": {
            "total_registrados": total_usuarios,
            "registros_ultimas_24h": registros_24h
        },
        "usuarios": [
            {
                "id": u.id,
                "apodo": u.apodo,
                "correo": u.correo,
                "plan": u.plan_nivel,
                "rol": u.role,
                "codigo_referido": u.codigo_referido,
                "chats_semana": u.chats_usados_semana,
                "ultimo_acceso": u.last_active_at.isoformat()
            }
            for u in usuarios
        ]
    }
