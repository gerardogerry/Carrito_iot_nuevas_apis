"""Errores de negocio y traducción de errores de MySQL a códigos HTTP."""
import logging
from mysql.connector import Error as ErrorMySQL

log = logging.getLogger("vehiculo_iot")


class ErrorNegocio(Exception):
    """Error esperado (dato inválido, no existe, conflicto). Se responde con su código HTTP."""

    def __init__(self, mensaje: str, codigo_http: int = 400) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_http = codigo_http


# MYSQL_ERRNO definidos en los Stored Procedures con SIGNAL
_ERRNO_SP = {5400: 400, 5404: 404, 5409: 409}


def traducir_error(e: ErrorMySQL) -> Exception:
    """Convierte un error de MySQL en ErrorNegocio (si es esperado) o error genérico (si no)."""
    if e.errno in _ERRNO_SP:
        return ErrorNegocio(e.msg.split(": ", 1)[-1] if e.msg else "Error de validación", _ERRNO_SP[e.errno])
    if e.errno == 1062:
        return ErrorNegocio("Registro duplicado", 409)
    if e.errno == 1451:
        return ErrorNegocio("No se puede eliminar: el registro está en uso", 409)
    if e.errno == 1452:
        return ErrorNegocio("Referencia inválida (el registro relacionado no existe)", 400)
    # Error inesperado: se registra en el log del servidor y NO se expone el detalle al cliente
    log.error("Error de base de datos (errno=%s): %s", e.errno, e.msg)
    return RuntimeError("Error interno de base de datos")