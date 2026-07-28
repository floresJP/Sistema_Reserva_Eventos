# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Tematica
# ──────────────────────────────────────────────────────────────────────────────

class Tematica:
    def __init__(self, descripcion, precio_base):
        self.id_tematica = None
        self.descripcion = descripcion
        self.precio_base = precio_base
        self.estado      = "Disponible"

    def activar(self):
        self.estado = "Disponible"

    def desactivar(self):
        self.estado = "No Disponible"

    def estado_disponible(self):
        return self.estado == "Disponible"

    def __str__(self):
        return f"[{self.id_tematica}] {self.descripcion} | S/.{self.precio_base:.2f} | {self.estado}"
    
    
    # Convierte el objeto en un diccionario para guardarlo en JSON
    def to_dict(self):
        return {
            "id_tematica": self.id_tematica,
            "descripcion": self.descripcion,
            "precio_base": self.precio_base,
            "estado": self.estado
        }

    # Crea un objeto Tematica a partir de un diccionario
    @classmethod
    def from_dict(cls, datos):
        tematica = cls(
            datos["descripcion"],
            datos["precio_base"]
        )
        tematica.id_tematica = datos["id_tematica"]
        tematica.estado = datos["estado"]
        return tematica