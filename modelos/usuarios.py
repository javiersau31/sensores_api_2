from pydantic import BaseModel, EmailStr
from datetime import datetime

# Modelo base de usuario
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str = "usuario"   # usuario o admin

# Para registrar usuarios
class UsuarioRegistro(UsuarioBase):
    password: str

# Para devolver usuarios desde MongoDB
class UsuarioDB(UsuarioBase):
    id: str
    fecha_registro: datetime

# Para login
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# Token JWT
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


from pydantic import BaseModel, EmailStr
from datetime import datetime

# Modelo base de usuario
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str = "usuario"   # usuario o admin

# Para registrar usuarios
class UsuarioRegistro(UsuarioBase):
    password: str

# Para devolver usuarios desde MongoDB
class UsuarioDB(UsuarioBase):
    id: str
    fecha_registro: datetime

# Para login
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

# Token JWT
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UsuarioLoginData(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: str

class LoginResponse(BaseModel):
    mensaje: str
    token: str
    usuario: UsuarioLoginData