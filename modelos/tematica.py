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