from datetime import datetime, timezone
from pydantic import BaseModel, field_validator, model_validator

class FechaRango(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime

    @field_validator("fecha_inicio")
    def validar_fecha_inicio(cls, value: datetime):
        # Convierte a aware si es naive
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    @field_validator("fecha_fin")
    def validar_fecha_fin(cls, value: datetime):
        # Convierte a aware si es naive
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    @model_validator(mode="after")
    def validar_rango(self):
        # Asegura consistencia de zonas horarias
        if self.fecha_inicio.tzinfo != self.fecha_fin.tzinfo:
            raise ValueError("Las fechas deben tener la misma zona horaria")
        if self.fecha_inicio >= self.fecha_fin:
            raise ValueError("fecha_inicio debe ser anterior a fecha_fin")
        return self