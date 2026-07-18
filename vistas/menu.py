from config.logger import Logger
from validaciones.validadores import (
    pedir_dato, ValidadorNombre, ValidadorDNI, ValidadorTelefono, ValidadorCorreo,
    ValidadorDireccion, ValidadorPrecio, ValidadorCodigo, ValidadorFecha, ValidadorHora,
    ValidadorEnteroPositivo, ValidadorTextoGeneral, ValidadorMetodoPago,
    DatoInvalidoError, CorreoDuplicadoError, ClienteNoEncontradoError,
    TematicaNoEncontradaError, ReservaNoEncontradaError,
    ServicioAdicionalNoEncontradoError, CuotaNoEncontradaError,
)
from modelos.cliente import Cliente
from modelos.tematica import Tematica
from modelos.reserva import Reserva
from modelos.servicio_adicional import ServicioAdicional
from modelos.pago import Pago
# ──────────────────────────────────────────────────────────────────────────────
# CAPA DE VISTA — Funciones del menú
# Cada llamada a pedir_dato() ahora recibe un OBJETO validador ya creado
# ──────────────────────────────────────────────────────────────────────────────
def mostrar_menu(cfg):
    print(f"\n{'=' * 50}")
    print(f"  {cfg.nombre} v{cfg.version}")
    print(f"  {cfg.empresa}")
    print(f"{'=' * 50}")
    print("  1. Registrar cliente")
    print("  2. Agregar tematica")
    print("  3. Crear reserva")
    print("  4. Agregar servicio adicional")
    print("  5. Registrar pago (genera cuotas automáticamente)")
    print("  6. Marcar cuota como pagada")
    print("  7. Listar clientes")
    print("  8. Listar tematicas")
    print("  9. Listar reservas")
    print("  10. Listar servicios de una reserva")
    print("  11. Listar pagos de una reserva")
    print("  12. Listar cuotas de un pago")
    print("  13. Ver reservas de un cliente")
    print("  14. Confirmar reserva")
    print("  15. Cancelar reserva")
    print("  16. Completar reserva")
    print("  17. Ver historial de logs")
    print("  0. Salir")
    print(f"{'=' * 50}")

def registrar_cliente(cdao):
    print("\n--- REGISTRAR CLIENTE ---")
    nombre    = pedir_dato("  Nombre    : ", ValidadorNombre("nombre"))
    apellido  = pedir_dato("  Apellido  : ", ValidadorNombre("apellido"))
    dni       = pedir_dato("  DNI (8 dígitos)      : ", ValidadorDNI())
    telefono  = pedir_dato("  Telefono (9 dígitos) : ", ValidadorTelefono())
    correo    = pedir_dato("  Correo    : ", ValidadorCorreo())
    try:
        c = cdao.registrar(Cliente(nombre, apellido, dni, telefono, correo))
        print(f"  OK Cliente registrado con ID={c.id_cliente}")
    except (DatoInvalidoError, CorreoDuplicadoError) as ex:
        print(f"  ERROR: {ex}")

def agregar_tematica(tdao):
    print("\n--- AGREGAR TEMATICA ---")
    descripcion = pedir_dato("  Descripcion : ", ValidadorDireccion("descripcion"))
    precio      = pedir_dato("  Precio base : ", ValidadorPrecio("precio_base"))
    t = tdao.insertar(Tematica(descripcion, precio))
    print(f"  OK Tematica agregada con ID={t.id_tematica}")

def crear_reserva(rdao):
    print("\n--- CREAR RESERVA ---")
    id_cliente   = pedir_dato("  ID Cliente (ej. C001) : ", ValidadorCodigo("C", "id_cliente"))
    id_tematica  = pedir_dato("  ID Tematica (ej. T001): ", ValidadorCodigo("T", "id_tematica"))
    fecha_evento = pedir_dato("  Fecha evento (YYYY-MM-DD): ", ValidadorFecha("fecha_evento"))
    hora_inicio  = pedir_dato("  Hora inicio (HH:MM) : ", ValidadorHora("hora_inicio"))
    hora_fin     = pedir_dato("  Hora fin    (HH:MM) : ", ValidadorHora("hora_fin"))
    direccion    = pedir_dato("  Direccion del evento: ", ValidadorDireccion("direccion"))

    edad = pedir_dato("  Edad cumpleañero (Enter si no aplica): ",ValidadorEnteroPositivo("edad_cumpleanero"),
                    opcional=True, valor_si_vacio=None)
    observ = input("  Observaciones (Enter para omitir)   : ").strip() or None
    try:
        r = rdao.crear(Reserva(fecha_evento, hora_inicio, hora_fin, direccion,
                                edad, observ, id_cliente, id_tematica))
        print(f"  OK Reserva creada con ID={r.id_reserva}")
    except (ClienteNoEncontradoError, TematicaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def agregar_servicio(sdao):
    print("\n--- AGREGAR SERVICIO ADICIONAL ---")
    id_reserva  = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    nombre      = pedir_dato("  Nombre del servicio  : ", ValidadorTextoGeneral("nombre_servicio_adicional"))
    descripcion = pedir_dato("  Descripcion          : ", ValidadorTextoGeneral("descripcion"))
    precio      = pedir_dato("  Precio               : ", ValidadorPrecio("precio"))
    try:
        s = sdao.insertar(ServicioAdicional(nombre, descripcion, precio, id_reserva))
        print(f"  OK Servicio agregado con ID={s.id_servicio_adicional}")
    except ReservaNoEncontradaError as ex:
        print(f"  ERROR: {ex}")

def registrar_pago(pdao, contexto):
    tdao, rdao, sdao, cuota_dao = contexto
    print("\n--- REGISTRAR PAGO ---")
    id_reserva = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))

    reserva = rdao.buscar_por_id(id_reserva)
    if not reserva:
        print(f"  ERROR: {ReservaNoEncontradaError(id_reserva)}")
        return

    tematica = tdao.buscar_por_id(reserva.id_tematica)
    monto_sugerido = (tematica.precio_base if tematica else 0) + sdao.calcularTotal(id_reserva)
    print(f"  (Monto sugerido según tematica + servicios: S/.{monto_sugerido:.2f})")

    monto        = pedir_dato("  Monto total   : ", ValidadorPrecio("monto_total"))
    metodo       = pedir_dato("  Metodo de pago (YAPE/PLIN/TRANSFERENCIA/EFECTIVO/TARJETA): ", ValidadorMetodoPago())
    total_cuotas = pedir_dato("  Numero de cuotas: ", ValidadorEnteroPositivo("total_cuotas"))

    try:
        p = pdao.registrar(Pago(monto, metodo, total_cuotas, id_reserva))
        print(f"  OK Pago registrado con ID={p.id_pago} (estado inicial: {p.estado_pago})")
        cuotas = cuota_dao.generarCuotas(p)
        print(f"  OK Se generaron {len(cuotas)} cuota(s):")
        for c in cuotas:
            print(f"    {c}")
    except ReservaNoEncontradaError as ex:
        print(f"  ERROR: {ex}")

def marcar_cuota_pagada(cuota_dao):
    print("\n--- MARCAR CUOTA COMO PAGADA ---")
    id_cuota = pedir_dato("  ID Cuota (ej. Q001): ", ValidadorCodigo("Q", "id_cuota"))
    try:
        c = cuota_dao.marcar_pagada(id_cuota)
        print(f"  OK Cuota marcada como pagada: {c}")
    except CuotaNoEncontradaError as ex:
        print(f"  ERROR: {ex}")

def listar_clientes(cdao):
    print("\n--- CLIENTES ---")
    clientes = cdao.obtener_todos()
    if clientes:
        for c in clientes: print(f"  {c}")
    else:
        print("  (No hay clientes registrados)")

def listar_tematicas(tdao):
    print("\n--- TEMATICAS ---")
    tematicas = tdao.obtener_todos()
    if tematicas:
        for t in tematicas: print(f"  {t}")
    else:
        print("  (No hay tematicas registradas)")

def listar_reservas(rdao):
    print("\n--- RESERVAS ---")
    reservas = rdao.obtener_todos()
    if reservas:
        for r in reservas: print(f"  {r}")
    else:
        print("  (No hay reservas registradas)")

def listar_servicios_reserva(sdao):
    print("\n--- SERVICIOS DE UNA RESERVA ---")
    id_reserva = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    servicios = sdao.obtener_por_reserva(id_reserva)
    if servicios:
        for s in servicios: print(f"  {s}")
        print(f"  TOTAL servicios: S/.{sdao.calcularTotal(id_reserva):.2f}")
    else:
        print("  (Esta reserva no tiene servicios adicionales)")

def listar_pagos_reserva(pdao):
    print("\n--- PAGOS DE UNA RESERVA ---")
    id_reserva = pedir_dato("  ID Reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    pagos = pdao.obtener_por_reserva(id_reserva)
    if pagos:
        for p in pagos: print(f"  {p}")
    else:
        print("  (Esta reserva no tiene pagos registrados)")

def listar_cuotas_pago(cuota_dao):
    print("\n--- CUOTAS DE UN PAGO ---")
    id_pago = pedir_dato("  ID Pago (ej. P001): ", ValidadorCodigo("P", "id_pago"))
    cuotas = cuota_dao.obtener_por_pago(id_pago)
    if cuotas:
        for c in cuotas: print(f"  {c}")
    else:
        print("  (Este pago no tiene cuotas registradas)")

def ver_reservas_cliente(cdao, rdao):
    print("\n--- RESERVAS DE UN CLIENTE ---")
    id_cliente = pedir_dato("  ID del cliente (ej. C001): ", ValidadorCodigo("C", "id_cliente"))
    try:
        reservas = cdao.obtenerReservas(id_cliente, rdao)
        if reservas:
            for r in reservas: print(f"  {r}")
        else:
            print("  (Este cliente no tiene reservas)")
    except (ClienteNoEncontradoError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def confirmar_reserva(rdao):
    print("\n--- CONFIRMAR RESERVA ---")
    id_reserva = pedir_dato("  ID de la reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    try:
        rdao.confirmar_reserva(id_reserva)
        print(f"  OK Reserva ID={id_reserva} confirmada")
    except (ReservaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def cancelar_reserva(rdao):
    print("\n--- CANCELAR RESERVA ---")
    id_reserva = pedir_dato("  ID de la reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    try:
        rdao.cancelar_reserva(id_reserva)
        print(f"  OK Reserva ID={id_reserva} cancelada")
    except (ReservaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")

def completar_reserva(rdao):
    print("\n--- COMPLETAR RESERVA ---")
    id_reserva = pedir_dato("  ID de la reserva (ej. R001): ", ValidadorCodigo("R", "id_reserva"))
    try:
        rdao.completar_reserva(id_reserva)
        print(f"  OK Reserva ID={id_reserva} completada")
    except (ReservaNoEncontradaError, DatoInvalidoError) as ex:
        print(f"  ERROR: {ex}")