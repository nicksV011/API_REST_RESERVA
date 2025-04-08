from bson import ObjectId
from app.db.database import reservas
from app.schemas.reserva_schema import ReservaCreate, Reserva
from datetime import datetime, timedelta
from typing import Optional

class ReservaModel:
    @staticmethod
    async def crear(reserva: ReservaCreate) -> Reserva:
        # Inserta en MongoDB
        result = await reservas.insert_one(reserva.dict())
        reserva_db = await reservas.find_one({"_id": result.inserted_id})
        return Reserva(**reserva_db, id=str(reserva_db["_id"]))

    @staticmethod
    async def obtener_por_id(reserva_id: str) -> Reserva:
        reserva = await reservas.find_one({"_id": ObjectId(reserva_id)})
        if reserva:
            return Reserva(**reserva, id=str(reserva["_id"]))
        return None
    
    @staticmethod
    async def obtener_todos() -> list[Reserva]:
        reservas_db = await reservas.find().to_list(length=None)
        return [
            Reserva(**reserva, id=str(reserva["_id"])) 
            for reserva in reservas_db
        ]

    @staticmethod
    async def actualizar(reserva_id: str, datos: dict) -> Reserva:
        await reservas.update_one(
            {"_id": ObjectId(reserva_id)},
            {"$set": datos}
        )
        return await ReservaModel.obtener_por_id(reserva_id)

    @staticmethod
    async def eliminar(reserva_id: str) -> bool:
        result = await reservas.delete_one({"_id": ObjectId(reserva_id)})
        return result.deleted_count > 0
    
    @staticmethod
    async def buscar_reserva_superpuesta(
        mesa: int,
        hora_inicio: datetime,
        hora_fin: datetime,
        exclude_id: Optional[str] = None
    ) -> bool:
        """Verifica superposición usando cálculos de tiempo en MongoDB"""
        query = {
            "mesa": mesa,
            "$expr": {
                "$and": [
                    # La reserva existente empieza antes de que termine la nueva
                    { "$lt": ["$hora_inicio", hora_fin] },
                    # La reserva existente termina después de que empiece la nueva
                    { "$gt": [
                        { "$add": ["$hora_inicio", {"$multiply": ["$duracion", 60*60*1000]}] },
                        hora_inicio
                    ]}
                ]
            }
        }

        # Excluye la reserva actual si es una actualización
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}

        reserva = await reservas.find_one(query)
        return reserva is not None
    
    @staticmethod
    async def verificar_disponibilidad(
        mesa: int,
        hora_inicio: datetime,
        duracion: int
    ) -> bool:
        hora_fin = hora_inicio + timedelta(hours=duracion)
        reserva_superpuesta = await ReservaModel.buscar_reserva_superpuesta(
            mesa, hora_inicio, hora_fin
        )
        return not reserva_superpuesta
    
    
    @staticmethod
    async def obtener_por_rango(
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> list[Reserva]:
       
        query = {
            "hora_inicio": {
                "$gte": fecha_inicio,  
                "$lt": fecha_fin     
            }
        }
        reservas_db = await reservas.find(query).to_list(length=None)
        return [
            Reserva(**reserva, id=str(reserva["_id"]))
            for reserva in reservas_db
        ]