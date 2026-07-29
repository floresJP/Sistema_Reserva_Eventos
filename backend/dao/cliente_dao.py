# dao/cliente_dao.py
import psycopg2
from config.logger import Logger
from config.base_datos import obtener_conexion
from modelos.cliente import Cliente
from validaciones.validadores import (
    GeneradorID,
    CorreoDuplicadoError,
    ClienteNoEncontradoError,
    ClienteConReservasError,
    DatoInvalidoError,
)
# ─────────────────────────────────────────────────
# PATRÓN DAO — ClienteDAO (conectado a PostgreSQL)
# ─────────────────────────────────────────────────
class ClienteDAO:
    PREFIJO = "C"

    def __init__(self):
        self.__log = Logger()
        self.__gen = GeneradorID()

    def registrar(self, cliente):
        # Paso 1: Verificar que el correo no esté duplicado
        if self.buscar_por_correo(cliente.correo):
            self.__log.warning(f"Correo duplicado: {cliente.correo}")
            raise CorreoDuplicadoError(cliente.correo)

        # Paso 2: Verificar que el DNI no esté duplicado
        if self.buscar_por_dni(cliente.dni):
            self.__log.warning(f"DNI duplicado: {cliente.dni}")
            raise DatoInvalidoError("dni", f"'{cliente.dni}' ya está registrado con otro cliente")

        # Paso 3: Generar el ID único del cliente (ej. "C003"),
        # consultando cuántos clientes existen realmente en la BD
        cliente.id_cliente = self.__gen.generar(self.PREFIJO, self.__siguiente_numero())

        # Paso 4: Abrir conexión a PostgreSQL y crear un cursor para ejecutar comandos SQL
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Paso 5: Ejecutar el INSERT para guardar el cliente en la tabla "cliente"
        # Los %s son marcadores de posición (placeholders) que psycopg2 reemplaza de forma segura
        cursor.execute(
            """INSERT INTO cliente (id_cliente, nombre, apellido, dni, telefono, correo, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (cliente.id_cliente, cliente.nombre, cliente.apellido, cliente.dni,
            cliente.telefono, cliente.correo, cliente.fecha_registro)
        )
        # Paso 6: Confirmar los cambios en la base de datos
        # Sin este commit(), el INSERT quedaría "pendiente" y se perdería al cerrar la conexión
        conn.commit()

        # Paso 7: Cerrar el cursor y la conexión (liberar recursos)
        cursor.close()
        conn.close()

        # Paso 8: Registrar en el log que el cliente fue guardado exitosamente
        self.__log.info(f"Cliente registrado: {cliente.nombre} (ID={cliente.id_cliente})")

        # Paso 9: Devolver el objeto cliente ya con su ID asignado
        return cliente

    def buscar_por_correo(self, correo):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cliente WHERE correo = %s", (correo,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return self.__fila_a_cliente(fila) if fila else None

    def buscar_por_dni(self, dni):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cliente WHERE dni = %s", (dni,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return self.__fila_a_cliente(fila) if fila else None

    def buscar_por_id(self, id_cliente):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cliente WHERE id_cliente = %s", (id_cliente,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return self.__fila_a_cliente(fila) if fila else None

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cliente ORDER BY nombre")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self.__fila_a_cliente(f) for f in filas]

    def actualizarDatos(self, id_cliente, telefono=None, correo=None):
        # Paso 1: Verificar que el cliente exista
        c = self.buscar_por_id(id_cliente)
        if not c:
            self.__log.error(f"Actualizar fallido: Cliente ID={id_cliente} no existe")
            raise ClienteNoEncontradoError(id_cliente)

        # Paso 2: Si no se pasó un dato nuevo, se mantiene el valor actual
        nuevo_telefono = telefono if telefono else c.telefono
        nuevo_correo = correo if correo else c.correo

        # Paso 3: Ejecutar el UPDATE en PostgreSQL
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cliente SET telefono=%s, correo=%s WHERE id_cliente=%s",
            (nuevo_telefono, nuevo_correo, id_cliente)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Paso 4: Actualizar también el objeto en memoria para devolverlo actualizado
        c.telefono = nuevo_telefono
        c.correo = nuevo_correo
        self.__log.info(f"Cliente actualizado: ID={id_cliente}")
        return c

    def eliminar(self, id_cliente):
        # Paso 1: Verificar que el cliente exista antes de intentar eliminarlo
        c = self.buscar_por_id(id_cliente)
        if not c:
            self.__log.error(f"Eliminar fallido: Cliente ID={id_cliente} no existe")
            raise ClienteNoEncontradoError(id_cliente)

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            # Paso 2: Intentar eliminar el cliente de la tabla
            cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
            conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            # Si el cliente tiene reservas asociadas, PostgreSQL bloquea el DELETE
            # por la FOREIGN KEY en la tabla "reserva" (integridad referencial)
            conn.rollback()
            cursor.close()
            conn.close()
            self.__log.warning(f"Eliminar fallido: Cliente ID={id_cliente} tiene reservas asociadas")
            raise ClienteConReservasError(id_cliente)

        cursor.close()
        conn.close()

        self.__log.info(f"Cliente eliminado: {c.nombre} {c.apellido} (ID={id_cliente})")
        return True

    def obtenerReservas(self, id_cliente, reserva_dao):
        if not self.buscar_por_id(id_cliente):
            raise ClienteNoEncontradoError(id_cliente)
        return reserva_dao.obtener_por_cliente(id_cliente)

    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM cliente")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total

    def __siguiente_numero(self):
        # Consulta cuántos clientes existen actualmente en la BD
        # y devuelve el próximo número consecutivo a usar en el ID
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM cliente")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total + 1

    def __fila_a_cliente(self, fila):
        # Convierte una fila de PostgreSQL (diccionario, por RealDictCursor)
        # en un objeto Cliente de nuestro modelo
        c = Cliente(fila["nombre"], fila["apellido"], fila["dni"],
        fila["telefono"], fila["correo"])
        c.id_cliente = fila["id_cliente"]
        c.fecha_registro = fila["fecha_registro"]
        return c