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
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./somos_libres.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SECRET_KEY = os.getenv("SECRET_KEY", "somos-libres-seguridad-produccion-2026-clave-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

security = HTTPBearer()

app = FastAPI(title="Somos Libres de Ansiedad Core API", version="4.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    sexo: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    profesion: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    situacion_sentimental: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cantidad_hijos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    biografia: Mapped[Optional[str]] = mapped_column(String(250), default="En camino hacia la serenidad.")
    
    plan_nivel: Mapped[str] = mapped_column(String(30), default="gratis")
    role: Mapped[str] = mapped_column(String(20), default="user")
    codigo_referido: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    referido_por: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    chats_usados_semana: Mapped[int] = mapped_column(Integer, default=0)
    audios_usados_semana: Mapped[int] = mapped_column(Integer, default=0)
    mensajes_directos_hoy: Mapped[int] = mapped_column(Integer, default=0)
    ultimo_dm_fecha: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    avatares_activos: Mapped[str] = mapped_column(String(255), default="[]")
    
    suscripcion_expira: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DirectMessageModel(Base):
    __tablename__ = "mensajes_directos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    remitente_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    destinatario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    contenido: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

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
    autor = relationship("UserModel")

class BuzonModel(Base):
    __tablename__ = "buzon_mensajes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    categoria: Mapped[str] = mapped_column(String(50), default="Consulta general")
    asunto: Mapped[str] = mapped_column(String(150), default="Sin asunto")
    mensaje: Mapped[str] = mapped_column(String(2000))
    respuesta_admin: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    estatus: Mapped[str] = mapped_column(String(30), default="Pendiente")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    autor = relationship("UserModel")

# Carga de catálogo RAG
CATALOGO_CACHE = {}
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

class DirectMessageCreate(BaseModel):
    destinatario_id: int
    contenido: str = Field(..., max_length=1000)

class CouponCreate(BaseModel):
    tipo: str

class CouponRedeem(BaseModel):
    codigo: str

class MuroPostCreate(BaseModel):
    contenido: str = Field(..., max_length=1000)
    is_anonimo: bool = False

class BuzonCreate(BaseModel):
    categoria: str = "Consulta general"
    asunto: str
    mensaje: str = Field(..., max_length=2000)

async def get_db():
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8')[:72], hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> UserModel:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    result = await db.execute(select(UserModel).where(UserModel.correo == correo))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.last_active_at = datetime.now(timezone.utc)
    await db.commit()
    return user

async def get_current_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acceso exclusivo de administrador.")
    return current_user

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

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if not data.terms_accepted or not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Acepta los términos y descargo de responsabilidad.")

    res = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    is_admin = (data.correo.strip().lower() == "somos.libredeansiedad@gmail.com")
    role = "admin" if is_admin else "user"
    plan = "amigo_todos" if is_admin else "gratis"

    while True:
        cod = str(random.randint(1111111, 9999999))
        c_res = await db.execute(select(UserModel).where(UserModel.codigo_referido == cod))
        if not c_res.scalar_one_or_none():
            break

    nuevo = UserModel(
        nombre_completo=data.nombre_completo,
        apodo=data.apodo,
        correo=data.correo,
        password_hash=hash_password(data.password),
        edad=data.edad,
        sexo=data.sexo,
        profesion=data.profesion,
        situacion_sentimental=data.situacion_sentimental,
        cantidad_hijos=data.cantidad_hijos,
        plan_nivel=plan,
        role=role,
        codigo_referido=cod,
        referido_por=data.codigo_referido
    )
    db.add(nuevo)
    await db.commit()
    return {"status": "success", "message": f"¡Bienvenido/a {data.apodo}!", "codigo_referido": cod}

@app.post("/api/auth/login", response_model=TokenResponse)
async def acceder_usuario(data: UserLogin, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    user = res.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    token = create_access_token({"sub": user.correo, "role": user.role})
    return TokenResponse(
        access_token=token,
        apodo=user.apodo,
        plan_actual=user.plan_nivel,
        role=user.role,
        codigo_referido=user.codigo_referido,
        pensamiento_dia=random.choice(PENSAMIENTOS_BIENVENIDA)
    )

@app.get("/api/avatares/catalogo")
async def obtener_avatares(current_user: UserModel = Depends(get_current_user)):
    activos = json.loads(current_user.avatares_activos)
    catalogo = []
    for k, v in CATALOGO_CACHE.items():
        catalogo.append({
            "id": k,
            "nombre": v["identidad"]["nombre_completo"],
            "pais": v["identidad"]["pais"],
            "bandera": v["identidad"]["bandera"],
            "tono": v["tono_linguistico"],
            "imagen": v["archivos"]["imagen"],
            "is_activo": k in activos,
            "disparador_inicial": random.choice(v.get("frases_bienvenida", ["Hola, aquí estoy para ti."]))
        })
    return {"status": "success", "avatares": catalogo}

@app.post("/api/avatares/seleccionar")
async def seleccionar_avatar(data: AvatarSelectRequest, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.avatar_id not in CATALOGO_CACHE:
        raise HTTPException(status_code=404, detail="Avatar no encontrado.")

    activos = json.loads(current_user.avatares_activos)
    max_permitidos = {"gratis": 1, "comunicador": 3, "amigo_todos": 10}.get(current_user.plan_nivel, 1)

    if data.avatar_id in activos:
        return {"status": "success", "message": "Avatar ya seleccionado.", "activos": activos}

    if len(activos) >= max_permitidos and current_user.role != "admin":
        raise HTTPException(status_code=403, detail=f"Tu plan solo permite {max_permitidos} avatar(es) activo(s).")

    activos.append(data.avatar_id)
    current_user.avatares_activos = json.dumps(activos)
    await db.commit()
    return {"status": "success", "message": "Avatar vinculado correctamente.", "activos": activos}

@app.post("/api/chat")
async def chat_con_avatar(data: UserMessage, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.avatar_id not in CATALOGO_CACHE:
        raise HTTPException(status_code=404, detail="Avatar no encontrado.")

    limite_texto = {"gratis": 25, "comunicador": 100, "amigo_todos": 999999}.get(current_user.plan_nivel, 25)
    limite_audio = {"gratis": 3, "comunicador": 10, "amigo_todos": 999999}.get(current_user.plan_nivel, 3)
    max_seg_audio = {"gratis": 10, "comunicador": 30, "amigo_todos": 60}.get(current_user.plan_nivel, 10)

    if current_user.chats_usados_semana >= limite_texto and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Límite de mensajes alcanzado.")

    if data.is_audio:
        if current_user.audios_usados_semana >= limite_audio and current_user.role != "admin":
            raise HTTPException(status_code=403, detail=f"Límite de {limite_audio} audios alcanzado.")
        if data.audio_duracion_segundos > max_seg_audio and current_user.role != "admin":
            raise HTTPException(status_code=400, detail=f"Audio excede {max_seg_audio}s.")
        current_user.audios_usados_semana += 1

    current_user.chats_usados_semana += 1
    await db.commit()

    avatar_info = CATALOGO_CACHE[data.avatar_id]
    user_msg = data.message.lower().strip()

    # Selección dinámica de respuesta terapéutica
    consejos_afines = []
    for libro in LIBROS_CACHE:
        if libro.get("id_libro") in avatar_info.get("libros_rag_afines", []):
            consejos_afines.append(libro.get("consejo_aplicable"))

    consejo = random.choice(consejos_afines) if consejos_afines else "Da un paso a la vez; la calma se construye momento a momento."

    if any(saludo in user_msg for saludo in ["hola", "buenas", "buenos dias", "que tal", "epa"]):
        respuesta = f"¡Hola {current_user.apodo}! Qué alegría encontrarte. Cuéntame con tranquilidad qué tienes en mente hoy."
    elif any(duda in user_msg for duda in ["nombre", "quien soy", "sabes mi"]):
        respuesta = f"Claro que sí, eres {current_user.apodo}. Estoy aquí para acompañarte paso a paso."
    elif any(mal in user_msg for mal in ["mal", "ansiedad", "miedo", "triste", "panico", "ayuda", "cansado"]):
        respuesta = f"{current_user.apodo}, entiendo lo que estás experimentando. Respira hondo y suelta los hombros. {consejo}"
    else:
        respuesta = f"Te escucho atentamente, {current_user.apodo}. {consejo} ¿Qué sientes en este momento?"

    return {
        "status": "success",
        "avatar_nombre": avatar_info["identidad"]["nombre_completo"],
        "respuesta": respuesta,
        "chats_restantes": max(0, limite_texto - current_user.chats_usados_semana),
        "audios_restantes": max(0, limite_audio - current_user.audios_usados_semana)
    }

# --- COMUNIDAD Y PERFILES SOCIALES ---
@app.get("/api/comunidad/perfiles")
async def listar_perfiles(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserModel).where(UserModel.id != current_user.id).limit(20))
    usuarios = res.scalars().all()
    return {
        "status": "success",
        "perfiles": [
            {"id": u.id, "apodo": u.apodo, "edad": u.edad, "profesion": u.profesion or "Miembro", "biografia": u.biografia}
            for u in usuarios
        ]
    }

@app.post("/api/comunidad/dm")
async def enviar_dm(data: DirectMessageCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    max_dms = {"gratis": 1, "comunicador": 5, "amigo_todos": 999999}.get(current_user.plan_nivel, 1)
    
    hoy = datetime.now(timezone.utc).date()
    if current_user.ultimo_dm_fecha and current_user.ultimo_dm_fecha.date() != hoy:
        current_user.mensajes_directos_hoy = 0

    if current_user.mensajes_directos_hoy >= max_dms and current_user.role != "admin":
        raise HTTPException(status_code=403, detail=f"Has alcanzado el límite de {max_dms} mensaje(s) directo(s) diario(s).")

    nuevo_dm = DirectMessageModel(
        remitente_id=current_user.id,
        destinatario_id=data.destinatario_id,
        contenido=data.contenido
    )
    current_user.mensajes_directos_hoy += 1
    current_user.ultimo_dm_fecha = datetime.now(timezone.utc)
    db.add(nuevo_dm)
    await db.commit()
    return {"status": "success", "message": "Mensaje directo enviado."}

@app.get("/api/comunidad/mis-dms")
async def ver_mis_dms(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DirectMessageModel).where(DirectMessageModel.destinatario_id == current_user.id).order_by(DirectMessageModel.created_at.desc()))
    mensajes = res.scalars().all()
    return {"status": "success", "mensajes": mensajes}

# --- MURO, BUZÓN Y CUPONES ---
@app.get("/api/muro")
async def obtener_muro(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(MuroPostModel).options(selectinload(MuroPostModel.autor)).order_by(MuroPostModel.created_at.desc()).limit(50)
    if current_user.plan_nivel == "gratis":
        query = query.where(MuroPostModel.plan_origen == "gratis")
    elif current_user.plan_nivel == "comunicador":
        query = query.where(MuroPostModel.plan_origen.in_(["gratis", "comunicador"]))
    res = await db.execute(query)
    posts = res.scalars().all()
    return {
        "status": "success",
        "posts": [{"id": p.id, "contenido": p.contenido, "autor": "Anónimo" if p.is_anonimo else p.autor.apodo, "fecha": p.created_at.isoformat()} for p in posts]
    }

@app.post("/api/muro", status_code=201)
async def crear_muro_post(data: MuroPostCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan_nivel == "gratis":
        raise HTTPException(status_code=403, detail="Tu plan solo permite lectura en el muro.")
    nuevo = MuroPostModel(user_id=current_user.id, plan_origen=current_user.plan_nivel, contenido=data.contenido, is_anonimo=data.is_anonimo)
    db.add(nuevo)
    await db.commit()
    return {"status": "success", "message": "Publicado con éxito."}

@app.post("/api/buzon/ticket")
async def enviar_ticket(data: BuzonCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ticket = BuzonModel(user_id=current_user.id, categoria=data.categoria, asunto=data.asunto, mensaje=data.mensaje)
    db.add(ticket)
    await db.commit()
    return {"status": "success", "message": "Ticket registrado."}

@app.get("/api/buzon/mis-tickets")
async def mis_tickets(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BuzonModel).where(BuzonModel.user_id == current_user.id).order_by(BuzonModel.created_at.desc()))
    return {"status": "success", "tickets": res.scalars().all()}

@app.post("/api/admin/cupones")
async def generar_cupon(data: CouponCreate, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    mapeo = {"verde": ("comunicador", 3), "azul": ("comunicador", 7), "rojo": ("amigo_todos", 3), "morado": ("amigo_todos", 7)}
    if data.tipo.lower() not in mapeo:
        raise HTTPException(status_code=400, detail="Tipo inválido (verde, azul, rojo, morado).")
    plan, dias = mapeo[data.tipo.lower()]
    codigo = f"SL-{data.tipo.upper()}-{random.randint(1000, 9999)}"
    cupon = CouponModel(codigo=codigo, tipo_plan=plan, duracion_dias=dias, expires_at=datetime.now(timezone.utc) + timedelta(minutes=30))
    db.add(cupon)
    await db.commit()
    return {"status": "success", "codigo": codigo, "tipo_plan": plan, "duracion_dias": dias, "validez_minutos": 30}

@app.post("/api/cupones/canjear")
async def canjear_cupon(data: CouponRedeem, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CouponModel).where(CouponModel.codigo == data.codigo.strip()))
    cupon = res.scalar_one_or_none()
    if not cupon or cupon.is_used:
        raise HTTPException(status_code=400, detail="Cupón inexistente o previamente utilizado.")
    
    exp = cupon.expires_at if cupon.expires_at.tzinfo else cupon.expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        raise HTTPException(status_code=400, detail="El cupón ha expirado.")

    current_user.plan_nivel = cupon.tipo_plan
    current_user.suscripcion_expira = datetime.now(timezone.utc) + timedelta(days=cupon.duracion_dias)
    cupon.is_used = True
    await db.commit()
    return {"status": "success", "message": f"Cupón canjeado: Plan {cupon.tipo_plan.title()}."}

@app.get("/api/admin/usuarios")
async def auditar_usuarios(admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserModel).order_by(UserModel.created_at.desc()))
    usuarios = res.scalars().all()
    hace_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    reg_24h = sum(1 for u in usuarios if (u.created_at if u.created_at.tzinfo else u.created_at.replace(tzinfo=timezone.utc)) >= hace_24h)
    return {
        "status": "success",
        "metricas": {"total_registrados": len(usuarios), "registros_ultimas_24h": reg_24h},
        "usuarios": [{"id": u.id, "apodo": u.apodo, "correo": u.correo, "plan": u.plan_nivel, "rol": u.role, "codigo_referido": u.codigo_referido, "chats_semana": u.chats_usados_semana} for u in usuarios]
    }
