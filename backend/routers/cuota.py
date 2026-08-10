# routers/cuota.py
from fastapi import APIRouter, HTTPException, status
from dao.cliente_dao import ClienteDAO
from dao.tematica_dao import TematicaDAO
from dao.reserva_dao import ReservaDAO
from dao.pago_dao import PagoDAO
from dao.cuota_dao import CuotaDAO
from modelos.cuota import Cuota
from schemas.cuota_schema import CuotaCrear, CuotaActualizar, CuotaRespuesta
from validaciones.validadores import PagoNoEncontradoError, CuotaNoEncontradaError

router = APIRouter(prefix="/cuotas", tags=["Cuotas"])

_cliente_dao  = ClienteDAO()
_tematica_dao = TematicaDAO()
_reserva_dao  = ReservaDAO(_cliente_dao, _tematica_dao)
_pago_dao     = PagoDAO(_reserva_dao)
_cuota_dao    = CuotaDAO(_pago_dao)


@router.post(
    "",
    response_model=CuotaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una cuota individual",
)
def crear_cuota(datos: CuotaCrear):
    """
    Inserta una cuota suelta asociada a un pago existente.

    Para generar automáticamente todas las cuotas de un pago de una sola vez,
    usar `POST /pagos/{id_pago}/generar-cuotas` en su lugar.

    404 si el pago indicado no existe.
    """
    cuota = Cuota(datos.numero_cuota, datos.monto, datos.fecha_vencimiento, datos.id_pago.upper())
    try:
        return _cuota_dao.insertar(cuota).to_dict()
    except PagoNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.get(
    "",
    response_model=list[CuotaRespuesta],
    summary="Listar todas las cuotas",
)
def listar_cuotas():
    """Devuelve todas las cuotas registradas en el sistema, de todos los pagos."""
    return [c.to_dict() for c in _cuota_dao.obtener_todos()]


@router.get(
    "/pago/{id_pago}",
    response_model=list[CuotaRespuesta],
    summary="Listar las cuotas de un pago",
)
def listar_por_pago(id_pago: str):
    """Devuelve todas las cuotas asociadas a un pago específico."""
    return [c.to_dict() for c in _cuota_dao.obtener_por_pago(id_pago.upper())]


@router.get(
    "/{id_cuota}",
    response_model=CuotaRespuesta,
    summary="Obtener una cuota por ID",
)
def obtener_cuota(id_cuota: str):
    """Busca y devuelve una cuota según su ID (ej. `Q001`). 404 si no existe."""
    cuota = _cuota_dao.buscar_por_id(id_cuota.upper())
    if not cuota:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Cuota ID={id_cuota} no encontrada")
    return cuota.to_dict()


@router.put(
    "/{id_cuota}",
    response_model=CuotaRespuesta,
    summary="Actualizar una cuota",
)
def actualizar_cuota(id_cuota: str, datos: CuotaActualizar):
    """Actualiza monto, fecha de vencimiento y/o estado de una cuota. 404 si no existe."""
    try:
        c = _cuota_dao.actualizar(
            id_cuota.upper(), monto=datos.monto,
            fecha_vencimiento=datos.fecha_vencimiento, estado=datos.estado,
        )
        return c.to_dict()
    except CuotaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.delete(
    "/{id_cuota}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una cuota",
)
def eliminar_cuota(id_cuota: str):
    """Elimina una cuota del sistema. 404 si no existe."""
    try:
        _cuota_dao.eliminar(id_cuota.upper())
    except CuotaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


# ── Cambio de estado (PATCH), separado del PUT generico ──
# Unico camino valido a estado="Pagada" (registra fecha_pago tambien).
@router.patch(
    "/{id_cuota}/pagar",
    response_model=CuotaRespuesta,
    summary="Marcar una cuota como pagada",
)
def marcar_pagada(id_cuota: str):
    """
    Marca la cuota como `Pagada` y registra automáticamente la fecha de pago.

    Es el único camino válido para pasar una cuota a estado `Pagada`
    (no se hace mediante el PUT genérico). 404 si la cuota no existe.
    """
    try:
        return _cuota_dao.marcar_pagada(id_cuota.upper()).to_dict()
    except CuotaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))