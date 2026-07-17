#────────────────────────────────────────────────────────────
# MODELO — Reserva
# ──────────────────────────────────────────────────────────────────────────────

import datetime

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
# 