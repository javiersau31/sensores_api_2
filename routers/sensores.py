from fastapi import APIRouter, HTTPException
from modelos.sensores import LecturasActuales as Lectura
from database import lecturas_collection, sensores_collection
from typing import List

router = APIRouter()


# Registrar lectura (desde ESP32)
@router.post("/registrar", response_model=Lectura)
def registrar_lectura(lectura: Lectura):

    # 1️ Guardar en historial
    lecturas_collection.insert_one(lectura.dict())

    # 2️ Guardar como lectura actual global
    sensores_collection.update_one(
        {"_id": "estado_general"},
        {"$set": lectura.dict()},
        upsert=True
    )

    return lectura


#Lectura para el dashboard--
@router.get("/actual", response_model=Lectura)
def obtener_actual():
    lectura = sensores_collection.find_one({"_id": "estado_general"})
    if not lectura:
        raise HTTPException(status_code=404, detail="No hay lecturas actuales")

    # Quitamos el _id si existe
    lectura.pop("_id", None)

    return Lectura(**lectura)


#actualizar lectura manualmente
@router.put("/actualizar", response_model=Lectura)
def actualizar_sensor(data: dict):

    result = sensores_collection.update_one(
        {"_id": "estado_general"},
        {"$set": data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")

    lectura = sensores_collection.find_one({"_id": "estado_general"})
    lectura.pop("_id", None)

    return Lectura(**lectura)


#Desactivar lectura de movimiento-
@router.put("/desactivar_movimiento", response_model=Lectura)
def desactivar_movimiento():

    result = sensores_collection.update_one(
        {"_id": "estado_general"},
        {"$set": {"movimiento": 0}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")

    lectura = sensores_collection.find_one({"_id": "estado_general"})
    lectura.pop("_id", None)

    return Lectura(**lectura)


#Abrir puerta
@router.put("/abrir_puerta", response_model=Lectura)
def abrir_puerta():
    # Guardamos una instrucción explícita en Mongo
    sensores_collection.update_one(
        {"_id": "estado_general"},
        {
            "$set": {
                "puerta": "abierta", 
                "comando_pendiente": True  # <--- ESTO ES LA CLAVE
            }
        }
    )

    lectura = sensores_collection.find_one({"_id": "estado_general"})
    lectura.pop("_id", None)
    return Lectura(**lectura)

# 2. Agrega este endpoint NUEVO para tu Script Python
@router.get("/verificar_comando")
def verificar_comando():
    """
    Este endpoint lo consultará tu Python local para saber si debe abrir.
    """
    doc = sensores_collection.find_one({"_id": "estado_general"})
    
    if doc and doc.get("comando_pendiente") == True:
        # Si hay comando, lo devolvemos y LO APAGAMOS inmediatamente
        # para que la puerta no se quede abriendo bucleada.
        sensores_collection.update_one(
            {"_id": "estado_general"},
            {"$set": {"comando_pendiente": False}}
        )
        return {"accion": "ABRIR"}
    
    return {"accion": "NADA"}

#Historial de lecturas
@router.get("/historial", response_model=List[Lectura])
def historial(limit: int = 100):
    cursor = lecturas_collection.find().sort("fecha", -1).limit(limit)

    return [Lectura(**doc) for doc in cursor]
