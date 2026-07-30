from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator

from validaciones.validadores import ValidadorNombre, ValidadorDNI, ValidadorTelefono, ValidadorCorreo
# ──────────────────────────────────────────────────────────────
# SCHEMA PARA CREAR CLIENTE
# Se utiliza cuando se registra un nuevo cliente.
# Todos los campos son obligatorios.
# ──────────────────────────────────────────────────────────────

class ClienteCrear(BaseModel):
    nombre: str
    apellido: str
    dni: str
    telefono: str
    correo: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        return ValidadorNombre("nombre").validar(valor)

    @field_validator("apellido")
    @classmethod
    def validar_apellido(cls, valor):
        return ValidadorNombre("apellido").validar(valor)

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):
        return ValidadorDNI().validar(valor)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor):
        return ValidadorTelefono().validar(valor)

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor):
        return ValidadorCorreo().validar(valor)

# ──────────────────────────────────────────────────────────────
# SCHEMA PARA ACTUALIZAR CLIENTE
# Permite modificar solamente algunos campos.
# Los campos son opcionales.
# ──────────────────────────────────────────────────────────────

class ClienteActualizar(BaseModel):

    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        if valor is None:
            return valor
        return ValidadorNombre("nombre").validar(valor)

    @field_validator("apellido")
    @classmethod
    def validar_apellido(cls, valor):
        if valor is None:
            return valor
        return ValidadorNombre("apellido").validar(valor)

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):
        if valor is None:
            return valor
        return ValidadorDNI().validar(valor)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor):
        if valor is None:
            return valor
        return ValidadorTelefono().validar(valor)

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor):
        if valor is None:
            return valor
        return ValidadorCorreo().validar(valor)

# ──────────────────────────────────────────────────────────────
# SCHEMA DE RESPUESTA
# Información que devuelve la API.
# ──────────────────────────────────────────────────────────────
class ClienteRespuesta(BaseModel):
    id_cliente: str
    nombre: str
    apellido: str
    dni: str
    telefono: str
    correo: str
    fecha_registro: date