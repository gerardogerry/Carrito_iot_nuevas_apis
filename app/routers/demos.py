"""DEMO (4 SP), movimientos DEMO (4 SP) y ejecución en tiempo real por WSS."""
import asyncio
from fastapi import APIRouter, status
from app.core.seguridad import protegido
from app.models.schemas import (DemoCrear, DemoActualizar, DemoEliminar, MovimientoDemoAgregar,
                                MovimientoDemoActualizar, MovimientoDemoEliminar, DemoIniciar, DemoCancelar)
from app.services.demo_runner import gestor_demos
from app.services.demo_service import ServicioDemo, ServicioMovimientoDemo
from app.services.vehiculo_service import ServicioVehiculo

router = APIRouter(prefix="/api")


@router.get("/vehiculos/{vehiculo_id}/demos", tags=["DEMO"], summary="Listar DEMO (sp_obtener_demos)")
async def listar_demos(vehiculo_id: int):
    await asyncio.to_thread(ServicioVehiculo.obtener, vehiculo_id)  # 404 si no existe
    filas = await asyncio.to_thread(ServicioDemo.listar, vehiculo_id)
    return {"vehiculo_id": vehiculo_id, "total": len(filas), "demos": filas}


@router.post("/demos/crear", tags=["DEMO"], status_code=status.HTTP_201_CREATED, dependencies=protegido,
             summary="Crear DEMO (sp_crear_demo) 🔒")
async def crear_demo(datos: DemoCrear):
    fila = await asyncio.to_thread(ServicioDemo.crear, datos.id_vehiculo, datos.nombre, datos.descripcion)
    return {"status": "success", "message": "DEMO creada", **fila}


@router.post("/demos/actualizar", tags=["DEMO"], dependencies=protegido,
             summary="Actualizar DEMO (sp_actualizar_demo) 🔒")
async def actualizar_demo(datos: DemoActualizar):
    fila = await asyncio.to_thread(ServicioDemo.actualizar, datos.id_demo, datos.nombre,
                                   datos.descripcion, datos.activo)
    return {"status": "success", "message": "DEMO actualizada", **fila}


@router.post("/demos/eliminar", tags=["DEMO"], dependencies=protegido,
             summary="Eliminar DEMO (sp_eliminar_demo) 🔒")
async def eliminar_demo(datos: DemoEliminar):
    fila = await asyncio.to_thread(ServicioDemo.eliminar, datos.id_demo)
    return {"status": "success", "message": "DEMO eliminada", **fila}


@router.get("/demos/{demo_id}/movimientos", tags=["DEMO"],
            summary="Movimientos de una DEMO (sp_obtener_movimientos_demo)")
async def listar_movimientos_demo(demo_id: int):
    filas = await asyncio.to_thread(ServicioMovimientoDemo.listar, demo_id)
    return {"demo_id": demo_id, "total": len(filas), "movimientos": filas}


@router.post("/demos/movimientos/agregar", tags=["DEMO"], status_code=status.HTTP_201_CREATED,
             dependencies=protegido, summary="Agregar movimiento a DEMO (sp_agregar_movimiento_demo) 🔒")
async def agregar_movimiento_demo(datos: MovimientoDemoAgregar):
    fila = await asyncio.to_thread(ServicioMovimientoDemo.agregar, datos.id_demo, datos.id_comando,
                                   datos.orden, datos.duracion_ms, datos.pausa_ms)
    return {"status": "success", "message": "Movimiento agregado a la DEMO", **fila}


@router.post("/demos/movimientos/actualizar", tags=["DEMO"], dependencies=protegido,
             summary="Actualizar movimiento de DEMO (sp_actualizar_movimiento_demo) 🔒")
async def actualizar_movimiento_demo(datos: MovimientoDemoActualizar):
    fila = await asyncio.to_thread(ServicioMovimientoDemo.actualizar, datos.id_demo_movimiento,
                                   datos.id_comando, datos.orden, datos.duracion_ms, datos.pausa_ms)
    return {"status": "success", "message": "Movimiento de DEMO actualizado", **fila}


@router.post("/demos/movimientos/eliminar", tags=["DEMO"], dependencies=protegido,
             summary="Eliminar movimiento de DEMO (sp_eliminar_movimiento_demo) 🔒")
async def eliminar_movimiento_demo(datos: MovimientoDemoEliminar):
    fila = await asyncio.to_thread(ServicioMovimientoDemo.eliminar, datos.id_demo_movimiento)
    return {"status": "success", "message": "Movimiento de DEMO eliminado", **fila}


# ----------------------- Ejecución en tiempo real -----------------------
@router.post("/vehiculos/demo", tags=["DEMO"], status_code=status.HTTP_202_ACCEPTED,
             summary="Iniciar DEMO en tiempo real (sp_obtener_movimientos_demo + sp_actualizar_estado)",
             description="Responde **202** de inmediato y transmite por WSS: `INICIO_DEMO`, N × `MOVIMIENTO_DEMO` "
                         "(respetando pausa y duración) y `FIN_DEMO`. Actualiza el último estado pero **no** "
                         "escribe en el historial. Solo una DEMO por vehículo (409 si ya hay una).")
async def iniciar_demo(datos: DemoIniciar):
    return await gestor_demos.iniciar(datos.vehiculo_id, datos.demo_id)


@router.post("/vehiculos/demo/cancelar", tags=["DEMO"], dependencies=protegido,
             summary="Cancelar la DEMO en ejecución 🔒",
             description="Detiene los pasos posteriores, deja el estado en DETENER y emite `DEMO_CANCELADA` por WSS.")
async def cancelar_demo(datos: DemoCancelar):
    return await gestor_demos.cancelar(datos.vehiculo_id)


@router.get("/vehiculos/{vehiculo_id}/demo/estado", tags=["DEMO"], summary="¿Hay una DEMO ejecutándose?")
async def estado_demo(vehiculo_id: int):
    return {"vehiculo_id": vehiculo_id, "demo_en_ejecucion": gestor_demos.en_ejecucion(vehiculo_id)}