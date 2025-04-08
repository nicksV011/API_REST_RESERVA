from app.models.reserva_model import ReservaModel
from app.schemas.reserva_schema import Reserva, ReservaCreate
from datetime import datetime, timedelta, timezone

class ReservaService:
    @staticmethod
    async def crear_reserva(reserva: ReservaCreate) -> dict:
        # Calcula la hora de finalización
        hora_fin = reserva.hora_inicio + timedelta(hours=reserva.duracion)
        
        # Verifica si hay reservas superpuestas en la misma mesa
        reserva_existente = await ReservaModel.buscar_reserva_superpuesta(
            reserva.mesa,
            reserva.hora_inicio,
            hora_fin
        )
        
        if reserva_existente:
            raise ValueError("La mesa ya está reservada en ese horario")
        
        # Crea la reserva
        return await ReservaModel.crear(reserva)
    @staticmethod
    async def obtener_reserva(reserva_id: str):
        return await ReservaModel.obtener_por_id(reserva_id)

    @staticmethod
    async def actualizar_reserva(reserva_id: str, datos_actualizar: ReservaCreate) -> Reserva:
        reserva_existente = await ReservaModel.obtener_por_id(reserva_id)
        if not reserva_existente:
            raise ValueError("Reserva no encontrada")
        
        # Detecta cambios en campos críticos
        cambios = {}
        if datos_actualizar.mesa is not None and datos_actualizar.mesa != reserva_existente.mesa:
            cambios["mesa"] = datos_actualizar.mesa
        if datos_actualizar.hora_inicio is not None and datos_actualizar.hora_inicio != reserva_existente.hora_inicio:
            cambios["hora_inicio"] = datos_actualizar.hora_inicio
        if datos_actualizar.duracion is not None and datos_actualizar.duracion != reserva_existente.duracion:
            cambios["duracion"] = datos_actualizar.duracion
        
        # Si hay cambios en mesa, hora_inicio o duracion, valida disponibilidad
        if cambios:
            nueva_hora_inicio = cambios.get("hora_inicio", reserva_existente.hora_inicio)
            nueva_duracion = cambios.get("duracion", reserva_existente.duracion)
            nueva_hora_fin = nueva_hora_inicio + timedelta(hours=nueva_duracion)
            
            reserva_superpuesta = await ReservaModel.buscar_reserva_superpuesta(
                mesa=cambios.get("mesa", reserva_existente.mesa),
                hora_inicio=nueva_hora_inicio,
                hora_fin=nueva_hora_fin,
                exclude_id=reserva_id  # Excluye la reserva actual
            )
            
            if reserva_superpuesta:
                raise ValueError("La nueva hora/mesa ya está ocupada")
        
        # Actualiza solo los campos proporcionados
        datos_actualizar_dict = datos_actualizar.dict(exclude_unset=True)
        return await ReservaModel.actualizar(reserva_id, datos_actualizar_dict)

    @staticmethod
    async def eliminar_reserva(reserva_id: str) -> bool:
        return await ReservaModel.eliminar(reserva_id)
    
    @staticmethod
    async def listar_reservas() -> list[Reserva]:
        return await ReservaModel.obtener_todos()
    
    @staticmethod
    async def verificar_disponibilidad(
        mesa: int,
        hora_inicio: datetime,
        duracion: int
    ) -> bool:
        return await ReservaModel.verificar_disponibilidad(
            mesa, hora_inicio, duracion
        )
        
    @staticmethod
    async def listar_por_rango(
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> list[Reserva]:
        # Convierte a UTC si es necesario
        if fecha_inicio.tzinfo is None:
            fecha_inicio = fecha_inicio.replace(tzinfo=timezone.utc)
        if fecha_fin.tzinfo is None:
            fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)
        
        return await ReservaModel.obtener_por_rango(fecha_inicio, fecha_fin)