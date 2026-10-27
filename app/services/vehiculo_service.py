"""Servicios de Vehículos (5 SP) y Comandos (4 SP)."""
from typing import List, Optional
from app.core.errores import ErrorNegocio
from app.services.base_service import ServicioBase, Fila


class ServicioVehiculo(ServicioBase):
    @classmethod
    def listar(cls) -> List[Fila]:                                    # sp_obtener_vehiculos
        return cls._consultar("sp_obtener_vehiculos")

    @classmethod
    def obtener(cls, id_vehiculo: int) -> Fila:                       # sp_obtener_vehiculo
        filas = cls._consultar("sp_obtener_vehiculo", [id_vehiculo])
        if not filas:
            raise ErrorNegocio(f"El vehículo {id_vehiculo} no existe", 404)
        return filas[0]

    @classmethod
    def crear(cls, nombre, modelo, descripcion, microcontrolador) -> Fila:   # sp_crear_vehiculo
        return cls._ejecutar("sp_crear_vehiculo", [nombre, modelo, descripcion, microcontrolador])

    @classmethod
    def actualizar(cls, id_vehiculo, nombre, modelo, descripcion, microcontrolador, activo) -> Fila:
        return cls._ejecutar("sp_actualizar_vehiculo",                # sp_actualizar_vehiculo
                             [id_vehiculo, nombre, modelo, descripcion, microcontrolador, int(activo)])

    @classmethod
    def eliminar(cls, id_vehiculo: int) -> Fila:                      # sp_eliminar_vehiculo
        return cls._ejecutar("sp_eliminar_vehiculo", [id_vehiculo])


class ServicioComando(ServicioBase):
    @classmethod
    def listar(cls, id_vehiculo: int) -> List[Fila]:                  # sp_obtener_comandos_vehiculo
        ServicioVehiculo.obtener(id_vehiculo)  # 404 si el vehículo no existe
        return cls._consultar("sp_obtener_comandos_vehiculo", [id_vehiculo])

    @classmethod
    def crear(cls, id_vehiculo, nombre, codigo, descripcion) -> Fila:        # sp_crear_comando
        return cls._ejecutar("sp_crear_comando", [id_vehiculo, nombre, codigo, descripcion])

    @classmethod
    def actualizar(cls, id_comando, nombre, codigo, descripcion, activo) -> Fila:  # sp_actualizar_comando
        return cls._ejecutar("sp_actualizar_comando", [id_comando, nombre, codigo, descripcion, int(activo)])

    @classmethod
    def eliminar(cls, id_comando: int) -> Fila:                       # sp_eliminar_comando
        return cls._ejecutar("sp_eliminar_comando", [id_comando])

    @classmethod
    def buscar_por_nombre(cls, id_vehiculo: int, nombre: str) -> Optional[Fila]:
        """Auxiliar (usa sp_obtener_comandos_vehiculo): ej. localizar 'DETENER'."""
        for c in cls._consultar("sp_obtener_comandos_vehiculo", [id_vehiculo]):
            if c["nombre"].upper() == nombre.upper() and c["activo"]:
                return c
        return None