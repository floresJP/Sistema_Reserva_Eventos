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
        
    