# dao/pago_dao.py
from config.logger import Logger
from validaciones.validadores import GeneradorID, ReservaNoEncontradaError, PagoNoEncontradoError
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — PagoDAO
# ──────────────────────────────────────────────────────────────────────────────
class PagoDAO:
    PREFIJO = "P"
    def __init__(self, reserva_dao):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__reserva_dao = reserva_dao

    def registrar(self, pago):
        if not self.__reserva_dao.buscar_por_id(pago.id_reserva):
            self.__log.error(f"Pago fallido: Reserva ID={pago.id_reserva} no existe")
            raise ReservaNoEncontradaError(pago.id_reserva)
        pago.id_pago = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(pago)
        self.__log.info(
            f"Pago registrado: {pago.id_pago} S/.{pago.monto_total:.2f} "
            f"({pago.metodo_pago}) para Reserva={pago.id_reserva}")
        return pago

    def buscar_por_id(self, id_pago):
        for p in self.__bd:
            if p.id_pago == id_pago: return p
        return None

    def obtener_por_reserva(self, id_reserva):
        return [p for p in self.__bd if p.id_reserva == id_reserva]

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda p: p.fecha_pago)

    def marcar_pagado(self, id_pago):
        p = self.buscar_por_id(id_pago)
        if not p:
            self.__log.error(f"Marcar pagado fallido: Pago ID={id_pago} no existe")
            raise PagoNoEncontradoError(id_pago)
        p.marcar_pagado()
        self.__log.info(f"Pago marcado como Pagado: ID={id_pago}")
        return p

    def total(self): return len(self.__bd)