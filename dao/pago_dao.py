# dao/pago_dao.py
from config.logger import Logger
from config.base_datos import obtener_conexion
from modelos.pago import Pago
from validaciones.validadores import GeneradorID, ReservaNoEncontradaError, PagoNoEncontradoError
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — PagoDAO
# ──────────────────────────────────────────────────────────────────────────────
class PagoDAO:
    PREFIJO = "P"
    def __init__(self, reserva_dao):
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__reserva_dao = reserva_dao

    def registrar(self, pago):
        #Verificar que la reserva exista antes de asociarle un pago
        if not self.__reserva_dao.buscar_por_id(pago.id_reserva):
            self.__log.error(f"Pago fallido: Reserva ID={pago.id_reserva} no existe")
            raise ReservaNoEncontradaError(pago.id_reserva)
        
        #Generar el ID único del pago (ej. "P003"),
        # consultando cuántos pagos existen realmente en la BD
        pago.id_pago = self.__gen.generar(self.PREFIJO, self.__siguiente_numero())
        
        #Abrir conexión a PostgreSQL y crear un cursor para ejecutar comandos SQL
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        #Ejecutar el INSERT para guardar el pago en la tabla "pago"
        cursor.execute(
        """INSERT INTO pago (id_pago, fecha_pago, monto_total, metodo_pago,
        estado_pago, total_cuotas, id_reserva)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (pago.id_pago, pago.fecha_pago, pago.monto_total, pago.metodo_pago,
        pago.estado_pago, pago.total_cuotas, pago.id_reserva)
        )
        #  Confirmar los cambios en la base de datos
        conn.commit()

        # Cerrar el cursor y la conexión (liberar recursos)
        cursor.close()
        conn.close()   
        self.__log.info(
            f"Pago registrado: {pago.id_pago} S/.{pago.monto_total:.2f} "
            f"({pago.metodo_pago}) para Reserva={pago.id_reserva}")
        return pago

    def buscar_por_id(self, id_pago):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pago WHERE id_pago = %s", (id_pago,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()          
        return self.__fila_a_pago(fila) if fila else None

    def obtener_por_reserva(self, id_reserva):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pago WHERE id_reserva = %s", (id_reserva,))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self.__fila_a_pago(f) for f in filas]

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pago ORDER BY fecha_pago")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self.__fila_a_pago(f) for f in filas]

    def marcar_pagado(self, id_pago):
        p = self.buscar_por_id(id_pago)
        if not p:
            self.__log.error(f"Marcar pagado fallido: Pago ID={id_pago} no existe")
            raise PagoNoEncontradoError(id_pago)
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE pago SET estado_pago=%s WHERE id_pago=%s", ("Pagado", id_pago))
        conn.commit()
        cursor.close()
        conn.close()
        p.marcar_pagado()
        self.__log.info(f"Pago marcado como Pagado: ID={id_pago}")
        return p

    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM pago")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total 
    
    def __siguiente_numero(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM pago")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total + 1

    def __fila_a_pago(self, fila):
        p = Pago(fila["monto_total"], fila["metodo_pago"], fila["total_cuotas"], fila["id_reserva"])
        p.id_pago = fila["id_pago"]
        p.fecha_pago = fila["fecha_pago"]
        p.estado_pago = fila["estado_pago"]
        return p