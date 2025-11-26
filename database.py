from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["integradoraII"]
usuarios_collection = db["usuarios"]
sensores_collection = db["sensores"]
