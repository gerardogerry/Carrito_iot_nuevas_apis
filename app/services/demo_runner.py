"""Ejecución asíncrona de una DEMO: transmite N movimientos por WebSocket con sus tiempos.
Regla: actualiza estado_vehiculo en cada paso, pero NO escribe en historial_comandos."""
import asyncio
import logging
import time
from typing import Dict, Optional
from app.core.errores import ErrorNegocio
from app.services.demo_service import ServicioDemo, ServicioMovimientoDemo
from app.services.movimiento_service import ServicioEstado
from app.services.vehiculo_service import ServicioComando, ServicioVehiculo
from app.websocket.websocket_manager import AdministradorConexiones, administrador

log = logging.getLogger("vehiculo_iot")


class GestorDemos:
    """Garantiza una sola DEMO por vehículo, la ejecuta en segundo plano y permite cancelarla."""

    def __init__(self, ws: AdministradorConexiones) -> None:
        self._ws = ws
        # vehiculo_id -> tarea asyncio (None = plaza reservada mientras se validan datos)
        self._activas: Dict[int, Optional[asyncio.Task]] = {}

    def en_ejecucion(self, vehiculo_id: int) -> bool:
        return vehiculo_id in self._activas

    async def iniciar(self, vehiculo_id: int, demo_id: int) -> dict:
        if self.en_ejecucion(vehiculo_id):
            raise ErrorNegocio(f"El vehículo {vehiculo_id} ya tiene una DEMO en ejecución", 409)
        self._activas[vehiculo_id] = None  # reserva inmediata: evita dos POST simultáneos
        try:
            vehiculo = await asyncio.to_thread(ServicioVehiculo.obtener, vehiculo_id)
            if not vehiculo["activo"]:
                raise ErrorNegocio("El vehículo está inactivo", 400)
            demo = await asyncio.to_thread(ServicioDemo.obtener, vehiculo_id, demo_id)
            if not demo["activo"]:
                raise ErrorNegocio("La DEMO está inactiva", 400)
            movimientos = await asyncio.to_thread(ServicioMovimientoDemo.listar, demo_id)
            if not movimientos:
                raise ErrorNegocio("La DEMO no tiene movimientos", 400)
            self._activas[vehiculo_id] = asyncio.create_task(
                self._ejecutar(vehiculo_id, demo, movimientos))
        except BaseException:
            self._activas.pop(vehiculo_id, None)
            raise
        total_ms = sum(m["pausa_ms"] + m["duracion_ms"] for m in movimientos)
        return {"status": "iniciada", "vehiculo_id": vehiculo_id, "demo_id": demo_id,
                "demo": demo["nombre"], "total_movimientos": len(movimientos),
                "duracion_estimada_ms": total_ms}

    async def cancelar(self, vehiculo_id: int) -> dict:
        tarea = self._activas.get(vehiculo_id)
        if tarea is None:
            raise ErrorNegocio("No hay una DEMO en ejecución para ese vehículo", 404)
        tarea.cancel()
        await asyncio.wait({tarea}, timeout=5)
        return {"status": "cancelada", "vehiculo_id": vehiculo_id}

    async def cancelar_todas(self) -> None:
        tareas = [t for t in self._activas.values() if t is not None]
        for t in tareas:
            t.cancel()
        if tareas:
            await asyncio.wait(tareas, timeout=5)

    async def _ejecutar(self, vehiculo_id: int, demo: dict, movimientos: list) -> None:
        total = len(movimientos)
        inicio = time.monotonic()
        ultimo_orden = 0
        try:
            await self._ws.difundir(vehiculo_id, {
                "evento": "INICIO_DEMO", "vehiculo_id": vehiculo_id, "demo_id": demo["id_demo"],
                "demo": demo["nombre"], "total_movimientos": total})
            for indice, mov in enumerate(movimientos, start=1):
                if mov["pausa_ms"] > 0:
                    await asyncio.sleep(mov["pausa_ms"] / 1000)
                # Solo estado (sp_actualizar_estado). NO se registra historial.
                await asyncio.to_thread(ServicioEstado.actualizar, vehiculo_id, mov["id_comando"], True)
                ultimo_orden = mov["orden"]
                await self._ws.difundir(vehiculo_id, {
                    "evento": "MOVIMIENTO_DEMO", "vehiculo_id": vehiculo_id, "demo_id": demo["id_demo"],
                    "indice": indice, "total_movimientos": total, "orden": mov["orden"],
                    "comando_id": mov["id_comando"], "comando": mov["comando"], "codigo": mov["codigo"],
                    "duracion_ms": mov["duracion_ms"], "pausa_ms": mov["pausa_ms"],
                    "transcurrido_ms": int((time.monotonic() - inicio) * 1000)})
                await asyncio.sleep(mov["duracion_ms"] / 1000)
            await self._ws.difundir(vehiculo_id, {
                "evento": "FIN_DEMO", "vehiculo_id": vehiculo_id, "demo_id": demo["id_demo"],
                "total_movimientos": total, "duracion_real_ms": int((time.monotonic() - inicio) * 1000)})
        except asyncio.CancelledError:
            detener = await self._detener(vehiculo_id)
            await self._ws.difundir(vehiculo_id, {
                "evento": "DEMO_CANCELADA", "vehiculo_id": vehiculo_id, "demo_id": demo["id_demo"],
                "ultimo_orden_ejecutado": ultimo_orden, "comando_detener": detener})
        except Exception as e:  # fallo inesperado: se avisa a los clientes y se libera el vehículo
            log.error("Fallo en DEMO %s: %s", demo["id_demo"], e)
            await self._ws.difundir(vehiculo_id, {
                "evento": "ERROR_DEMO", "vehiculo_id": vehiculo_id, "demo_id": demo["id_demo"],
                "mensaje": "La DEMO se interrumpió por un error interno"})
        finally:
            self._activas.pop(vehiculo_id, None)

    async def _detener(self, vehiculo_id: int) -> Optional[str]:
        """Al cancelar deja el estado en DETENER (si existe ese comando). No toca el historial."""
        try:
            cmd = await asyncio.to_thread(ServicioComando.buscar_por_nombre, vehiculo_id, "DETENER")
            if cmd:
                await asyncio.to_thread(ServicioEstado.actualizar, vehiculo_id, cmd["id_comando"], True)
                return cmd["nombre"]
        except Exception as e:
            log.error("No se pudo dejar el vehículo en DETENER: %s", e)
        return None


gestor_demos = GestorDemos(administrador)