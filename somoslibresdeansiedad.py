import json
import os
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from urllib.parse import quote

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import bcrypt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

# Base de Datos Asíncrona
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./somos_libres.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SECRET_KEY = os.getenv("SECRET_KEY", "somos-libres-seguridad-produccion-2026-clave-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

security = HTTPBearer()

app = FastAPI(
    title="Somos Libres de Ansiedad Core API",
    version="3.6.1",
    description="Backend oficial optimizado con persistencia robusta, JWT, motor conversacional orgánico y comunidad."
)

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(120))
    apodo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    edad: Mapped[int] = mapped_column(Integer)
    plan_nivel: Mapped[str] = mapped_column(String(30), default="gratis")
    role: Mapped[str] = mapped_column(String(20), default="user")
    chats_usados_semana: Mapped[int] = mapped_column(Integer, default=0)
    suscripcion_expira: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_stealth: Mapped[bool] = mapped_column(Boolean, default=False)
    posts = relationship("MuroPostModel", back_populates="autor", cascade="all, delete-orphan")
    sugerencias = relationship("BuzonModel", back_populates="autor", cascade="all, delete-orphan")

class CouponModel(Base):
    __tablename__ = "cupones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    tipo_plan: Mapped[str] = mapped_column(String(30))
    duracion_dias: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

class MuroPostModel(Base):
    __tablename__ = "muro_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    contenido: Mapped[str] = mapped_column(String(1000))
    is_anonimo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    autor = relationship("UserModel", back_populates="posts")

class BuzonModel(Base):
    __tablename__ = "buzon_mensajes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    mensaje: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    autor = relationship("UserModel", back_populates="sugerencias")

async def get_db():
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Esquemas Pydantic
class UserRegister(BaseModel):
    nombre_completo: str
    apodo: str
    correo: EmailStr
    password: str = Field(..., min_length=6)
    edad: int
    codigo_referido: Optional[str] = None
    terms_accepted: bool
    disclaimer_accepted: bool

class UserLogin(BaseModel):
    correo: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    plan_actual: str
    role: str
    pensamiento_dia: str

class CouponCreate(BaseModel):
    tipo: str = Field(..., description="verde, azul, rojo, morado")

class CouponRedeem(BaseModel):
    codigo: str

class MuroPostCreate(BaseModel):
    contenido: str = Field(..., max_length=1000)
    is_anonimo: bool = False

class BuzonCreate(BaseModel):
    mensaje: str = Field(..., max_length=1000)

class UserMessage(BaseModel):
    message: str
    avatar_id: str

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
    return user

async def get_current_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso exclusivo de administrador.")
    return current_user

# URL canónica de GitHub
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/lacontadoraia-hub/somos-libres-de-ansiedad/main/avatares"

class RAGCatalogEngine:
    def __init__(self):
        self.catalogo_data = {"plataforma": "Somos Libres de Ansiedad", "biblioteca_rag": [], "avatares_oficiales": []}
        self.cargar_catalogo()

    def cargar_catalogo(self):
        ruta = "catalogo_rag_avatares.json"
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    self.catalogo_data = json.load(f)
            except Exception as e:
                print(f"Error cargando catálogo RAG: {e}")

    def obtener_avatar_por_id(self, avatar_id: str):
        for av in self.catalogo_data.get("avatares_oficiales", []):
            if av.get("id_avatar") == avatar_id:
                return av
        return None

rag_engine = RAGCatalogEngine()

PENSAMIENTOS_BIENVENIDA = [
    "Respira hondo, suelta los hombros y tómate tu tiempo. Este es tu espacio seguro.",
    "No tienes que resolver todo hoy; un solo paso a la vez es suficiente.",
    "Tus emociones son válidas. Lo que sientes hoy no define quién serás mañana.",
    "La calma no es la ausencia de caos, sino la paz que construyes en tu interior."
]

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED, summary="Registro de usuario")
async def registrar_usuario(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if not data.terms_accepted or not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Debes aceptar los términos y el descargo médico.")

    result = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    hashed_pw = hash_password(data.password)
    role = "admin" if data.correo == "somos.libredeansiedad@gmail.com" else "user"
    plan = "amigo_todos" if role == "admin" else "gratis"

    nuevo_usuario = UserModel(
        nombre_completo=data.nombre_completo,
        apodo=data.apodo,
        correo=data.correo,
        password_hash=hashed_pw,
        edad=data.edad,
        plan_nivel=plan,
        role=role
    )
    db.add(nuevo_usuario)
    await db.commit()
    return {"status": "success", "message": f"¡Bienvenido/a {data.apodo}! Registro completado."}

@app.post("/api/auth/login", response_model=TokenResponse, summary="Acceso de usuarios")
async def acceder_usuario(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas.")

    access_token = create_access_token(data={"sub": user.correo, "role": user.role})
    pensamiento = random.choice(PENSAMIENTOS_BIENVENIDA)
    return TokenResponse(access_token=access_token, plan_actual=user.plan_nivel, role=user.role, pensamiento_dia=pensamiento)

@app.get("/api/avatares/catalogo", summary="Obtener lista de avatares")
async def obtener_avatares(current_user: UserModel = Depends(get_current_user)):
    catalogo = []
    for av in rag_engine.catalogo_data.get("avatares_oficiales", []):
        nombre_foto = av.get("archivos", {}).get("imagen", "")
        foto_encoded = quote(nombre_foto)
        catalogo.append({
            "avatar_id": av.get("id_avatar"),
            "nombre": av.get("identidad", {}).get("nombre_completo"),
            "edad": av.get("identidad", {}).get("edad"),
            "nacionalidad": av.get("identidad", {}).get("pais"),
            "bandera": av.get("identidad", {}).get("bandera"),
            "especialidad": av.get("identidad", {}).get("especialidad"),
            "foto_url": f"{GITHUB_RAW_BASE}/{foto_encoded}",
            "descripcion": av.get("historia_superacion", "")[:250] + "..."
        })
    return {"avatares": catalogo}

@app.post("/api/chat", summary="Chat con Avatar y Motor Conversacional Orgánico")
async def chat_con_avatar(data: UserMessage, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    limites = {"gratis": 25, "comunicador": 100, "amigo_todos": 999999}
    limite_semanal = limites.get(current_user.plan_nivel, 25)

    if current_user.chats_usados_semana >= limite_semanal and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Has alcanzado el límite semanal de tu plan.")

    avatar = rag_engine.obtener_avatar_por_id(data.avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar no encontrado.")

    current_user.chats_usados_semana += 1
    await db.commit()

    nombre = avatar.get("identidad", {}).get("nombre_completo", "Tu guía")
    mensaje_lower = data.message.lower().strip()

    saludos = ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos", "hey", "qué tal", "que tal", "como estas", "cómo estás"]
    if any(s in mensaje_lower for s in saludos):
        respuestas_saludo = [
            f"¡Hola! Muy bien, gracias por preguntar. Qué alegría saludarte. ¿Cómo te sientes en este momento?",
            f"¡Hola! Por aquí todo en calma. Me alegra que me saludes, ¿de qué te gustaría hablar hoy?",
            f"¡Hola! Todo bien por acá. Respira hondo y cuéntame, ¿cómo ha ido tu día?"
        ]
        respuesta = random.choice(respuestas_saludo)
    else:
        respuestas_organicas = [
            f"Te escucho con atención. A veces la mente va muy deprisa, pero recuerda que aquí puedes detenerte un momento.",
            f"Entiendo lo que dices y lo que sientes es muy válido. No tienes que cargar con todo hoy.",
            f"Gracias por abrirte y contarme esto. Respira profundo, vayamos un paso a la vez.",
            f"Es comprensible que te sientas así. Vamos a mirarlo con tranquilidad y sin juicios."
        ]
        respuesta = random.choice(respuestas_organicas)

    chats_restantes = max(0, limite_semanal - current_user.chats_usados_semana)
    return {"status": "success", "response": respuesta, "chats_restantes": chats_restantes}

@app.post("/api/admin/cupones", summary="Generar cupón (Admin)")
async def generar_cupon(data: CouponCreate, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    mapeo = {
        "verde": ("comunicador", 3),
        "azul": ("comunicador", 7),
        "rojo": ("amigo_todos", 3),
        "morado": ("amigo_todos", 7)
    }
    if data.tipo not in mapeo:
        raise HTTPException(status_code=400, detail="Tipo inválido (verde, azul, rojo, morado).")

    plan, dias = mapeo[data.tipo]
    codigo = f"SL-{data.tipo.upper()}-{random.randint(1000, 9999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    nuevo_cupon = CouponModel(codigo=codigo, tipo_plan=plan, duracion_dias=dias, expires_at=expires_at)
    db.add(nuevo_cupon)
    await db.commit()
    return {"status": "success", "codigo": codigo, "tipo_plan": plan, "duracion_dias": dias, "expira_en_minutos": 30}

@app.post("/api/cupones/canjear", summary="Canjear cupón")
async def canjear_cupon(data: CouponRedeem, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CouponModel).where(CouponModel.codigo == data.codigo))
    cupon = result.scalar_one_or_none()

    if not cupon or cupon.is_used:
        raise HTTPException(status_code=400, detail="Cupón inválido o ya utilizado.")

    if datetime.now(timezone.utc) > cupon.expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=400, detail="El cupón ha expirado (validez de 30 min).")

    current_user.plan_nivel = cupon.tipo_plan
    current_user.suscripcion_expira = datetime.now(timezone.utc) + timedelta(days=cupon.duracion_dias)
    cupon.is_used = True
    await db.commit()
    return {"status": "success", "message": f"¡Cupón aplicado! Tu plan ahora es: {cupon.tipo_plan}"}

@app.get("/api/muro", summary="Obtener publicaciones del Muro")
async def obtener_muro(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan_nivel == "gratis":
        raise HTTPException(status_code=403, detail="Tu plan no tiene acceso completo al Muro.")

    query = select(MuroPostModel).options(selectinload(MuroPostModel.autor)).order_by(MuroPostModel.created_at.desc()).limit(50)
    result = await db.execute(query)
    posts = result.scalars().all()

    lista_posts = [
        {
            "id": p.id,
            "contenido": p.contenido,
            "autor": "Anónimo" if p.is_anonimo else p.autor.apodo,
            "fecha": p.created_at.isoformat()
        }
        for p in posts
    ]
    return {"status": "success", "posts": lista_posts}

@app.post("/api/muro", status_code=status.HTTP_201_CREATED, summary="Publicar en el Muro")
async def crear_muro_post(data: MuroPostCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan_nivel == "gratis":
        raise HTTPException(status_code=403, detail="El plan gratis no permite publicar en el Muro.")

    nuevo_post = MuroPostModel(user_id=current_user.id, contenido=data.contenido, is_anonimo=data.is_anonimo)
    db.add(nuevo_post)
    await db.commit()
    return {"status": "success", "message": "Publicación registrada en el Muro."}

@app.post("/api/buzon/mensaje", summary="Enviar sugerencia o reporte")
async def enviar_buzon(data: BuzonCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    nuevo_mensaje = BuzonModel(user_id=current_user.id, mensaje=data.mensaje)
    db.add(nuevo_mensaje)
    await db.commit()
    return {"status": "success", "message": "Mensaje recibido correctamente."}
