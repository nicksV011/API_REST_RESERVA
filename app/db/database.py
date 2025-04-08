from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongo_uri)
database = client.Cluster0 
reservas = database.get_collection("reservas") 