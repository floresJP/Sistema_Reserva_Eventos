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
        
        # Marca la cuota como pagada
    def marcarPagada(self, fecha_pago=None):
        self.fecha_pago = fecha_pago if fecha_pago else datetime.date.today()
        self.estado = "Pagada"
        # Verifica si la cuota ya venció
    def verificarVencimiento(self):
        if self.estado == "Pagada":
            return False
        # Si la fecha actual supera la fecha de vencimiento
        if datetime.date.today() > self.fecha_vencimiento:
            self.estado = "Vencida"
            return True
        return False
    # Devuelve una representación en texto de la cuota
    def __str__(self):
        pago_str = self.fecha_pago if self.fecha_pago else "—"
        return (f"[{self.id_cuota}] Cuota #{self.numero_cuota} | S/.{self.monto:.2f} | "
                f"Vence:{self.fecha_vencimiento} | Pagada:{pago_str} | "
                f"{self.estado} | Pago:{self.id_pago}")
        # Convierte el objeto en un diccionario para guardarlo en JSON
    def to_dict(self):
        return {
            "id_cuota": self.id_cuota,
            "numero_cuota": self.numero_cuota,
            "monto": self.monto,
            "fecha_vencimiento": str(self.fecha_vencimiento),
            "fecha_pago": str(self.fecha_pago) if self.fecha_pago else None,
            "estado": self.estado,
            "id_pago": self.id_pago
        }

    # Crea un objeto Cuota a partir de un diccionario
    @classmethod
    def from_dict(cls, datos):
        cuota = cls(
            datos["numero_cuota"],
            datos["monto"],
            datetime.date.fromisoformat(datos["fecha_vencimiento"]),
            datos["id_pago"]
        )

        # Recupera los datos almacenados
        cuota.id_cuota = datos["id_cuota"]
        cuota.estado = datos["estado"]

        # Si la cuota ya fue pagada, recupera la fecha de pago
        if datos["fecha_pago"]:
            cuota.fecha_pago = datetime.date.fromisoformat(datos["fecha_pago"])

        return cuota
    
