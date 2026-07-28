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
        
        # Convierte el objeto en un diccionario para guardarlo en JSON
    def to_dict(self):
        return {
            "id_servicio_adicional": self.id_servicio_adicional,
            "nombre_servicio_adicional": self.nombre_servicio_adicional,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "estado": self.estado,
            "id_reserva": self.id_reserva
        }

    # Crea un objeto ServicioAdicional a partir de un diccionario
    @classmethod
    def from_dict(cls, datos):
        servicio = cls(
            datos["nombre_servicio_adicional"],
            datos["descripcion"],
            datos["precio"],
            datos["id_reserva"]
        )
        servicio.id_servicio_adicional = datos["id_servicio_adicional"]
        servicio.estado = datos["estado"]
        return servicio