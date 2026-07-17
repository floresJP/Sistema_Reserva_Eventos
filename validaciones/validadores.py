# ──────────────────────────────────────────────────────────────────────────────
# EXCEPCIONES PERSONALIZADAS
# ──────────────────────────────────────────────────────────────────────────────
import datetime
import re
from abc import ABC, abstractmethod


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
        