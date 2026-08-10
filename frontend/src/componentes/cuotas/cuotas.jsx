// componentes/cuotas/cuotas.jsx
//
// Vista ADMINISTRATIVA de Cuotas -- lista TODAS las cuotas del sistema
// (a diferencia de CuotasReserva.jsx, que es solo de UNA reserva y es
// de solo lectura). Esta si tiene Editar y Eliminar.
// Filtro por reserva: el ID de Reserva en cada
// fila de la tabla es clickeable -- al presionarlo, se activa el
// filtro y aparece la tarjeta resumen (mismo estilo que
// CuotasReserva.jsx) arriba de la tabla, en la misma pantalla, con
// scroll suave hacia arriba. Hay un chip con X para quitar el filtro.
//
// "Editar" ahora es un MODAL flotante (mismo patron que el modal de
// servicios adicionales en reservas.jsx) en vez de navegar a otra
// pantalla -- la lista se queda visible detras.
import { useEffect, useState } from "react";
import { FaSearch, FaPen, FaTrash, FaTimes, FaCheck } from "react-icons/fa";
import api from "../api/axios";

// mismo patron de extraccion de error que ya uso en reservas.jsx y pagos.jsx
function extraerMensajeError(err, mensajePorDefecto) {
  const detalle = err.response?.data?.detail;
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle)) {
    return detalle
      .map((e) => `${e.loc?.[e.loc.length - 1] ?? "campo"}: ${e.msg}`)
      .join(" | ");
  }
  return mensajePorDefecto;
}

const FORMULARIO_VACIO = {
  monto: "",
  fecha_vencimiento: "",
  estado: "Pendiente",
};

function Cuotas() {
  const [cuotas, setCuotas] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [reservas, setReservas] = useState([]);
  const [clientes, setClientes] = useState([]);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  // Reemplaza a "vista": null = modal cerrado, objeto = cuota en edicion
  // (mismo patron que reservaServicios en reservas.jsx)
  const [cuotaEditando, setCuotaEditando] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const [busqueda, setBusqueda] = useState("");

  // "" = ver todas las reservas mezcladas (comportamiento original).
  // se activa clickeando el ID de Reserva en la tabla 
  //  Se usa para: (1) filtrar la tabla a solo sus cuotas, y
  // (2) calcular la tarjeta resumen de esa reserva.
  const [reservaFiltro, setReservaFiltro] = useState("");

  const cargarDatos = async () => {
    setCargando(true);
    try {
      const [resCuotas, resPagos, resReservas, resClientes] = await Promise.all([
        api.get("/cuotas"),
        api.get("/pagos"),
        api.get("/reservas"),
        api.get("/clientes"),
      ]);
      setCuotas(resCuotas.data);
      setPagos(resPagos.data);
      setReservas(resReservas.data);
      setClientes(resClientes.data);
    } catch {
      setError("No se pudo cargar la lista de cuotas.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarDatos();
  }, []);

  // cadena de relaciones: cuota -> pago -> reserva -> cliente.
  // cada cuota solo trae id_pago, asi que hay que ir "subiendo" para
  // sacar el nombre del cliente (igual que clienteDeReserva en pagos.jsx)
  const pagoDeCuota = (id_pago) => pagos.find((p) => p.id_pago === id_pago);

  const reservaDeCuota = (id_pago) => {
    const pago = pagoDeCuota(id_pago);
    return pago ? reservas.find((r) => r.id_reserva === pago.id_reserva) : null;
  };

  const nombreClienteDeCuota = (id_pago) => {
    const reserva = reservaDeCuota(id_pago);
    if (!reserva) return "—";
    const c = clientes.find((c) => c.id_cliente === reserva.id_cliente);
    return c ? `${c.nombre} ${c.apellido}` : "—";
  };

  // ── Resumen de la reserva elegida en el filtro (mismo calculo que
  // uso en CuotasReserva.jsx, pero aca dependen de reservaFiltro en
  // vez de una prop fija) ──
  const reservaElegida = reservas.find((r) => r.id_reserva === reservaFiltro);
  const pagosDeReservaFiltro = pagos.filter((p) => p.id_reserva === reservaFiltro);
  const cuotasDeReservaFiltro = cuotas.filter((c) =>
    pagosDeReservaFiltro.some((p) => p.id_pago === c.id_pago)
  );
  const nombreClienteFiltro = reservaElegida
    ? (() => {
        const c = clientes.find((c) => c.id_cliente === reservaElegida.id_cliente);
        return c ? `${c.nombre} ${c.apellido}` : "—";
      })()
    : "—";
  const totalFiltro = pagosDeReservaFiltro.reduce((acc, p) => acc + Number(p.monto_total), 0);
  const inicialFiltro = (
    cuotasDeReservaFiltro.find((c) => c.numero_cuota === 1)?.monto ?? 0
  );
  const pagadoFiltro = cuotasDeReservaFiltro
    .filter((c) => c.estado === "Pagada")
    .reduce((acc, c) => acc + Number(c.monto), 0);
  const saldoFiltro = totalFiltro - pagadoFiltro;

  const textoBusqueda = busqueda.trim().toLowerCase();
  const cuotasFiltradas = cuotas
    // si hay una reserva elegida (clickeando el ID en la tabla), primero
    // se recorta a solo las cuotas de esa reserva; si no, se queda con todas
    .filter((c) =>
      reservaFiltro ? reservaDeCuota(c.id_pago)?.id_reserva === reservaFiltro : true
    )
    .filter((c) =>
      `${c.id_pago} ${nombreClienteDeCuota(c.id_pago)} ${c.estado}`
        .toLowerCase()
        .includes(textoBusqueda)
    );

  // mismos colores que uso en CuotasReserva.jsx, para que se vea igual
    const colorEstado = (estado) => {
    switch (estado) {
      case "Pagada":
        return { backgroundColor: "#d1f5e0", color: "#0f7a45" };
      case "Pendiente":
        return { backgroundColor: "#fde9c8", color: "#a3670f" };
      case "Vencida":
        return { backgroundColor: "#fbd7dd", color: "#c2273f" };
      default:
        return { backgroundColor: "#e5e5e5", color: "#333" };
    }
  };

  const abrirEdicionCuota = (c) => {
    setCuotaEditando(c);
    setFormulario({
      monto: c.monto,
      fecha_vencimiento: c.fecha_vencimiento,
      // Si la cuota ya esta Pagada, el select solo tiene sentido dejarla
      // en Pendiente/Vencida como punto de partida visual -- pero el
      // valor real que se guarde depende de lo que el usuario elija,
      // "Pagada" ya no es una opcion aca (ver mas abajo, PUT no la marca
      // pagada de verdad -- eso va por el boton dedicado).
      estado: c.estado === "Pagada" ? "Pendiente" : c.estado,
    });
    setErrorFormulario("");
  };

  const cerrarModalEdicion = () => {
    setCuotaEditando(null);
    setFormulario(FORMULARIO_VACIO);
    setErrorFormulario("");
  };

  const cambiarCampo = (campo) => (e) =>
    setFormulario((f) => ({ ...f, [campo]: e.target.value }));

  // Este PUT SOLO corrige datos (monto, fecha de vencimiento, o pasar
  // entre Pendiente <-> Vencida). NUNCA marca "Pagada" -- CuotaDAO.actualizar()
  // no acepta fecha_pago, asi que si se mandara "Pagada" por aca quedaria
  // el badge verde pero SIN fecha de pago real guardada (inconsistente).
  // El unico camino correcto a "Pagada" es marcarPagada(), mas abajo,
  // que llama a PATCH /cuotas/{id}/pagar (ese si guarda la fecha real).
  const guardarCuota = (e) => {
    e.preventDefault();
    if (!cuotaEditando) return;
    setGuardando(true);
    setErrorFormulario("");

    api
      .put(`/cuotas/${cuotaEditando.id_cuota}`, {
        monto: Number(formulario.monto),
        fecha_vencimiento: formulario.fecha_vencimiento,
        estado: formulario.estado,
      })
      .then(() => {
        cargarDatos();
        cerrarModalEdicion();
      })
      .catch((err) => {
        setErrorFormulario(
          extraerMensajeError(err, "No se pudo guardar la cuota. Revisa los datos.")
        );
      })
      .finally(() => setGuardando(false));
  };

  const eliminarCuota = (c) => {
    if (!window.confirm(`¿Eliminar la cuota N° ${c.numero_cuota} (id ${c.id_cuota})?`)) return;
    api
      .delete(`/cuotas/${c.id_cuota}`)
      .then(() => cargarDatos())
      .catch((err) => {
        alert(extraerMensajeError(err, "No se pudo eliminar la cuota."));
      });
  };

  // Unico camino real a "Pagada": PATCH dedicado, que ademas de cambiar
  // el estado registra fecha_pago = hoy en el backend (ver
  // CuotaDAO.marcar_pagada en cuota_dao.py).
  const marcarPagada = (c) => {
    api
      .patch(`/cuotas/${c.id_cuota}/pagar`)
      .then(() => cargarDatos())
      .catch((err) => {
        alert(extraerMensajeError(err, "No se pudo marcar la cuota como pagada."));
      });
  };

  return (
    <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1200 }}>
      <div className="mb-1">
        <h2 className="fw-bold mb-1">Cuotas</h2>
        <p className="text-muted mb-0">Lista de todas las cuotas registradas</p>
      </div>

      <div className="position-relative mt-4 mb-3" style={{ maxWidth: 420 }}>
        <input
          type="text"
          className="form-control rounded-3 py-2 ps-3 pe-5"
          placeholder="Buscar cuota..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <FaSearch
          className="position-absolute text-muted"
          style={{ right: 16, top: "50%", transform: "translateY(-50%)" }}
        />
      </div>

      {/* chip de filtro.el filtro se
          activa clickeando el ID de reserva directo en la fila de la
          tabla (mas abajo). Este chip solo sirve para ver que reserva
          esta filtrada y para quitar el filtro con la X */}
      {reservaFiltro && (
        <button
          type="button"
          className="btn btn-sm rounded-pill px-3 py-1 mb-3 d-inline-flex align-items-center gap-2"
          style={{ backgroundColor: "#efe6fc", color: "#7c3aed", border: "none" }}
          onClick={() => setReservaFiltro("")}
        >
          Viendo cuotas de {reservaFiltro}
          <FaTimes size={11} />
        </button>
      )}

      {/* tarjeta resumen: SOLO aparece si hay una reserva elegida
          (clickeando su ID en la tabla) -- mismo estilo (fondo lila)
          que en CuotasReserva.jsx */}
      {reservaFiltro && (
        <div className="rounded-4 p-4 mb-3" style={{ backgroundColor: "#eeeef7" }}>
          <div className="d-flex flex-wrap justify-content-between align-items-start gap-3">
            <div>
              <p className="mb-1">
                <span className="fw-semibold">Reserva: </span>
                <span className="fw-bold">{reservaFiltro}</span>
              </p>
              <p className="mb-0">
                <span className="fw-semibold">Cliente: </span>
                <span className="fw-bold">{nombreClienteFiltro}</span>
              </p>
            </div>
            <div className="d-flex gap-4">
              <p className="mb-0">
                <span className="fw-semibold">Total: </span>
                <span className="fw-bold">S/ {totalFiltro.toFixed(2)}</span>
              </p>
              <p className="mb-0">
                <span className="fw-semibold">Inicial: </span>
                <span className="fw-bold">S/ {Number(inicialFiltro).toFixed(2)}</span>
              </p>
              <p className="mb-0">
                <span className="fw-semibold">Saldo: </span>
                <span className="fw-bold">S/ {saldoFiltro.toFixed(2)}</span>
              </p>
            </div>
          </div>
        </div>
      )}

      <div
        className="card shadow-sm border-0 rounded-4 p-3 overflow-auto"
        style={{ maxHeight: "70vh" }}
      >
        {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}

        {cargando ? (
          <p className="text-muted mb-0 p-3">Cargando...</p>
        ) : cuotasFiltradas.length === 0 ? (
          <p className="text-muted mb-0 p-3">
            {textoBusqueda || reservaFiltro
              ? "No se encontraron cuotas."
              : "Aún no hay cuotas registradas."}
          </p>
        ) : (
          <div className="table-responsive">
            <table className="table align-middle mb-0">
              <thead className="sticky-top bg-white">
                <tr className="text-muted small">
                  <th className="fw-semibold">ID</th>
                  <th className="fw-semibold">N° Cuota</th>
                  <th className="fw-semibold">Reserva</th>
                  <th className="fw-semibold">Cliente</th>
                  <th className="fw-semibold text-end">Monto</th>
                  <th className="fw-semibold">Fecha Vencimiento</th>
                  <th className="fw-semibold">Estado</th>
                  <th className="fw-semibold">Fecha Pago</th>
                  <th className="fw-semibold text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {cuotasFiltradas.map((c) => {
                  const reserva = reservaDeCuota(c.id_pago);
                  return (
                    <tr key={c.id_cuota}>
                      <td className="fw-semibold">{c.id_cuota}</td>
                      <td>{c.numero_cuota === 1 ? "1 (Inicial)" : c.numero_cuota}</td>
                      <td>
                        {/* aca es donde se activa el filtro . window.scrollTo es para que
                            la tarjeta resumen "suba" a la vista, por si
                            la tabla estaba desplazada hacia abajo */}
                        {reserva ? (
                          <button
                            type="button"
                            className="btn btn-link p-0 fw-semibold text-decoration-underline"
                            style={{ color: "#7c3aed" }}
                            onClick={() => {
                              setReservaFiltro(reserva.id_reserva);
                              window.scrollTo({ top: 0, behavior: "smooth" });
                            }}
                          >
                            {reserva.id_reserva}
                          </button>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>{nombreClienteDeCuota(c.id_pago)}</td>
                      <td className="text-end">S/ {Number(c.monto).toFixed(2)}</td>
                      <td>{c.fecha_vencimiento}</td>
                      <td>
                        <span
                          className="badge rounded-pill px-3 py-2 fw-semibold"
                          style={colorEstado(c.estado)}
                        >
                          {c.estado}
                        </span>
                      </td>
                      <td className="text-muted">{c.fecha_pago ?? "———"}</td>
                      <td className="text-end">
                        <div className="d-flex justify-content-end gap-2 flex-nowrap">
                          {/* Marcar pagada: solo si todavia no lo esta.
                              Este es el UNICO camino que registra
                              fecha_pago real (ver marcarPagada arriba). */}
                          {c.estado !== "Pagada" && (
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#22c55e", color: "white" }}
                              title="Marcar como pagada"
                              onClick={() => marcarPagada(c)}
                            >
                              <FaCheck size={12} />
                            </button>
                          )}
                          <button
                            type="button"
                            className="btn btn-sm rounded-2"
                            style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                            title="Editar"
                            onClick={() => abrirEdicionCuota(c)}
                          >
                            <FaPen size={13} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-sm rounded-2"
                            style={{ backgroundColor: "#e0466f", color: "white" }}
                            title="Eliminar"
                            onClick={() => eliminarCuota(c)}
                          >
                            <FaTrash size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ────────────────────────────────────────────
          MODAL FLOTANTE: Editar cuota. Mismo patron que el modal de
          servicios adicionales en reservas.jsx -- fondo oscuro fijo,
          tarjeta blanca centrada, click afuera cierra (stopPropagation
          evita que el click DENTRO de la tarjeta la cierre).
          ──────────────────────────────────────────── */}
      {cuotaEditando && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
          style={{ backgroundColor: "rgba(0,0,0,0.45)", zIndex: 1050 }}
          onClick={cerrarModalEdicion}
        >
          <div
            className="bg-white rounded-4 shadow-lg p-4"
            style={{ maxWidth: 520, width: "90%", maxHeight: "85vh", overflowY: "auto" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="d-flex justify-content-between align-items-start mb-1">
              <div>
                <h5 className="fw-bold mb-1">Editar Cuota {cuotaEditando.id_cuota}</h5>
                <p className="text-muted small mb-0">Modifica los datos de la cuota</p>
              </div>
              <button
                type="button"
                className="btn btn-sm btn-light rounded-2"
                onClick={cerrarModalEdicion}
              >
                <FaTimes size={13} />
              </button>
            </div>

            {errorFormulario && (
              <div className="alert alert-danger py-2 mt-3">{errorFormulario}</div>
            )}

            <form onSubmit={guardarCuota} className="mt-4">
              <div className="row g-3">
                <div className="col-12 col-sm-6">
                  <label className="form-label fw-semibold">Monto</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    className="form-control rounded-3 py-2"
                    value={formulario.monto}
                    onChange={cambiarCampo("monto")}
                    required
                  />
                </div>

                <div className="col-12 col-sm-6">
                  <label className="form-label fw-semibold">Fecha de vencimiento</label>
                  <input
                    type="date"
                    className="form-control rounded-3 py-2"
                    value={formulario.fecha_vencimiento}
                    onChange={cambiarCampo("fecha_vencimiento")}
                    required
                  />
                </div>

                {/* "Pagada" NO esta como opcion aca a proposito: marcar
                    una cuota como pagada de verdad (con su fecha_pago
                    real) se hace con el boton dedicado en la tabla, no
                    editando este formulario. */}
                <div className="col-12">
                  <label className="form-label fw-semibold">Estado</label>
                  <select
                    className="form-select rounded-3 py-2"
                    value={formulario.estado}
                    onChange={cambiarCampo("estado")}
                    required
                  >
                    <option value="Pendiente">Pendiente</option>
                    <option value="Vencida">Vencida</option>
                  </select>
                  <p className="text-muted small mt-1 mb-0">
                    Para marcar la cuota como pagada, usa el botón de la lista.
                  </p>
                </div>
              </div>

              <div className="d-flex justify-content-end gap-2 mt-4">
                <button
                  type="button"
                  className="btn btn-light rounded-3 px-4 py-2"
                  onClick={cerrarModalEdicion}
                  disabled={guardando}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="btn rounded-3 px-4 py-2 text-white fw-semibold"
                  style={{ backgroundColor: "#7c3aed" }}
                  disabled={guardando}
                >
                  {guardando ? "Guardando..." : "Guardar Cambios"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Cuotas;