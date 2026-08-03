// componentes/clientes.jsx
import { useEffect, useState } from "react";
import { FaSearch, FaPen, FaTrash, FaPlus } from "react-icons/fa";
import api from "../api/axios";

// Estado inicial del formulario (alta o edicion)
const FORMULARIO_VACIO = { nombre: "", apellido: "", dni: "", telefono: "", correo: "" };

function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [vista, setVista] = useState("lista"); // "lista" | "formulario"
  const [idEditando, setIdEditando] = useState(null); // null => estamos creando
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const [busqueda, setBusqueda] = useState("");

  const cargarClientes = () => {
    api
      .get("/clientes")
      .then((res) => setClientes(res.data))
      .catch(() => setError("No se pudo cargar la lista de clientes."))
      .finally(() => setCargando(false));
  };

  useEffect(() => {
    cargarClientes();
  }, []);

  // Filtra por nombre, apellido, dni o correo
  const textoBusqueda = busqueda.trim().toLowerCase();
  const clientesFiltrados = clientes.filter((c) =>
    `${c.nombre} ${c.apellido} ${c.dni} ${c.correo}`.toLowerCase().includes(textoBusqueda)
  );

  const abrirNuevoCliente = () => {
    setIdEditando(null);
    setFormulario(FORMULARIO_VACIO);
    setErrorFormulario("");
    setVista("formulario");
  };

  const abrirEdicionCliente = (cliente) => {
    setIdEditando(cliente.id_cliente);
    setFormulario({
      nombre: cliente.nombre,
      apellido: cliente.apellido,
      dni: cliente.dni,
      telefono: cliente.telefono,
      correo: cliente.correo,
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

  const guardarCliente = (e) => {
    e.preventDefault();
    setGuardando(true);
    setErrorFormulario("");

    const peticion = idEditando
      ? api.put(`/clientes/${idEditando}`, formulario)
      : api.post("/clientes", formulario);

    peticion
      .then(() => {
        cargarClientes();
        cancelarFormulario();
      })
      .catch((err) => {
        const detalle = err.response?.data?.detail;
        setErrorFormulario(detalle || "No se pudo guardar el cliente. Revisa los datos.");
      })
      .finally(() => setGuardando(false));
  };

  const eliminarCliente = (cliente) => {
    if (!window.confirm(`¿Eliminar a ${cliente.nombre} ${cliente.apellido}?`)) return;
    api
      .delete(`/clientes/${cliente.id_cliente}`)
      .then(() => cargarClientes())
      .catch((err) => {
        const detalle = err.response?.data?.detail;
        alert(detalle || "No se pudo eliminar el cliente.");
      });
  };

  // ────────────────────────────────────────────────
  // VISTA: FORMULARIO (alta / edicion)
  // ────────────────────────────────────────────────
  if (vista === "formulario") {
    return (
      <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1200 }}>
        <h2 className="fw-bold mb-1">Clientes</h2>
        <p className="text-muted mb-4">
          {idEditando ? "Edita los datos del cliente" : "Registra datos del cliente"}
        </p>

        <form onSubmit={guardarCliente}>
          {errorFormulario && (
            <div className="alert alert-danger py-2">{errorFormulario}</div>
          )}

          <div className="row g-4">
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Nombre</label>
              <input
                type="text"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese nombre"
                value={formulario.nombre}
                onChange={cambiarCampo("nombre")}
                required
              />
            </div>
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Telefono</label>
              <input
                type="text"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese telefono"
                value={formulario.telefono}
                onChange={cambiarCampo("telefono")}
                required
              />
            </div>

            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Apellido</label>
              <input
                type="text"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese apellido"
                value={formulario.apellido}
                onChange={cambiarCampo("apellido")}
                required
              />
            </div>
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Correo</label>
              <input
                type="email"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese correo"
                value={formulario.correo}
                onChange={cambiarCampo("correo")}
                required
              />
            </div>

            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">DNI</label>
              <input
                type="text"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese DNI"
                value={formulario.dni}
                onChange={cambiarCampo("dni")}
                required
              />
            </div>
          </div>

          <div className="d-flex justify-content-end gap-2 mt-5">
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
              {guardando ? "Guardando..." : "Guardar Cliente"}
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
          <h2 className="fw-bold mb-1">Clientes</h2>
          <p className="text-muted mb-0">Lista de clientes registrados</p>
        </div>
        <button
          type="button"
          className="btn rounded-3 px-3 py-2 text-white fw-semibold d-flex align-items-center gap-2"
          style={{ backgroundColor: "#7c3aed" }}
          onClick={abrirNuevoCliente}
        >
          <FaPlus size={14} /> Nuevo Cliente
        </button>
      </div>

      <div className="position-relative mt-4 mb-3" style={{ maxWidth: 420 }}>
        <input
          type="text"
          className="form-control rounded-3 py-2 ps-3 pe-5"
          placeholder="Buscar cliente..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <FaSearch className="position-absolute text-muted" style={{ right: 16, top: "50%", transform: "translateY(-50%)" }} />
      </div>

      <div className="card shadow-sm border-0 rounded-4 p-3">
        {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}

        {cargando ? (
          <p className="text-muted mb-0 p-3">Cargando...</p>
        ) : clientesFiltrados.length === 0 ? (
          <p className="text-muted mb-0 p-3">
            {textoBusqueda ? "No se encontraron clientes." : "Aún no hay clientes registrados."}
          </p>
        ) : (
          <div className="table-responsive">
            <table className="table align-middle mb-0">
              <thead>
                <tr className="text-muted small">
                  <th className="fw-semibold">ID</th>
                  <th className="fw-semibold">DNI</th>
                  <th className="fw-semibold">Nombre</th>
                  <th className="fw-semibold">Apellido</th>
                  <th className="fw-semibold">Telefono</th>
                  <th className="fw-semibold">Correo</th>
                  <th className="fw-semibold text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {clientesFiltrados.map((c) => (
                  <tr key={c.id_cliente}>
                    <td className="fw-semibold">{c.id_cliente}</td>
                    <td>{c.dni}</td>
                    <td>{c.nombre}</td>
                    <td>{c.apellido}</td>
                    <td>{c.telefono}</td>
                    <td>{c.correo}</td>
                    <td className="text-end">
                      <button
                        type="button"
                        className="btn btn-sm rounded-2 me-2"
                        style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                        title="Editar"
                        onClick={() => abrirEdicionCliente(c)}
                      >
                        <FaPen size={13} />
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm rounded-2"
                        style={{ backgroundColor: "#e0466f", color: "white" }}
                        title="Eliminar"
                        onClick={() => eliminarCliente(c)}
                      >
                        <FaTrash size={13} />
                      </button>
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

export default Clientes;