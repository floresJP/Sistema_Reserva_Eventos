# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Pago
# ──────────────────────────────────────────────────────────────────────────────
import datetime

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