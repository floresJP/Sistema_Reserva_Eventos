# routers/cliente.py
from fastapi import APIRouter, HTTPException, status

from dao.cliente_dao import ClienteDAO
from dao.reserva_dao import ReservaDAO
from dao.tematica_dao import TematicaDAO
from modelos.cliente import Cliente
from schemas.cliente_schema import ClienteCrear, ClienteActualizar, ClienteRespuesta
from schemas.reserva_schema import ReservaRespuesta
from validaciones.validadores import (
    CorreoDuplicadoError, ClienteNoEncontradoError, ClienteConReservasError, DatoInvalidoError,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])

_cliente_dao  = ClienteDAO()
_tematica_dao = TematicaDAO()
_reserva_dao  = ReservaDAO(_cliente_dao, _tematica_dao)


@router.post(
    "",
    response_model=ClienteRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo cliente",
)
def crear_cliente(datos: ClienteCrear):
    """
    Crea un nuevo cliente en el sistema.

    - Valida que el correo no esté registrado por otro cliente (409 si lo está).
    - Valida el formato de nombre, DNI, teléfono y correo (400 si son inválidos).
    """
    cliente = Cliente(datos.nombre, datos.apellido, datos.dni, datos.telefono, datos.correo)
    try:
        return _cliente_dao.registrar(cliente).to_dict()
    except CorreoDuplicadoError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))
    except DatoInvalidoError as ex:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(ex))


@router.get(
    "",
    response_model=list[ClienteRespuesta],
    summary="Listar todos los clientes",
)
def listar_clientes():
    """Devuelve la lista completa de clientes registrados en el sistema."""
    return [c.to_dict() for c in _cliente_dao.obtener_todos()]


@router.get(
    "/{id_cliente}",
    response_model=ClienteRespuesta,
    summary="Obtener un cliente por ID",
)
def obtener_cliente(id_cliente: str):
    """Busca y devuelve un cliente según su ID (ej. `C001`). 404 si no existe."""
    cliente = _cliente_dao.buscar_por_id(id_cliente.upper())
    if not cliente:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Cliente ID={id_cliente} no encontrado")
    return cliente.to_dict()


@router.get(
    "/{id_cliente}/reservas",
    response_model=list[ReservaRespuesta],
    summary="Listar las reservas de un cliente",
)
def reservas_del_cliente(id_cliente: str):
    """Devuelve todas las reservas asociadas al cliente indicado. 404 si el cliente no existe."""
    try:
        return [r.to_dict() for r in _cliente_dao.obtenerReservas(id_cliente.upper(), _reserva_dao)]
    except ClienteNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.put(
    "/{id_cliente}",
    response_model=ClienteRespuesta,
    summary="Actualizar los datos de un cliente",
)
def actualizar_cliente(id_cliente: str, datos: ClienteActualizar):
    """
    Actualiza los datos de un cliente existente.

    - 404 si el cliente no existe.
    - 409 si el nuevo correo ya pertenece a otro cliente.
    - 400 si algún dato no cumple el formato esperado.
    """
    try:
        c = _cliente_dao.actualizarDatos(
            id_cliente.upper(),
            nombre=datos.nombre, apellido=datos.apellido, dni=datos.dni,
            telefono=datos.telefono, correo=datos.correo,
        )
        return c.to_dict()
    except ClienteNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except CorreoDuplicadoError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))
    except DatoInvalidoError as ex:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(ex))


@router.delete(
    "/{id_cliente}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un cliente",
)
def eliminar_cliente(id_cliente: str):
    """
    Elimina un cliente del sistema.

    - 404 si el cliente no existe.
    - 409 si el cliente tiene reservas asociadas (no se puede eliminar).
    """
    try:
        _cliente_dao.eliminar(id_cliente.upper())
    except ClienteNoEncontradoError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except ClienteConReservasError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))