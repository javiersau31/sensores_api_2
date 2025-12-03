from fastapi import FastAPI
from routers import usuarios,sensores
from database import db
from database import usuarios_collection
from datetime import datetime

app = FastAPI()

app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(sensores.router, prefix="/sensores", tags=["Sensores"])

@app.get("/")
def home():
    return {"mensaje": "API funcionando"}



@app.get("/test-db")
async def test_db():
    try:
        result = await db.list_collection_names()
        return {"ok": True, "colecciones": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    

@app.get("/test-insert")
async def test_insert():
    try:
        doc = {
            "nombre": "prueba_conexion",
            "timestamp": datetime.utcnow()
        }

        resultado = await usuarios_collection.insert_one(doc)

        # Recuperar el documento recién insertado
        encontrado = await usuarios_collection.find_one({"_id": resultado.inserted_id})

        return {
            "ok": True,
            "insertado_id": str(resultado.inserted_id),
            "documento": {
                "nombre": encontrado["nombre"],
                "timestamp": encontrado["timestamp"].isoformat()
            }
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}    
