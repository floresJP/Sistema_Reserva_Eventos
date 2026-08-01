# schemas/servicio_adicional_schema.py
from typing import Optional
from pydantic import BaseModel, field_validator
from validaciones.validadores import ValidadorTextoGeneral, ValidadorPrecio

# ──────────────────────────────────────────────────────────────
# SCHEMA PARA CREAR SERVICIO ADICIONAL
# "estado" NO se pide aca: el modelo lo asigna solo como "Activo"
# al crearse (ver modelos/servicio_adicional.py __init__).
# ──────────────────────────────────────────────────────────────
class ServicioAdicionalCrear(BaseModel):
    nombre_servicio_adicional: str
    descripcion: str
    precio: float
    id_reserva: str

    # ValidadorTextoGeneral (a diferencia de ValidadorNombre) SI permite
    # numeros -- util porque nombres de servicio tipo "DJ y sonido 4h"
    # o "Torta 20 personas" son validos.
    @field_validator("nombre_servicio_adicional")
    @classmethod
    def validar_nombre(cls, valor):
        return ValidadorTextoGeneral("nombre_servicio_adicional").validar(valor)

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor):
        return ValidadorTextoGeneral("descripcion").validar(valor)

    @field_validator("precio")
    @classmethod
    def validar_precio(cls, valor):
        return ValidadorPrecio("precio").validar(valor)


# ──────────────────────────────────────────────────────────────
# SCHEMA PARA ACTUALIZAR SERVICIO ADICIONAL
# Aqui SI se permite editar "estado" (a diferencia de Reserva),
# porque en este modelo el cambio Activo/Inactivo es un simple
# toggle sin reglas de transicion como las de Reserva
# (Pendiente -> Confirmada -> Completada).
# ──────────────────────────────────────────────────────────────
class ServicioAdicionalActualizar(BaseModel):
    nombre_servicio_adicional: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    estado: Optional[str] = None

    @field_validator("nombre_servicio_adicional")
    @classmethod
    def validar_nombre(cls, valor):
        if valor is None:
            return valor
        return ValidadorTextoGeneral("nombre_servicio_adicional").validar(valor)

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor):
        if valor is None:
            return valor
        return ValidadorTextoGeneral("descripcion").validar(valor)

    @field_validator("precio")
    @classmethod
    def validar_precio(cls, valor):
        if valor is None:
            return valor
        return ValidadorPrecio("precio").validar(valor)

    # Restringe "estado" a los DOS unicos valores que usa el modelo
    # (ver modelos/servicio_adicional.py: activar()/desactivar()).
    # Sin esto, alguien podria mandar por la API un estado inventado
    # como "Pausado" que el modelo nunca esperaria.
    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor):
        if valor is None:
            return valor
        valor = valor.strip()
        if valor not in ("Activo", "Inactivo"):
            raise ValueError("El estado debe ser 'Activo' o 'Inactivo'")
        return valor

# ──────────────────────────────────────────────────────────────
# SCHEMA DE RESPUESTA
# Debe coincidir exactamente con ServicioAdicional.to_dict()
# ──────────────────────────────────────────────────────────────
class ServicioAdicionalRespuesta(BaseModel):
    id_servicio_adicional: str
    nombre_servicio_adicional: str
    descripcion: str
    precio: float
    estado: str          # "Activo" | "Inactivo"
    id_reserva: str