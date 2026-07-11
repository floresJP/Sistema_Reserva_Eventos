# DAOSingleton_reservas.py
# Sistema de Gestión de Reservas — Singleton + DAO + Validaciones (4 pilares de POO)
# 6 tablas del esquema: BD_SISTEMA_RESERVA (SQL Server)
#   cliente, tematica, reserva, servicio_adicional, pago, cuota

# 4 PILARES DE POO aplicados en el módulo de Validaciones:
#   ABSTRACCION     -> ValidadorBase(ABC) con @abstractmethod validar()
#   ENCAPSULAMIENTO -> self._campo, self._prefijo guardados dentro de cada objeto
#   HERENCIA        -> cada Validador___ hereda de ValidadorBase
#   POLIMORFISMO    -> todos se llaman igual (objeto.validar(texto)) pero
#                      cada uno hace algo distinto por dentro
import datetime
import re
from abc import ABC, abstractmethod