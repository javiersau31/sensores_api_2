from fastapi import APIRouter, HTTPException
from modelos.sensores import SensorDato, SpotActual, HistorialLectura, DatoAccesoRFID
from database import spots_actuales_collection, historial_lecturas_collection, accesos_collection,usuarios_collection
from datetime import datetime
from bson import ObjectId
from modelos.usuarios import UsuarioDB

router = APIRouter()


@router.post("/registrar_acceso")
def registrar_acceso(datos: DatoAccesoRFID):
    fecha = datetime.utcnow()
    
    # 1. BUSCAR USUARIO DUEÑO DE LA TARJETA
    # Buscamos en la colección de usuarios alguien que tenga este UID en su lista de tarjetas
    usuario_doc = usuarios_collection.find_one({"tarjetas.uid": datos.uid})
    
    nombre_usuario = "Desconocido"
    usuario_id = None
    acceso_autorizado = False

    if usuario_doc:
        usuario = UsuarioDB(**usuario_doc) # Convertimos a objeto Pydantic
        nombre_usuario = usuario.nombre
        usuario_id = str(usuario.id)
        acceso_autorizado = True
        
        # Opcional: Aquí podrías activar la puerta automáticamente si es autorizado
        # spots_actuales_collection.update_one({"_id": datos.spot_id}, {"$set": {"comando_puerta": True}})

    # 2. CREAR REGISTRO DE ACCESO
    acceso_doc = {
        "spot_id": datos.spot_id,
        "tarjeta_uid": datos.uid,
        "usuario_id": usuario_id,
        "nombre_usuario": nombre_usuario, # Guardamos el nombre para historial rápido
        "fecha": fecha,
        "autorizado": acceso_autorizado,
        "tipo": "ENTRADA_RFID"
    }

    accesos_collection.insert_one(acceso_doc)

    # 3. RESPONDER
    if acceso_autorizado:
        return {"mensaje": f"Bienvenido {nombre_usuario}", "acceso": True}
    else:
        return {"mensaje": "Tarjeta no registrada", "acceso": False}


@router.post("/crear_spot")
def crear_spot(spot: SpotActual):
    doc = {
        "_id": spot.id,
        "nombre": spot.nombre,
        "ubicacion_id": spot.ubicacion.dict(),
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
