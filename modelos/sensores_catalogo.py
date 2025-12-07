from pydantic import BaseModel

class SensorCatalogo(BaseModel):
    id: str
    tipo: str
    descripcion: str
    unidad: str

