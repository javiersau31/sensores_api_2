from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Union

class SensorDato(BaseModel):
    sensor_id: str
    tipo: str   # temperatura / gas / movimiento / humedad / puerta...
    ultimo_dato: Union[int, float]
    
class SpotActual(BaseModel):
    id: str
    nombre: str
    ubicacion_id: str
    
    ultimo_estado: List[SensorDato]

    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)

class HistorialLectura(BaseModel):
    id: str
    spot_id: str
    
    lecturas: List[SensorDato]

    fecha_lectura: datetime = Field(default_factory=datetime.utcnow)



