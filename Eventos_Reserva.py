# DAOSingleton_reservas.py
# Sistema de Gestión de Reservas — Singleton + DAO + Validaciones (4 pilares de POO)
# 6 tablas del esquema: BD_SISTEMA_RESERVA (SQL Server)
#   cliente, tematica, reserva, servicio_adicional, pago, cuota

# 4 PILARES DE POO aplicados en el módulo de Validaciones:
#   ABSTRACCION     -> ValidadorBase(ABC) con @abstractmethod validar()
#   ENCAPSULAMIENTO -> self._campo, self._prefijo guardados dentro de cada objeto
#   HERENCIA        -> cada Validador___ hereda de ValidadorBase
#   POLIMORFISMO    -> todos se llaman igual (objeto.validar(texto)) pero
#                      cada uno hace algo distinto por dentro
import datetime
import re
from abc import ABC, abstractmethod
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN SINGLETON #1 — Logger
# ──────────────────────────────────────────────────────────────────────────────
class Logger:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._logs = []
        return cls._instancia

    def _registrar(self, nivel, mensaje):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self._logs.append({"hora": hora, "nivel": nivel, "msg": mensaje})

    def info(self, msg):    self._registrar("INFO",    msg)
    def warning(self, msg): self._registrar("WARNING", msg)
    def error(self, msg):   self._registrar("ERROR",   msg)

    def mostrar_logs(self):
        print(f"\n=== HISTORIAL DEL SISTEMA ({len(self._logs)} eventos) ===")
        for log in self._logs:
            print(f"  [{log['hora']}] {log['nivel']:7} | {log['msg']}")

    def limpiar(self):
        self._logs.clear()
        print("  OK Historial de logs limpiado")
        
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN SINGLETON #2 — SistemaConfig
# ──────────────────────────────────────────────────────────────────────────────
class SistemaConfig:
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
            cls._inst.nombre  = "SISTEMA DE RESERVA DE EVENTOS"
            cls._inst.version = "1.0"
            cls._inst.empresa = "Eventix"
            cls._inst.autor   = "AMPUERO - PASCACIO"

            Logger().info(
                f"Sistema Iniciado: {cls._inst.nombre} "
                f"Version: {cls._inst.version}"
                f"Empresa: {cls._inst.empresa} "
                f"Autor: {cls._inst.autor}")
        return cls._inst

# ──────────────────────────────────────────────────────────────────────────────
# EXCEPCIONES PERSONALIZADAS
# ──────────────────────────────────────────────────────────────────────────────
class ClienteNoEncontradoError(Exception):
    def __init__(self, id_cliente):
        super().__init__(f"Cliente ID={id_cliente} no encontrado")

class CorreoDuplicadoError(Exception):
    def __init__(self, correo):
        super().__init__(f"Correo '{correo}' ya registrado")

class TematicaNoEncontradaError(Exception):
    def __init__(self, id_tematica):
        super().__init__(f"Tematica ID={id_tematica} no encontrada")

class ReservaNoEncontradaError(Exception):
    def __init__(self, id_reserva):
        super().__init__(f"Reserva ID={id_reserva} no encontrada")

class ServicioAdicionalNoEncontradoError(Exception):
    def __init__(self, id_servicio):
        super().__init__(f"Servicio adicional ID={id_servicio} no encontrado")

class PagoNoEncontradoError(Exception):
    def __init__(self, id_pago):
        super().__init__(f"Pago ID={id_pago} no encontrado")

class CuotaNoEncontradaError(Exception):
    def __init__(self, id_cuota):
        super().__init__(f"Cuota ID={id_cuota} no encontrada")

class DatoInvalidoError(Exception):
    def __init__(self, campo, motivo):
        super().__init__(f"Dato inválido en '{campo}': {motivo}")
        
# ──────────────────────────────────────────────────────────────────────────────
# GENERADOR DE IDs CON PREFIJO
# Genera códigos tipo 'C001', 'T001', 'R001' — igual formato que tu SQL.
# ──────────────────────────────────────────────────────────────────────────────
class GeneradorID:
    def generar(self, prefijo, numero):
        if numero > 999:
            raise DatoInvalidoError("id", f"límite de códigos alcanzado para el prefijo '{prefijo}'")
        return f"{prefijo}{numero:03d}"
    
# ──────────────────────────────────────────────────────────────────────────────
# ValidadorBase es una clase ABSTRACTA: no se puede crear un objeto ValidadorBase() 
# directamente (ABC + abstractmethod lo impiden).
# ──────────────────────────────────────────────────────────────────────────────
class ValidadorBase(ABC):
    def __init__(self, campo):
        self._campo = campo

    @abstractmethod
    def validar(self, texto):
        pass
# ──────────────────────────────────────────────────────────────────────────────
# polimorfismo (mismo método, comportamiento distinto según la clase).
# ──────────────────────────────────────────────────────────────────────────────
class ValidadorNombre(ValidadorBase):
    def __init__(self, campo="nombre"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        if not texto:
            raise DatoInvalidoError(self._campo, "no puede estar vacío")
        # regex: solo letras (con tildes y ñ) y espacios. Rechaza números.
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", texto):
            raise DatoInvalidoError(self._campo, "solo se permiten letras y espacios (sin números)")
        # .title() convierte "juan perez" -> "Juan Perez"
        return texto.title()

class ValidadorDNI(ValidadorBase):
    def __init__(self):
        super().__init__("dni")

    def validar(self, texto):
        texto = texto.strip()
        if not texto:
            raise DatoInvalidoError(self._campo, "no puede estar vacío")
        # \d{8} = exactamente 8 dígitos, ni más ni menos, sin letras.
        if not re.match(r"^\d{8}$", texto):
            raise DatoInvalidoError(self._campo, "debe tener exactamente 8 dígitos numéricos (sin letras)")
        return texto

class ValidadorTelefono(ValidadorBase):
    def __init__(self):
        super().__init__("telefono")

    def validar(self, texto):
        texto = texto.strip()
        if not texto:
            raise DatoInvalidoError(self._campo, "no puede estar vacío")
        # \d{9} = exactamente 9 dígitos, igual que telefono VARCHAR(9) en el SQL.
        if not re.match(r"^\d{9}$", texto):
            raise DatoInvalidoError(self._campo, "debe tener exactamente 9 dígitos numéricos (sin letras)")
        return texto

class ValidadorCorreo(ValidadorBase):
    def __init__(self):
        super().__init__("correo")

    def validar(self, texto):
        # Se guarda siempre en minúscula, sin importar cómo lo escriba el usuario.
        texto = texto.strip().lower()
        if not texto:
            raise DatoInvalidoError(self._campo, "no puede estar vacío")
        # Formato básico usuario@dominio.ext
        if not re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", texto):
            raise DatoInvalidoError(self._campo, "formato inválido, debe ser tipo usuario@dominio.com")
        return texto

class ValidadorDireccion(ValidadorBase):
    # Se sigue usando para la direccion del EVENTO en Reserva
    # (ya no se usa para Cliente, esa columna fue eliminada del esquema).
    def __init__(self, campo="direccion"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        if not texto:
            raise DatoInvalidoError(self._campo, "no puede estar vacía")
        if len(texto) < 5:
            raise DatoInvalidoError(self._campo, "debe tener al menos 5 caracteres")
        return texto

class ValidadorTextoGeneral(ValidadorBase):
    # A diferencia de ValidadorNombre, este SÍ permite números
    # (útil para "nombre_servicio_adicional" tipo "DJ y sonido 4h").
    def __init__(self, campo="texto"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        if not texto:
            raise DatoInvalidoError(self._campo, "no puede estar vacío")
        if len(texto) < 3:
            raise DatoInvalidoError(self._campo, "debe tener al menos 3 caracteres")
        return texto

class ValidadorPrecio(ValidadorBase):
    def __init__(self, campo="precio"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        try:
            valor = float(texto)
        except ValueError:
            raise DatoInvalidoError(self._campo, "debe ser un número (ej. 150.50)")
        if valor < 0:
            raise DatoInvalidoError(self._campo, "no puede ser negativo")
        return valor

class ValidadorEnteroPositivo(ValidadorBase):
    def __init__(self, campo="valor"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        try:
            valor = int(texto)
        except ValueError:
            raise DatoInvalidoError(self._campo, "debe ser un número entero (sin letras)")
        if valor <= 0:
            raise DatoInvalidoError(self._campo, "debe ser un número mayor a 0")
        return valor

class ValidadorHora(ValidadorBase):
    def __init__(self, campo="hora"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        # HH:MM en formato 24 horas: 00-23 : 00-59
        if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", texto):
            raise DatoInvalidoError(self._campo, "formato inválido, debe ser HH:MM (ej. 14:30)")
        return texto

class ValidadorFecha(ValidadorBase):
    def __init__(self, campo="fecha"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip()
        try:
            # strptime valida fechas REALES (rechaza 2026-02-30, por ejemplo).
            return datetime.datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            raise DatoInvalidoError(self._campo, "formato inválido, debe ser YYYY-MM-DD (ej. 2026-07-10)")
        
class ValidadorCodigo(ValidadorBase):
    # Valida formato tipo 'C001', 'T007', 'R012': prefijo + 3 dígitos.
    def __init__(self, prefijo, campo="id"):
        super().__init__(campo)
        # ENCAPSULAMIENTO: cada objeto ValidadorCodigo guarda SU propio prefijo
        # (uno para clientes, otro para tematicas, otro para reservas, etc.)
        self._prefijo = prefijo

    def validar(self, texto):
        texto = texto.strip().upper()
        patron = rf"^{self._prefijo}\d{{3}}$"
        if not re.match(patron, texto):
            raise DatoInvalidoError(self._campo, f"debe tener el formato '{self._prefijo}' + 3 dígitos (ej. {self._prefijo}001)")
        return texto
    
class ValidadorMetodoPago(ValidadorBase):
    METODOS_VALIDOS = {"YAPE", "PLIN", "TRANSFERENCIA", "EFECTIVO", "TARJETA"}

    def __init__(self, campo="metodo_pago"):
        super().__init__(campo)

    def validar(self, texto):
        texto = texto.strip().upper()
        if texto not in self.METODOS_VALIDOS:
            opciones = ", ".join(sorted(self.METODOS_VALIDOS))
            raise DatoInvalidoError(self._campo, f"debe ser uno de: {opciones}")
        return texto
# ──────────────────────────────────────────────────────────────────────────────
# HELPER DE ENTRADA — pedir_dato()
# recibe un OBJETO validador ya creado (ej. ValidadorDNI()) en vez
# de una función suelta. Llama a validador_obj.validar(texto) 
# ──────────────────────────────────────────────────────────────────────────────
def pedir_dato(mensaje, validador_obj, opcional=False, valor_si_vacio=None):
    while True:
        texto = input(mensaje)
        if opcional and not texto.strip():
            return valor_si_vacio
        try:
            return validador_obj.validar(texto)
        except DatoInvalidoError as ex:
            print(f"  ERROR: {ex}")
        
        
# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Cliente
# (sin direccion: la direccion que importa es la del EVENTO, vive en Reserva)
# ──────────────────────────────────────────────────────────────────────────────
class Cliente:
    def __init__(self, nombre, apellido, dni, telefono, correo):
        self.id_cliente     = None
        self.nombre         = nombre
        self.apellido       = apellido
        self.dni            = dni
        self.telefono       = telefono
        self.correo         = correo
        self.fecha_registro = datetime.date.today()

    def __str__(self):
        return (f"[{self.id_cliente}] {self.nombre} {self.apellido} | "
                f"DNI:{self.dni} | {self.correo} | {self.telefono}")
# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Tematica
# ──────────────────────────────────────────────────────────────────────────────
class Tematica:
    def __init__(self, descripcion, precio_base):
        self.id_tematica = None
        self.descripcion = descripcion
        self.precio_base = precio_base
        self.estado      = "Disponible"

    def activar(self):
        self.estado = "Disponible"

    def desactivar(self):
        self.estado = "No Disponible"

    def estado_disponible(self):
        return self.estado == "Disponible"

    def __str__(self):
        return f"[{self.id_tematica}] {self.descripcion} | S/.{self.precio_base:.2f} | {self.estado}"
#────────────────────────────────────────────────────────────
# MODELO — Reserva
# ──────────────────────────────────────────────────────────────────────────────
class Reserva:
    def __init__(self, fecha_evento, hora_inicio, hora_fin, direccion,edad_cumpleanero, observaciones, id_cliente, id_tematica):
        self.id_reserva       = None
        self.fecha_reserva    = datetime.date.today()
        self.fecha_evento     = fecha_evento
        self.hora_inicio      = hora_inicio
        self.hora_fin         = hora_fin
        self.direccion        = direccion
        self.edad_cumpleanero = edad_cumpleanero
        self.observaciones    = observaciones
        self.estado           = "Pendiente"
        self.id_cliente       = id_cliente
        self.id_tematica      = id_tematica

    def confirmar(self):
        self.estado = "Confirmada"

    def cancelar(self):
        self.estado = "Cancelada"

    def completar(self):
        self.estado = "Completada"

    def __str__(self):
        return (f"[{self.id_reserva}] Evento:{self.fecha_evento} "
                f"{self.hora_inicio}-{self.hora_fin} | {self.direccion} | "
                f"Estado:{self.estado} | Cliente:{self.id_cliente} | Tematica:{self.id_tematica}")
# ──────────────────────────────────────────────────────────────────────────────
# MODELO — ServicioAdicional
# ──────────────────────────────────────────────────────────────────────────────
class ServicioAdicional:
    def __init__(self, nombre_servicio, descripcion, precio, id_reserva):
        self.id_servicio_adicional     = None
        self.nombre_servicio_adicional = nombre_servicio
        self.descripcion               = descripcion
        self.precio                    = precio
        self.estado                    = "Activo"
        self.id_reserva                = id_reserva

    def activar(self):
        self.estado = "Activo"

    def desactivar(self):
        self.estado = "Inactivo"

    def __str__(self):
        return (f"[{self.id_servicio_adicional}] {self.nombre_servicio_adicional} | "
                f"S/.{self.precio:.2f} | {self.estado} | Reserva:{self.id_reserva}")
# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Pago
# ──────────────────────────────────────────────────────────────────────────────
class Pago:
    def __init__(self, monto_total, metodo_pago, total_cuotas, id_reserva):
        self.id_pago       = None
        self.fecha_pago    = datetime.date.today()
        self.monto_total   = monto_total
        self.metodo_pago   = metodo_pago
        self.estado_pago   = "Pagado" if total_cuotas == 1 else "Pendiente"
        self.total_cuotas  = total_cuotas
        self.id_reserva    = id_reserva

    def marcar_pago_parcial(self):
        self.estado_pago = "Pago parcial"

    def marcar_pagado(self):
        self.estado_pago = "Pagado"

    def __str__(self):
        return (f"[{self.id_pago}] {self.fecha_pago} | S/.{self.monto_total:.2f} | "
                f"{self.metodo_pago} | {self.estado_pago} | Cuotas:{self.total_cuotas} | "
                f"Reserva:{self.id_reserva}")
# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Cuota
# ──────────────────────────────────────────────────────────────────────────────
class Cuota:
    def __init__(self, numero_cuota, monto, fecha_vencimiento, id_pago):
        self.id_cuota           = None
        self.numero_cuota       = numero_cuota
        self.monto              = monto
        self.fecha_vencimiento  = fecha_vencimiento
        self.fecha_pago         = None
        self.estado             = "Pendiente"
        self.id_pago            = id_pago

    def marcarPagada(self, fecha_pago=None):
        self.fecha_pago = fecha_pago if fecha_pago else datetime.date.today()
        self.estado = "Pagada"

    def verificarVencimiento(self):
        if self.estado == "Pagada":
            return False
        if datetime.date.today() > self.fecha_vencimiento:
            self.estado = "Vencida"
            return True
        return False

    def __str__(self):
        pago_str = self.fecha_pago if self.fecha_pago else "—"
        return (f"[{self.id_cuota}] Cuota #{self.numero_cuota} | S/.{self.monto:.2f} | "
                f"Vence:{self.fecha_vencimiento} | Pagada:{pago_str} | "
                f"{self.estado} | Pago:{self.id_pago}")
        
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ClienteDAO
# ──────────────────────────────────────────────────────────────────────────────
class ClienteDAO:
    PREFIJO = "C"

    def __init__(self):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()

    def registrar(self, cliente):
        if self.buscar_por_correo(cliente.correo):
            self.__log.warning(f"Correo duplicado: {cliente.correo}")
            raise CorreoDuplicadoError(cliente.correo)
        if self.buscar_por_dni(cliente.dni):
            self.__log.warning(f"DNI duplicado: {cliente.dni}")
            raise DatoInvalidoError("dni", f"'{cliente.dni}' ya está registrado con otro cliente")

        cliente.id_cliente = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(cliente)
        self.__log.info(f"Cliente registrado: {cliente.nombre} (ID={cliente.id_cliente})")
        return cliente

    def buscar_por_correo(self, correo):
        for c in self.__bd:
            if c.correo == correo: return c
        return None

    def buscar_por_dni(self, dni):
        for c in self.__bd:
            if c.dni == dni: return c
        return None

    def buscar_por_id(self, id_cliente):
        for c in self.__bd:
            if c.id_cliente == id_cliente: return c
        return None

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda c: c.nombre)

    def actualizarDatos(self, id_cliente, telefono=None, correo=None):
        c = self.buscar_por_id(id_cliente)
        if not c:
            self.__log.error(f"Actualizar fallido: Cliente ID={id_cliente} no existe")
            raise ClienteNoEncontradoError(id_cliente)
        if telefono:  c.telefono  = telefono
        if correo:    c.correo    = correo
        self.__log.info(f"Cliente actualizado: ID={id_cliente}")
        return c

    def obtenerReservas(self, id_cliente, reserva_dao):
        if not self.buscar_por_id(id_cliente):
            raise ClienteNoEncontradoError(id_cliente)
        return reserva_dao.obtener_por_cliente(id_cliente)

    def total(self): return len(self.__bd)
    
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — TematicaDAO
# ──────────────────────────────────────────────────────────────────────────────
class TematicaDAO:
    PREFIJO = "T"

    def __init__(self):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()

    def insertar(self, tematica):
        tematica.id_tematica = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(tematica)
        self.__log.info(f"Tematica agregada: {tematica.descripcion} (ID={tematica.id_tematica})")
        return tematica

    def buscar_por_id(self, id_tematica):
        for t in self.__bd:
            if t.id_tematica == id_tematica: return t
        return None

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda t: t.descripcion)

    def obtener_disponibles(self):
        return [t for t in self.__bd if t.estado_disponible()]

    def total(self): return len(self.__bd)
    
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ReservaDAO
# ──────────────────────────────────────────────────────────────────────────────
class ReservaDAO:
    PREFIJO = "R"

    def __init__(self, cliente_dao, tematica_dao):
        self.__bd  = []
        self.__cid = 1
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
        reserva.id_reserva = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(reserva)
        self.__log.info(f"Reserva creada: ID={reserva.id_reserva} para Cliente={reserva.id_cliente}")
        return reserva
    
    def buscar_por_id(self, id_reserva):
        for r in self.__bd:
            if r.id_reserva == id_reserva: return r
        return None

    def obtener_por_cliente(self, id_cliente):
        return [r for r in self.__bd if r.id_cliente == id_cliente]

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda r: r.fecha_evento)

    def confirmar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Confirmar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        r.confirmar()
        self.__log.info(f"Reserva confirmada: ID={id_reserva}")
        return r

    def cancelar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Cancelar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        r.cancelar()
        self.__log.info(f"Reserva cancelada: ID={id_reserva}")
        return r

    def completar_reserva(self, id_reserva):
        r = self.buscar_por_id(id_reserva)
        if not r:
            self.__log.error(f"Completar fallido: Reserva ID={id_reserva} no existe")
            raise ReservaNoEncontradaError(id_reserva)
        r.completar()
        self.__log.info(f"Reserva completada: ID={id_reserva}")
        return r

    def total(self): return len(self.__bd)
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — ServicioAdicionalDAO
# ──────────────────────────────────────────────────────────────────────────────
class ServicioAdicionalDAO:
    PREFIJO = "S"
    def __init__(self, reserva_dao):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()
        self.__reserva_dao = reserva_dao

    def insertar(self, servicio):
        if not self.__reserva_dao.buscar_por_id(servicio.id_reserva):
            self.__log.error(f"Servicio fallido: Reserva ID={servicio.id_reserva} no existe")
            raise ReservaNoEncontradaError(servicio.id_reserva)
        servicio.id_servicio_adicional = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(servicio)
        self.__log.info(
            f"Servicio adicional agregado: {servicio.nombre_servicio_adicional} "
            f"(ID={servicio.id_servicio_adicional}) para Reserva={servicio.id_reserva}")
        return servicio

    def buscar_por_id(self, id_servicio):
        for s in self.__bd:
            if s.id_servicio_adicional == id_servicio: return s
        return None

    def obtener_por_reserva(self, id_reserva):
        return [s for s in self.__bd if s.id_reserva == id_reserva]

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda s: s.nombre_servicio_adicional)

    def calcularTotal(self, id_reserva):
        servicios = self.obtener_por_reserva(id_reserva)
        return sum(s.precio for s in servicios)

    def eliminar(self, id_servicio):
        s = self.buscar_por_id(id_servicio)
        if not s:
            self.__log.error(f"Eliminar fallido: Servicio ID={id_servicio} no existe")
            raise ServicioAdicionalNoEncontradoError(id_servicio)
        self.__bd.remove(s)
        self.__log.info(f"Servicio adicional eliminado: {s.nombre_servicio_adicional} (ID={id_servicio})")
        return True

    def total(self): return len(self.__bd)
    
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
    

# ──────────────────────────────────────────────────────────────────────────────
# CAPA DE VISTA — Funciones del menú
# Cada llamada a pedir_dato() ahora recibe un OBJETO validador ya creado
# ──────────────────────────────────────────────────────────────────────────────
def mostrar_menu(cfg):
    print(f"\n{'=' * 50}")
    print(f"  {cfg.nombre} v{cfg.version}")
    print(f"  {cfg.empresa}")
    print(f"{'=' * 50}")
    print("  1. Registrar cliente")
    print("  2. Agregar tematica")
    print("  3. Crear reserva")
    print("  4. Agregar servicio adicional")
    print("  5. Registrar pago (genera cuotas automáticamente)")
    print("  6. Marcar cuota como pagada")
    print("  7. Listar clientes")
    print("  8. Listar tematicas")
    print("  9. Listar reservas")
    print("  10. Listar servicios de una reserva")
    print("  11. Listar pagos de una reserva")
    print("  12. Listar cuotas de un pago")
    print("  13. Ver reservas de un cliente")
    print("  14. Confirmar reserva")
    print("  15. Cancelar reserva")
    print("  16. Completar reserva")
    print("  17. Ver historial de logs")
    print("  0. Salir")
    print(f"{'=' * 50}")

def registrar_cliente(cdao):
    print("\n--- REGISTRAR CLIENTE ---")
    nombre    = pedir_dato("  Nombre    : ", ValidadorNombre("nombre"))
    apellido  = pedir_dato("  Apellido  : ", ValidadorNombre("apellido"))
    dni       = pedir_dato("  DNI (8 dígitos)      : ", ValidadorDNI())
    telefono  = pedir_dato("  Telefono (9 dígitos) : ", ValidadorTelefono())
    correo    = pedir_dato("  Correo    : ", ValidadorCorreo())
    try:
        c = cdao.registrar(Cliente(nombre, apellido, dni, telefono, correo))
        print(f"  OK Cliente registrado con ID={c.id_cliente}")
    except (DatoInvalidoError, CorreoDuplicadoError) as ex:
        print(f"  ERROR: {ex}")

def agregar_tematica(tdao):
    print("\n--- AGREGAR TEMATICA ---")
    descripcion = pedir_dato("  Descripcion : ", ValidadorDireccion("descripcion"))
    precio      = pedir_dato("  Precio base : ", ValidadorPrecio("precio_base"))
    t = tdao.insertar(Tematica(descripcion, precio))
    print(f"  OK Tematica agregada con ID={t.id_tematica}")

def crear_reserva(rdao):
    print("\n--- CREAR RESERVA ---")
    id_cliente   = pedir_dato("  ID Cliente (ej. C001) : ", ValidadorCodigo("C", "id_cliente"))
    id_tematica  = pedir_dato("  ID Tematica (ej. T001): ", ValidadorCodigo("T", "id_tematica"))
    fecha_evento = pedir_dato("  Fecha evento (YYYY-MM-DD): ", ValidadorFecha("fecha_evento"))
    hora_inicio  = pedir_dato("  Hora inicio (HH:MM) : ", ValidadorHora("hora_inicio"))
    hora_fin     = pedir_dato("  Hora fin    (HH:MM) : ", ValidadorHora("hora_fin"))
    direccion    = pedir_dato("  Direccion del evento: ", ValidadorDireccion("direccion"))

    edad = pedir_dato("  Edad cumpleañero (Enter si no aplica): ",ValidadorEnteroPositivo("edad_cumpleanero"),
                    opcional=True, valor_si_vacio=None)
    observ = input("  Observaciones (Enter para omitir)   : ").strip() or None
    try:
        r = rdao.crear(Reserva(fecha_evento, hora_inicio, hora_fin, direccion,
                                edad, observ, id_cliente, id_tematica))
        print(f"  OK Reserva creada con ID={r.id_reserva}")
    except (ClienteNoEncontradoError, TematicaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def agregar_servicio(sdao):
    print("\n--- AGREGAR SERVICIO ADICIONAL ---")
    id_reserva  = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    nombre      = pedir_dato("  Nombre del servicio  : ", ValidadorTextoGeneral("nombre_servicio_adicional"))
    descripcion = pedir_dato("  Descripcion          : ", ValidadorTextoGeneral("descripcion"))
    precio      = pedir_dato("  Precio               : ", ValidadorPrecio("precio"))
    try:
        s = sdao.insertar(ServicioAdicional(nombre, descripcion, precio, id_reserva))
        print(f"  OK Servicio agregado con ID={s.id_servicio_adicional}")
    except ReservaNoEncontradaError as ex:
        print(f"  ERROR: {ex}")

def registrar_pago(pdao, contexto):
    tdao, rdao, sdao, cuota_dao = contexto
    print("\n--- REGISTRAR PAGO ---")
    id_reserva = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))

    reserva = rdao.buscar_por_id(id_reserva)
    if not reserva:
        print(f"  ERROR: {ReservaNoEncontradaError(id_reserva)}")
        return

    tematica = tdao.buscar_por_id(reserva.id_tematica)
    monto_sugerido = (tematica.precio_base if tematica else 0) + sdao.calcularTotal(id_reserva)
    print(f"  (Monto sugerido según tematica + servicios: S/.{monto_sugerido:.2f})")

    monto        = pedir_dato("  Monto total   : ", ValidadorPrecio("monto_total"))
    metodo       = pedir_dato("  Metodo de pago (YAPE/PLIN/TRANSFERENCIA/EFECTIVO/TARJETA): ", ValidadorMetodoPago())
    total_cuotas = pedir_dato("  Numero de cuotas: ", ValidadorEnteroPositivo("total_cuotas"))

    try:
        p = pdao.registrar(Pago(monto, metodo, total_cuotas, id_reserva))
        print(f"  OK Pago registrado con ID={p.id_pago} (estado inicial: {p.estado_pago})")
        cuotas = cuota_dao.generarCuotas(p)
        print(f"  OK Se generaron {len(cuotas)} cuota(s):")
        for c in cuotas:
            print(f"    {c}")
    except ReservaNoEncontradaError as ex:
        print(f"  ERROR: {ex}")

def marcar_cuota_pagada(cuota_dao):
    print("\n--- MARCAR CUOTA COMO PAGADA ---")
    id_cuota = pedir_dato("  ID Cuota (ej. Q001): ", ValidadorCodigo("Q", "id_cuota"))
    try:
        c = cuota_dao.marcar_pagada(id_cuota)
        print(f"  OK Cuota marcada como pagada: {c}")
    except CuotaNoEncontradaError as ex:
        print(f"  ERROR: {ex}")

def listar_clientes(cdao):
    print("\n--- CLIENTES ---")
    clientes = cdao.obtener_todos()
    if clientes:
        for c in clientes: print(f"  {c}")
    else:
        print("  (No hay clientes registrados)")

def listar_tematicas(tdao):
    print("\n--- TEMATICAS ---")
    tematicas = tdao.obtener_todos()
    if tematicas:
        for t in tematicas: print(f"  {t}")
    else:
        print("  (No hay tematicas registradas)")

def listar_reservas(rdao):
    print("\n--- RESERVAS ---")
    reservas = rdao.obtener_todos()
    if reservas:
        for r in reservas: print(f"  {r}")
    else:
        print("  (No hay reservas registradas)")

def listar_servicios_reserva(sdao):
    print("\n--- SERVICIOS DE UNA RESERVA ---")
    id_reserva = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    servicios = sdao.obtener_por_reserva(id_reserva)
    if servicios:
        for s in servicios: print(f"  {s}")
        print(f"  TOTAL servicios: S/.{sdao.calcularTotal(id_reserva):.2f}")
    else:
        print("  (Esta reserva no tiene servicios adicionales)")

def listar_pagos_reserva(pdao):
    print("\n--- PAGOS DE UNA RESERVA ---")
    id_reserva = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    pagos = pdao.obtener_por_reserva(id_reserva)
    if pagos:
        for p in pagos: print(f"  {p}")
    else:
        print("  (Esta reserva no tiene pagos registrados)")

def listar_cuotas_pago(cuota_dao):
    print("\n--- CUOTAS DE UN PAGO ---")
    id_pago = pedir_dato("  ID Pago (ej. P001): ", ValidadorCodigo("P", "id_pago"))
    cuotas = cuota_dao.obtener_por_pago(id_pago)
    if cuotas:
        for c in cuotas: print(f"  {c}")
    else:
        print("  (Este pago no tiene cuotas registradas)")

def ver_reservas_cliente(cdao, rdao):
    print("\n--- RESERVAS DE UN CLIENTE ---")
    id_cliente = pedir_dato("  ID del cliente (ej. C001): ", ValidadorCodigo("C", "id_cliente"))
    try:
        reservas = cdao.obtenerReservas(id_cliente, rdao)
        if reservas:
            for r in reservas: print(f"  {r}")
        else:
            print("  (Este cliente no tiene reservas)")
    except (ClienteNoEncontradoError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def confirmar_reserva(rdao):
    print("\n--- CONFIRMAR RESERVA ---")
    id_reserva = pedir_dato("  ID de la reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    try:
        rdao.confirmar_reserva(id_reserva)
        print(f"  OK Reserva ID={id_reserva} confirmada")
    except (ReservaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def cancelar_reserva(rdao):
    print("\n--- CANCELAR RESERVA ---")
    id_reserva = pedir_dato("  ID de la reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    try:
        rdao.cancelar_reserva(id_reserva)
        print(f"  OK Reserva ID={id_reserva} cancelada")
    except (ReservaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def completar_reserva(rdao):
    print("\n--- COMPLETAR RESERVA ---")
    id_reserva = pedir_dato("  ID de la reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    try:
        rdao.completar_reserva(id_reserva)
        print(f"  OK Reserva ID={id_reserva} completada")
    except (ReservaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")
# ──────────────────────────────────────────────────────────────────────────────
# ORQUESTADOR — main()
# ──────────────────────────────────────────────────────────────────────────────
def main():
    cfg   = SistemaConfig()
    cdao  = ClienteDAO()
    tdao  = TematicaDAO()
    rdao  = ReservaDAO(cdao, tdao)
    sdao  = ServicioAdicionalDAO(rdao)
    pdao  = PagoDAO(rdao)
    qdao  = CuotaDAO(pdao)

    while True:
        mostrar_menu(cfg)
        opcion = input("  Elige una opción: ").strip()

        try:
            match opcion:
                case "1":  registrar_cliente(cdao)
                case "2":  agregar_tematica(tdao)
                case "3":  crear_reserva(rdao)
                case "4":  agregar_servicio(sdao)
                case "5":  registrar_pago(pdao, (tdao, rdao, sdao, qdao))
                case "6":  marcar_cuota_pagada(qdao)
                case "7":  listar_clientes(cdao)
                case "8":  listar_tematicas(tdao)
                case "9":  listar_reservas(rdao)
                case "10": listar_servicios_reserva(sdao)
                case "11": listar_pagos_reserva(pdao)
                case "12": listar_cuotas_pago(qdao)
                case "13": ver_reservas_cliente(cdao, rdao)
                case "14": confirmar_reserva(rdao)
                case "15": cancelar_reserva(rdao)
                case "16": completar_reserva(rdao)
                case "17": Logger().mostrar_logs()
                case "0":
                    Logger().info("Sistema cerrado por el usuario")
                    print("\n  Hasta luego.")
                    break
                case _:
                    print("  Opción no válida, elige entre 0 y 17")
        except Exception as ex:
            Logger().error(f"Error inesperado: {ex}")
            print(f"  ERROR INESPERADO: {ex}")

if __name__ == "__main__":
    main()