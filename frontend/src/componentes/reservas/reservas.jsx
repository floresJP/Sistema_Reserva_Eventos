// componentes/reservas.jsx
import { useEffect, useState } from "react";
import {
  FaSearch,
  FaPen,
  FaTrash,
  FaPlus,
  FaCheck,
  FaBan,
  FaFlagCheckered,
  FaShoppingCart,
  FaTimes,
} from "react-icons/fa";
import api from "../api/axios";

const FORMULARIO_VACIO = {
  fecha_evento: "",
  hora_inicio: "",
  hora_fin: "",
  direccion: "",
  edad_cumpleanero: "",
  observaciones: "",
  id_cliente: "",
  id_tematica: "",
};

const SERVICIO_VACIO = { nombre_servicio_adicional: "", descripcion: "", precio: "", estado: "Activo" };

// ────────────────────────────────────────────────
// HELPER: extraer un mensaje legible de un error de axios.
// err.response.data.detail puede ser un STRING (HTTPException nuestra,
// ej. 404/409) o un ARRAY de {loc, msg, type} (error 422 de validacion
// de Pydantic). Sin este helper, cualquier 422 caia siempre al mensaje
// generico sin decir que campo fallo y por que.
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

function Reservas() {
  // ── Estados de datos que vienen de la API ──
  const [reservas, setReservas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [tematicas, setTematicas] = useState([]);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [vista, setVista] = useState("lista"); // "lista" | "formulario"
  const [idEditando, setIdEditando] = useState(null);
  // Guarda el estado actual de la reserva en edicion, SOLO para mostrarlo
  // como informativo en el campo "Estado" del formulario (deshabilitado).
  // No se manda al backend -- el cambio real es via los botones de la tabla
  // (PATCH /confirmar, /cancelar, /completar), porque ReservaActualizar
  // (el schema del PUT) no acepta "estado".
  const [estadoActual, setEstadoActual] = useState("Pendiente");
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const [busqueda, setBusqueda] = useState("");

  // ── Estados SOLO del modal de servicios adicionales ──
  const [reservaServicios, setReservaServicios] = useState(null); // reserva activa en el modal, null = cerrado
  const [listaServicios, setListaServicios] = useState([]);
  const [totalServicios, setTotalServicios] = useState(0);
  const [formularioServicio, setFormularioServicio] = useState(SERVICIO_VACIO);
  const [editandoServicioId, setEditandoServicioId] = useState(null); // null = modo "agregar"
  const [cargandoServicios, setCargandoServicios] = useState(false);
  const [guardandoServicio, setGuardandoServicio] = useState(false);
  const [errorServicios, setErrorServicios] = useState("");

  const cargarReservas = async () => {
    setCargando(true);
    try {
      const [resReservas, resClientes, resTematicas] = await Promise.all([
        api.get("/reservas"),
        api.get("/clientes"),
        api.get("/tematicas"),
      ]);
      setReservas(resReservas.data);
      setClientes(resClientes.data);
      setTematicas(resTematicas.data);
    } catch {
      setError("No se pudo cargar la lista de reservas.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarReservas();
  }, []);

  const nombreCliente = (id_cliente) => {
    const c = clientes.find((c) => c.id_cliente === id_cliente);
    return c ? `${c.nombre} ${c.apellido}` : id_cliente;
  };

  const nombreTematica = (id_tematica) => {
    const t = tematicas.find((t) => t.id_tematica === id_tematica);
    return t ? t.descripcion : id_tematica;
  };

  const textoBusqueda = busqueda.trim().toLowerCase();
  const reservasFiltradas = reservas.filter((r) =>
    `${nombreCliente(r.id_cliente)} ${nombreTematica(r.id_tematica)} ${r.direccion}`
      .toLowerCase()
      .includes(textoBusqueda)
  );

  const colorEstado = (estado) => {
    switch (estado) {
      case "Confirmada":
        return { backgroundColor: "#d1f5e0", color: "#0f7a45" };
      case "Pendiente":
        return { backgroundColor: "#fde9c8", color: "#a3670f" };
      case "Cancelada":
        return { backgroundColor: "#fbd7dd", color: "#c2273f" };
      case "Completada":
        return { backgroundColor: "#dbe4ff", color: "#3949ab" };
      default:
        return { backgroundColor: "#e5e5e5", color: "#333" };
    }
  };

  // ── Formulario de Reserva: abrir / cerrar ──
  const abrirNuevaReserva = () => {
    setIdEditando(null);
    setEstadoActual("Pendiente"); // toda reserva nueva nace Pendiente
    setFormulario(FORMULARIO_VACIO);
    setErrorFormulario("");
    setVista("formulario");
  };

  const abrirEdicionReserva = (r) => {
    setIdEditando(r.id_reserva);
    setEstadoActual(r.estado);
    setFormulario({
      fecha_evento: r.fecha_evento,
      hora_inicio: r.hora_inicio,
      hora_fin: r.hora_fin,
      direccion: r.direccion,
      edad_cumpleanero: r.edad_cumpleanero ?? "",
      observaciones: r.observaciones || "",
      id_cliente: r.id_cliente,
      id_tematica: r.id_tematica,
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

  const guardarReserva = (e) => {
    e.preventDefault();
    setGuardando(true);
    setErrorFormulario("");

    const edad = formulario.edad_cumpleanero === "" ? null : Number(formulario.edad_cumpleanero);

    // El PUT (edicion) nunca incluye id_cliente ni id_tematica porque
    // ReservaActualizar (el schema) no los acepta -- son inmutables
    // una vez creada la reserva.
    const peticion = idEditando
      ? api.put(`/reservas/${idEditando}`, {
          fecha_evento: formulario.fecha_evento,
          hora_inicio: formulario.hora_inicio,
          hora_fin: formulario.hora_fin,
          direccion: formulario.direccion,
          edad_cumpleanero: edad,
          observaciones: formulario.observaciones,
        })
      : api.post("/reservas", {
          fecha_evento: formulario.fecha_evento,
          hora_inicio: formulario.hora_inicio,
          hora_fin: formulario.hora_fin,
          direccion: formulario.direccion,
          edad_cumpleanero: edad,
          observaciones: formulario.observaciones,
          id_cliente: formulario.id_cliente,
          id_tematica: formulario.id_tematica,
        });

    peticion
      .then(() => {
        cargarReservas();
        cancelarFormulario();
      })
      .catch((err) => {
        setErrorFormulario(
          extraerMensajeError(err, "No se pudo guardar la reserva. Revisa los datos.")
        );
      })
      .finally(() => setGuardando(false));
  };

  // ojo: este delete ahora se puede llamar desde CUALQUIER estado
  // (Pendiente, Confirmada, Cancelada, Completada) porque el boton
  // de Eliminar quedo visible siempre en la tabla. El backend igual
  // valida con su propia regla (ver el catch de abajo, error 409 si
  // tiene pagos/servicios asociados), asi que aunque el boton este
  // siempre ahi, no significa que SIEMPRE se pueda borrar.
  const eliminarReserva = (r) => {
    if (!window.confirm(`¿Eliminar la reserva ${r.id_reserva}?`)) return;
    api
      .delete(`/reservas/${r.id_reserva}`)
      .then(() => cargarReservas())
      .catch((err) => {
        // Si la reserva tiene pagos/servicios asociados, PostgreSQL
        // bloquea el DELETE por foreign key y el backend responde 409
        // (ReservaConDependenciasError) -- se muestra el detalle real.
        alert(extraerMensajeError(err, "No se pudo eliminar la reserva."));
      });
  };

  // Endpoints separados a proposito (/confirmar, /cancelar, /completar):
  // cada transicion es una regla de negocio distinta, no una edicion
  // libre de campos.
  const cambiarEstado = (id_reserva, accion) => {
    api
      .patch(`/reservas/${id_reserva}/${accion}`)
      .then(() => cargarReservas())
      .catch((err) => {
        alert(extraerMensajeError(err, `No se pudo ${accion} la reserva.`));
      });
  };

  // ────────────────────────────────────────────────
  // MODAL: servicios adicionales de una reserva
  //   GET    /servicios-adicionales/reserva/{id_reserva}        -> lista
  //   GET    /servicios-adicionales/reserva/{id_reserva}/total  -> total
  //   POST   /servicios-adicionales                              -> crear
  //   PUT    /servicios-adicionales/{id_servicio_adicional}       -> editar
  //   DELETE /servicios-adicionales/{id_servicio_adicional}       -> eliminar
  //
  // El campo real que devuelve la API es "id_servicio_adicional"
  // (ver ServicioAdicionalRespuesta en el schema) -- OJO con este nombre,
  // es distinto al de otras entidades (id_cliente, id_reserva, etc.).
  //
  // REGLA: si la reserva ya esta "Completada" o "Cancelada", el modal
  // se abre en modo SOLO LECTURA -- se ve la lista con el badge
  // Activo/Inactivo de cada servicio, pero no el formulario de
  // agregar/editar ni los botones de editar/eliminar por fila.
  // Esto lo controla "modalSoloLectura" mas abajo.
  // ────────────────────────────────────────────────

  const cargarServiciosDeReserva = async (id_reserva) => {
    setCargandoServicios(true);
    try {
      const [resLista, resTotal] = await Promise.all([
        api.get(`/servicios-adicionales/reserva/${id_reserva}`),
        api.get(`/servicios-adicionales/reserva/${id_reserva}/total`),
      ]);
      setListaServicios(resLista.data);
      setTotalServicios(resTotal.data.total_servicios ?? 0);
    } catch {
      setErrorServicios("No se pudieron cargar los servicios de esta reserva.");
    } finally {
      setCargandoServicios(false);
    }
  };

  const abrirModalServicios = (r) => {
    setReservaServicios(r);
    setErrorServicios("");
    setFormularioServicio(SERVICIO_VACIO);
    setEditandoServicioId(null); // arranca siempre en modo "agregar"
    cargarServiciosDeReserva(r.id_reserva);
  };

  const cerrarModalServicios = () => {
    setReservaServicios(null);
    setListaServicios([]);
    setTotalServicios(0);
    setFormularioServicio(SERVICIO_VACIO);
    setEditandoServicioId(null);
    setErrorServicios("");
  };

  // true cuando la reserva del modal ya no admite cambios en sus
  // servicios adicionales (evento ya paso o se cancelo).
  const modalSoloLectura =
    reservaServicios?.estado === "Completada" || reservaServicios?.estado === "Cancelada";

  const cambiarCampoServicio = (campo) => (e) =>
    setFormularioServicio((s) => ({ ...s, [campo]: e.target.value }));

  // alterna Activo <-> Inactivo cada vez que se presiona el boton de
  // Estado en el form de servicio (ya no es un <select>, es un boton
  // tipo badge que va cambiando de valor con cada click)
  const alternarEstadoServicio = () =>
    setFormularioServicio((s) => ({
      ...s,
      estado: s.estado === "Activo" ? "Inactivo" : "Activo",
    }));

  // Precarga el formulario con los datos del servicio a editar.
  // Mismo patron que empezarEdicion en clientes.jsx / abrirEdicionReserva.
  const empezarEdicionServicio = (s) => {
    setEditandoServicioId(s.id_servicio_adicional);
    setFormularioServicio({
      nombre_servicio_adicional: s.nombre_servicio_adicional,
      descripcion: s.descripcion,
      precio: s.precio,
      estado: s.estado,
    });
    setErrorServicios("");
  };

  const cancelarEdicionServicio = () => {
    setEditandoServicioId(null);
    setFormularioServicio(SERVICIO_VACIO);
    setErrorServicios("");
  };

  // Crea (POST) o edita (PUT), segun editandoServicioId.
  const guardarServicio = (e) => {
    e.preventDefault();
    if (!reservaServicios) return;
    setGuardandoServicio(true);
    setErrorServicios("");

    // El PUT (edicion) SI acepta "estado" (Activo/Inactivo) porque el
    // schema ServicioAdicionalActualizar lo permite -- a diferencia de
    // Reserva, aca no hay maquina de estados con transiciones, es un
    // simple toggle. El POST (crear) NO manda estado: el backend lo
    // asigna solo como "Activo" al crearse, aunque en el form ya se vea
    // el boton de Estado (por eso en el boton dejamos el comentario de
    // que en creacion el backend igual lo ignora).
    const peticion = editandoServicioId
      ? api.put(`/servicios-adicionales/${editandoServicioId}`, {
          nombre_servicio_adicional: formularioServicio.nombre_servicio_adicional,
          descripcion: formularioServicio.descripcion,
          precio: Number(formularioServicio.precio),
          estado: formularioServicio.estado,
        })
      : api.post("/servicios-adicionales", {
          nombre_servicio_adicional: formularioServicio.nombre_servicio_adicional,
          descripcion: formularioServicio.descripcion,
          precio: Number(formularioServicio.precio),
          id_reserva: reservaServicios.id_reserva,
        });

    peticion
      .then(() => {
        setFormularioServicio(SERVICIO_VACIO);
        setEditandoServicioId(null);
        cargarServiciosDeReserva(reservaServicios.id_reserva); // refresca lista + total
      })
      .catch((err) => {
        setErrorServicios(
          extraerMensajeError(
            err,
            editandoServicioId ? "No se pudo editar el servicio." : "No se pudo agregar el servicio."
          )
        );
      })
      .finally(() => setGuardandoServicio(false));
  };

  const eliminarServicio = (servicio) => {
    if (!window.confirm(`¿Eliminar "${servicio.nombre_servicio_adicional}"?`)) return;
    api
      .delete(`/servicios-adicionales/${servicio.id_servicio_adicional}`)
      .then(() => cargarServiciosDeReserva(reservaServicios.id_reserva))
      .catch((err) => {
        alert(extraerMensajeError(err, "No se pudo eliminar el servicio."));
      });
  };

  // ────────────────────────────────────────────────
  // VISTA: FORMULARIO -- layout 2 columnas, siguiendo el diseño de Figma.
  // El campo "ID" se quito del formulario: en modo edicion se muestra
  // junto al titulo (texto simple), y en modo creacion no aplica porque
  // aun no existe (lo genera el backend al guardar).
  // ────────────────────────────────────────────────
  if (vista === "formulario") {
    return (
      <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1000 }}>
        <h2 className="fw-bold mb-1">
          {idEditando ? `Editar Reserva ${idEditando}` : "Nueva Reserva"}
        </h2>
        <p className="text-muted mb-4">
          {idEditando ? "Modifica los datos de la reserva" : "Completa los datos de la reserva"}
        </p>

        <form onSubmit={guardarReserva}>
          {errorFormulario && (
            <div className="alert alert-danger py-2">{errorFormulario}</div>
          )}

          <div className="row g-4">
            {/* ── COLUMNA IZQUIERDA ── */}
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Cliente</label>
              <select
                className="form-select rounded-3 py-2 mb-3"
                value={formulario.id_cliente}
                onChange={cambiarCampo("id_cliente")}
                disabled={idEditando !== null}
                required
              >
                <option value="">Seleccione cliente</option>
                {clientes.map((c) => (
                  <option key={c.id_cliente} value={c.id_cliente}>
                    {c.nombre} {c.apellido}
                  </option>
                ))}
              </select>

              <label className="form-label fw-semibold">Fecha de Evento</label>
              <input
                type="date"
                className="form-control rounded-3 py-2 mb-3"
                value={formulario.fecha_evento}
                onChange={cambiarCampo("fecha_evento")}
                required
              />

              <label className="form-label fw-semibold">Hora Inicio</label>
              <input
                type="time"
                className="form-control rounded-3 py-2 mb-3"
                value={formulario.hora_inicio}
                onChange={cambiarCampo("hora_inicio")}
                required
              />

              <label className="form-label fw-semibold">Hora Fin</label>
              <input
                type="time"
                className="form-control rounded-3 py-2 mb-3"
                value={formulario.hora_fin}
                onChange={cambiarCampo("hora_fin")}
                required
              />

              <label className="form-label fw-semibold">
                Observaciones <span className="text-muted fw-normal">(opcional)</span>
              </label>
              <textarea
                className="form-control rounded-3 py-2"
                rows={3}
                placeholder="Ingrese observaciones"
                value={formulario.observaciones}
                onChange={cambiarCampo("observaciones")}
              />
            </div>

            {/* ── COLUMNA DERECHA ── */}
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Dirección del Evento</label>
              <input
                type="text"
                className="form-control rounded-3 py-2 mb-3"
                placeholder="Ingrese dirección"
                value={formulario.direccion}
                onChange={cambiarCampo("direccion")}
                required
              />

              <label className="form-label fw-semibold">Temática</label>
              <select
                className="form-select rounded-3 py-2 mb-3"
                value={formulario.id_tematica}
                onChange={cambiarCampo("id_tematica")}
                disabled={idEditando !== null}
                required
              >
                <option value="">Seleccione temática</option>
                {tematicas.map((t) => (
                  <option key={t.id_tematica} value={t.id_tematica}>
                    {t.descripcion} — S/ {Number(t.precio_base).toFixed(2)}
                  </option>
                ))}
              </select>

              {/* Campo Estado: deshabilitado a proposito. El PUT de
                  edicion (ReservaActualizar) NO acepta "estado" -- los
                  cambios de estado van por los botones Confirmar /
                  Cancelar / Completar de la tabla (endpoints PATCH
                  separados). Aca solo se muestra el estado actual. */}
              <label className="form-label fw-semibold">Estado</label>
              <input
                type="text"
                className="form-control rounded-3 py-2 mb-1"
                value={estadoActual}
                disabled
              />
              <p className="text-muted small mb-3">
                El estado se cambia desde los botones de la lista de reservas
                (Confirmar / Cancelar / Completar).
              </p>

              <label className="form-label fw-semibold">Edad Cumpleañero</label>
              <input
                type="number"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese edad"
                value={formulario.edad_cumpleanero}
                onChange={cambiarCampo("edad_cumpleanero")}
              />
            </div>
          </div>

          {idEditando && (
            <p className="text-muted small mt-4 mb-0">
              Los servicios adicionales (show, decoración, snacks, etc.) se administran
              desde el botón <FaShoppingCart size={11} /> en la lista de reservas.
            </p>
          )}

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
              {guardando ? "Guardando..." : "Guardar Reserva"}
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
          <h2 className="fw-bold mb-1">Reserva</h2>
          <p className="text-muted mb-0">Lista de reservas realizadas</p>
        </div>
        <button
          type="button"
          className="btn rounded-3 px-3 py-2 text-white fw-semibold d-flex align-items-center gap-2"
          style={{ backgroundColor: "#7c3aed" }}
          onClick={abrirNuevaReserva}
        >
          <FaPlus size={14} /> Nueva Reserva
        </button>
      </div>

      <div className="position-relative mt-4 mb-3" style={{ maxWidth: 420 }}>
        <input
          type="text"
          className="form-control rounded-3 py-2 ps-3 pe-5"
          placeholder="Buscar reserva ...."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <FaSearch
          className="position-absolute text-muted"
          style={{ right: 16, top: "50%", transform: "translateY(-50%)" }}
        />
      </div>

      {/* card como "cuadro" con su propio scroll: maxHeight + overflow-auto
          hace que la barra de scroll salga DENTRO de este recuadro y no
          en toda la pagina */}
      <div
        className="card shadow-sm border-0 rounded-4 p-3 overflow-auto"
        style={{ maxHeight: "70vh" }}
      >
        {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}

        {cargando ? (
          <p className="text-muted mb-0 p-3">Cargando...</p>
        ) : reservasFiltradas.length === 0 ? (
          <p className="text-muted mb-0 p-3">
            {textoBusqueda ? "No se encontraron reservas." : "Aún no hay reservas registradas."}
          </p>
        ) : (
          <div className="table-responsive">
            <table className="table align-middle mb-0">
              <thead className="sticky-top bg-white">
                <tr className="text-muted small">
                  <th className="fw-semibold">ID</th>
                  <th className="fw-semibold">Cliente</th>
                  <th className="fw-semibold">Fecha Evento</th>
                  <th className="fw-semibold">Temática</th>
                  <th className="fw-semibold">Hora Inicio</th>
                  <th className="fw-semibold">Hora Fin</th>
                  <th className="fw-semibold">Dirección</th>
                  <th className="fw-semibold">Observaciones</th>
                  <th className="fw-semibold">Estado</th>
                  <th className="fw-semibold text-end">Edad</th>
                  <th className="fw-semibold text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {reservasFiltradas.map((r) => (
                  <tr key={r.id_reserva}>
                    <td className="fw-semibold">{r.id_reserva}</td>
                    <td>{nombreCliente(r.id_cliente)}</td>
                    <td>{r.fecha_evento}</td>
                    <td>{nombreTematica(r.id_tematica)}</td>
                    <td>{r.hora_inicio}</td>
                    <td>{r.hora_fin}</td>
                    <td>{r.direccion}</td>
                    <td>{r.observaciones || "—"}</td>
                    <td>
                      <span
                        className="badge rounded-pill px-3 py-2 fw-semibold"
                        style={colorEstado(r.estado)}
                      >
                        {r.estado}
                      </span>
                    </td>
                    <td className="text-end">{r.edad_cumpleanero ?? "—"}</td>
                    <td className="text-end">
                      {/* ────────────────────────────────────────────
                          reglas por estado (asi quedamos):
                            Pendiente  -> Editar, Confirmar, Cancelar
                            Confirmada -> Editar, Completar
                            Cancelada  -> solo visualizar (sin acciones de edicion/estado)
                            Completada -> solo visualizar + boton de
                                          Servicios adicionales, en modo
                                          lectura (badge Activo/Inactivo,
                                          sin poder tocar nada)
                          y "Eliminar" va SIEMPRE, en los 4 casos, fuera
                          de todos los if de arriba -- por eso esta al
                          final del div, suelto, sin condicion.
                          ──────────────────────────────────────────── */}
                      <div className="d-flex justify-content-end gap-2 flex-nowrap">
                        {r.estado === "Pendiente" && (
                          <>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                              title="Editar"
                              onClick={() => abrirEdicionReserva(r)}
                            >
                              <FaPen size={13} />
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#22c55e", color: "white" }}
                              title="Confirmar"
                              onClick={() => cambiarEstado(r.id_reserva, "confirmar")}
                            >
                              <FaCheck size={12} />
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#ef4444", color: "white" }}
                              title="Cancelar"
                              onClick={() => cambiarEstado(r.id_reserva, "cancelar")}
                            >
                              <FaBan size={12} />
                            </button>
                          </>
                        )}

                        {r.estado === "Confirmada" && (
                          <>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                              title="Editar"
                              onClick={() => abrirEdicionReserva(r)}
                            >
                              <FaPen size={13} />
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#3949ab", color: "white" }}
                              title="Completar"
                              onClick={() => cambiarEstado(r.id_reserva, "completar")}
                            >
                              <FaFlagCheckered size={12} />
                            </button>
                          </>
                        )}

                        {/* Cancelada ya no muestra ni siquiera texto de
                            "solo lectura" -- ese texto quedaba pegado al
                            costado del boton Eliminar y se veia raro,
                            asi que se saco. La fila igual se ve normal,
                            solo que sin botones de estado. */}

                        {/* Completada: unico boton de estado/gestion es
                            "ver servicios adicionales", en modo lectura
                            (ver modalSoloLectura mas arriba en el
                            componente) */}
                        {r.estado === "Completada" && (
                          <button
                            type="button"
                            className="btn btn-sm rounded-2"
                            style={{ backgroundColor: "#8b5cf6", color: "white" }}
                            title="Ver servicios adicionales"
                            onClick={() => abrirModalServicios(r)}
                          >
                            <FaShoppingCart size={13} />
                          </button>
                        )}

                        {/* Pendiente y Confirmada tambien pueden gestionar
                            servicios adicionales (agregar/editar/eliminar) */}
                        {(r.estado === "Pendiente" || r.estado === "Confirmada") && (
                          <button
                            type="button"
                            className="btn btn-sm rounded-2"
                            style={{ backgroundColor: "#8b5cf6", color: "white" }}
                            title="Servicios adicionales"
                            onClick={() => abrirModalServicios(r)}
                          >
                            <FaShoppingCart size={13} />
                          </button>
                        )}

                        {/* Eliminar: va SIEMPRE, en los 4 estados, por
                            eso esta suelto aca abajo sin ningun if.
                            El backend es el que realmente decide si se
                            puede borrar o no (ver el catch en
                            eliminarReserva, mas arriba: si tiene pagos
                            o servicios asociados tira 409 y no deja). */}
                        <button
                          type="button"
                          className="btn btn-sm rounded-2"
                          style={{ backgroundColor: "#e0466f", color: "white" }}
                          title="Eliminar"
                          onClick={() => eliminarReserva(r)}
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

      {/* ────────────────────────────────────────────
          MODAL: Servicios adicionales de una reserva.
          ──────────────────────────────────────────── */}
      {reservaServicios && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
          style={{ backgroundColor: "rgba(0,0,0,0.45)", zIndex: 1050 }}
          onClick={cerrarModalServicios}
        >
          <div
            className="bg-white rounded-4 shadow-lg p-4"
            style={{ maxWidth: 560, width: "90%", maxHeight: "85vh", overflowY: "auto" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="d-flex justify-content-between align-items-start mb-1">
              <div>
                <h5 className="fw-bold mb-1">Servicios adicionales</h5>
                <p className="text-muted small mb-0">
                  Reserva {reservaServicios.id_reserva} — {nombreCliente(reservaServicios.id_cliente)}
                  {modalSoloLectura && (
                    <span className="ms-2 badge bg-secondary">Solo lectura</span>
                  )}
                </p>
              </div>
              <button
                type="button"
                className="btn btn-sm btn-light rounded-2"
                onClick={cerrarModalServicios}
              >
                <FaTimes size={13} />
              </button>
            </div>

            {errorServicios && (
              <div className="alert alert-danger py-2 mt-3">{errorServicios}</div>
            )}

            {/* Lista de servicios YA guardados para esta reserva */}
            <div className="mt-4">
              <h6 className="fw-semibold small text-muted mb-2">Servicios agregados</h6>

              {cargandoServicios ? (
                <p className="text-muted small">Cargando...</p>
              ) : listaServicios.length === 0 ? (
                <p className="text-muted small">Aún no hay servicios agregados a esta reserva.</p>
              ) : (
                <>
                  {listaServicios.map((s) => (
                    <div
                      key={s.id_servicio_adicional}
                      className="d-flex align-items-center justify-content-between border-bottom py-2"
                    >
                      <div>
                        <div className="fw-semibold small">
                          {s.nombre_servicio_adicional}
                          {/* badge de estado SIEMPRE visible. En reservas
                              Completada/Cancelada esta es la UNICA info
                              de estado que queda, porque abajo se ocultan
                              los botones de editar/eliminar del servicio
                              (modo solo lectura) */}
                          <span
                            className="badge ms-2"
                            style={{
                              fontSize: 10,
                              backgroundColor: s.estado === "Activo" ? "#d1f5e0" : "#e5e5e5",
                              color: s.estado === "Activo" ? "#0f7a45" : "#555",
                            }}
                          >
                            {s.estado}
                          </span>
                        </div>
                        {s.descripcion && (
                          <div className="text-muted small">{s.descripcion}</div>
                        )}
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <span className="fw-semibold small">
                          S/ {Number(s.precio).toFixed(2)}
                        </span>
                        {/* editar/eliminar servicio solo si la reserva
                            NO esta en modo solo-lectura */}
                        {!modalSoloLectura && (
                          <>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                              title="Editar"
                              onClick={() => empezarEdicionServicio(s)}
                            >
                              <FaPen size={12} />
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm rounded-2"
                              style={{ backgroundColor: "#e0466f", color: "white" }}
                              title="Eliminar"
                              onClick={() => eliminarServicio(s)}
                            >
                              <FaTrash size={12} />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}

                  <div className="d-flex justify-content-between align-items-center mt-3 fw-bold">
                    <span>Total servicios</span>
                    <span>S/ {Number(totalServicios).toFixed(2)}</span>
                  </div>
                </>
              )}
            </div>

            {/* formulario de agregar/editar servicio: se oculta entero
                en modo solo-lectura, no tiene sentido mostrarlo si de
                todas formas no se puede guardar nada nuevo */}
            {!modalSoloLectura && (
              <form onSubmit={guardarServicio} className="mt-4 pt-3 border-top">
                <h6 className="fw-semibold small text-muted mb-3">
                  {editandoServicioId ? "Editar servicio" : "Agregar servicio"}
                </h6>

                <div className="row g-2">
                  <div className="col-12">
                    <input
                      type="text"
                      className="form-control form-control-sm rounded-2"
                      placeholder="Nombre (ej. Show infantil)"
                      value={formularioServicio.nombre_servicio_adicional}
                      onChange={cambiarCampoServicio("nombre_servicio_adicional")}
                      required
                    />
                  </div>
                  <div className="col-12">
                    <input
                      type="text"
                      className="form-control form-control-sm rounded-2"
                      placeholder="Descripción"
                      value={formularioServicio.descripcion}
                      onChange={cambiarCampoServicio("descripcion")}
                      required
                    />
                  </div>

                  <div className="col-12 col-sm-4">
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      className="form-control form-control-sm rounded-2"
                      placeholder="Precio"
                      value={formularioServicio.precio}
                      onChange={cambiarCampoServicio("precio")}
                      required
                    />
                  </div>

                  {/* Estado ahora se ve SIEMPRE, no solo editando.
                      Es un boton (no select): cada click alterna entre
                      Activo/Inactivo via alternarEstadoServicio.
                      OJO: al CREAR (POST) el backend igual ignora este
                      valor y pone "Activo" por defecto sin importar lo
                      que se muestre aca -- solo se manda de verdad
                      cuando se esta editando (PUT), ver guardarServicio */}
                  <div className="col-12 col-sm-4">
                    <button
                      type="button"
                      className="btn btn-sm w-100 rounded-2 fw-semibold"
                      style={{
                        backgroundColor: formularioServicio.estado === "Activo" ? "#d1f5e0" : "#e5e5e5",
                        color: formularioServicio.estado === "Activo" ? "#0f7a45" : "#555",
                      }}
                      onClick={alternarEstadoServicio}
                    >
                      {formularioServicio.estado}
                    </button>
                  </div>

                  <div className="col-12 col-sm-4">
                    <button
                      type="submit"
                      className="btn btn-sm w-100 rounded-2 text-white fw-semibold"
                      style={{ backgroundColor: "#7c3aed" }}
                      disabled={guardandoServicio}
                    >
                      {guardandoServicio
                        ? "Guardando..."
                        : editandoServicioId
                        ? "Guardar cambios"
                        : "Agregar"}
                    </button>
                  </div>

                  {/* boton para salir del modo edicion sin guardar nada */}
                  {editandoServicioId && (
                    <div className="col-12">
                      <button
                        type="button"
                        className="btn btn-sm btn-light w-100 rounded-2"
                        onClick={cancelarEdicionServicio}
                        disabled={guardandoServicio}
                      >
                        Cancelar edición
                      </button>
                    </div>
                  )}
                </div>
              </form>
            )}

            <div className="d-flex justify-content-end mt-4">
              <button
                type="button"
                className="btn btn-light rounded-3 px-4 py-2"
                onClick={cerrarModalServicios}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reservas;