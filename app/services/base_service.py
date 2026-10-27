"""Clase base de los servicios: ejecuta Stored Procedures y normaliza resultados."""
from typing import Any, Dict, List, Sequence, Tuple
from mysql.connector import Error as ErrorMySQL
from app.core.database import ConexionBD
from app.core.errores import traducir_error

Fila = Dict[str, Any]
_CAMPOS_BOOL = ("activo", "conectado")


class ServicioBase:
    """Todo acceso a datos pasa por aquí: CALL a un SP, commit/rollback y traducción de errores."""

    @staticmethod
    def _normalizar(filas: List[Fila]) -> List[Fila]:
        for fila in filas:
            for campo in _CAMPOS_BOOL:
                if campo in fila and fila[campo] is not None:
                    fila[campo] = bool(fila[campo])
        return filas

    @staticmethod
    def _leer_resultados(cursor) -> List[Fila]:
        filas: List[Fila] = []
        for resultado in cursor.stored_results():
            filas.extend(resultado.fetchall())
        return filas

    @classmethod
    def _consultar(cls, sp: str, params: Sequence[Any] = ()) -> List[Fila]:
        """CALL de solo lectura (GET)."""
        with ConexionBD() as conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.callproc(sp, list(params))
                filas = cls._leer_resultados(cursor)
                cursor.close()
                return cls._normalizar(filas)
            except ErrorMySQL as e:
                raise traducir_error(e)

    @classmethod
    def _ejecutar(cls, sp: str, params: Sequence[Any] = ()) -> Fila:
        """CALL de escritura con COMMIT; devuelve la primera fila (id afectado)."""
        return cls._transaccion([(sp, params)])[0]

    @classmethod
    def _transaccion(cls, llamadas: List[Tuple[str, Sequence[Any]]]) -> List[Fila]:
        """Varios SP en UNA sola transacción: o se confirman todos o se revierten todos."""
        with ConexionBD() as conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                primeras: List[Fila] = []
                for sp, params in llamadas:
                    cursor.callproc(sp, list(params))
                    filas = cls._leer_resultados(cursor)
                    primeras.append(filas[0] if filas else {})
                conexion.commit()
                cursor.close()
                return primeras
            except ErrorMySQL as e:
                conexion.rollback()
                raise traducir_error(e)