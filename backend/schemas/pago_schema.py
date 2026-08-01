# schemas/pago_schema.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator
from validaciones.validadores import ValidadorPrecio, ValidadorEnteroPositivo, ValidadorMetodoPago

# ──────────────────────────────────────────────────────────────
# SCHEMA PARA CREAR PAGO
# "estado_pago" NO se pide aca: el modelo lo calcula solo, segun
# total_cuotas (ver modelos/pago.py __init__):
#   - si total_cuotas == 1  -> arranca en "Pagado"
#   - si total_cuotas > 1   -> arranca en "Pendiente"
# "fecha_pago" tampoco se pide: el modelo la pone en la fecha de HOY
# automaticamente al crearse.
# ──────────────────────────────────────────────────────────────
class PagoCrear(BaseModel):
    monto_total: float
    metodo_pago: str
    total_cuotas: int
    id_reserva: str

    @field_validator("monto_total")
    @classmethod
    def validar_monto_total(cls, valor):
        return ValidadorPrecio("monto_total").validar(valor)

    # Reutiliza el validador que ya usa la consola: solo acepta
    # YAPE, PLIN, TRANSFERENCIA, EFECTIVO, TARJETA (ver validadores.py
    # ValidadorMetodoPago.METODOS_VALIDOS). Ademas normaliza a MAYUSCULAS.
    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, valor):
        return ValidadorMetodoPago("metodo_pago").validar(valor)

    @field_validator("total_cuotas")
    @classmethod
    def validar_total_cuotas(cls, valor):
        return ValidadorEnteroPositivo("total_cuotas").validar(valor)


# ──────────────────────────────────────────────────────────────
# SCHEMA PARA ACTUALIZAR PAGO
# NO incluye "estado_pago". Las transiciones de estado_pago
# (Pendiente -> Pago parcial -> Pagado) tienen su propia logica
# de negocio (marcar_pago_parcial() / marcar_pagado() en el modelo)
# y deben ir por endpoints separados en el router, no por este
# PUT generico de edicion de datos.
# ──────────────────────────────────────────────────────────────
class PagoActualizar(BaseModel):
    monto_total: Optional[float] = None
    metodo_pago: Optional[str] = None
    total_cuotas: Optional[int] = None

    @field_validator("monto_total")
    @classmethod
    def validar_monto_total(cls, valor):
        if valor is None:
            return valor
        return ValidadorPrecio("monto_total").validar(valor)

    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, valor):
        if valor is None:
            return valor
        return ValidadorMetodoPago("metodo_pago").validar(valor)

    @field_validator("total_cuotas")
    @classmethod
    def validar_total_cuotas(cls, valor):
        if valor is None:
            return valor
        return ValidadorEnteroPositivo("total_cuotas").validar(valor)


# ──────────────────────────────────────────────────────────────
# SCHEMA DE RESPUESTA
# ──────────────────────────────────────────────────────────────
class PagoRespuesta(BaseModel):
    id_pago: str
    fecha_pago: date
    monto_total: float
    metodo_pago: str
    estado_pago: str      # "Pendiente" | "Pago parcial" | "Pagado"
    total_cuotas: int
    id_reserva: str