from fastapi import APIRouter, HTTPException
from modelos.sensores import LecturasActuales as Lectura
from database import lecturas_collection, sensores_collection
from typing import List

router = APIRouter()

# ---------------------------------------------------------
# 1. REGISTRAR LECTURA (Desde Python/ESP32)
# ---------------------------------------------------------
@router.post("/registrar", response_model=Lectura)
def registrar_lectura(lectura: Lectura):
    # 1. Guardar en historial (colección de logs)
    lecturas_collection.insert_one(lectura.dict())

    # 2. Guardar como lectura actual global (estado actual)
    sensores_collection.update_one(
        {"_id": "estado_general"},
        {"$set": lectura.dict()},
        upsert=True
    )

    return lectura

# ---------------------------------------------------------
# 2. OBTENER LECTURA ACTUAL (Para Dashboard iOS)
# ---------------------------------------------------------
@router.get("/actual", response_model=Lectura)
def obtener_actual():
    lectura = sensores_collection.find_one({"_id": "estado_general"})
    
    if not lectura:
        raise HTTPException(status_code=404, detail="No hay lecturas actuales")

    # Quitamos el _id de Mongo para que no falle Pydantic
    lectura.pop("_id", None)

    return Lectura(**lectura)

# ---------------------------------------------------------
# 3. ACTUALIZAR MANUALMENTE (Debug)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 4. DESACTIVAR MOVIMIENTO (Resetear alarma)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 5. ABRIR PUERTA (Desde Botón iOS)
# ---------------------------------------------------------
@router.put("/abrir_puerta", response_model=Lectura)
def abrir_puerta():
    # Establecemos la puerta como abierta Y activamos la bandera de comando
    sensores_collection.update_one(
        {"_id": "estado_general"},
        {
            "$set": {
                "puerta": "abierta", 
                "comando_pendiente": True 
            }
        }
    )

    lectura = sensores_collection.find_one({"_id": "estado_general"})
    lectura.pop("_id", None)
    return Lectura(**lectura)

# ---------------------------------------------------------
# 6. VERIFICAR COMANDO (Consultado por Python Script)
# ---------------------------------------------------------
@router.get("/verificar_comando")
def verificar_comando():
    """
    Este endpoint lo consultará tu Python local para saber si debe abrir.
    """
    doc = sensores_collection.find_one({"_id": "estado_general"})
    
    # Verificamos si existe el documento y si comando_pendiente es True
    if doc and doc.get("comando_pendiente") is True:
        # Si hay comando, lo devolvemos y LO APAGAMOS inmediatamente
        # para que la puerta no se quede abriendo en bucle.
        sensores_collection.update_one(
            {"_id": "estado_general"},
            {"$set": {"comando_pendiente": False}}
        )
        return {"accion": "ABRIR"}
    
    return {"accion": "NADA"}

# ---------------------------------------------------------
# 7. HISTORIAL
# ---------------------------------------------------------
@router.get("/historial", response_model=List[Lectura])
def historial(limit: int = 100):
    cursor = lecturas_collection.find().sort("fecha", -1).limit(limit)
    return [Lectura(**doc) for doc in cursor]