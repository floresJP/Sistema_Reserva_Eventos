# routers/pago.py
from fastapi import APIRouter, HTTPException, status
from dao.cliente_dao import ClienteDAO
from dao.tematica_dao import TematicaDAO
from dao.reserva_dao import ReservaDAO
from dao.pago_dao import PagoDAO
from dao.cuota_dao import CuotaDAO
from modelos.pago import Pago
from schemas.pago_schema import PagoCrear, PagoActualizar, PagoRespuesta
from schemas.cuota_schema import CuotaRespuesta
from validaciones.validadores import ReservaNoEncontradaError, PagoNoEncontradoError, PagoConCuotasError

router = APIRouter(prefix="/pagos", tags=["Pagos"])

_cliente_dao  = ClienteDAO()
_tematica_dao = TematicaDAO()
_reserva_dao  = ReservaDAO(_cliente_dao, _tematica_dao)
_pago_dao     = PagoDAO(_reserva_dao)
_cuota_dao    = CuotaDAO(_pago_dao)


@router.post(
    "",
    response_model=PagoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo pago",
)
def crear_pago(datos: PagoCrear):
    """
    Registra un pago asociado a una reserva existente.

    `metodo_pago` se normaliza automáticamente a MAYÚSCULAS en el schema.
    404 si la reserva indicada no existe.
    """
    pago = Pago(datos.monto_total, datos.metodo_pago, datos.total_cuotas, datos.id_reserva.upper(), datos.fecha_pago)
    try:
        return _pago_dao.registrar(pago).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.get(
    "",
    response_model=list[PagoRespuesta],
    summary="Listar todos los pagos",
)
def listar_pagos():
    """Devuelve la lista completa de pagos registrados en el sistema."""
    return [p.to_dict() for p in _pago_dao.obtener_todos()]


@router.get(
    "/reserva/{id_reserva}",
    response_model=list[PagoRespuesta],
    summary="Listar los pagos de una reserva",
)
def listar_por_reserva(id_reserva: str):
    """Devuelve todos los pagos asociados a una reserva específica."""
    return [p.to_dict() for p in _pago_dao.obtener_por_reserva(id_reserva.upper())]


@router.get(
    "/{id_pago}",
    response_model=PagoRespuesta,
    summary="Obtener un pago por ID",
)
def obtener_pago(id_pago: str):
    """Busca y devuelve un pago según su ID (ej. `P001`). 404 si no existe."""
    pago = _pago_dao.buscar_por_id(id_pago.upper())
    if not pago:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Pago ID={id_pago} no encontrado")
    return pago.to_dict()


@router.put(
    "/{id_pago}",
    response_model=PagoRespuesta,
    summary="Actualizar un pago",
)
def actualizar_pago(id_pago: str, datos: PagoActualizar):
    """Actualiza monto total, método de pago y/o número de cuotas. 404 si no existe."""
    try:
        p = _pago_dao.actualizar(
            id_pago.upper(), monto_total=datos.monto_total,
            metodo_pago=datos.metodo_pago, total_cuotas=datos.total_cuotas,
        )
        return p.to_dict()
    except PagoNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.delete(
    "/{id_pago}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un pago",
)
def eliminar_pago(id_pago: str):
    """
    Elimina un pago del sistema.

    - 404 si el pago no existe.
    - 409 si el pago ya tiene cuotas generadas (no se puede eliminar).
    """
    try:
        _pago_dao.eliminar(id_pago.upper())
    except PagoNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except PagoConCuotasError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))


# ── Cambio de estado (PATCH), separado del PUT generico ──
@router.patch(
    "/{id_pago}/pagar",
    response_model=PagoRespuesta,
    summary="Marcar un pago como pagado",
)
def marcar_pagado(id_pago: str):
    """Marca el pago como pagado. 404 si el pago no existe."""
    try:
        return _pago_dao.marcar_pagado(id_pago.upper()).to_dict()
    except PagoNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


# ── Generar cuotas del pago (solo si total_cuotas > 1) ──
@router.post(
    "/{id_pago}/generar-cuotas",
    response_model=list[CuotaRespuesta],
    summary="Generar las cuotas de un pago",
)
def generar_cuotas(id_pago: str):
    """
    Genera automáticamente todas las cuotas de un pago, repartiendo el
    monto total entre el número de cuotas indicado (`total_cuotas`).

    Solo tiene efecto si `total_cuotas` es mayor a 1. 404 si el pago no existe.
    """
    pago = _pago_dao.buscar_por_id(id_pago.upper())
    if not pago:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Pago ID={id_pago} no encontrado")
    cuotas = _cuota_dao.generarCuotas(pago)
    return [c.to_dict() for c in cuotas]