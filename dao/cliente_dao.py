# dao/cliente_dao.py
from config.logger import Logger
from validaciones.validadores import GeneradorID, CorreoDuplicadoError, ClienteNoEncontradoError, DatoInvalidoError
# ─────────────────────────────────────────────────
# PATRÓN DAO — ClienteDAO
# ─────────────────────────────────────────────────
class ClienteDAO:
    PREFIJO = "C"

    def __init__(self):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()

    def registrar(self, cliente):
        if self.buscar_por_correo(cliente.correo):
            self.__log.warning(f"Correo duplicado: {cliente.correo}")
            raise CorreoDuplicadoError(cliente.correo)
        if self.buscar_por_dni(cliente.dni):
            self.__log.warning(f"DNI duplicado: {cliente.dni}")
            raise DatoInvalidoError("dni", f"'{cliente.dni}' ya está registrado con otro cliente")

        cliente.id_cliente = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(cliente)
        self.__log.info(f"Cliente registrado: {cliente.nombre} (ID={cliente.id_cliente})")
        return cliente

    def buscar_por_correo(self, correo):
        for c in self.__bd:
            if c.correo == correo: return c
        return None

    def buscar_por_dni(self, dni):
        for c in self.__bd:
            if c.dni == dni: return c
        return None

    def buscar_por_id(self, id_cliente):
        for c in self.__bd:
            if c.id_cliente == id_cliente: return c
        return None

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda c: c.nombre)

    def actualizarDatos(self, id_cliente, telefono=None, correo=None):
        c = self.buscar_por_id(id_cliente)
        if not c:
            self.__log.error(f"Actualizar fallido: Cliente ID={id_cliente} no existe")
            raise ClienteNoEncontradoError(id_cliente)
        if telefono:  c.telefono  = telefono
        if correo:    c.correo    = correo
        self.__log.info(f"Cliente actualizado: ID={id_cliente}")
        return c

    def obtenerReservas(self, id_cliente, reserva_dao):
        if not self.buscar_por_id(id_cliente):
            raise ClienteNoEncontradoError(id_cliente)
        return reserva_dao.obtener_por_cliente(id_cliente)

    def total(self): return len(self.__bd)