#────────────────────────────────────────────────────────────
# MODELO — Reserva
# ──────────────────────────────────────────────────────────────────────────────

import datetime

class Reserva:
    def __init__(self, fecha_evento, hora_inicio, hora_fin, direccion,edad_cumpleanero, observaciones, id_cliente, id_tematica):
        self.id_reserva       = None
        self.fecha_reserva    = datetime.date.today()
        self.fecha_evento     = fecha_evento
        self.hora_inicio      = hora_inicio
        self.hora_fin         = hora_fin
        self.direccion        = direccion
        self.edad_cumpleanero = edad_cumpleanero
        self.observaciones    = observaciones
        self.estado           = "Pendiente"
        self.id_cliente       = id_cliente
        self.id_tematica      = id_tematica

    def confirmar(self):
        self.estado = "Confirmada"

    def cancelar(self):
        self.estado = "Cancelada"

    def completar(self):
        self.estado = "Completada"

    def __str__(self):
        return (f"[{self.id_reserva}] Evento:{self.fecha_evento} "
                f"{self.hora_inicio}-{self.hora_fin} | {self.direccion} | "
                f"Estado:{self.estado} | Cliente:{self.id_cliente} | Tematica:{self.id_tematica}")
        
    # Convierte el objeto en un diccionario para guardarlo en JSON
    def to_dict(self):
        return {
            "id_reserva": self.id_reserva,
            "fecha_reserva": str(self.fecha_reserva),
            "fecha_evento": str(self.fecha_evento),
            "hora_inicio": str(self.hora_inicio),
            "hora_fin": str(self.hora_fin),
            "direccion": self.direccion,
            "edad_cumpleanero": self.edad_cumpleanero,
            "observaciones": self.observaciones,
            "estado": self.estado,
            "id_cliente": self.id_cliente,
            "id_tematica": self.id_tematica
        }

    # Crea un objeto Reserva a partir de un diccionario
    @classmethod
    def from_dict(cls, datos):
        reserva = cls(
            datetime.date.fromisoformat(datos["fecha_evento"]),
            datetime.time.fromisoformat(datos["hora_inicio"]),
            datetime.time.fromisoformat(datos["hora_fin"]),
            datos["direccion"],
            datos["edad_cumpleanero"],
            datos["observaciones"],
            datos["id_cliente"],
            datos["id_tematica"]
        )
        reserva.id_reserva = datos["id_reserva"]
        reserva.fecha_reserva = datetime.date.fromisoformat(datos["fecha_reserva"])
        reserva.estado = datos["estado"]
        return reserva