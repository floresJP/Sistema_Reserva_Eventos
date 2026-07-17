# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Cuota
# ──────────────────────────────────────────────────────────────────────────────
import datetime
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
