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
        
    # Convierte el objeto Cliente en un diccionario
    # para poder guardarlo en un archivo JSON
    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "dni": self.dni,
            "telefono": self.telefono,
            "correo": self.correo,
            "fecha_registro": str(self.fecha_registro)
        }

    # Crea un objeto Cliente a partir de un diccionario
    @classmethod
    def from_dict(cls, datos):

        # Crea un nuevo objeto con los datos del diccionario
        cliente = cls(
            datos["nombre"],
            datos["apellido"],
            datos["dni"],
            datos["telefono"],
            datos["correo"]
        )
        # Recupera el ID que tenía el cliente al guardarse
        cliente.id_cliente = datos["id_cliente"]

        # Devuelve el objeto Cliente ya reconstruido
        return cliente