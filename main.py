# main.py importaciones para corra correctamente 
from config.base_datos import inicializar
from config.sistema_config import SistemaConfig
from config.logger import Logger
from dao.cliente_dao import ClienteDAO
from dao.tematica_dao import TematicaDAO
from dao.reserva_dao import ReservaDAO
from dao.servicio_adicional_dao import ServicioAdicionalDAO
from dao.pago_dao import PagoDAO
from dao.cuota_dao import CuotaDAO
from vistas.menu import (
    mostrar_menu, registrar_cliente, agregar_tematica, crear_reserva,
    agregar_servicio, registrar_pago, marcar_cuota_pagada,
    listar_clientes, listar_tematicas, listar_reservas,
    listar_servicios_reserva, listar_pagos_reserva, listar_cuotas_pago,
    ver_reservas_cliente, confirmar_reserva, cancelar_reserva, completar_reserva,)
# ─────────────────────────────────────────────────
# ORQUESTADOR — main()
# ─────────────────────────────────────────────────
def main():
    inicializar() 
    cfg   = SistemaConfig()
    cdao  = ClienteDAO()
    tdao  = TematicaDAO()
    rdao  = ReservaDAO(cdao, tdao)
    sdao  = ServicioAdicionalDAO(rdao)
    pdao  = PagoDAO(rdao)
    qdao  = CuotaDAO(pdao)

    while True:
        mostrar_menu(cfg)
        opcion = input("  Elige una opción: ").strip()

        try:
            match opcion:
                case "1":  registrar_cliente(cdao)
                case "2":  agregar_tematica(tdao)
                case "3":  crear_reserva(rdao)
                case "4":  agregar_servicio(sdao)
                case "5":  registrar_pago(pdao, (tdao, rdao, sdao, qdao))
                case "6":  marcar_cuota_pagada(qdao)
                case "7":  listar_clientes(cdao)
                case "8":  listar_tematicas(tdao)
                case "9":  listar_reservas(rdao)
                case "10": listar_servicios_reserva(sdao)
                case "11": listar_pagos_reserva(pdao)
                case "12": listar_cuotas_pago(qdao)
                case "13": ver_reservas_cliente(cdao, rdao)
                case "14": confirmar_reserva(rdao)
                case "15": cancelar_reserva(rdao)
                case "16": completar_reserva(rdao)
                case "17": Logger().mostrar_logs()
                case "0":
                    Logger().info("Sistema cerrado por el usuario")
                    print("\n  Hasta luego.")
                    break
                case _:
                    print("  Opción no válida, elige entre 0 y 17")
        except Exception as ex:
            Logger().error(f"Error inesperado: {ex}")
            print(f"  ERROR INESPERADO: {ex}")

if __name__ == "__main__":
    main()