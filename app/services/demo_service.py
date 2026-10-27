"""Servicios de DEMO (4 SP) y movimientos de DEMO (4 SP)."""
from typing import List
from app.core.errores import ErrorNegocio
from app.services.base_service import ServicioBase, Fila


class ServicioDemo(ServicioBase):
    @classmethod
    def listar(cls, id_vehiculo: int) -> List[Fila]:                  # sp_obtener_demos
        return cls._consultar("sp_obtener_demos", [id_vehiculo])

    @classmethod
    def obtener(cls, id_vehiculo: int, id_demo: int) -> Fila:
        """Auxiliar: la DEMO debe existir y pertenecer al vehículo."""
        for d in cls.listar(id_vehiculo):
            if d["id_demo"] == id_demo:
                return d
        raise ErrorNegocio(f"La DEMO {id_demo} no existe para el vehículo {id_vehiculo}", 404)

    @classmethod
    def crear(cls, id_vehiculo, nombre, descripcion) -> Fila:         # sp_crear_demo
        return cls._ejecutar("sp_crear_demo", [id_vehiculo, nombre, descripcion])

    @classmethod
    def actualizar(cls, id_demo, nombre, descripcion, activo) -> Fila:        # sp_actualizar_demo
        return cls._ejecutar("sp_actualizar_demo", [id_demo, nombre, descripcion, int(activo)])

    @classmethod
    def eliminar(cls, id_demo: int) -> Fila:                          # sp_eliminar_demo
        return cls._ejecutar("sp_eliminar_demo", [id_demo])


class ServicioMovimientoDemo(ServicioBase):
    @classmethod
    def listar(cls, id_demo: int) -> List[Fila]:                      # sp_obtener_movimientos_demo
        return cls._consultar("sp_obtener_movimientos_demo", [id_demo])

    @classmethod
    def agregar(cls, id_demo, id_comando, orden, duracion_ms, pausa_ms) -> Fila:   # sp_agregar_movimiento_demo
        return cls._ejecutar("sp_agregar_movimiento_demo", [id_demo, id_comando, orden, duracion_ms, pausa_ms])

    @classmethod
    def actualizar(cls, id_mov, id_comando, orden, duracion_ms, pausa_ms) -> Fila:  # sp_actualizar_movimiento_demo
        return cls._ejecutar("sp_actualizar_movimiento_demo", [id_mov, id_comando, orden, duracion_ms, pausa_ms])

    @classmethod
    def eliminar(cls, id_mov: int) -> Fila:                           # sp_eliminar_movimiento_demo
        return cls._ejecutar("sp_eliminar_movimiento_demo", [id_mov])