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
        
# Cambia el estado a Pago parcial
    def marcar_pago_parcial(self):
        self.estado_pago = "Pago parcial"
# Cambia el estado a Pagado
    def marcar_pagado(self):
        self.estado_pago = "Pagado"

# Devuelve una representación en texto del pago
    def __str__(self):
        return (f"[{self.id_pago}] {self.fecha_pago} | S/.{self.monto_total:.2f} | "
                f"{self.metodo_pago} | {self.estado_pago} | Cuotas:{self.total_cuotas} | "
                f"Reserva:{self.id_reserva}")
        
        # Convierte el objeto en un diccionario para guardarlo en JSON
    def to_dict(self):
        return {
            "id_pago": self.id_pago,
            "fecha_pago": str(self.fecha_pago),
            "monto_total": self.monto_total,
            "metodo_pago": self.metodo_pago,
            "estado_pago": self.estado_pago,
            "total_cuotas": self.total_cuotas,
            "id_reserva": self.id_reserva
        }

    # Crea un objeto Pago a partir de un diccionario
    @classmethod
    def from_dict(cls, datos):

        # Crea el objeto con los datos principales
        pago = cls(
            datos["monto_total"],
            datos["metodo_pago"],
            datos["total_cuotas"],
            datos["id_reserva"]
        )

        # Recupera los datos almacenados
        pago.id_pago = datos["id_pago"]
        pago.estado_pago = datos["estado_pago"]
        pago.fecha_pago = datetime.date.fromisoformat(datos["fecha_pago"])

        return pago