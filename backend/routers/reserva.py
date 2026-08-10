# routers/reserva.py
from fastapi import APIRouter, HTTPException, status
from dao.cliente_dao import ClienteDAO
from dao.tematica_dao import TematicaDAO
from dao.reserva_dao import ReservaDAO
from modelos.reserva import Reserva
from schemas.reserva_schema import ReservaCrear, ReservaActualizar, ReservaRespuesta
from validaciones.validadores import (
    ClienteNoEncontradoError,
    TematicaNoEncontradaError,
    ReservaNoEncontradaError,
    ReservaConDependenciasError,
    DatoInvalidoError,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

_cliente_dao  = ClienteDAO()
_tematica_dao = TematicaDAO()
_reserva_dao  = ReservaDAO(_cliente_dao, _tematica_dao)


@router.post(
    "",
    response_model=ReservaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva reserva",
)
def crear_reserva(datos: ReservaCrear):
    """
    Crea una nueva reserva de evento.

    404 si el cliente o la temática indicados no existen.
    """
    reserva = Reserva(
        datos.fecha_evento, datos.hora_inicio, datos.hora_fin, datos.direccion,
        datos.edad_cumpleanero, datos.observaciones, datos.id_cliente.upper(), datos.id_tematica.upper()
    )
    try:
        return _reserva_dao.crear(reserva).to_dict()
    except (ClienteNoEncontradoError, TematicaNoEncontradaError) as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.get(
    "",
    response_model=list[ReservaRespuesta],
    summary="Listar todas las reservas",
)
def listar_reservas():
    """Devuelve la lista completa de reservas registradas en el sistema."""
    return [r.to_dict() for r in _reserva_dao.obtener_todos()]


@router.get(
    "/{id_reserva}",
    response_model=ReservaRespuesta,
    summary="Obtener una reserva por ID",
)
def obtener_reserva(id_reserva: str):
    """Busca y devuelve una reserva según su ID (ej. `R001`). 404 si no existe."""
    reserva = _reserva_dao.buscar_por_id(id_reserva.upper())
    if not reserva:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Reserva ID={id_reserva} no encontrada")
    return reserva.to_dict()


@router.put(
    "/{id_reserva}",
    response_model=ReservaRespuesta,
    summary="Actualizar una reserva",
)
def actualizar_reserva(id_reserva: str, datos: ReservaActualizar):
    """
    Actualiza fecha, horario, dirección y demás datos de una reserva.

    - 404 si la reserva no existe.
    - 400 si `hora_fin` es menor o igual a `hora_inicio`.
    """
    try:
        r = _reserva_dao.actualizar(
            id_reserva.upper(), fecha_evento=datos.fecha_evento, hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin, direccion=datos.direccion,
            edad_cumpleanero=datos.edad_cumpleanero, observaciones=datos.observaciones,
        )
        return r.to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except DatoInvalidoError as ex:
        # hora_fin <= hora_inicio (validado en el DAO)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(ex))


@router.delete(
    "/{id_reserva}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una reserva",
)
def eliminar_reserva(id_reserva: str):
    """
    Elimina una reserva del sistema.

    - 404 si la reserva no existe.
    - 409 si la reserva tiene servicios adicionales o pagos asociados.
    """
    try:
        _reserva_dao.eliminar(id_reserva.upper())
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except ReservaConDependenciasError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))


# ── Cambios de estado (PATCH), separados del PUT generico ──
@router.patch(
    "/{id_reserva}/confirmar",
    response_model=ReservaRespuesta,
    summary="Confirmar una reserva",
)
def confirmar_reserva(id_reserva: str):
    """Cambia el estado de la reserva a `Confirmada`. 404 si no existe."""
    try:
        return _reserva_dao.confirmar_reserva(id_reserva.upper()).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.patch(
    "/{id_reserva}/cancelar",
    response_model=ReservaRespuesta,
    summary="Cancelar una reserva",
)
def cancelar_reserva(id_reserva: str):
    """Cambia el estado de la reserva a `Cancelada`. 404 si no existe."""
    try:
        return _reserva_dao.cancelar_reserva(id_reserva.upper()).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.patch(
    "/{id_reserva}/completar",
    response_model=ReservaRespuesta,
    summary="Completar una reserva",
)
def completar_reserva(id_reserva: str):
    """Cambia el estado de la reserva a `Completada`, tras realizarse el evento. 404 si no existe."""
    try:
        return _reserva_dao.completar_reserva(id_reserva.upper()).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))