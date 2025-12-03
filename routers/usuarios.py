from fastapi import APIRouter, HTTPException, status
from modelos.usuarios import UsuarioRegistro, UsuarioLogin, UsuarioDB,LoginResponse
from utils.hash import hash_password, verify_password
from database import usuarios_collection
from datetime import datetime
from bson import ObjectId
from utils.jwt_manager import crear_access_token
from typing import List

router = APIRouter()

# Convertir documento Mongo → UsuarioDB
def usuario_mongo_a_dict(usuario_mongo):
    return UsuarioDB(
        id=str(usuario_mongo["_id"]),
        nombre=usuario_mongo["nombre"],
        email=usuario_mongo["email"],
        rol=usuario_mongo["rol"],
        fecha_registro=usuario_mongo["fecha_registro"]
    )


# Registrar usuario
@router.post("/registro", response_model=UsuarioDB)
def registrar_usuario(usuario: UsuarioRegistro):

    # Validar si el email ya existe
    existe = usuarios_collection.find_one({"email": usuario.email})
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )

    # Crear documento para Mongo
    nuevo_usuario = {
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol,
        "password": hash_password(usuario.password),
        "fecha_registro": datetime.utcnow()
    }

    # Insertar
    resultado = usuarios_collection.insert_one(nuevo_usuario)
    nuevo_usuario["_id"] = resultado.inserted_id

    # Retornar en formato Pydantic (sin password)
    return usuario_mongo_a_dict(nuevo_usuario)


#login usuario
@router.post("/login",response_model=LoginResponse )
def login_usuario(datos: UsuarioLogin):

    # Buscar usuario por email
    usuario = usuarios_collection.find_one({"email": datos.email})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciales incorrectas."
        )

    # Verificar contraseña
    if not verify_password(datos.password, usuario["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales incorrectas."
        )

    # Crear Token JWT
    token = crear_access_token({
        "id": str(usuario["_id"]),
        "email": usuario["email"],
        "rol": usuario["rol"]
    })

    return {
        "mensaje": "Login exitoso",
        "token": token,
        "usuario": {
            "id": str(usuario["_id"]),
            "nombre": usuario["nombre"],
            "email": usuario["email"],
            "rol": usuario["rol"]
        }
    }

router.get("/todos",response_model=List[UsuarioDB] )
def obtener_usuarios():
    usuarios = usuarios_collection.find()
    return [usuario_mongo_a_dict(u) for u in usuarios]


router.delete("/eliminar/{usuario_id}")
def eliminar_usuario(usuario_id:str):
    resultado = usuarios_collection.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return {"mensaje": "Usuario eliminado correctamente."}