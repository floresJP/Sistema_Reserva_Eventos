# dao/tematica_dao.py
from config.logger import Logger
from config.base_datos import obtener_conexion
from modelos.tematica import Tematica
from validaciones.validadores import GeneradorID
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — TematicaDAO
# ──────────────────────────────────────────────────────────────────────────────
class TematicaDAO:
    PREFIJO = "T"

    def __init__(self):
        self.__log = Logger()
        self.__gen = GeneradorID()

    def insertar(self, tematica):
        # Paso 1: Generar el ID único de la tematica (ej. "T003"),
        # consultando cuántas tematicas existen realmente en la BD
        tematica.id_tematica = self.__gen.generar(self.PREFIJO, self.__siguiente_numero())
        # Paso 2: Abrir conexión a PostgreSQL y crear un cursor para ejecutar comandos SQL
        conn = obtener_conexion()
        cursor = conn.cursor()        
        # Paso 3: Ejecutar el INSERT para guardar la tematica en la tabla "tematica"
        # Los %s son marcadores de posición que psycopg2 reemplaza de forma segura
        cursor.execute(
        """INSERT INTO tematica (id_tematica, descripcion, precio_base, estado)
        VALUES (%s, %s, %s, %s)""",
        (tematica.id_tematica, tematica.descripcion, tematica.precio_base, tematica.estado)
        )
        # Paso 4: Confirmar los cambios en la base de datos
        conn.commit()
        # Paso 5: Cerrar el cursor y la conexión (liberar recursos)
        cursor.close()
        conn.close()        
        self.__log.info(f"Tematica agregada: {tematica.descripcion} (ID={tematica.id_tematica})")
        return tematica

    def buscar_por_id(self, id_tematica):
        # Consulta la tematica directamente en PostgreSQL por su ID
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tematica WHERE id_tematica = %s", (id_tematica,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()        
        return self.__fila_a_tematica(fila) if fila else None

    def obtener_todos(self):
        # Trae todas las tematicas ordenadas alfabéticamente por descripción
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tematica ORDER BY descripcion")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()        
        return [self.__fila_a_tematica(f) for f in filas]

    def obtener_disponibles(self):
        # Filtra directamente en SQL las tematicas con estado 'Disponible'
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tematica WHERE estado = %s", ("Disponible",))
        filas = cursor.fetchall()
        cursor.close()
        conn.close()        
        return [self.__fila_a_tematica(f) for f in filas]

    def total(self):
        # Cuenta cuántas tematicas hay guardadas en la base de datos
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM tematica")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total
    def __siguiente_numero(self):
        # Consulta cuántas tematicas existen actualmente en la BD
        # y devuelve el próximo número consecutivo a usar en el ID
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM tematica")
        total = cursor.fetchone()["total"]
        cursor.close()
        conn.close()
        return total + 1

    def __fila_a_tematica(self, fila):
        # Convierte una fila de PostgreSQL (diccionario, por RealDictCursor)
        # en un objeto Tematica de nuestro modelo
        t = Tematica(fila["descripcion"], fila["precio_base"])
        t.id_tematica = fila["id_tematica"]
        t.estado = fila["estado"]
        return t
    
        