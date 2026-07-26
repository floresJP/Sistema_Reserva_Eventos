# dao/cuota_dao.py
import datetime
from config.logger import Logger
from config.base_datos import obtener_conexion
from validaciones.validadores import GeneradorID, PagoNoEncontradoError, CuotaNoEncontradaError
from modelos.cuota import Cuota
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — CuotaDAO
# ──────────────────────────────────────────────────────────────────────────────
class CuotaDAO:
    PREFIJO = "Q"
    def __init__(self, pago_dao):
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__pago_dao = pago_dao

    def insertar(self, cuota):
        #  Verificar que el pago exista antes de asociarle una cuota
        if not self.__pago_dao.buscar_por_id(cuota.id_pago):
            self.__log.error(f"Cuota fallida: Pago ID={cuota.id_pago} no existe")
            raise PagoNoEncontradoError(cuota.id_pago)
        # consultando cuántas cuotas existen realmente en la BD
        cuota.id_cuota = self.__gen.generar(self.PREFIJO, self.__siguiente_numero())
        #  Abrir conexión a PostgreSQL y crear un cursor para ejecutar comandos SQL
        conn = obtener_conexion()
        cursor = conn.cursor()
        #  Ejecutar el INSERT para guardar la cuota en la tabla "cuota"
        cursor.execute(
            """INSERT INTO cuota (id_cuota, numero_cuota, monto, fecha_vencimiento,fecha_pago, estado, id_pago) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (cuota.id_cuota, cuota.numero_cuota, cuota.monto, cuota.fecha_vencimiento,cuota.fecha_pago, cuota.estado, cuota.id_pago)
            )
        # Confirmar los cambios en la base de datos
        conn.commit()
        # Cerrar el cursor y la conexión (liberar recursos)
        cursor.close()
        conn.close()
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
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cuota WHERE id_cuota = %s", (id_cuota,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return self.__fila_a_cuota(fila) if fila else None

    def obtener_por_pago(self, id_pago):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cuota WHERE id_pago = %s ORDER BY numero_cuota", (id_pago,))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()        
        return [self.__fila_a_cuota(f) for f in filas]
        
    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cuota ORDER BY fecha_vencimiento")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self.__fila_a_cuota(f) for f in filas]
    
    def marcar_pagada(self, id_cuota, fecha_pago=None):
        c = self.buscar_por_id(id_cuota)
        if not c:
            self.__log.error(f"Marcar pagada fallido: Cuota ID={id_cuota} no existe")
            raise CuotaNoEncontradaError(id_cuota)
        # Calcula la fecha de pago real ANTES de actualizar la BD
        nueva_fecha_pago = fecha_pago if fecha_pago else datetime.date.today()
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
        "UPDATE cuota SET estado=%s, fecha_pago=%s WHERE id_cuota=%s",
        ("Pagada", nueva_fecha_pago, id_cuota)
        )
        conn.commit()
        cursor.close()
        conn.close()       
        c.marcarPagada(nueva_fecha_pago)
        self.__log.info(f"Cuota marcada como Pagada: ID={id_cuota}")
        return c

    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM cuota")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total
    
    def __siguiente_numero(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM cuota")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total + 1

    def __fila_a_cuota(self, fila):
        c = Cuota(fila["numero_cuota"], fila["monto"], fila["fecha_vencimiento"], fila["id_pago"])
        c.id_cuota = fila["id_cuota"]
        c.fecha_pago = fila["fecha_pago"]
        c.estado = fila["estado"]
        return c
    