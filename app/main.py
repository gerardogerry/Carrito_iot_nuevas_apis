"""Punto de entrada de la API Vehículo IoT (FastAPI + POO + Amazon RDS)."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import configuracion
from app.core.errores import ErrorNegocio
from app.routers import demos, movimientos, vehiculos, websockets
from app.services.demo_runner import gestor_demos

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

ETIQUETAS = [
    {"name": "Vehículos", "description": "5 SP: `sp_obtener_vehiculos`, `sp_obtener_vehiculo`, `sp_crear_vehiculo`, `sp_actualizar_vehiculo`, `sp_eliminar_vehiculo`."},
    {"name": "Comandos", "description": "4 SP: `sp_obtener_comandos_vehiculo`, `sp_crear_comando`, `sp_actualizar_comando`, `sp_eliminar_comando`."},
    {"name": "Estado", "description": "2 SP: `sp_obtener_estado`, `sp_actualizar_estado` + movimiento individual transaccional."},
    {"name": "Historial", "description": "2 SP: `sp_obtener_historial` (máx. 10, descendente), `sp_registrar_historial`."},
    {"name": "DEMO", "description": "8 SP: 4 de DEMO y 4 de movimientos DEMO + ejecución en tiempo real por WSS."},
    {"name": "WebSockets", "description": "Canal `wss://<dominio>/ws/vehiculo/{id}` (ver README)."},
]


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    configuracion.validar()          # falla al arrancar si falta algo en .env
    yield
    await gestor_demos.cancelar_todas()


app = FastAPI(
    title="API Vehículo IoT",
    description=("API pública en Amazon EC2 con FastAPI + POO, Amazon RDS (21 Stored Procedures) y WebSocket seguro.\n\n"
                 "🔒 = requiere encabezado `X-API-Key` (botón **Authorize**)."),
    version="2.0.0",
    openapi_tags=ETIQUETAS,
    lifespan=ciclo_de_vida,
)


@app.exception_handler(ErrorNegocio)
async def manejar_error_negocio(_: Request, e: ErrorNegocio):
    return JSONResponse(status_code=e.codigo_http, content={"detail": e.mensaje})


@app.exception_handler(Exception)
async def manejar_error_interno(_: Request, e: Exception):
    logging.getLogger("vehiculo_iot").exception("Error no controlado")
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


@app.get("/", include_in_schema=False)
async def raiz():
    return {"servicio": "API Vehículo IoT", "docs": "/docs"}


@app.get("/health", tags=["Estado"], summary="Verificación de salud del servicio")
async def salud():
    return {"status": "ok"}


app.include_router(vehiculos.router)
app.include_router(movimientos.router)
app.include_router(demos.router)
app.include_router(websockets.router)