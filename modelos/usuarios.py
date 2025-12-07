from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


# -------------------------
#  TARJETAS
# -------------------------
class Tarjeta(BaseModel):
    uid: str
    descripcion: Optional[str] = None
    fecha_registro: datetime


# -------------------------
# BASE USUARIO
# -------------------------
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str = "usuario"   # usuario | admin


# -------------------------
# REGISTRO
# -------------------------
class UsuarioRegistro(UsuarioBase):
    password: str


# -------------------------
# USUARIO COMO SE GUARDA EN MONGO
# -------------------------
class UsuarioDB(UsuarioBase):
    id: Optional[str] = None  # Se generará como str(ObjectId)
    tarjetas: List[Tarjeta] = []
    fecha_registro: datetime


# -------------------------
# LOGIN
# -------------------------
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# RESPUESTA JWT
# -------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------------
# DATOS DEL USUARIO PA' RESPUESTA
# -------------------------
class UsuarioLoginData(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str
    tarjetas: List[Tarjeta] = []


# -------------------------
# RESPUESTA COMPLETA
# -------------------------
class LoginResponse(BaseModel):
    mensaje: str
    token: str
    usuario: UsuarioLoginData
