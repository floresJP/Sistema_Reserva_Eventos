# routers/servicio_adicional.py
from fastapi import APIRouter, HTTPException, status
from dao.cliente_dao import ClienteDAO
from dao.tematica_dao import TematicaDAO
from dao.reserva_dao import ReservaDAO
from dao.servicio_adicional_dao import ServicioAdicionalDAO
from modelos.servicio_adicional import ServicioAdicional
from schemas.servicio_adicional_schema import (
    ServicioAdicionalCrear, ServicioAdicionalActualizar, ServicioAdicionalRespuesta,
)
from validaciones.validadores import ReservaNoEncontradaError, ServicioAdicionalNoEncontradoError

router = APIRouter(prefix="/servicios-adicionales", tags=["ServiciosAdicionales"])

_cliente_dao  = ClienteDAO()
_tematica_dao = TematicaDAO()
_reserva_dao  = ReservaDAO(_cliente_dao, _tematica_dao)
_servicio_dao = ServicioAdicionalDAO(_reserva_dao)


@router.post("", response_model=ServicioAdicionalRespuesta, status_code=status.HTTP_201_CREATED)
def crear_servicio(datos: ServicioAdicionalCrear):
    servicio = ServicioAdicional(
        datos.nombre_servicio_adicional, datos.descripcion, datos.precio, datos.id_reserva.upper()
    )
    try:
        return _servicio_dao.insertar(servicio).to_dict()
    except ReservaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.get("", response_model=list[ServicioAdicionalRespuesta])
def listar_servicios():
    return [s.to_dict() for s in _servicio_dao.obtener_todos()]


# Rutas especificas antes de "/{id_servicio}" para que FastAPI no
# confunda "reserva" o el id_reserva con un id_servicio.
@router.get("/reserva/{id_reserva}", response_model=list[ServicioAdicionalRespuesta])
def listar_por_reserva(id_reserva: str):
    return [s.to_dict() for s in _servicio_dao.obtener_por_reserva(id_reserva.upper())]


@router.get("/reserva/{id_reserva}/total")
def total_por_reserva(id_reserva: str):
    # Suma de precios de los servicios de una reserva (para mostrar en el frontend)
    return {"id_reserva": id_reserva.upper(), "total_servicios": _servicio_dao.calcularTotal(id_reserva.upper())}


@router.get("/{id_servicio}", response_model=ServicioAdicionalRespuesta)
def obtener_servicio(id_servicio: str):
    servicio = _servicio_dao.buscar_por_id(id_servicio.upper())
    if not servicio:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Servicio adicional ID={id_servicio} no encontrado")
    return servicio.to_dict()


@router.put("/{id_servicio}", response_model=ServicioAdicionalRespuesta)
def actualizar_servicio(id_servicio: str, datos: ServicioAdicionalActualizar):
    try:
        s = _servicio_dao.actualizar(
            id_servicio.upper(),
            nombre_servicio_adicional=datos.nombre_servicio_adicional,
            descripcion=datos.descripcion, precio=datos.precio, estado=datos.estado,
        )
        return s.to_dict()
    except ServicioAdicionalNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.delete("/{id_servicio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio(id_servicio: str):
    try:
        _servicio_dao.eliminar(id_servicio.upper())
    except ServicioAdicionalNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))