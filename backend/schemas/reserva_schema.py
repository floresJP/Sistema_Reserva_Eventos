# schemas/reserva_schema.py
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, field_validator
from validaciones.validadores import ValidadorDireccion, ValidadorEnteroPositivo

# ──────────────────────────────────────────────────────────────
# SCHEMA PARA CREAR RESERVA
# Se usa cuando el cliente registra una nueva reserva de evento.
# "estado" NO se pide aca: el modelo Reserva lo asigna solo como
# "Pendiente" al crearse (ver modelos/reserva.py __init__).
# ──────────────────────────────────────────────────────────────
class ReservaCrear(BaseModel):
    fecha_evento: date
    hora_inicio: time
    hora_fin: time
    direccion: str
    edad_cumpleanero: Optional[int] = None   # opcional, igual que en el SQL (INT NULL)
    observaciones: Optional[str] = None      # opcional, igual que en el SQL (TEXT NULL)
    id_cliente: str
    id_tematica: str

    # Reutiliza el mismo validador que usa la consola (validadores.py)
    # para mantener UNA sola regla de "direccion valida" en todo el proyecto.
    @field_validator("direccion")
    @classmethod
    def validar_direccion(cls, valor):
        return ValidadorDireccion("direccion").validar(valor)

    # edad_cumpleanero es opcional: solo se valida si el cliente SI la mando.
    @field_validator("edad_cumpleanero")
    @classmethod
    def validar_edad(cls, valor):
        if valor is None:
            return valor
        return ValidadorEnteroPositivo("edad_cumpleanero").validar(valor)

    # ────────────────────────────────────────────────────────────
    # VALIDACION CRUZADA (compara DOS campos entre si).
    # Pydantic valida los campos en el ORDEN en que estan declarados
    # arriba: como "hora_inicio" esta antes que "hora_fin", cuando
    # se valida "hora_fin" ya tenemos "hora_inicio" disponible en
    # el parametro "info" (info.data = dict con los campos YA validados).
    # Por eso este validador necesita el parametro extra "info",
    # a diferencia de los demas validadores que solo reciben "valor".
    # NOTA: esta regla NO existe en validadores.py porque ese archivo
    # solo valida UN campo a la vez; esto es logica de negocio propia
    # del schema (evita reservas donde el evento "termina antes de empezar").
    # ────────────────────────────────────────────────────────────
    @field_validator("hora_fin")
    @classmethod
    def validar_hora_fin(cls, valor, info):
        hora_inicio = info.data.get("hora_inicio")
        # El "is not None" es por seguridad: si hora_inicio fallo su
        # propia validacion, no estaria en info.data y evitamos un
        # error en cadena confuso.
        if hora_inicio is not None and valor <= hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return valor

# ──────────────────────────────────────────────────────────────
# SCHEMA PARA ACTUALIZAR RESERVA
# NO incluye "estado" a proposito. Los cambios de estado
# (Pendiente -> Confirmada -> Completada, o -> Cancelada) van por
# endpoints separados en el router (ej. PATCH /reserva/{id}/confirmar),
# que llaman a reserva_dao.confirmar_reserva() / cancelar_reserva() /
# completar_reserva() -- NO por este PUT generico de edicion de datos.
# ──────────────────────────────────────────────────────────────
class ReservaActualizar(BaseModel):
    fecha_evento: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    direccion: Optional[str] = None
    edad_cumpleanero: Optional[int] = None
    observaciones: Optional[str] = None

    @field_validator("direccion")
    @classmethod
    def validar_direccion(cls, valor):
        if valor is None:
            return valor
        return ValidadorDireccion("direccion").validar(valor)

    @field_validator("edad_cumpleanero")
    @classmethod
    def validar_edad(cls, valor):
        if valor is None:
            return valor
        return ValidadorEnteroPositivo("edad_cumpleanero").validar(valor)

    # NOTA: no se agrego aqui la validacion cruzada hora_fin > hora_inicio
    # porque en una actualizacion parcial el cliente podria mandar solo
    # UNA de las dos horas (la otra queda en None) y no tendriamos con
    # que compararla. Si se necesita mantener esa regla tambien al editar,
    # habria que validarla en el DAO (con las horas ya combinadas: la
    # nueva si vino, o la existente en BD si no vino), no aqui.
# ──────────────────────────────────────────────────────────────
# SCHEMA DE RESPUESTA
# Debe coincidir exactamente con Reserva.to_dict()
# ──────────────────────────────────────────────────────────────
class ReservaRespuesta(BaseModel):
    id_reserva: str
    fecha_reserva: date
    fecha_evento: date
    hora_inicio: time
    hora_fin: time
    direccion: str
    edad_cumpleanero: Optional[int] = None
    observaciones: Optional[str] = None
    estado: str          # "Pendiente" | "Confirmada" | "Cancelada" | "Completada"
    id_cliente: str
    id_tematica: str