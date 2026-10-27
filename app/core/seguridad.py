"""Protección de operaciones sensibles con una API Key en el encabezado X-API-Key."""
import secrets
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from app.core.config import configuracion

_encabezado = APIKeyHeader(name="X-API-Key", auto_error=False,
                           description="Clave requerida para crear, actualizar, eliminar y cancelar DEMO")


async def requerir_api_key(clave: str = Security(_encabezado)) -> None:
    esperada = configuracion.api_key
    if not clave or not esperada or not secrets.compare_digest(clave, esperada):
        raise HTTPException(status_code=401, detail="API Key inválida o ausente (encabezado X-API-Key)")


protegido = [Depends(requerir_api_key)]