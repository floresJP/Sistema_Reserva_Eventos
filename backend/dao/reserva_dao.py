# dao/reserva_dao.py
from config.logger import Logger
from validaciones.validadores import GeneradorID, ClienteNoEncontradoError, TematicaNoEncontradaError, ReservaNoEncontradaError
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ReservaDAO
# ──────────────────────────────────────────────────────────────────────────────
class ReservaDAO:
    PREFIJO = "R"

    def __init__(self, cliente_dao, tematica_dao):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__cliente_dao  = cliente_dao
        self.__tematica_dao = tematica_dao

    def crear(self, reserva):
        if not self.__cliente_dao.buscar_por_id(reserva.id_cliente):
            self.__log.error(f"Reserva fallida: Cliente ID={reserva.id_cliente} no existe")
            raise ClienteNoEncontradoError(reserva.id_cliente)
        if not self.__tematica_dao.buscar_por_id(reserva.id_tematica):
            self.__log.error(f"Reserva fallida: Tematica ID={reserva.id_tematica} no existe")
            raise TematicaNoEncontradaError(reserva.id_tematica)
        reserva.id_reserva = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(reserva)
        self.__log.info(f"Reserva creada: ID={reserva.id_reserva} para Cliente={reserva.id_cliente}")
        return reserva
    
    def buscar_por_id(self, id_reserva):
        for r in self.__bd:
            if r.id_reserva == id_reserva: return r
        return None

    def obtener_por_cliente(self, id_cliente):
        return [r for r in self.__bd if r.id_cliente == id_cliente]

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda r: r.fecha_evento)

    def confirmar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Confirmar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        r.confirmar()
        self.__log.info(f"Reserva confirmada: ID={id_reserva}")
        return r

    def cancelar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Cancelar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        r.cancelar()
        self.__log.info(f"Reserva cancelada: ID={id_reserva}")
        return r

    def completar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Completar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        r.completar()
        self.__log.info(f"Reserva completada: ID={id_reserva}")
        return r

    def total(self): return len(self.__bd)