"""Acceso a MySQL/Amazon RDS mediante un pool de conexiones (POO + context manager)."""
import threading
import time
from mysql.connector import pooling
from app.core.config import configuracion


class GestorConexiones:
    """Crea (una sola vez) y entrega conexiones de un pool."""

    _pool = None
    _candado = threading.Lock()

    @classmethod
    def _obtener_pool(cls):
        if cls._pool is None:
            with cls._candado:
                if cls._pool is None:
                    cls._pool = pooling.MySQLConnectionPool(
                        pool_name="vehiculo_iot_pool",
                        pool_size=configuracion.db_pool_size,
                        host=configuracion.db_host,
                        port=configuracion.db_port,
                        user=configuracion.db_user,
                        password=configuracion.db_password,
                        database=configuracion.db_name,
                        charset="utf8mb4",
                        connection_timeout=10,
                    )
        return cls._pool

    @classmethod
    def obtener(cls):
        pool = cls._obtener_pool()
        for _ in range(25):  # espera hasta ~5 s si el pool está ocupado
            try:
                conexion = pool.get_connection()
                conexion.ping(reconnect=True, attempts=3, delay=1)
                return conexion
            except pooling.PoolError:
                time.sleep(0.2)
        raise RuntimeError("No hay conexiones disponibles en el pool")


class ConexionBD:
    """Uso:  with ConexionBD() as conexion: ...   (devuelve la conexión al pool al salir)."""

    def __init__(self) -> None:
        self.conexion = None

    def __enter__(self):
        self.conexion = GestorConexiones.obtener()
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conexion is not None:
            try:
                if exc_type is not None:
                    self.conexion.rollback()
            finally:
                self.conexion.close()
        return False