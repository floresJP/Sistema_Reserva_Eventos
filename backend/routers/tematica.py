# routers/tematica.py
from fastapi import APIRouter, HTTPException, status
from dao.tematica_dao import TematicaDAO
from modelos.tematica import Tematica
from schemas.tematica_schema import TematicaCrear, TematicaActualizar, TematicaRespuesta
from validaciones.validadores import TematicaNoEncontradaError, TematicaConReservasError

router = APIRouter(prefix="/tematicas", tags=["Tematicas"])
_tematica_dao = TematicaDAO()


@router.post("", response_model=TematicaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_tematica(datos: TematicaCrear):
    tematica = Tematica(datos.descripcion, datos.precio_base)
    return _tematica_dao.insertar(tematica).to_dict()


@router.get("", response_model=list[TematicaRespuesta])
def listar_tematicas(solo_disponibles: bool = False):
    """?solo_disponibles=true filtra solo estado='Disponible'."""
    if solo_disponibles:
        return [t.to_dict() for t in _tematica_dao.obtener_disponibles()]
    return [t.to_dict() for t in _tematica_dao.obtener_todos()]


@router.get("/{id_tematica}", response_model=TematicaRespuesta)
def obtener_tematica(id_tematica: str):
    tematica = _tematica_dao.buscar_por_id(id_tematica.upper())
    if not tematica:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Tematica ID={id_tematica} no encontrada")
    return tematica.to_dict()


@router.put("/{id_tematica}", response_model=TematicaRespuesta)
def actualizar_tematica(id_tematica: str, datos: TematicaActualizar):
    try:
        t = _tematica_dao.actualizar(
            id_tematica.upper(),
            descripcion=datos.descripcion, precio_base=datos.precio_base, estado=datos.estado,
        )
        return t.to_dict()
    except TematicaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.delete("/{id_tematica}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tematica(id_tematica: str):
    try:
        _tematica_dao.eliminar(id_tematica.upper())
    except TematicaNoEncontradaError as ex:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(ex))
    except TematicaConReservasError as ex:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(ex))