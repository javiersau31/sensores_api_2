from fastapi import APIRouter, HTTPException, status
from modelos.sensores import LecturasActuales
from database import sensores_collection

router = APIRouter()

@router.get("/actual", response_model=LecturasActuales)
def obtener_lecturas_actuales():

    # Buscar la última lectura insertada
    lectura = sensores_collection.find_one(
        sort=[("_id", -1)]  # Orden por ID DESC (lo más reciente)
    )

    if not lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay lecturas registradas aún."
        )

    return {
        "temperatura": str(lectura.get("temperatura", "0")),
        "humedad": str(lectura.get("humedad", "0")),
        "gas": str(lectura.get("gas", "0")),
        "movimiento": lectura.get("movimiento", "Desconocido"),
        "puerta": lectura.get("puerta", "Desconocido")
    }
