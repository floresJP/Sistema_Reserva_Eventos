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


@router.post("", response_model=ReservaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_reserva(datos: ReservaCrear):
    reserva = Reserva(
        datos.fecha_evento, datos.hora_inicio, datos.hora_fin, datos.direccion,
        datos.edad_cumpleanero, datos.observaciones, datos.id_cliente.upper(), datos.id_tematica.upper()
    )
    try:
        return _reserva_dao.crear(reserva).to_dict()
    except (ClienteNoEncontradoError, TematicaNoEncontradaError) as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.get("", response_model=list[ReservaRespuesta])
def listar_reservas():
    return [r.to_dict() for r in _reserva_dao.obtener_todos()]


@router.get("/{id_reserva}", response_model=ReservaRespuesta)
def obtener_reserva(id_reserva: str):
    reserva = _reserva_dao.buscar_por_id(id_reserva.upper())
    if not reserva:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Reserva ID={id_reserva} no encontrada")
    return reserva.to_dict()


@router.put("/{id_reserva}", response_model=ReservaRespuesta)
def actualizar_reserva(id_reserva: str, datos: ReservaActualizar):
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


@router.delete("/{id_reserva}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reserva(id_reserva: str):
    try:
        _reserva_dao.eliminar(id_reserva.upper())
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except ReservaConDependenciasError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))


# ── Cambios de estado (PATCH), separados del PUT generico ──
@router.patch("/{id_reserva}/confirmar", response_model=ReservaRespuesta)
def confirmar_reserva(id_reserva: str):
    try:
        return _reserva_dao.confirmar_reserva(id_reserva.upper()).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.patch("/{id_reserva}/cancelar", response_model=ReservaRespuesta)
def cancelar_reserva(id_reserva: str):
    try:
        return _reserva_dao.cancelar_reserva(id_reserva.upper()).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.patch("/{id_reserva}/completar", response_model=ReservaRespuesta)
def completar_reserva(id_reserva: str):
    try:
        return _reserva_dao.completar_reserva(id_reserva.upper()).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))