# schemas/cuota_schema.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator
from validaciones.validadores import ValidadorPrecio, ValidadorEnteroPositivo

# ──────────────────────────────────────────────────────────────
# CREAR CUOTA
# "estado" no se pide: el modelo lo pone en "Pendiente" al crear.
# "fecha_pago" no se pide: queda en None hasta marcarPagada().
# ──────────────────────────────────────────────────────────────
class CuotaCrear(BaseModel):
    numero_cuota: int
    monto: float
    fecha_vencimiento: date
    id_pago: str

    @field_validator("numero_cuota")
    @classmethod
    def validar_numero_cuota(cls, valor):
        return ValidadorEnteroPositivo("numero_cuota").validar(valor)

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, valor):
        return ValidadorPrecio("monto").validar(valor)


# ──────────────────────────────────────────────────────────────
# ACTUALIZAR CUOTA
# "estado" solo acepta Pendiente/Vencida. "Pagada" queda fuera
# porque este UPDATE no toca fecha_pago -> quedaria inconsistente.
# Para pagar una cuota: usar PATCH /cuota/{id}/pagar (marcar_pagada).
# ──────────────────────────────────────────────────────────────
class CuotaActualizar(BaseModel):
    monto: Optional[float] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[str] = None

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, valor):
        if valor is None:
            return valor
        return ValidadorPrecio("monto").validar(valor)

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor):
        if valor is None:
            return valor
        valor = valor.strip()
        if valor not in ("Pendiente", "Vencida"):
            raise ValueError(
                "Estado debe ser 'Pendiente' o 'Vencida'. "
                "Para pagar, usa /cuota/{id}/pagar"
            )
        return valor


# ──────────────────────────────────────────────────────────────
# RESPUESTA — coincide con Cuota.to_dict()
# ──────────────────────────────────────────────────────────────
class CuotaRespuesta(BaseModel):
    id_cuota: str
    numero_cuota: int
    monto: float
    fecha_vencimiento: date
    fecha_pago: Optional[date] = None
    estado: str          # Pendiente | Pagada | Vencida
    id_pago: str