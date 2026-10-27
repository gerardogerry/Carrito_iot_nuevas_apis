"""Canal WebSocket por vehículo: /ws/vehiculo/{vehiculo_id}  (WSS detrás de Nginx + HTTPS)."""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.errores import ErrorNegocio
from app.services.demo_runner import gestor_demos
from app.services.movimiento_service import ServicioEstado
from app.websocket.websocket_manager import administrador

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/vehiculo/{vehiculo_id}")
async def canal_vehiculo(websocket: WebSocket, vehiculo_id: int):
    await websocket.accept()
    try:
        estado = await asyncio.to_thread(ServicioEstado.obtener, vehiculo_id)
    except ErrorNegocio as e:
        await administrador.enviar(websocket, {"evento": "ERROR", "mensaje": e.mensaje})
        await websocket.close(code=4404)
        return
    except Exception:
        await administrador.enviar(websocket, {"evento": "ERROR", "mensaje": "Error interno"})
        await websocket.close(code=1011)
        return

    administrador.registrar(websocket, vehiculo_id)
    try:
        # Al conectar: último estado guardado en RDS
        await administrador.enviar(websocket, {
            "evento": "ESTADO_ACTUAL", "vehiculo_id": vehiculo_id, "estado": estado,
            "demo_en_ejecucion": gestor_demos.en_ejecucion(vehiculo_id)})
        while True:
            texto = await websocket.receive_text()
            if texto.strip().lower() == "ping":
                await administrador.enviar(websocket, {"evento": "PONG"})
    except WebSocketDisconnect:
        pass
    finally:
        administrador.desconectar(websocket, vehiculo_id)