# config/logger.py
# PATRÓN SINGLETON #1 — Logger 
# Todos los módulos comparten la misma instancia y la misma lista de logs

import datetime
#____________________________________________________
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