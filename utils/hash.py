from passlib.context import CryptContext

# Algoritmo recomendado para APIs
pwd_context = CryptContext(schemes=["argon-2"], deprecated="auto")

def hash_password(password: str):
    """Devuelve la contraseña hasheada"""
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña ingresada coincida con la almacenada"""
    return pwd_context.verify(password[:72], hashed_password)
