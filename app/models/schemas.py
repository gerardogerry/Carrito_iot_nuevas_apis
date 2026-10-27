"""Esquemas Pydantic: validan las entradas de la API antes de tocar la base de datos."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Solo letras, números, guion, guion bajo, punto y espacio (evita caracteres raros en origen)
PATRON_ORIGEN = r"^[A-Za-z0-9_\-. ]+$"


class _ModeloBase(BaseModel):
    """Limpia espacios en todos los textos recibidos."""

    @field_validator("*", mode="before")
    @classmethod
    def _limpiar_texto(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


# ---------------------------- Vehículos ----------------------------
class VehiculoCrear(_ModeloBase):
    nombre: str = Field(..., min_length=1, max_length=80, examples=["Excavadora IoT"])
    modelo: Optional[str] = Field(None, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    microcontrolador: Optional[str] = Field(None, max_length=50, examples=["ESP8266"])


class VehiculoActualizar(VehiculoCrear):
    id_vehiculo: int = Field(..., gt=0)
    activo: bool = True


class VehiculoEliminar(_ModeloBase):
    id_vehiculo: int = Field(..., gt=0)


# ----------------------------- Comandos ----------------------------
class ComandoCrear(_ModeloBase):
    id_vehiculo: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=1, max_length=60, examples=["ADELANTE"])
    codigo: int = Field(..., ge=0, le=65535)
    descripcion: Optional[str] = Field(None, max_length=255)


class ComandoActualizar(_ModeloBase):
    id_comando: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=1, max_length=60)
    codigo: int = Field(..., ge=0, le=65535)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class ComandoEliminar(_ModeloBase):
    id_comando: int = Field(..., gt=0)


# ------------------------ Estado y movimientos ----------------------
class EstadoActualizar(_ModeloBase):
    id_vehiculo: int = Field(..., gt=0)
    id_comando: Optional[int] = Field(None, gt=0)
    conectado: bool = True


class MovimientoIndividual(_ModeloBase):
    """POST /api/vehiculos/movimiento"""
    vehiculo_id: int = Field(..., gt=0, examples=[1])
    comando_id: int = Field(..., gt=0, examples=[1])
    origen: str = Field("API", min_length=1, max_length=30, pattern=PATRON_ORIGEN, examples=["ThunderClient"])


class HistorialRegistrar(_ModeloBase):
    id_vehiculo: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    origen: str = Field("MANUAL", min_length=1, max_length=30, pattern=PATRON_ORIGEN)


# ------------------------------- DEMO -------------------------------
class DemoCrear(_ModeloBase):
    id_vehiculo: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=1, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)


class DemoActualizar(_ModeloBase):
    id_demo: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=1, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True


class DemoEliminar(_ModeloBase):
    id_demo: int = Field(..., gt=0)


class MovimientoDemoAgregar(_ModeloBase):
    id_demo: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    orden: int = Field(..., ge=1)
    duracion_ms: int = Field(..., ge=1, le=600_000)
    pausa_ms: int = Field(0, ge=0, le=600_000)


class MovimientoDemoActualizar(_ModeloBase):
    id_demo_movimiento: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    orden: int = Field(..., ge=1)
    duracion_ms: int = Field(..., ge=1, le=600_000)
    pausa_ms: int = Field(0, ge=0, le=600_000)


class MovimientoDemoEliminar(_ModeloBase):
    id_demo_movimiento: int = Field(..., gt=0)


class DemoIniciar(_ModeloBase):
    """POST /api/vehiculos/demo"""
    vehiculo_id: int = Field(..., gt=0, examples=[1])
    demo_id: int = Field(..., gt=0, examples=[3])


class DemoCancelar(_ModeloBase):
    """POST /api/vehiculos/demo/cancelar"""
    vehiculo_id: int = Field(..., gt=0, examples=[1])