from pydantic import BaseModel

class LecturasActuales(BaseModel):
    temperatura: str
    humedad: str
    gas: str
    movimiento: str
    puerta: str
