# dao/reserva_dao.py
import psycopg2
from config.logger import Logger
from validaciones.validadores import GeneradorID, ClienteNoEncontradoError, TematicaNoEncontradaError, ReservaNoEncontradaError, ReservaConDependenciasError,DatoInvalidoError
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
    
    def actualizar(self, id_reserva, fecha_evento=None, hora_inicio=None, hora_fin=None,
                direccion=None, edad_cumpleanero=None, observaciones=None):
        # Paso 1: Verificar que la reserva exista
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Actualizar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)

        # Paso 2: Si no se pasó un dato nuevo, se mantiene el valor actual
        nueva_fecha_evento = fecha_evento if fecha_evento else r.fecha_evento
        nueva_hora_inicio = hora_inicio if hora_inicio else r.hora_inicio
        nueva_hora_fin = hora_fin if hora_fin else r.hora_fin
        nueva_direccion = direccion if direccion else r.direccion
        nueva_edad = edad_cumpleanero if edad_cumpleanero is not None else r.edad_cumpleanero
        nuevas_observaciones = observaciones if observaciones is not None else r.observaciones
                
        # Paso 2b: Ahora que ya tenemos las DOS horas finales combinadas
        # (la nueva si vino en la peticion, o la que ya tenia la reserva
        # si no vino), SI podemos comparar con seguridad.
        if nueva_hora_fin <= nueva_hora_inicio:
            self.__log.error(f"Actualizar fallido: Reserva ID={id_reserva} hora_fin <= hora_inicio")
            raise DatoInvalidoError("hora_fin", "debe ser posterior a hora_inicio")

        # Paso 3: Ejecutar el UPDATE en PostgreSQL
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE reserva SET fecha_evento=%s, hora_inicio=%s, hora_fin=%s,
            direccion=%s, edad_cumpleanero=%s, observaciones=%s WHERE id_reserva=%s""",
            (nueva_fecha_evento, nueva_hora_inicio, nueva_hora_fin,
            nueva_direccion, nueva_edad, nuevas_observaciones, id_reserva)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Paso 4: Actualizar también el objeto en memoria para devolverlo actualizado
        r.fecha_evento = nueva_fecha_evento
        r.hora_inicio = nueva_hora_inicio
        r.hora_fin = nueva_hora_fin
        r.direccion = nueva_direccion
        r.edad_cumpleanero = nueva_edad
        r.observaciones = nuevas_observaciones
        self.__log.info(f"Reserva actualizada: ID={id_reserva}")
        return r

    def eliminar(self, id_reserva):
        # Paso 1: Verificar que la reserva exista antes de intentar eliminarla
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Eliminar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reserva WHERE id_reserva = %s", (id_reserva,))
            conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            # Si la reserva tiene servicios adicionales o pagos asociados,
            # PostgreSQL bloquea el DELETE por las FOREIGN KEY correspondientes
            conn.rollback()
            cursor.close()
            conn.close()
            self.__log.warning(f"Eliminar fallido: Reserva ID={id_reserva} tiene servicios o pagos asociados")
            raise ReservaConDependenciasError(id_reserva)

        cursor.close()
        conn.close()
        self.__log.info(f"Reserva eliminada: ID={id_reserva}")
        return True
    
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
        cursor.execute("SELECT MAX(CAST(SUBSTRING(id_reserva FROM 2) AS INTEGER)) AS maximo FROM reserva")
        resultado = cursor.fetchone()["maximo"]
        cursor.close()
        conn.close()
        return (resultado or 0)+1

    def __fila_a_reserva(self, fila):
        r = Reserva(fila["fecha_evento"], fila["hora_inicio"], fila["hora_fin"],
                fila["direccion"], fila["edad_cumpleanero"], fila["observaciones"],
                fila["id_cliente"], fila["id_tematica"])
        r.id_reserva = fila["id_reserva"]
        r.fecha_reserva = fila["fecha_reserva"]
        r.estado = fila["estado"]
        return r

    