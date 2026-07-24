import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Este módulo reemplaza SQLite/SQL Server por PostgreSQL.
# La conexión usa RealDictCursor para que cada fila se comporte como un
# diccionario (fila["columna"]) igual que se usa en los DAO del proyecto.

def obtener_conexion():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "bd_sistema_reserva"),
        user=os.getenv("DB_USER", "postgres"),
        # password=os.getenv("DB_PASSWORD", "admi123"), "el password de la maquina donde se corre el Posgred"
        password=os.getenv("DB_PASSWORD", "admi123"),
        cursor_factory=RealDictCursor,
        )
    return conn

def inicializar():
    """
    Crea las tablas si aún no existen (equivalente al script SQL Server,
    adaptado a PostgreSQL). Se llama UNA vez al iniciar el sistema.
        CREATE DATABASE bd_sistema_reserva;
    """
    # "IF NOT EXISTS" evita un error si la tabla ya fue creada en una ejecución anterior.
    conn = obtener_conexion()
    cursor = conn.cursor()
    # Tabla cliente: id_cliente VARCHAR(4) (para poder guardar texto tipo "C001")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente (
            id_cliente     VARCHAR(4) PRIMARY KEY,
            nombre         VARCHAR(40) NOT NULL,
            apellido       VARCHAR(60) NOT NULL,
            dni            VARCHAR(8) NOT NULL,
            telefono       VARCHAR(9) NOT NULL,
            correo         VARCHAR(50) NOT NULL UNIQUE,
            fecha_registro DATE NOT NULL
        )
    """)
# NUMERIC(10,2): tipo de dato exacto para montos de dinero — 10 dígitos en total,
# 2 de ellos decimales (ej. 12345678.90). A diferencia de FLOAT, no tiene errores
# de redondeo, es el tipo recomendado para precios y montos.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tematica (
            id_tematica  VARCHAR(4) PRIMARY KEY,
            descripcion  TEXT NOT NULL,
            precio_base  NUMERIC(10, 2) NOT NULL,
            estado       VARCHAR(20) NOT NULL
        )
    """)
    # Tabla reserva: tiene FOREIGN KEY que enlaza con cliente y tematica.
    # FOREIGN KEY garantiza integridad referencial: no se puede registrar una reserva
    # con un id_cliente o id_tematica que no exista en sus tablas respectivas.

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserva (
            id_reserva       VARCHAR(4) PRIMARY KEY,
            fecha_reserva    DATE NOT NULL,
            fecha_evento     DATE NOT NULL,
            hora_inicio      TIME(0) NOT NULL,
            hora_fin         TIME(0) NOT NULL,
            direccion        VARCHAR(90) NOT NULL,
            edad_cumpleanero INT NULL,
            observaciones    TEXT NULL,
            estado           VARCHAR(20) NOT NULL,
            id_cliente       VARCHAR(4) NOT NULL REFERENCES cliente(id_cliente),
            id_tematica      VARCHAR(4) NOT NULL REFERENCES tematica(id_tematica)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicio_adicional (
            id_servicio_adicional     VARCHAR(4) PRIMARY KEY,
            nombre_servicio_adicional VARCHAR(50) NOT NULL,
            descripcion               TEXT NOT NULL,
            precio                    NUMERIC(10, 2) NOT NULL,
            estado                    VARCHAR(20) NOT NULL,
            id_reserva                VARCHAR(4) NOT NULL REFERENCES reserva(id_reserva)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pago (
            id_pago      VARCHAR(4) PRIMARY KEY,
            fecha_pago   DATE NOT NULL,
            monto_total  NUMERIC(10, 2) NOT NULL,
            metodo_pago  VARCHAR(30) NOT NULL,
            estado_pago  VARCHAR(30) NOT NULL,
            total_cuotas INT NOT NULL,
            id_reserva   VARCHAR(4) NOT NULL REFERENCES reserva(id_reserva)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuota (
            id_cuota          VARCHAR(4) PRIMARY KEY,
            numero_cuota      INT NOT NULL,
            monto             NUMERIC(10, 2) NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            fecha_pago        DATE NULL,
            estado            VARCHAR(20) NOT NULL,
            id_pago           VARCHAR(4) NOT NULL REFERENCES pago(id_pago)
        )
    """)

    # conn.commit() confirma todos los cambios (equivale a "guardar" en la BD).
    # Sin commit(), los cambios se pierden al cerrar la conexión.
    conn.commit()
    cursor.close()
    conn.close()