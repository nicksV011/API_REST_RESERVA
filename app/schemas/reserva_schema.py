from pydantic import BaseModel, ValidationInfo, field_validator, model_validator, Field
from datetime import datetime, time, timedelta
from bson import ObjectId

class ReservaBase(BaseModel):
    mesa: int 
    hora_inicio: datetime
    duracion: int 
    personas: int 
    nombre_cliente: str 

    # Validaciones para las mesas (1-5)
    @field_validator("mesa")
    def validar_mesa(cls, value):
        if not 1 <= value <= 5:
            raise ValueError("La mesa debe estar entre 1 y 5")
        return value

    # Validaciones para el número de personas (1-6)
    @field_validator("personas")
    def validar_personas(cls, value):
        if not 1 <= value <= 6:
            raise ValueError("El número de personas debe estar entre 1 y 6")
        return value

    # Validaciones para la duración (mínimo 1 hora)
    @field_validator("duracion")
    def validar_duracion(cls, value):
        if not 1 <= value <= 3:
            raise ValueError("La duración debe ser al menos 1 hora y máximo 3 horas")
        return value

    # Validación horaria (4:00 PM a 10:00 PM)
    @model_validator(mode="after")
    def validar_hora(cls, values):
        hora_inicio = values.hora_inicio
        if hora_inicio:
            hora = hora_inicio.time()
            if not (time(16, 0) <= hora <= time(22, 0)):
                raise ValueError("La reserva debe ser entre 4:00 PM y 10:00 PM")
        return values

class ReservaCreate(ReservaBase):
    pass

class Reserva(ReservaBase):
    id: str = Field(alias="_id")
    
    @model_validator(mode="before")
    def convert_objectid_to_str(cls, data: dict) -> dict:
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        return data

    class Config:
        from_attributes = True
        populate_by_name = True  
        
class DisponibilidadQuery(BaseModel):
    mesa: int = Field(..., ge=1, le=5)
    hora_inicio: datetime = Field(...)
    duracion: int = Field(..., ge=1)

    @field_validator("hora_inicio")
    def validar_horario_restaurante(cls, value: datetime) -> datetime:
        hora = value.time()
        if not (time(16, 0) <= hora <= time(22, 0)):
            raise ValueError("El horario debe estar entre 4:00 PM y 10:00 PM")
        return value

    @field_validator("duracion")
    def validar_duracion_maxima(cls, value: int, info: ValidationInfo) -> int:
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio:
            # Calcula la hora de finalización
            hora_fin = hora_inicio + timedelta(hours=value)
            # Permite terminar hasta la medianoche (00:00:00 del día siguiente)
            midnight = (hora_inicio.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1))
            
            if hora_fin > midnight:
                raise ValueError("La reserva no puede terminar después de la medianoche")
        return value
    
    @field_validator("mesa")
    def validar_mesa(cls, value):
        if not 1 <= value <= 5:
            raise ValueError("La mesa debe estar entre 1 y 5")
        return value

