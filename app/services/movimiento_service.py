"""Servicios de Estado (2 SP), Historial (2 SP) y el movimiento individual transaccional."""
from typing import List, Optional
from app.core.errores import ErrorNegocio
from app.services.base_service import ServicioBase, Fila


class ServicioEstado(ServicioBase):
    @classmethod
    def obtener(cls, id_vehiculo: int) -> Fila:                       # sp_obtener_estado
        filas = cls._consultar("sp_obtener_estado", [id_vehiculo])
        if not filas:
            raise ErrorNegocio(f"El vehículo {id_vehiculo} no existe", 404)
        return filas[0]

    @classmethod
    def actualizar(cls, id_vehiculo: int, id_comando: Optional[int], conectado: bool = True) -> Fila:
        return cls._ejecutar("sp_actualizar_estado",                  # sp_actualizar_estado
                             [id_vehiculo, id_comando, int(conectado)])


class ServicioHistorial(ServicioBase):
    @classmethod
    def recientes(cls, id_vehiculo: int) -> List[Fila]:               # sp_obtener_historial
        ServicioEstado.obtener(id_vehiculo)  # 404 si el vehículo no existe
        return cls._consultar("sp_obtener_historial", [id_vehiculo])[:10]

    @classmethod
    def registrar(cls, id_vehiculo: int, id_comando: int, origen: str) -> Fila:   # sp_registrar_historial
        return cls._ejecutar("sp_registrar_historial", [id_vehiculo, id_comando, origen])


class ServicioMovimiento(ServicioBase):
    @classmethod
    def registrar_individual(cls, id_vehiculo: int, id_comando: int, origen: str) -> Fila:
        """sp_actualizar_estado + sp_registrar_historial en UNA transacción.
        Si cualquiera falla (vehículo/comando inválido) se hace ROLLBACK de ambos."""
        cls._transaccion([
            ("sp_actualizar_estado", [id_vehiculo, id_comando, 1]),
            ("sp_registrar_historial", [id_vehiculo, id_comando, origen]),
        ])
        return ServicioEstado.obtener(id_vehiculo)