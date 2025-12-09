from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Union, Optional


class UbicacionSpot(BaseModel):
    id: str       # Ej: "SUC0001"
    nombre: str   # Ej: "Torreón Centro"

# --- Modelo para cada dato de sensor ---
class SensorDato(BaseModel):
    sensor_id: str               # Ej: temp01, gas01, pir01
    tipo: str                    # Ej: temperatura, gas, movimiento
    ultimo_dato: Union[float, int, str]  # Ej: 23.5, 0, "OK"


# --- Estado actual de un Spot (una ubicación con sensores) ---
class SpotActual(BaseModel):
    id: str                      # Ej: "01"
    nombre: str                  # Ej: "principal"
    ubicacion: UbicacionSpot            # Ej: "SUC0001"
    ultimo_estado: Optional[List[SensorDato]] = Field(default_factory=list) 
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)


# --- Historial de lecturas (cada registro que viene de Raspberry) ---
class HistorialLectura(BaseModel):
    id: Optional[str] = None                     # Se generará como str(ObjectId)
    spot_id: str                 # El spot al que pertenece
    lecturas: List[SensorDato]   # Misma estructura de estado actual
    fecha_lectura: datetime = Field(default_factory=datetime.utcnow)


class DatoAccesoRFID(BaseModel):
    spot_id: str
    uid: str

