# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN SINGLETON #2 — SistemaConfig
# Centraliza la configuración del sistema. Todos los módulos leen los
# mismos datos (nombre, versión, empresa) sin pasarlos como parámetros.
# ────────────────────────────────────────────────────
from config.logger import Logger


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
