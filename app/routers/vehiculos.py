"""Vehículos (5 SP) y Comandos (4 SP)."""
import asyncio
from fastapi import APIRouter, status
from app.core.seguridad import protegido
from app.models.schemas import (VehiculoCrear, VehiculoActualizar, VehiculoEliminar,
                                ComandoCrear, ComandoActualizar, ComandoEliminar)
from app.services.vehiculo_service import ServicioVehiculo, ServicioComando

router = APIRouter(prefix="/api")


# ------------------------------ VEHÍCULOS ------------------------------
@router.get("/vehiculos", tags=["Vehículos"], summary="Listar vehículos (sp_obtener_vehiculos)")
async def listar_vehiculos():
    filas = await asyncio.to_thread(ServicioVehiculo.listar)
    return {"total": len(filas), "vehiculos": filas}


@router.get("/vehiculos/{vehiculo_id}", tags=["Vehículos"], summary="Obtener un vehículo (sp_obtener_vehiculo)")
async def obtener_vehiculo(vehiculo_id: int):
    return await asyncio.to_thread(ServicioVehiculo.obtener, vehiculo_id)


@router.post("/vehiculos/crear", tags=["Vehículos"], status_code=status.HTTP_201_CREATED,
             dependencies=protegido, summary="Crear vehículo (sp_crear_vehiculo) 🔒")
async def crear_vehiculo(datos: VehiculoCrear):
    fila = await asyncio.to_thread(ServicioVehiculo.crear, datos.nombre, datos.modelo,
                                   datos.descripcion, datos.microcontrolador)
    return {"status": "success", "message": "Vehículo creado", **fila}


@router.post("/vehiculos/actualizar", tags=["Vehículos"], dependencies=protegido,
             summary="Actualizar vehículo (sp_actualizar_vehiculo) 🔒")
async def actualizar_vehiculo(datos: VehiculoActualizar):
    fila = await asyncio.to_thread(ServicioVehiculo.actualizar, datos.id_vehiculo, datos.nombre, datos.modelo,
                                   datos.descripcion, datos.microcontrolador, datos.activo)
    return {"status": "success", "message": "Vehículo actualizado", **fila}


@router.post("/vehiculos/eliminar", tags=["Vehículos"], dependencies=protegido,
             summary="Eliminar vehículo (sp_eliminar_vehiculo) 🔒")
async def eliminar_vehiculo(datos: VehiculoEliminar):
    fila = await asyncio.to_thread(ServicioVehiculo.eliminar, datos.id_vehiculo)
    return {"status": "success", "message": "Vehículo eliminado", **fila}


# ------------------------------- COMANDOS ------------------------------
@router.get("/vehiculos/{vehiculo_id}/comandos", tags=["Comandos"],
            summary="Comandos de un vehículo (sp_obtener_comandos_vehiculo)")
async def listar_comandos(vehiculo_id: int):
    filas = await asyncio.to_thread(ServicioComando.listar, vehiculo_id)
    return {"vehiculo_id": vehiculo_id, "total": len(filas), "comandos": filas}


@router.post("/comandos/crear", tags=["Comandos"], status_code=status.HTTP_201_CREATED,
             dependencies=protegido, summary="Crear comando (sp_crear_comando) 🔒")
async def crear_comando(datos: ComandoCrear):
    fila = await asyncio.to_thread(ServicioComando.crear, datos.id_vehiculo, datos.nombre,
                                   datos.codigo, datos.descripcion)
    return {"status": "success", "message": "Comando creado", **fila}


@router.post("/comandos/actualizar", tags=["Comandos"], dependencies=protegido,
             summary="Actualizar comando (sp_actualizar_comando) 🔒")
async def actualizar_comando(datos: ComandoActualizar):
    fila = await asyncio.to_thread(ServicioComando.actualizar, datos.id_comando, datos.nombre,
                                   datos.codigo, datos.descripcion, datos.activo)
    return {"status": "success", "message": "Comando actualizado", **fila}


@router.post("/comandos/eliminar", tags=["Comandos"], dependencies=protegido,
             summary="Eliminar comando (sp_eliminar_comando) 🔒")
async def eliminar_comando(datos: ComandoEliminar):
    fila = await asyncio.to_thread(ServicioComando.eliminar, datos.id_comando)
    return {"status": "success", "message": "Comando eliminado", **fila}