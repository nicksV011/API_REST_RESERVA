from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.reserva_schema import DisponibilidadQuery, ReservaCreate, Reserva
from app.services.reserva_service import ReservaService
from app.schemas.fecha_schema import FechaRango

router = APIRouter()

@router.post("/reservas/", response_model=Reserva, status_code=status.HTTP_201_CREATED)
async def crear_reserva(reserva: ReservaCreate):
    try:
        return await ReservaService.crear_reserva(reserva)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reservas/{reserva_id}", response_model=Reserva, status_code=status.HTTP_200_OK)
async def obtener_reserva(reserva_id: str):
    reserva = await ReservaService.obtener_reserva(reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@router.get("/reservas/", response_model=list[Reserva], status_code=status.HTTP_200_OK)
async def listar_reservas():
    return await ReservaService.listar_reservas()

@router.put("/reservas/{reserva_id}", response_model=Reserva, status_code=status.HTTP_200_OK)
async def actualizar_reserva(reserva_id: str, datos: ReservaCreate):
    try:
        return await ReservaService.actualizar_reserva(reserva_id, datos)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
    
@router.delete("/reservas/{reserva_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def eliminar_reserva(reserva_id: str):
    success = await ReservaService.eliminar_reserva(reserva_id)
    if success:
        return {"message": "Reserva eliminada"}
    raise HTTPException(status_code=404, detail="Reserva no encontrada")

@router.get("/disponibilidad/", response_model=dict, status_code=status.HTTP_200_OK)
async def verificar_disponibilidad(
    params: DisponibilidadQuery = Depends()
):
    disponible = await ReservaService.verificar_disponibilidad(
        params.mesa,
        params.hora_inicio,
        params.duracion
    )
    return {
        "mesa": params.mesa,
        "hora_inicio": params.hora_inicio,
        "duracion": params.duracion,
        "disponible": disponible
    }
    
@router.get("/reservas/rango-horario/", response_model=list[Reserva])
async def listar_por_rango(
    fecha_inicio: datetime = Query(..., description="Fecha inicio del rango"),
    fecha_fin: datetime = Query(..., description="Fecha fin del rango")
):
    # Validar usando el esquema
    fecha_rango = FechaRango(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    return await ReservaService.listar_por_rango(
        fecha_rango.fecha_inicio,
        fecha_rango.fecha_fin
    )