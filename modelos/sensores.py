from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class SensorDato(BaseModel):
    sensor_id: str
    tipo: str
    ultimo_dato: float | int
    
class SpotActual(BaseModel):
    id: str
    nombre: str
    ubicacion_id: str
    ultimo_estado: list[SensorDato]
    fecha_actualizacion: datetime

class HistorialLectura(BaseModel):
    id: str
    spot_id: str
    lecturas: list[SensorDato]
    fecha_lectura: datetime


