"""Estado (2 SP), Historial (2 SP) y movimiento individual con notificación WSS."""
import asyncio
from fastapi import APIRouter, status
from app.core.seguridad import protegido
from app.models.schemas import EstadoActualizar, HistorialRegistrar, MovimientoIndividual
from app.services.movimiento_service import ServicioEstado, ServicioHistorial, ServicioMovimiento
from app.websocket.websocket_manager import administrador

router = APIRouter(prefix="/api")


# -------------------------------- ESTADO --------------------------------
@router.get("/vehiculos/{vehiculo_id}/estado", tags=["Estado"],
            summary="Último estado del vehículo (sp_obtener_estado)")
async def obtener_estado(vehiculo_id: int):
    return await asyncio.to_thread(ServicioEstado.obtener, vehiculo_id)


@router.post("/vehiculos/estado/actualizar", tags=["Estado"], dependencies=protegido,
             summary="Actualizar estado directamente (sp_actualizar_estado) 🔒")
async def actualizar_estado(datos: EstadoActualizar):
    fila = await asyncio.to_thread(ServicioEstado.actualizar, datos.id_vehiculo, datos.id_comando, datos.conectado)
    return {"status": "success", "message": "Estado actualizado", **fila}


@router.post("/vehiculos/movimiento", tags=["Estado"],
             summary="Movimiento individual (sp_actualizar_estado + sp_registrar_historial en una transacción)",
             description="Valida vehículo y comando, actualiza el estado y registra el historial en **una "
                         "transacción**. Después notifica `NUEVO_MOVIMIENTO` a todos los clientes WSS del vehículo.")
async def registrar_movimiento(datos: MovimientoIndividual):
    estado = await asyncio.to_thread(ServicioMovimiento.registrar_individual,
                                     datos.vehiculo_id, datos.comando_id, datos.origen)
    notificados = await administrador.difundir(datos.vehiculo_id, {
        "evento": "NUEVO_MOVIMIENTO", "vehiculo_id": datos.vehiculo_id,
        "comando_id": datos.comando_id, "comando": estado["comando"], "codigo": estado["codigo"],
        "origen": datos.origen, "fecha_actualizacion": estado["fecha_actualizacion"]})
    return {"status": "success", "message": "Estado actualizado e historial registrado",
            "estado": estado, "clientes_wss_notificados": notificados}


# ------------------------------- HISTORIAL ------------------------------
@router.get("/vehiculos/{vehiculo_id}/historial", tags=["Historial"],
            summary="Últimos 10 movimientos individuales (sp_obtener_historial)",
            description="Máximo 10 registros, del más reciente al más antiguo. No incluye movimientos DEMO.")
async def obtener_historial(vehiculo_id: int):
    filas = await asyncio.to_thread(ServicioHistorial.recientes, vehiculo_id)
    return {"vehiculo_id": vehiculo_id, "total": len(filas), "historial": filas}


@router.post("/historial/registrar", tags=["Historial"], status_code=status.HTTP_201_CREATED,
             dependencies=protegido, summary="Registrar historial directamente (sp_registrar_historial) 🔒")
async def registrar_historial(datos: HistorialRegistrar):
    fila = await asyncio.to_thread(ServicioHistorial.registrar, datos.id_vehiculo, datos.id_comando, datos.origen)
    return {"status": "success", "message": "Movimiento registrado en historial", **fila}