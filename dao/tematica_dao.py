# dao/tematica_dao.py
from config.logger import Logger
from validaciones.validadores import GeneradorID
# ──────────────────────────────────────────────────────────────────────────────
# PATRÓN DAO — TematicaDAO
# ──────────────────────────────────────────────────────────────────────────────
class TematicaDAO:
    PREFIJO = "T"

    def __init__(self):
        self.__bd  = []
        self.__cid = 1
        self.__log = Logger()
        self.__gen = GeneradorID()

    def insertar(self, tematica):
        tematica.id_tematica = self.__gen.generar(self.PREFIJO, self.__cid)
        self.__cid += 1
        self.__bd.append(tematica)
        self.__log.info(f"Tematica agregada: {tematica.descripcion} (ID={tematica.id_tematica})")
        return tematica

    def buscar_por_id(self, id_tematica):
        for t in self.__bd:
            if t.id_tematica == id_tematica: return t
        return None

    def obtener_todos(self):
        return sorted(self.__bd, key=lambda t: t.descripcion)

    def obtener_disponibles(self):
        return [t for t in self.__bd if t.estado_disponible()]

    def total(self): return len(self.__bd)