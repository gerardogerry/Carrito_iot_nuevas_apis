"""Configuración central: lee las variables de entorno (.env) una sola vez."""
import os
from dotenv import load_dotenv

load_dotenv()


class Configuracion:
    """Agrupa los parámetros de la aplicación. Nunca se imprimen ni se devuelven por la API."""

    def __init__(self) -> None:
        self.db_host: str = os.getenv("DB_HOST", "127.0.0.1")
        self.db_port: int = int(os.getenv("DB_PORT", "3306"))
        self.db_user: str = os.getenv("DB_USER", "")
        self.db_password: str = os.getenv("DB_PASSWORD", "")
        self.db_name: str = os.getenv("DB_NAME", "vehiculo_iot")
        self.db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
        self.api_key: str = os.getenv("API_KEY", "")

    def validar(self) -> None:
        faltantes = [n for n, v in (("DB_USER", self.db_user),
                                    ("DB_PASSWORD", self.db_password),
                                    ("API_KEY", self.api_key)) if not v]
        if faltantes:
            raise RuntimeError(f"Faltan variables en .env: {', '.join(faltantes)}")


configuracion = Configuracion()