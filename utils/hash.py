from passlib.context import CryptContext

# Algoritmo recomendado para APIs
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Devuelve la contraseña hasheada"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña ingresada coincida con la almacenada"""
    return pwd_context.verify(password, hashed_password)
