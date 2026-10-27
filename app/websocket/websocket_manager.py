"""Administra las conexiones WebSocket agrupadas por vehículo."""
from typing import Dict, List
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder


class AdministradorConexiones:
    """Un vehículo = un grupo de clientes. Los mensajes nunca se mezclan entre vehículos."""

    def __init__(self) -> None:
        self._conexiones: Dict[int, List[WebSocket]] = {}

    def registrar(self, websocket: WebSocket, vehiculo_id: int) -> None:
        self._conexiones.setdefault(vehiculo_id, []).append(websocket)

    def desconectar(self, websocket: WebSocket, vehiculo_id: int) -> None:
        grupo = self._conexiones.get(vehiculo_id, [])
        if websocket in grupo:
            grupo.remove(websocket)
        if not grupo:
            self._conexiones.pop(vehiculo_id, None)

    def total(self, vehiculo_id: int) -> int:
        return len(self._conexiones.get(vehiculo_id, []))

    async def enviar(self, websocket: WebSocket, mensaje: dict) -> None:
        # jsonable_encoder convierte datetime/Decimal a texto para que el JSON sea válido
        await websocket.send_json(jsonable_encoder(mensaje))

    async def difundir(self, vehiculo_id: int, mensaje: dict) -> int:
        """Envía el mensaje a TODOS los clientes del vehículo. Devuelve cuántos lo recibieron."""
        enviados = 0
        for ws in list(self._conexiones.get(vehiculo_id, [])):
            try:
                await self.enviar(ws, mensaje)
                enviados += 1
            except Exception:
                self.desconectar(ws, vehiculo_id)  # cliente caído: se limpia
        return enviados


administrador = AdministradorConexiones()