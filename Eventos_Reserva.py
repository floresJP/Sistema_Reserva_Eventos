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
