from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class LecturasActuales(BaseModel):
    temperatura: float
    humedad: float
    gas: int = Field(..., ge=0, le=4095)
    movimiento: int = Field(..., ge=0, le=1)
    puerta: str
    fecha: Optional[datetime] = Field(default_factory=datetime.utcnow)
