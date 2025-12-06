from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["integradoraII"]
usuarios_collection = db["usuarios"]
sucursales_collection = db["sucursales"]
sensores_catalogo_collection = db["sensores_catalogo"]
spots_actuales_collection = db["spots_actuales"]
historial_lecturas_collection = db["historial_lecturas"]
