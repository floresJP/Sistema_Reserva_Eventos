# dao/servicio_adicional_dao.py
from config.logger import Logger
from config.base_datos import obtener_conexion
from modelos.servicio_adicional import ServicioAdicional
from validaciones.validadores import GeneradorID, ReservaNoEncontradaError, ServicioAdicionalNoEncontradoError

# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ServicioAdicionalDAO
# ──────────────────────────────────────────────────────────────────────────────
class ServicioAdicionalDAO:
    PREFIJO = "S"
    def __init__(self, reserva_dao):
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__reserva_dao = reserva_dao

    def insertar(self, servicio):
        # Paso 1: Verificar que la reserva exista antes de asociarle un servicio
        if not self.__reserva_dao.buscar_por_id(servicio.id_reserva):
            self.__log.error(f"Servicio fallido: Reserva ID={servicio.id_reserva} no existe")
            raise ReservaNoEncontradaError(servicio.id_reserva)
        # Paso 2: Generar el ID único del servicio, consultando cuántos existen en la BD
        servicio.id_servicio_adicional = self.__gen.generar(self.PREFIJO, self.__siguiente_numero())
        # Paso 3: Abrir conexión a PostgreSQL y crear un cursor para ejecutar comandos
        conn = obtener_conexion()
        cursor = conn.cursor() 
        # Paso 4: Ejecutar el INSERT para guardar el servicio en la tabla "servicio_adicional"
        cursor.execute(
        """INSERT INTO servicio_adicional (id_servicio_adicional, nombre_servicio_adicional, descripcion, precio, estado, id_reserva)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (servicio.id_servicio_adicional, servicio.nombre_servicio_adicional,
        servicio.descripcion, servicio.precio, servicio.estado, servicio.id_reserva)
        )
        # Paso 5: Confirmar los cambios en la base de datos
        conn.commit()
        # Paso 6: Cerrar el cursor y la conexión (liberar recursos)
        cursor.close()
        conn.close()        
        self.__log.info (f"Servicio adicional agregado:{servicio.nombre_servicio_adicional}"
            f"(ID={servicio.id_servicio_adicional}) para Reserva={servicio.id_reserva}")
        return servicio

    def buscar_por_id(self, id_servicio):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicio_adicional WHERE id_servicio_adicional = %s", (id_servicio,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return self.__fila_a_servicio(fila) if fila else None

    def obtener_por_reserva(self, id_reserva):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicio_adicional WHERE id_reserva = %s", (id_reserva,))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()        
        return [self.__fila_a_servicio(f) for f in filas]

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicio_adicional ORDER BY nombre_servicio_adicional")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()        
        return [self.__fila_a_servicio(f) for f in filas]

    def calcularTotal(self, id_reserva):
        servicios = self.obtener_por_reserva(id_reserva)
        return sum(s.precio for s in servicios)

    def eliminar(self, id_servicio):
        s = self.buscar_por_id(id_servicio)
        if not s:
            self.__log.error(f"Eliminar fallido: Servicio ID={id_servicio} no existe")
            raise ServicioAdicionalNoEncontradoError(id_servicio)
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM servicio_adicional WHERE id_servicio_adicional = %s", (id_servicio,))
        conn.commit()
        cursor.close()
        conn.close()
        self.__log.info(f"Servicio adicional eliminado: {s.nombre_servicio_adicional} (ID={id_servicio})")
        return True

    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM servicio_adicional")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total
    
    def __siguiente_numero(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM servicio_adicional")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total + 1

    def __fila_a_servicio(self, fila):
        s = ServicioAdicional(fila["nombre_servicio_adicional"], fila["descripcion"],
        fila["precio"], fila["id_reserva"])
        s.id_servicio_adicional = fila["id_servicio_adicional"]
        s.estado = fila["estado"]
        return s