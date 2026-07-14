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