import json
import os
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
import bcrypt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, select, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

# Delegación al motor cognitivo de Rafael
from cerebro_avatares import (
    obtener_catalogo_formateado,
    existe_avatar,
    procesar_respuesta_avatar
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./somos_libres.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SECRET_KEY = os.getenv("SECRET_KEY", "somos-libres-seguridad-produccion-2026-clave-jwt")
CRON_SECRET_KEY = os.getenv("CRON_SECRET_KEY", "somos-libres-cron-mantenimiento-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

security = HTTPBearer()

app = FastAPI(title="Somos Libres de Ansiedad Core API", version="4.6.2")

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
    biografia: Mapped[Optional[str]] = mapped_column(String(2000), default="En camino hacia la serenidad.")
    foto_perfil: Mapped[Optional[str]] = mapped_column(String(100000), nullable=True)
    
    plan_nivel: Mapped[str] = mapped_column(String(30), default="gratis")
    role: Mapped[str] = mapped_column(String(20), default="user")
    codigo_referido: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    referido_por: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    chats_usados_semana: Mapped[int] = mapped_column(Integer, default=0)
    mensajes_directos_hoy: Mapped[int] = mapped_column(Integer, default=0)
    ultimo_dm_fecha: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    avatares_activos: Mapped[str] = mapped_column(String(255), default="[]")
    
    suscripcion_expira: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class FriendshipModel(Base):
    __tablename__ = "amistades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    solicitante_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    receptor_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    estatus: Mapped[str] = mapped_column(String(20), default="pendiente")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DirectMessageModel(Base):
    __tablename__ = "mensajes_directos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    remitente_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    destinatario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    contenido: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PaymentChatMessageModel(Base):
    __tablename__ = "mensajes_conciliacion_pago"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    emisor_rol: Mapped[str] = mapped_column(String(20))
    plan_solicitado: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metodo_pago: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    monto_referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mensaje: Mapped[str] = mapped_column(String(2000))
    comprobante_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
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
    categoria_emocional: Mapped[str] = mapped_column(String(40), default="ansiedad_cotidiana")
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

class UserRegister(BaseModel):
    nombre_completo: str
    apodo: str
    correo: EmailStr
    password: str = Field(..., min_length=5)
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
    pregunta_secreta: Optional[str] = None

class ProfileUpdate(BaseModel):
    profesion: Optional[str] = None
    situacion_sentimental: Optional[str] = None
    cantidad_hijos: Optional[int] = None
    biografia: Optional[str] = Field(None, max_length=2000)
    foto_perfil: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    apodo: str
    plan_actual: str
    role: str
    codigo_referido: str
    pensamiento_dia: str

class AvatarSelectRequest(BaseModel):
    avatar_id: str

# Entrada de mensaje enriquecida con historial previo
class UserMessage(BaseModel):
    avatar_id: str
    message: str
    historial_previo: Optional[List[str]] = None

class DirectMessageCreate(BaseModel):
    destinatario_id: int
    contenido: str = Field(..., max_length=1000)

class FriendshipRequest(BaseModel):
    usuario_id: int

class PaymentMessageCreate(BaseModel):
    mensaje: str = Field(..., max_length=2000)
    plan_solicitado: Optional[str] = None
    metodo_pago: Optional[str] = None
    monto_referencia: Optional[str] = None
    comprobante_url: Optional[str] = None
    para_usuario_id: Optional[int] = None

class CouponCreate(BaseModel):
    tipo: str

class CouponRedeem(BaseModel):
    codigo: str

class RewardAffiliateCreate(BaseModel):
    usuario_id: int
    tipo_premio: str

class MuroPostCreate(BaseModel):
    contenido: str = Field(..., max_length=1000)
    categoria_emocional: str = "ansiedad_cotidiana"
    is_anonimo: bool = False

class BuzonCreate(BaseModel):
    categoria: str = "Consulta general"
    asunto: str
    mensaje: str = Field(..., max_length=2000)

async def get_db():
    async with async_session() as session:
        yield session

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

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        res = await db.execute(select(UserModel).where(UserModel.correo == "somos.libredeansiedad@gmail.com"))
        admin_user = res.scalar_one_or_none()
        if not admin_user:
            admin_nuevo = UserModel(
                nombre_completo="Juan Carlos Lee",
                apodo="Admin Juan Carlos",
                correo="somos.libredeansiedad@gmail.com",
                password_hash=hash_password("Admin"),
                edad=35,
                plan_nivel="amigo_todos",
                role="admin",
                codigo_referido="0000000",
                biografia="Fundador y Administrador General de Somos Libres de Ansiedad."
            )
            db.add(admin_nuevo)
            await db.commit()

PENSAMIENTOS_BIENVENIDA = [
    "Respira hondo, suelta los hombros y tómate tu tiempo. Este es tu espacio seguro.",
    "No tienes que resolver todo hoy; un solo paso a la vez es suficiente.",
    "Tus emociones son válidas. Lo que sientes hoy no define quién serás mañana.",
    "La calma no es la ausencia de caos, sino la paz que construyes en tu interior.",
    "Está bien hacer una pausa. El descanso también es parte del camino."
]

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if not data.terms_accepted or not data.disclaimer_accepted:
        raise HTTPException(status_code=400, detail="Acepta los términos y el descargo de responsabilidad médica.")

    if data.correo.strip().lower() == "somos.libredeansiedad@gmail.com":
        raise HTTPException(status_code=400, detail="Esta cuenta maestra ya existe en el sistema.")

    res = await db.execute(select(UserModel).where(UserModel.correo == data.correo))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

    while True:
        cod = str(random.randint(1111111, 9999999))
        c_res = await db.execute(select(UserModel).where(UserModel.codigo_referido == cod))
        if not c_res.scalar_one_or_none():
            break

    plan_inicial = "gratis"
    expira_inicial = None
    cod_ref = data.codigo_referido.strip() if data.codigo_referido else None
    
    if cod_ref:
        res_patrocinador = await db.execute(select(UserModel).where(UserModel.codigo_referido == cod_ref))
        if res_patrocinador.scalar_one_or_none():
            plan_inicial = "amigo_todos"
            expira_inicial = datetime.now(timezone.utc) + timedelta(days=1)

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
        plan_nivel=plan_inicial,
        suscripcion_expira=expira_inicial,
        role="user",
        codigo_referido=cod,
        referido_por=cod_ref
    )
    db.add(nuevo)
    await db.commit()
    msg = f"¡Bienvenido/a {data.apodo}! Has recibido 1 día de cortesía en el Plan Amigo de Todos." if plan_inicial == "amigo_todos" else f"¡Bienvenido/a {data.apodo}!"
    return {"status": "success", "message": msg, "codigo_referido": cod}

@app.post("/api/auth/login", response_model=TokenResponse)
async def acceder_usuario(data: UserLogin, db: AsyncSession = Depends(get_db)):
    correo_limpio = data.correo.strip().lower()
    res = await db.execute(select(UserModel).where(UserModel.correo == correo_limpio))
    user = res.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    if correo_limpio == "somos.libredeansiedad@gmail.com":
        if not data.pregunta_secreta or data.pregunta_secreta.strip().capitalize() != "Sombra":
            raise HTTPException(status_code=403, detail="Respuesta de confirmación incorrecta para la cuenta administradora.")

    if user.suscripcion_expira:
        exp = user.suscripcion_expira if user.suscripcion_expira.tzinfo else user.suscripcion_expira.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > exp and user.role != "admin":
            user.plan_nivel = "gratis"
            user.suscripcion_expira = None
            await db.commit()

    token = create_access_token({"sub": user.correo, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        apodo=user.apodo,
        plan_actual=user.plan_nivel,
        role=user.role,
        codigo_referido=user.codigo_referido,
        pensamiento_dia=random.choice(PENSAMIENTOS_BIENVENIDA)
    )

@app.get("/api/usuario/mi-perfil")
async def obtener_mi_perfil(current_user: UserModel = Depends(get_current_user)):
    return {
        "status": "success",
        "perfil": {
            "id": current_user.id,
            "nombre_completo": current_user.nombre_completo,
            "apodo": current_user.apodo,
            "correo": current_user.correo,
            "edad": current_user.edad,
            "sexo": current_user.sexo,
            "profesion": current_user.profesion,
            "situacion_sentimental": current_user.situacion_sentimental,
            "cantidad_hijos": current_user.cantidad_hijos,
            "biografia": current_user.biografia,
            "foto_perfil": current_user.foto_perfil,
            "plan_nivel": current_user.plan_nivel,
            "codigo_referido": current_user.codigo_referido
        }
    }

@app.put("/api/usuario/mi-perfil")
async def actualizar_mi_perfil(data: ProfileUpdate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.profesion is not None:
        current_user.profesion = data.profesion
    if data.situacion_sentimental is not None:
        current_user.situacion_sentimental = data.situacion_sentimental
    if data.cantidad_hijos is not None:
        current_user.cantidad_hijos = data.cantidad_hijos
    if data.biografia is not None:
        current_user.biografia = data.biografia
    if data.foto_perfil is not None:
        current_user.foto_perfil = data.foto_perfil
    await db.commit()
    return {"status": "success", "message": "Perfil actualizado correctamente."}

@app.get("/api/comunidad/perfiles")
async def listar_perfiles_comunidad(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(UserModel).where(
            and_(UserModel.id != current_user.id, UserModel.role != "admin")
        ).limit(40)
    )
    usuarios = res.scalars().all()

    amistades_res = await db.execute(
        select(FriendshipModel).where(
            or_(
                FriendshipModel.solicitante_id == current_user.id,
                FriendshipModel.receptor_id == current_user.id
            )
        )
    )
    amistades = amistades_res.scalars().all()
    estado_amigos = {}
    for a in amistades:
        otro = a.receptor_id if a.solicitante_id == current_user.id else a.solicitante_id
        estado_amigos[otro] = (a.id, a.estatus, a.solicitante_id == current_user.id)

    lista = []
    for u in usuarios:
        info_amistad = estado_amigos.get(u.id, (None, "ninguna", False))
        
        if current_user.plan_nivel == "gratis" and u.plan_nivel != "gratis":
            apodo_vis = "Miembro en Serenidad (Incógnito)"
            prof_vis = "Miembro Privado"
            bio_vis = "Perfil reservado para miembros de planes superiores."
            foto_vis = None
        else:
            apodo_vis = u.apodo
            prof_vis = u.profesion or "Miembro"
            bio_vis = u.biografia
            foto_vis = u.foto_perfil

        lista.append({
            "id": u.id,
            "apodo": apodo_vis,
            "edad": u.edad if current_user.plan_nivel != "gratis" or u.plan_nivel == "gratis" else "--",
            "sexo": u.sexo or "No especificado",
            "profesion": prof_vis,
            "situacion_sentimental": u.situacion_sentimental or "No especificado",
            "biografia": bio_vis,
            "foto_perfil": foto_vis,
            "amistad_id": info_amistad[0],
            "amistad_estatus": info_amistad[1],
            "soy_solicitante": info_amistad[2],
            "es_incognito": current_user.plan_nivel == "gratis" and u.plan_nivel != "gratis"
        })
    return {"status": "success", "perfiles": lista}

@app.post("/api/comunidad/amistad/solicitar")
async def enviar_solicitud_amistad(data: FriendshipRequest, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan_nivel == "gratis" and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="No puedes enviar solicitudes de amistad en el Plan Gratis. Actualiza a Plan Comunicador para conectar con la comunidad."
        )

    if data.usuario_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes enviarte una solicitud a ti mismo.")

    check = await db.execute(
        select(FriendshipModel).where(
            or_(
                and_(FriendshipModel.solicitante_id == current_user.id, FriendshipModel.receptor_id == data.usuario_id),
                and_(FriendshipModel.solicitante_id == data.usuario_id, FriendshipModel.receptor_id == current_user.id)
            )
        )
    )
    if check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe una relación o solicitud en curso.")

    nueva = FriendshipModel(solicitante_id=current_user.id, receptor_id=data.usuario_id, estatus="pendiente")
    db.add(nueva)
    await db.commit()
    return {"status": "success", "message": "Solicitud de amistad enviada con éxito."}

@app.post("/api/comunidad/amistad/{amistad_id}/responder")
async def responder_amistad(amistad_id: int, aceptar: bool, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(FriendshipModel).where(FriendshipModel.id == amistad_id, FriendshipModel.receptor_id == current_user.id))
    solicitud = res.scalar_one_or_none()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")

    solicitud.estatus = "aceptada" if aceptar else "rechazada"
    await db.commit()
    return {"status": "success", "message": f"Solicitud {'aceptada' if aceptar else 'rechazada'}."}

@app.post("/api/comunidad/dm")
async def enviar_dm(data: DirectMessageCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    son_amigos_res = await db.execute(
        select(FriendshipModel).where(
            or_(
                and_(FriendshipModel.solicitante_id == current_user.id, FriendshipModel.receptor_id == data.destinatario_id),
                and_(FriendshipModel.solicitante_id == data.destinatario_id, FriendshipModel.receptor_id == current_user.id)
            ),
            FriendshipModel.estatus == "aceptada"
        )
    )
    son_amigos = son_amigos_res.scalar_one_or_none() is not None

    if not son_amigos and current_user.role != "admin":
        max_dms = {"gratis": 1, "comunicador": 5, "amigo_todos": 999999}.get(current_user.plan_nivel, 1)
        hoy = datetime.now(timezone.utc).date()
        if current_user.ultimo_dm_fecha and current_user.ultimo_dm_fecha.date() != hoy:
            current_user.mensajes_directos_hoy = 0

        if current_user.mensajes_directos_hoy >= max_dms:
            raise HTTPException(status_code=403, detail=f"Límite de {max_dms} mensaje(s) diario(s) alcanzado. ¡Sé amigo de este usuario para chatear sin límites!")

        current_user.mensajes_directos_hoy += 1
        current_user.ultimo_dm_fecha = datetime.now(timezone.utc)

    nuevo_dm = DirectMessageModel(
        remitente_id=current_user.id,
        destinatario_id=data.destinatario_id,
        contenido=data.contenido
    )
    db.add(nuevo_dm)
    await db.commit()
    return {"status": "success", "message": "Mensaje enviado."}

@app.get("/api/comunidad/conversacion/{otro_usuario_id}")
async def ver_conversacion(otro_usuario_id: int, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(DirectMessageModel).where(
            or_(
                and_(DirectMessageModel.remitente_id == current_user.id, DirectMessageModel.destinatario_id == otro_usuario_id),
                and_(DirectMessageModel.remitente_id == otro_usuario_id, DirectMessageModel.destinatario_id == current_user.id)
            )
        ).order_by(DirectMessageModel.created_at.asc())
    )
    return {"status": "success", "mensajes": res.scalars().all()}

# --- CONCILIACIÓN DE PAGOS ---
@app.get("/api/pagos/mis-mensajes")
async def obtener_chat_pago_usuario(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(PaymentChatMessageModel).where(PaymentChatMessageModel.user_id == current_user.id).order_by(PaymentChatMessageModel.created_at.asc())
    )
    return {"status": "success", "mensajes": res.scalars().all()}

@app.post("/api/pagos/enviar-mensaje")
async def enviar_mensaje_pago_usuario(data: PaymentMessageCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    nuevo = PaymentChatMessageModel(
        user_id=current_user.id,
        emisor_rol="user",
        plan_solicitado=data.plan_solicitado,
        metodo_pago=data.metodo_pago,
        monto_referencia=data.monto_referencia,
        mensaje=data.mensaje,
        comprobante_url=data.comprobante_url
    )
    db.add(nuevo)
    await db.commit()
    return {"status": "success", "message": "Reporte de conciliación enviado al Administrador."}

@app.get("/api/admin/pagos/conversaciones")
async def listar_conversaciones_pago_admin(admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    subq = select(PaymentChatMessageModel.user_id).distinct()
    res = await db.execute(subq)
    user_ids = res.scalars().all()
    
    res_users = await db.execute(select(UserModel).where(UserModel.id.in_(user_ids)))
    usuarios = res_users.scalars().all()
    return {"status": "success", "usuarios_con_pago": [{"id": u.id, "apodo": u.apodo, "correo": u.correo, "plan": u.plan_nivel} for u in usuarios]}

@app.get("/api/admin/pagos/usuario/{user_id}")
async def ver_chat_pago_admin(user_id: int, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(PaymentChatMessageModel).where(PaymentChatMessageModel.user_id == user_id).order_by(PaymentChatMessageModel.created_at.asc())
    )
    return {"status": "success", "mensajes": res.scalars().all()}

@app.post("/api/admin/pagos/responder")
async def responder_pago_admin(data: PaymentMessageCreate, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    if not data.para_usuario_id:
        raise HTTPException(status_code=400, detail="Debes indicar el ID del usuario.")
    
    nuevo = PaymentChatMessageModel(
        user_id=data.para_usuario_id,
        emisor_rol="admin",
        mensaje=data.mensaje
    )
    db.add(nuevo)
    await db.commit()
    return {"status": "success", "message": "Respuesta de pago enviada."}

# --- CATÁLOGO Y CHAT DELEGADO AL CEREBRO MODULAR DE RAFAEL ---
@app.get("/api/avatares/catalogo")
async def obtener_avatares(current_user: UserModel = Depends(get_current_user)):
    activos = json.loads(current_user.avatares_activos)
    limite_texto = {"gratis": 25, "comunicador": 100, "amigo_todos": 999999}.get(current_user.plan_nivel, 25)
    catalogo = obtener_catalogo_formateado(activos)
    return {
        "status": "success", 
        "avatares": catalogo,
        "chats_restantes": max(0, limite_texto - current_user.chats_usados_semana),
        "total_chats_plan": limite_texto
    }

@app.post("/api/avatares/seleccionar")
async def seleccionar_avatar(data: AvatarSelectRequest, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not existe_avatar(data.avatar_id):
        raise HTTPException(status_code=404, detail="Avatar no encontrado.")

    activos = json.loads(current_user.avatares_activos)
    max_permitidos = {"gratis": 1, "comunicador": 3, "amigo_todos": 10}.get(current_user.plan_nivel, 1)

    if data.avatar_id in activos:
        return {"status": "success", "message": "Avatar ya seleccionado.", "activos": activos}

    if len(activos) >= max_permitidos and current_user.role != "admin":
        raise HTTPException(status_code=403, detail=f"Tu plan solo permite {max_permitidos} avatar activo.")

    activos.append(data.avatar_id)
    current_user.avatares_activos = json.dumps(activos)
    await db.commit()
    return {"status": "success", "message": "Avatar seleccionado con éxito.", "activos": activos}

@app.post("/api/chat")
async def chat_con_avatar(data: UserMessage, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not existe_avatar(data.avatar_id):
        raise HTTPException(status_code=404, detail="Avatar no encontrado.")

    limite_texto = {"gratis": 25, "comunicador": 100, "amigo_todos": 999999}.get(current_user.plan_nivel, 25)

    if current_user.chats_usados_semana >= limite_texto and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Has alcanzado el límite semanal de mensajes de tu plan.")

    current_user.chats_usados_semana += 1
    await db.commit()

    perfil_dict = {
        "apodo": current_user.apodo,
        "nombre_completo": current_user.nombre_completo,
        "cantidad_hijos": current_user.cantidad_hijos,
        "profesion": current_user.profesion,
        "situacion_sentimental": current_user.situacion_sentimental,
        "biografia": current_user.biografia
    }

    # SE INTEGRA EL HISTORIAL PREVIO HACIA RAFAEL
    nombre_av, resp, es_crisis = procesar_respuesta_avatar(
        avatar_id=data.avatar_id, 
        mensaje_usuario=data.message, 
        perfil_usuario=perfil_dict, 
        historial_reciente=data.historial_previo or []
    )

    return {
        "status": "success",
        "avatar_nombre": nombre_av,
        "respuesta": resp,
        "is_crisis": es_crisis,
        "chats_restantes": max(0, limite_texto - current_user.chats_usados_semana)
    }

# --- MURO, BUZÓN Y MANTENIMIENTO ---
@app.get("/api/muro")
async def obtener_muro(categoria: Optional[str] = None, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(MuroPostModel).options(selectinload(MuroPostModel.autor)).order_by(MuroPostModel.created_at.desc()).limit(50)
    
    if current_user.plan_nivel == "gratis":
        query = query.where(MuroPostModel.plan_origen == "gratis")
    elif current_user.plan_nivel == "comunicador":
        query = query.where(MuroPostModel.plan_origen.in_(["gratis", "comunicador"]))
    
    if categoria and categoria != "todas":
        query = query.where(MuroPostModel.categoria_emocional == categoria)

    res = await db.execute(query)
    posts = res.scalars().all()
    return {
        "status": "success",
        "posts": [
            {
                "id": p.id,
                "categoria_emocional": p.categoria_emocional,
                "contenido": p.contenido,
                "autor": "Anónimo" if p.is_anonimo else p.autor.apodo,
                "fecha": p.created_at.isoformat()
            }
            for p in posts
        ]
    }

@app.post("/api/muro", status_code=201)
async def crear_muro_post(data: MuroPostCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan_nivel == "gratis":
        raise HTTPException(status_code=403, detail="Tu plan solo permite lectura en el muro. Pasa a Comunicador para participar.")
    nuevo = MuroPostModel(
        user_id=current_user.id,
        plan_origen=current_user.plan_nivel,
        categoria_emocional=data.categoria_emocional,
        contenido=data.contenido,
        is_anonimo=data.is_anonimo
    )
    db.add(nuevo)
    await db.commit()
    return {"status": "success", "message": "Publicado con éxito en el Muro."}

@app.post("/api/buzon/ticket")
async def enviar_ticket(data: BuzonCreate, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ticket = BuzonModel(user_id=current_user.id, categoria=data.categoria, asunto=data.asunto, mensaje=data.mensaje)
    db.add(ticket)
    await db.commit()
    return {"status": "success", "message": "Ticket registrado en Soporte."}

@app.get("/api/buzon/mis-tickets")
async def mis_tickets(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(BuzonModel).where(BuzonModel.user_id == current_user.id).order_by(BuzonModel.created_at.desc()))
    return {"status": "success", "tickets": res.scalars().all()}

@app.post("/api/admin/cupones")
async def generar_cupon(data: CouponCreate, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    mapeo = {"verde": ("comunicador", 3), "azul": ("comunicador", 7), "rojo": ("amigo_todos", 3), "morado": ("amigo_todos", 7)}
    if data.tipo.lower() not in mapeo:
        raise HTTPException(status_code=400, detail="Tipo de cupón inválido (verde, azul, rojo, morado).")
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
    return {"status": "success", "message": f"Cupón activado con éxito. Ahora disfrutas del Plan {cupon.tipo_plan.title()}."}

@app.get("/api/admin/afiliados")
async def auditar_afiliados(admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    res_users = await db.execute(select(UserModel))
    todos = res_users.scalars().all()
    
    arbol = {}
    for u in todos:
        if u.referido_por:
            arbol.setdefault(u.referido_por, []).append(u)

    resultado = []
    for u in todos:
        hijos = arbol.get(u.codigo_referido, [])
        total_ref = len(hijos)
        ref_pagos = sum(1 for h in hijos if h.plan_nivel in ["comunicador", "amigo_todos"])
        
        resultado.append({
            "usuario_id": u.id,
            "apodo": u.apodo,
            "correo": u.correo,
            "codigo_referido": u.codigo_referido,
            "plan_actual": u.plan_nivel,
            "suscripcion_expira": u.suscripcion_expira.isoformat() if u.suscripcion_expira else None,
            "total_referidos": total_ref,
            "referidos_pagos": ref_pagos,
            "aplica_bono_conversion": (total_ref >= 10 and ref_pagos >= 5),
            "aplica_gran_meta": (total_ref >= 100)
        })

    return {"status": "success", "afiliados": resultado}

@app.post("/api/admin/afiliados/premiar")
async def premiar_afiliado(data: RewardAffiliateCreate, admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserModel).where(UserModel.id == data.usuario_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    dias_a_sumar = 7 if data.tipo_premio == "bono_conversion" else 365
    nombre_premio = "1 Semana Amigo de Todos" if data.tipo_premio == "bono_conversion" else "1 Año Amigo de Todos"

    ahora = datetime.now(timezone.utc)
    base_fecha = user.suscripcion_expira if (user.suscripcion_expira and user.suscripcion_expira > ahora) else ahora
    
    user.plan_nivel = "amigo_todos"
    user.suscripcion_expira = base_fecha + timedelta(days=dias_a_sumar)
    await db.commit()

    return {
        "status": "success", 
        "message": f"Premio de {nombre_premio} adjudicado a {user.apodo}.",
        "nueva_expiracion": user.suscripcion_expira.isoformat()
    }

@app.post("/api/cron/mantenimiento")
async def ejecutar_mantenimiento_programado(x_cron_key: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if x_cron_key != CRON_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Clave de cron no autorizada.")

    ahora = datetime.now(timezone.utc)
    hace_7_dias = ahora - timedelta(days=7)

    res_users = await db.execute(select(UserModel))
    usuarios = res_users.scalars().all()
    chats_reseteados = 0
    planes_revertidos = 0

    for u in usuarios:
        if u.chats_usados_semana > 0:
            u.chats_usados_semana = 0
            chats_reseteados += 1
        
        if u.suscripcion_expira and u.role != "admin":
            exp = u.suscripcion_expira if u.suscripcion_expira.tzinfo else u.suscripcion_expira.replace(tzinfo=timezone.utc)
            if ahora > exp:
                u.plan_nivel = "gratis"
                u.suscripcion_expira = None
                planes_revertidos += 1

    dms_del = await db.execute(delete(DirectMessageModel).where(DirectMessageModel.created_at < hace_7_dias))
    await db.commit()

    return {
        "status": "success",
        "chats_semanales_reseteados": chats_reseteados,
        "planes_vencidos_revertidos": planes_revertidos,
        "mensajes_directos_purgados": dms_del.rowcount
    }

@app.get("/api/admin/backup")
async def descargar_backup_completo(admin: UserModel = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    u_res = await db.execute(select(UserModel))
    usuarios = u_res.scalars().all()
    p_res = await db.execute(select(MuroPostModel))
    posts = p_res.scalars().all()
    d_res = await db.execute(select(DirectMessageModel))
    dms = d_res.scalars().all()
    c_res = await db.execute(select(CouponModel))
    cupones = c_res.scalars().all()
    pay_res = await db.execute(select(PaymentChatMessageModel))
    pagos = pay_res.scalars().all()

    return {
        "status": "success",
        "fecha_backup": datetime.now(timezone.utc).isoformat(),
        "usuarios": [
            {
                "id": u.id, "nombre_completo": u.nombre_completo, "apodo": u.apodo, "correo": u.correo,
                "password_hash": u.password_hash, "edad": u.edad, "sexo": u.sexo, "profesion": u.profesion,
                "situacion_sentimental": u.situacion_sentimental, "cantidad_hijos": u.cantidad_hijos,
                "biografia": u.biografia, "plan_nivel": u.plan_nivel, "role": u.role,
                "codigo_referido": u.codigo_referido, "referido_por": u.referido_por,
                "chats_usados_semana": u.chats_usados_semana, "avatares_activos": u.avatares_activos
            }
            for u in usuarios
        ],
        "muro_posts": [{"id": p.id, "user_id": p.user_id, "categoria": p.categoria_emocional, "contenido": p.contenido, "fecha": p.created_at.isoformat()} for p in posts],
        "mensajes_directos": [{"id": d.id, "remitente_id": d.remitente_id, "destinatario_id": d.destinatario_id, "contenido": d.contenido, "fecha": d.created_at.isoformat()} for d in dms],
        "cupones": [{"codigo": c.codigo, "tipo_plan": c.tipo_plan, "duracion_dias": c.duracion_dias, "usado": c.is_used} for c in cupones],
        "mensajes_pago": [{"user_id": py.user_id, "emisor": py.emisor_rol, "mensaje": py.mensaje, "plan": py.plan_solicitado, "metodo": py.metodo_pago, "fecha": py.created_at.isoformat()} for py in pagos]
    }

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
