from fastapi import APIRouter, HTTPException
from modelos.sensores import SensorDato, SpotActual, HistorialLectura
from database import spots_actuales_collection, historial_lecturas_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/crear_spot")
def crear_spot(spot: SpotActual):
    doc = {
        "_id": spot.id,
        "nombre": spot.nombre,
        "ubicacion_id": spot.ubicacion_id,
        "ultimo_estado": [],
        "fecha_actualizacion": datetime.utcnow(),
        "comando_puerta": False
    }

    spots_actuales_collection.insert_one(doc)

    return {"mensaje": "Spot creado correctamente", "spot_id": spot.id}


# ---------------------------------------------------------
# 1. REGISTRAR LECTURA COMPLETA DESDE ESP32
# ---------------------------------------------------------
@router.post("/registrar/{spot_id}")
def registrar_lectura(spot_id: str, datos: list[SensorDato]):
    fecha = datetime.utcnow()

    # -----------------------------------------------------
    # Guardar en HISTORIAL
    # -----------------------------------------------------
    historial_doc = {
        "spot_id": spot_id,
        "lecturas": [d.dict() for d in datos],
        "fecha_lectura": fecha
    }

    historial_lecturas_collection.insert_one(historial_doc)

    # -----------------------------------------------------
    # Actualizar ESTADO ACTUAL
    # -----------------------------------------------------
    spots_actuales_collection.update_one(
        {"_id": spot_id},
        {
            "$set": {
                "ultimo_estado": [d.dict() for d in datos],
                "fecha_actualizacion": fecha
            }
        },
        upsert=True
    )

    return {
        "mensaje": "Lectura registrada correctamente",
        "spot_id": spot_id,
        "fecha": fecha
    }



# ---------------------------------------------------------
# 2. OBTENER ESTADO ACTUAL DE UN SPOT
# ---------------------------------------------------------
@router.get("/actual/{spot_id}", response_model=SpotActual)
def obtener_actual(spot_id: str):
    doc = spots_actuales_collection.find_one({"_id": spot_id})

    if not doc:
        raise HTTPException(status_code=404, detail="Spot no encontrado")

    doc["id"] = str(doc["_id"])
    doc.pop("_id")

    return SpotActual(**doc)



# ---------------------------------------------------------
# 3. RESET DE MOVIMIENTO
# ---------------------------------------------------------
@router.put("/reset_movimiento/{spot_id}")
def reset_movimiento(spot_id: str):

    spot = spots_actuales_collection.find_one({"_id": spot_id})
    if not spot:
        raise HTTPException(status_code=404, detail="Spot no encontrado")

    sensores = spot["ultimo_estado"]
    
    # Cambiar movimiento a 0
    for sensor in sensores:
        if sensor["tipo"] == "movimiento":
            sensor["ultimo_dato"] = 0

    spots_actuales_collection.update_one(
        {"_id": spot_id},
        {"$set": {"ultimo_estado": sensores}}
    )

    return {"mensaje": "Movimiento reseteado"}



# ---------------------------------------------------------
# 4. SOLICITAR COMANDO PARA ABRIR PUERTA (Desde iOS)
# ---------------------------------------------------------
@router.put("/abrir_puerta/{spot_id}")
def abrir_puerta(spot_id: str):

    spots_actuales_collection.update_one(
        {"_id": spot_id},
        {"$set": {"comando_puerta": True}}
    )

    return {"mensaje": "Comando enviado: ABRIR PUERTA"}



# ---------------------------------------------------------
# 5. ESP32 VERIFICA SI HAY COMANDO PENDIENTE
# ---------------------------------------------------------
@router.get("/verificar_comando/{spot_id}")
def verificar_comando(spot_id: str):

    doc = spots_actuales_collection.find_one({"_id": spot_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Spot no encontrado")

    if doc.get("comando_puerta") == True:
        # apagar comando inmediatamente
        spots_actuales_collection.update_one(
            {"_id": spot_id},
            {"$set": {"comando_puerta": False}}
        )
        return {"accion": "ABRIR"}

    return {"accion": "NADA"}



# ---------------------------------------------------------
# 6. HISTORIAL COMPLETO DEL SPOT
# ---------------------------------------------------------
@router.get("/historial/{spot_id}")
def historial(spot_id: str, limit: int = 50):

    cursor = (
        historial_lecturas_collection
        .find({"spot_id": spot_id})
        .sort("fecha_lectura", -1)
        .limit(limit)
    )

    resultados = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id")
        resultados.append(HistorialLectura(**doc))

    return resultados
