# ──────────────────────────────────────────────────────────────────────────────
# MODELO — Cliente
#────────────────────────────────────────────────────────────────────────
import datetime

class Cliente:
    def __init__(self, nombre, apellido, dni, telefono, correo):
        self.id_cliente     = None
        self.nombre         = nombre
        self.apellido       = apellido
        self.dni            = dni
        self.telefono       = telefono
        self.correo         = correo
        self.fecha_registro = datetime.date.today()

    def __str__(self):
        return (f"[{self.id_cliente}] {self.nombre} {self.apellido} | "
                f"DNI:{self.dni} | {self.correo} | {self.telefono}")