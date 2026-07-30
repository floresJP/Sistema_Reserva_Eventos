# schemas/tematica_schema.py
from typing import Optional
from pydantic import BaseModel, field_validator
from validaciones.validadores import ValidadorTextoGeneral, ValidadorPrecio

class TematicaCrear(BaseModel):
    descripcion: str
    precio_base: float

    @field_validator("descripcion")
    @classmethod
    
    def validar_descripcion(cls, valor):
        return ValidadorTextoGeneral("descripcion").validar(valor)

    @field_validator("precio_base")
    @classmethod
    
    def validar_precio_base(cls, valor):
        return ValidadorPrecio("precio_base").validar(valor)

class TematicaActualizar(BaseModel):
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    estado: Optional[str] = None

    @field_validator("descripcion")
    @classmethod
    
    def validar_descripcion(cls, valor):
        if valor is None:
            return valor
        return ValidadorTextoGeneral("descripcion").validar(valor)

    @field_validator("precio_base")
    @classmethod
    
    def validar_precio_base(cls, valor):
        if valor is None:
            return valor
        return ValidadorPrecio("precio_base").validar(valor)

    @field_validator("estado")
    @classmethod
    
    def validar_estado(cls, valor):
        if valor is None:
            return valor
        valor = valor.strip()
        if valor not in ("Disponible", "No Disponible"):
            raise ValueError("El estado debe ser 'Disponible' o 'No Disponible'")
        return valor

class TematicaRespuesta(BaseModel):
    id_tematica: str
    descripcion: str
    precio_base: float
    estado: str