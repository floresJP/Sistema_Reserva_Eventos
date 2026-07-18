# dao/cuota_dao.py
import datetime
from config.logger import Logger
from validaciones.validadores import GeneradorID, PagoNoEncontradoError, CuotaNoEncontradaError
from modelos.cuota import Cuota
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — CuotaDAO
# ──────────────────────────────────────────────────────────────────────────────
class CuotaDAO:
    PREFIJO = "Q"
    def __init__(self, pago_dao):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__pago_dao = pago_dao

    def insertar(self, cuota):
        if not self.__pago_dao.buscar_por_id(cuota.id_pago):
            self.__log.error(f"Cuota fallida: Pago ID={cuota.id_pago} no existe")
            raise PagoNoEncontradoError(cuota.id_pago)

        cuota.id_cuota = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(cuota)
        self.__log.info(f"Cuota creada: {cuota.id_cuota} #{cuota.numero_cuota} para Pago={cuota.id_pago}")
        return cuota

    def generarCuotas(self, pago):
        # BUG CORREGIDO: antes, la creacion e insercion de la cuota solo
        # ocurria dentro del "else", por lo que la ULTIMA cuota (i == n)
        # nunca se creaba. Ahora vencimiento/cuota/insertar/append
        # se ejecutan siempre, sin importar si es la ultima cuota o no.
        n = pago.total_cuotas
        monto_cuota = round(pago.monto_total / n, 2)
        cuotas_creadas = []

        for i in range(1, n + 1):
            if i == n:
                monto = round(pago.monto_total - monto_cuota * (n - 1), 2)
            else:
                monto = monto_cuota
            vencimiento = self.__sumar_meses(pago.fecha_pago, i - 1)
            cuota = Cuota(i, monto, vencimiento, pago.id_pago)
            self.insertar(cuota)
            cuotas_creadas.append(cuota)

        self.__log.info(f"Generadas {n} cuotas para Pago={pago.id_pago}")
        return cuotas_creadas

    def __sumar_meses(self, fecha, meses):
        mes = fecha.month - 1 + meses
        anio = fecha.year + mes // 12
        mes = mes % 12 + 1
        dia = min(fecha.day, [31,29 if anio % 4 == 0 else 28,31,30,31,30,31,31,30,31,30,31][mes - 1])
        return datetime.date(anio, mes, dia)

    def buscar_por_id(self, id_cuota):
        for c in self.__bd:
            if c.id_cuota == id_cuota: return c
        return None

    def obtener_por_pago(self, id_pago):
        return sorted(
            [c for c in self.__bd if c.id_pago == id_pago],
            key=lambda c: c.numero_cuota)
        
    def obtener_todos(self):
        return sorted(self.__bd, key=lambda c: c.fecha_vencimiento)

    def marcar_pagada(self, id_cuota, fecha_pago=None):
        c = self.buscar_por_id(id_cuota)
        if not c:
            self.__log.error(f"Marcar pagada fallido: Cuota ID={id_cuota} no existe")
            raise CuotaNoEncontradaError(id_cuota)
        c.marcarPagada(fecha_pago)
        self.__log.info(f"Cuota marcada como Pagada: ID={id_cuota}")
        return c

    def total(self): return len(self.__bd)
    