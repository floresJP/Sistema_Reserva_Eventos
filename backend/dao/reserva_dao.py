# dao/reserva_dao.py
from config.logger import Logger
from validaciones.validadores import GeneradorID, ClienteNoEncontradoError, TematicaNoEncontradaError, ReservaNoEncontradaError
from config.base_datos import obtener_conexion
from modelos.reserva import Reserva
#──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ReservaDAO
# ──────────────────────────────────────────────────────────────────────────────
class ReservaDAO:
    PREFIJO = "R"

    def __init__(self, cliente_dao, tematica_dao):
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
        reserva.id_reserva = self.__gen.generar(self.PREFIJO, self.__siguiente_numero())
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
        """INSERT INTO reserva (id_reserva, fecha_reserva, fecha_evento, hora_inicio, hora_fin,
        direccion, edad_cumpleanero, observaciones, estado,
        id_cliente, id_tematica)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (reserva.id_reserva, reserva.fecha_reserva, reserva.fecha_evento,
        reserva.hora_inicio, reserva.hora_fin, reserva.direccion,
        reserva.edad_cumpleanero, reserva.observaciones, reserva.estado,
        reserva.id_cliente, reserva.id_tematica)
        )
        conn.commit()
        cursor.close()
        conn.close()
        self.__log.info(f"Reserva creada: ID={reserva.id_reserva} para Cliente={reserva.id_cliente}")
        return reserva
    
    def buscar_por_id(self, id_reserva):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reserva WHERE id_reserva = %s", (id_reserva,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return self.__fila_a_reserva(fila) if fila else None

    def obtener_por_cliente(self, id_cliente):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reserva WHERE id_cliente = %s", (id_cliente,))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self.__fila_a_reserva(f) for f in filas]

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reserva ORDER BY fecha_evento")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self.__fila_a_reserva(f) for f in filas]
        
    def confirmar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Confirmar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE reserva SET estado=%s WHERE id_reserva=%s", ("Confirmada", id_reserva))
        conn.commit()
        cursor.close()
        conn.close()
        r.confirmar()
        self.__log.info(f"Reserva confirmada: ID={id_reserva}")   
        return r

    def cancelar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Cancelar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE reserva SET estado=%s WHERE id_reserva=%s", ("Cancelada", id_reserva))
        conn.commit()
        cursor.close()
        conn.close()
        r.cancelar()       
        self.__log.info(f"Reserva cancelada: ID={id_reserva}")
        return r

    def completar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Completar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("UPDATE reserva SET estado=%s WHERE id_reserva=%s", ("Completada", id_reserva))
        conn.commit()
        cursor.close()
        conn.close()
        r.completar()       
        self.__log.info(f"Reserva completada: ID={id_reserva}")
        return r
    
    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM reserva")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total
    
    def __siguiente_numero(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM reserva")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total + 1

    def __fila_a_reserva(self, fila):
        r = Reserva(fila["fecha_evento"], fila["hora_inicio"], fila["hora_fin"],
                fila["direccion"], fila["edad_cumpleanero"], fila["observaciones"],
                fila["id_cliente"], fila["id_tematica"])
        r.id_reserva = fila["id_reserva"]
        r.fecha_reserva = fila["fecha_reserva"]
        r.estado = fila["estado"]
        return r

    