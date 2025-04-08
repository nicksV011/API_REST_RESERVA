from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import reserva_routes
from app.db.database import client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Servidor iniciado. Conexión a MongoDB establecida.")
    try:
        await client.admin.command("ping")
        print("✅ Conexión a MongoDB exitosa")
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        raise e  
    yield  
    # Shutdown
    print("🚀 Servidor detenido. Cerrando conexión a MongoDB...")
    if client:
        await client.close()
        print("✅ Conexión a MongoDB cerrada.")
    else:
        print("❌ No se pudo cerrar la conexión a MongoDB.")

# Inicializa FastAPI con lifespan
app = FastAPI(
    title="API de Reservas de Restaurantes",
    description="API para gestionar reservas de mesas en un restaurante",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.include_router(reserva_routes.router, prefix="/api/v1")