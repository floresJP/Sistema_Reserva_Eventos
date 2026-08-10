// componentes/pagos.jsx
import { useEffect, useState } from "react";
import { FaSearch, FaPen, FaTrash, FaPlus, FaCheck, FaListOl } from "react-icons/fa";
import api from "../api/axios";

// Los 5 unicos valores que acepta ValidadorMetodoPago en el backend.
const METODOS_PAGO = ["YAPE", "PLIN", "TRANSFERENCIA", "EFECTIVO", "TARJETA"];

// Fecha de hoy en formato YYYY-MM-DD, para precargar el input type="date".
const hoyISO = () => new Date().toISOString().slice(0, 10);

const FORMULARIO_VACIO = {
  id_reserva: "",
  metodo_pago: "",
  total_cuotas: 1,
  monto_total: "",
  fecha_pago: hoyISO(),
};

// ────────────────────────────────────────────────
// HELPER: mismo patron que en reservas.jsx / servicios adicionales.
// err.response.data.detail puede ser STRING (404/409) o ARRAY (422 Pydantic).
// ────────────────────────────────────────────────
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

function Pagos() {
  const [pagos, setPagos] = useState([]);
  const [reservas, setReservas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [cuotas, setCuotas] = useState([]); // TODAS las cuotas, para saber cuales pagos ya las generaron

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [vista, setVista] = useState("lista"); // "lista" | "formulario"
  const [idEditando, setIdEditando] = useState(null);
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const [busqueda, setBusqueda] = useState("");

  const cargarDatos = async () => {
    setCargando(true);
    try {
      const [resPagos, resReservas, resClientes, resCuotas] = await Promise.all([
        api.get("/pagos"),
        api.get("/reservas"),
        api.get("/clientes"),
        api.get("/cuotas"),
      ]);
      setPagos(resPagos.data);
      setReservas(resReservas.data);
      setClientes(resClientes.data);
      setCuotas(resCuotas.data);
    } catch {
      setError("No se pudo cargar la lista de pagos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarDatos();
  }, []);

  const nombreCliente = (id_cliente) => {
    const c = clientes.find((c) => c.id_cliente === id_cliente);
    return c ? `${c.nombre} ${c.apellido}` : id_cliente;
  };

  // A partir del id_reserva de un PAGO, encuentra la reserva y de ahi el cliente.
  const clienteDeReserva = (id_reserva) => {
    const r = reservas.find((r) => r.id_reserva === id_reserva);
    return r ? nombreCliente(r.id_cliente) : "—";
  };

  // true si el pago ya tiene AL MENOS una cuota generada. Se usa para
  // ocultar "Generar cuotas" despues del primer uso, porque
  // CuotaDAO.generarCuotas() no valida duplicados -- si se llama dos
  // veces, crea cuotas repetidas.
  const tieneCuotasGeneradas = (id_pago) => cuotas.some((c) => c.id_pago === id_pago);

  // Reserva seleccionada actualmente EN EL FORMULARIO (para mostrar el
  // nombre del cliente en modo lectura debajo del select de Reserva).
  const reservaSeleccionada = reservas.find((r) => r.id_reserva === formulario.id_reserva);

  const textoBusqueda = busqueda.trim().toLowerCase();
  const pagosFiltrados = pagos.filter((p) =>
    `${p.id_pago} ${clienteDeReserva(p.id_reserva)} ${p.metodo_pago} ${p.estado_pago}`
      .toLowerCase()
      .includes(textoBusqueda)
  );

  const colorEstadoPago = (estado) => {
    switch (estado) {
      case "Pagado":
        return { backgroundColor: "#d1f5e0", color: "#0f7a45" };
      case "Pago parcial":
        return { backgroundColor: "#fde9c8", color: "#a3670f" };
      case "Pendiente":
        return { backgroundColor: "#fbd7dd", color: "#c2273f" };
      default:
        return { backgroundColor: "#e5e5e5", color: "#333" };
    }
  };

  const abrirNuevoPago = () => {
    setIdEditando(null);
    setFormulario(FORMULARIO_VACIO); // ya trae fecha_pago = hoy
    setErrorFormulario("");
    setVista("formulario");
  };

  const abrirEdicionPago = (p) => {
    setIdEditando(p.id_pago);
    setFormulario({
      id_reserva: p.id_reserva,
      metodo_pago: p.metodo_pago,
      total_cuotas: p.total_cuotas,
      monto_total: p.monto_total,
      fecha_pago: p.fecha_pago, // ya viene en formato YYYY-MM-DD desde el backend
    });
    setErrorFormulario("");
    setVista("formulario");
  };

  const cancelarFormulario = () => {
    setVista("lista");
    setFormulario(FORMULARIO_VACIO);
    setIdEditando(null);
    setErrorFormulario("");
  };

  const cambiarCampo = (campo) => (e) =>
    setFormulario((f) => ({ ...f, [campo]: e.target.value }));

  const guardarPago = (e) => {
    e.preventDefault();
    setGuardando(true);
    setErrorFormulario("");

    // El PUT (edicion) NO incluye id_reserva ni fecha_pago -- ambos son
    // inmutables una vez creado el pago (PagoActualizar no los acepta,
    // ver schema). El POST (creacion) SI manda fecha_pago, para poder
    // registrar pagos que ocurrieron en otro dia distinto a hoy.
    const peticion = idEditando
      ? api.put(`/pagos/${idEditando}`, {
          monto_total: Number(formulario.monto_total),
          metodo_pago: formulario.metodo_pago,
          total_cuotas: Number(formulario.total_cuotas),
        })
      : api.post("/pagos", {
          monto_total: Number(formulario.monto_total),
          metodo_pago: formulario.metodo_pago,
          total_cuotas: Number(formulario.total_cuotas),
          id_reserva: formulario.id_reserva,
          fecha_pago: formulario.fecha_pago,
        });

    peticion
      .then(() => {
        cargarDatos();
        cancelarFormulario();
      })
      .catch((err) => {
        setErrorFormulario(
          extraerMensajeError(err, "No se pudo guardar el pago. Revisa los datos.")
        );
      })
      .finally(() => setGuardando(false));
  };

  const eliminarPago = (p) => {
    if (!window.confirm(`¿Eliminar el pago ${p.id_pago}?`)) return;
    api
      .delete(`/pagos/${p.id_pago}`)
      .then(() => cargarDatos())
      .catch((err) => {
        // Si el pago ya tiene cuotas generadas, el backend responde 409
        // (PagoConCuotasError) y no deja borrar.
        alert(extraerMensajeError(err, "No se pudo eliminar el pago."));
      });
  };

  const marcarPagado = (id_pago) => {
    api
      .patch(`/pagos/${id_pago}/pagar`)
      .then(() => cargarDatos())
      .catch((err) => {
        alert(extraerMensajeError(err, "No se pudo marcar el pago como pagado."));
      });
  };

  const generarCuotas = (id_pago) => {
    api
      .post(`/pagos/${id_pago}/generar-cuotas`)
      .then((res) => {
        alert(`Se generaron ${res.data.length} cuota(s) correctamente.`);
        cargarDatos(); // refresca pagos + cuotas, asi tieneCuotasGeneradas queda al dia
      })
      .catch((err) => {
        alert(extraerMensajeError(err, "No se pudieron generar las cuotas."));
      });
  };

  // ────────────────────────────────────────────────
  // VISTA: FORMULARIO
  // ────────────────────────────────────────────────
  if (vista === "formulario") {
    return (
      <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1000 }}>
        <h2 className="fw-bold mb-1">
          {idEditando ? `Editar Pago ${idEditando}` : "Registrar Pago"}
        </h2>
        <p className="text-muted mb-4">
          {idEditando ? "Modifica los datos del pago" : "Registra el pago de la reserva"}
        </p>

        <form onSubmit={guardarPago}>
          {errorFormulario && (
            <div className="alert alert-danger py-2">{errorFormulario}</div>
          )}

          <div className="row g-4">
            {/* ── COLUMNA IZQUIERDA ── */}
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Reserva</label>
              <select
                className="form-select rounded-3 py-2 mb-1"
                value={formulario.id_reserva}
                onChange={cambiarCampo("id_reserva")}
                disabled={idEditando !== null}
                required
              >
                <option value="">Seleccione reserva</option>
                {reservas.map((r) => (
                  <option key={r.id_reserva} value={r.id_reserva}>
                    {r.id_reserva} — {r.fecha_evento}
                  </option>
                ))}
              </select>
              {idEditando && (
                <p className="text-muted small mb-3">
                  La reserva no se puede cambiar una vez creado el pago.
                </p>
              )}

              <label className="form-label fw-semibold mt-3">Cliente</label>
              {/* Se autocompleta solo al elegir la Reserva. Es informativo,
                  no se manda al backend (PagoCrear no tiene campo cliente,
                  el cliente ya esta implicito via la reserva). */}
              <input
                type="text"
                className="form-control rounded-3 py-2"
                value={reservaSeleccionada ? nombreCliente(reservaSeleccionada.id_cliente) : ""}
                placeholder="Se completa al elegir la reserva"
                disabled
              />
            </div>

            {/* ── COLUMNA DERECHA ── */}
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Método de pago</label>
              <select
                className="form-select rounded-3 py-2 mb-3"
                value={formulario.metodo_pago}
                onChange={cambiarCampo("metodo_pago")}
                required
              >
                <option value="">Seleccione método</option>
                {METODOS_PAGO.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>

              <label className="form-label fw-semibold">Cuotas</label>
              <input
                type="number"
                min="1"
                className="form-control rounded-3 py-2 mb-1"
                value={formulario.total_cuotas}
                onChange={cambiarCampo("total_cuotas")}
                required
              />
              <p className="text-muted small mb-3">
                1 cuota = el pago queda "Pagado" de una vez. Más de 1 = queda
                "Pendiente" y se generan las cuotas después, desde la lista.
              </p>

              <label className="form-label fw-semibold">Monto total</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-control rounded-3 py-2 mb-3"
                placeholder="0.00"
                value={formulario.monto_total}
                onChange={cambiarCampo("monto_total")}
                required
              />

              <label className="form-label fw-semibold">Fecha de pago</label>
              {/* Editable en creacion (por defecto hoy, pero se puede
                  cambiar para registrar un pago que ocurrio otro dia).
                  En edicion queda deshabilitada: PagoActualizar no
                  acepta fecha_pago, una vez creado el pago no se
                  puede modificar la fecha. */}
              <input
                type="date"
                className="form-control rounded-3 py-2 mb-1"
                value={formulario.fecha_pago}
                onChange={cambiarCampo("fecha_pago")}
                disabled={idEditando !== null}
                required={idEditando === null}
              />
              {idEditando && (
                <p className="text-muted small mb-0">
                  La fecha de pago no se puede modificar una vez registrado el pago.
                </p>
              )}
            </div>
          </div>

          <div className="d-flex justify-content-end gap-2 mt-4">
            <button
              type="button"
              className="btn btn-light rounded-3 px-4 py-2"
              onClick={cancelarFormulario}
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
              {guardando ? "Guardando..." : idEditando ? "Guardar Cambios" : "Registrar Pago"}
            </button>
          </div>
        </form>
      </div>
    );
  }

  // ────────────────────────────────────────────────
  // VISTA: LISTA
  // ────────────────────────────────────────────────
  return (
    <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1200 }}>
      <div className="d-flex align-items-start justify-content-between mb-1">
        <div>
          <h2 className="fw-bold mb-1">Pagos</h2>
          <p className="text-muted mb-0">Lista de pagos registrados</p>
        </div>
        <button
          type="button"
          className="btn rounded-3 px-3 py-2 text-white fw-semibold d-flex align-items-center gap-2"
          style={{ backgroundColor: "#7c3aed" }}
          onClick={abrirNuevoPago}
        >
          <FaPlus size={14} /> Nuevo Pago
        </button>
      </div>

      <div className="position-relative mt-4 mb-3" style={{ maxWidth: 420 }}>
        <input
          type="text"
          className="form-control rounded-3 py-2 ps-3 pe-5"
          placeholder="Buscar pago..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <FaSearch
          className="position-absolute text-muted"
          style={{ right: 16, top: "50%", transform: "translateY(-50%)" }}
        />
      </div>

      <div
        className="card shadow-sm border-0 rounded-4 p-3 overflow-auto"
        style={{ maxHeight: "70vh" }}
      >
        {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}

        {cargando ? (
          <p className="text-muted mb-0 p-3">Cargando...</p>
        ) : pagosFiltrados.length === 0 ? (
          <p className="text-muted mb-0 p-3">
            {textoBusqueda ? "No se encontraron pagos." : "Aún no hay pagos registrados."}
          </p>
        ) : (
          <div className="table-responsive">
            <table className="table align-middle mb-0">
              <thead className="sticky-top bg-white">
                <tr className="text-muted small">
                  <th className="fw-semibold">ID</th>
                  <th className="fw-semibold">Reserva</th>
                  <th className="fw-semibold">Cliente</th>
                  <th className="fw-semibold">Método</th>
                  <th className="fw-semibold text-end">Cuotas</th>
                  <th className="fw-semibold text-end">Monto Total</th>
                  <th className="fw-semibold">Fecha Pago</th>
                  <th className="fw-semibold">Estado</th>
                  <th className="fw-semibold text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pagosFiltrados.map((p) => (
                  <tr key={p.id_pago}>
                    <td className="fw-semibold">{p.id_pago}</td>
                    <td>{p.id_reserva}</td>
                    <td>{clienteDeReserva(p.id_reserva)}</td>
                    <td>{p.metodo_pago}</td>
                    <td className="text-end">{p.total_cuotas}</td>
                    <td className="text-end">S/ {Number(p.monto_total).toFixed(2)}</td>
                    <td>{p.fecha_pago}</td>
                    <td>
                      <span
                        className="badge rounded-pill px-3 py-2 fw-semibold"
                        style={colorEstadoPago(p.estado_pago)}
                      >
                        {p.estado_pago}
                      </span>
                    </td>
                    <td className="text-end">
                      <div className="d-flex justify-content-end gap-2 flex-nowrap">
                        {/* Generar cuotas: solo si el pago se dividio en
                            mas de 1 cuota Y todavia no tiene ninguna
                            cuota creada (evita duplicados, ver
                            tieneCuotasGeneradas mas arriba). */}
                        {p.total_cuotas > 1 && !tieneCuotasGeneradas(p.id_pago) && (
                          <button
                            type="button"
                            className="btn btn-sm rounded-2"
                            style={{ backgroundColor: "#3949ab", color: "white" }}
                            title="Generar cuotas"
                            onClick={() => generarCuotas(p.id_pago)}
                          >
                            <FaListOl size={12} />
                          </button>
                        )}

                        {/* Marcar pagado: solo si todavia no esta Pagado */}
                        {p.estado_pago !== "Pagado" && (
                          <button
                            type="button"
                            className="btn btn-sm rounded-2"
                            style={{ backgroundColor: "#22c55e", color: "white" }}
                            title="Marcar como pagado"
                            onClick={() => marcarPagado(p.id_pago)}
                          >
                            <FaCheck size={12} />
                          </button>
                        )}

                        <button
                          type="button"
                          className="btn btn-sm rounded-2"
                          style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                          title="Editar"
                          onClick={() => abrirEdicionPago(p)}
                        >
                          <FaPen size={13} />
                        </button>
                        <button
                          type="button"
                          className="btn btn-sm rounded-2"
                          style={{ backgroundColor: "#e0466f", color: "white" }}
                          title="Eliminar"
                          onClick={() => eliminarPago(p)}
                        >
                          <FaTrash size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Pagos;