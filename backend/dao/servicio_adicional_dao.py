# dao/servicio_adicional_dao.py
from config.logger import Logger
from validaciones.validadores import GeneradorID, ReservaNoEncontradaError, ServicioAdicionalNoEncontradoError

# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ServicioAdicionalDAO
# ──────────────────────────────────────────────────────────────────────────────
class ServicioAdicionalDAO:
    PREFIJO = "S"
    def __init__(self, reserva_dao):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__reserva_dao = reserva_dao

    def insertar(self, servicio):
        if not self.__reserva_dao.buscar_por_id(servicio.id_reserva):
            self.__log.error(f"Servicio fallido: Reserva ID={servicio.id_reserva} no existe")
            raise ReservaNoEncontradaError(servicio.id_reserva)
        servicio.id_servicio_adicional = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(servicio)
        self.__log.info(
            f"Servicio adicional agregado: {servicio.nombre_servicio_adicional} "
            f"(ID={servicio.id_servicio_adicional}) para Reserva={servicio.id_reserva}")
        return servicio

    def buscar_por_id(self, id_servicio):
        for s in self.__bd:
            if s.id_servicio_adicional == id_servicio: return s
        return None

    def obtener_por_reserva(self, id_reserva):
        return [s for s in self.__bd if s.id_reserva == id_reserva]

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda s: s.nombre_servicio_adicional)

    def calcularTotal(self, id_reserva):
        servicios = self.obtener_por_reserva(id_reserva)
        return sum(s.precio for s in servicios)

    def eliminar(self, id_servicio):
        s = self.buscar_por_id(id_servicio)
        if not s:
            self.__log.error(f"Eliminar fallido: Servicio ID={id_servicio} no existe")
            raise ServicioAdicionalNoEncontradoError(id_servicio)
        self.__bd.remove(s)
        self.__log.info(f"Servicio adicional eliminado: {s.nombre_servicio_adicional} (ID={id_servicio})")
        return True

    def total(self): return len(self.__bd)