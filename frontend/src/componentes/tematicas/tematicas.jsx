// componentes/tematicas.jsx
import { useEffect, useState } from "react";
import { FaSearch, FaPen, FaTrash, FaPlus, FaCheck, FaChevronLeft, FaChevronRight, FaImage } from "react-icons/fa";
import api from ".. /api/axios";

// ────────────────────────────────────────────────
// CATALOGO DE IMAGENES PREDETERMINADAS
// ────────────────────────────────────────────────
const CARPETA_IMAGENES = "/images/tematicas/";
const CATALOGO_IMAGENES = [
  { id: "princesas.jpg", nombre: "Princesas" },
  { id: "futbol.jpg", nombre: "Futbol" },
  { id: "superheroes.jpg", nombre: "Superheroes" },
  { id: "ositos.jpg", nombre: "Ositos" },
  { id: "dinosaurios.jpg", nombre: "Dinosaurios" },
  { id: "piratas.jpg", nombre: "Piratas" },
  { id: "cumpleanos.jpg", nombre: "Cumpleaños" },
  { id: "espacio.jpg", nombre: "Espacio" },
  { id: "animales.jpg", nombre: "Animales" },
];

const FORMULARIO_VACIO = { descripcion: "", precio_base: "", imagen_url: "", estado: "Disponible" };
const TEMATICAS_POR_PAGINA = 4;

function Tematicas() {
  const [tematicas, setTematicas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [vista, setVista] = useState("lista"); // "lista" | "formulario"
  const [idEditando, setIdEditando] = useState(null); // null => estamos creando
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);

  const [imagenesConError, setImagenesConError] = useState([]);
  const marcarImagenConError = (nombreImagen) =>
    setImagenesConError((lista) =>
      lista.includes(nombreImagen) ? lista : [...lista, nombreImagen]
    );

  const cargarTematicas = () => {
    api
      .get("/tematicas")
      .then((res) => setTematicas(res.data))
      .catch(() => setError("No se pudo cargar la lista de tematicas."))
      .finally(() => setCargando(false));
  };

  useEffect(() => {
    cargarTematicas();
  }, []);

  const textoBusqueda = busqueda.trim().toLowerCase();
  const tematicasFiltradas = tematicas.filter((t) =>
    `${t.descripcion} ${t.estado}`.toLowerCase().includes(textoBusqueda)
  );

  const totalPaginas = Math.max(1, Math.ceil(tematicasFiltradas.length / TEMATICAS_POR_PAGINA));
  const paginaSegura = Math.min(pagina, totalPaginas);
  const inicio = (paginaSegura - 1) * TEMATICAS_POR_PAGINA;
  const tematicasPagina = tematicasFiltradas.slice(inicio, inicio + TEMATICAS_POR_PAGINA);

  const cambiarBusqueda = (e) => {
    setBusqueda(e.target.value);
    setPagina(1);
  };

  const abrirNuevaTematica = () => {
    setIdEditando(null);
    setFormulario(FORMULARIO_VACIO);
    setErrorFormulario("");
    setVista("formulario");
  };

  const abrirEdicionTematica = (tematica) => {
    setIdEditando(tematica.id_tematica);
    setFormulario({
      descripcion: tematica.descripcion,
      precio_base: tematica.precio_base,
      imagen_url: tematica.imagen_url || "",
      estado: tematica.estado,
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

  const seleccionarImagen = (idImagen) => {
    setFormulario((f) => ({
      ...f,
      imagen_url: f.imagen_url === idImagen ? "" : idImagen,
    }));
  };

  const guardarTematica = (e) => {
    e.preventDefault();
    setGuardando(true);
    setErrorFormulario("");

    const datosBase = {
      descripcion: formulario.descripcion,
      precio_base: Number(formulario.precio_base),
      imagen_url: formulario.imagen_url || null,
    };

    const peticion = idEditando
      ? api.put(`/tematicas/${idEditando}`, { ...datosBase, estado: formulario.estado })
      : api.post("/tematicas", datosBase);

    peticion
      .then(() => {
        cargarTematicas();
        cancelarFormulario();
      })
      .catch((err) => {
        const detalle = err.response?.data?.detail;
        setErrorFormulario(detalle || "No se pudo guardar la tematica. Revisa los datos.");
      })
      .finally(() => setGuardando(false));
  };

  const eliminarTematica = (tematica) => {
    if (!window.confirm(`¿Eliminar la tematica "${tematica.descripcion}"?`)) return;
    api
      .delete(`/tematicas/${tematica.id_tematica}`)
      .then(() => cargarTematicas())
      .catch((err) => {
        const detalle = err.response?.data?.detail;
        alert(detalle || "No se pudo eliminar la tematica.");
      });
  };

  // ──────────────────
  // VISTA: FORMULARIO 
  // ──────────────────
  if (vista === "formulario") {
    return (
      <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1200 }}>
        <h2 className="fw-bold mb-1">Tematicas</h2>
        <p className="text-muted mb-4">
          {idEditando ? "Edita los datos de la tematica" : "Completa los datos de la tematica"}
        </p>

        <form onSubmit={guardarTematica}>
          {errorFormulario && (
            <div className="alert alert-danger py-2">{errorFormulario}</div>
          )}

          <div className="row g-4">
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Descripcion</label>
              <input
                type="text"
                className="form-control rounded-3 py-2"
                placeholder="Ingrese descripcion de la tematica"
                value={formulario.descripcion}
                onChange={cambiarCampo("descripcion")}
                required
              />
            </div>
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Precio Base</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-control rounded-3 py-2"
                placeholder="0.00"
                value={formulario.precio_base}
                onChange={cambiarCampo("precio_base")}
                required
              />
            </div>

            {idEditando && (
              <div className="col-12 col-md-6">
                <label className="form-label fw-semibold">Estado</label>
                <select
                  className="form-select rounded-3 py-2"
                  value={formulario.estado}
                  onChange={cambiarCampo("estado")}
                >
                  <option value="Disponible">Disponible</option>
                  <option value="No Disponible">No Disponible</option>
                </select>
              </div>
            )}
          </div>

          {/* ──────────────────────────────────────
              SELECCION DE IMAGEN (catalogo predefinido)
              ────────────────────────────────────── */}
          <div className="mt-4">
            <label className="form-label fw-semibold d-block">Imagen de la tematica</label>
            <p className="text-muted small mb-3">
              Elige una imagen del catalogo. Si no seleccionas ninguna, se usara una imagen por defecto.
            </p>

            <div className="row g-3">
              {CATALOGO_IMAGENES.map((img) => {
                const seleccionada = formulario.imagen_url === img.id;
                return (
                  <div className="col-6 col-sm-4 col-md-3 col-lg-2" key={img.id}>
                    <button
                      type="button"
                      onClick={() => seleccionarImagen(img.id)}
                      className="btn p-0 w-100 rounded-3 overflow-hidden position-relative text-start"
                      style={{
                        border: seleccionada ? "3px solid #7c3aed" : "1px solid #e0e0e0",
                        boxShadow: seleccionada ? "0 0 0 3px rgba(124,58,237,0.15)" : "none",
                      }}
                      title={img.nombre}
                    >
                      {imagenesConError.includes(img.id) ? (
                        <div
                          className="w-100 d-flex align-items-center justify-content-center text-muted"
                          style={{ height: 80, backgroundColor: "#f1f1f4" }}
                        >
                          <FaImage size={22} />
                        </div>
                      ) : (
                        <img
                          src={`${CARPETA_IMAGENES}${img.id}`}
                          alt={img.nombre}
                          className="w-100"
                          style={{ height: 80, objectFit: "cover", backgroundColor: "#f1f1f4" }}
                          onError={() => marcarImagenConError(img.id)}
                        />
                      )}
                      <div className="px-2 py-2 small fw-semibold text-truncate" style={{ backgroundColor: "white" }}>
                        {img.nombre}
                      </div>

                      {seleccionada && (
                        <span
                          className="position-absolute d-flex align-items-center justify-content-center rounded-circle text-white"
                          style={{ top: 6, right: 6, width: 22, height: 22, backgroundColor: "#7c3aed" }}
                        >
                          <FaCheck size={11} />
                        </span>
                      )}
                    </button>
                  </div>
                );
              })}
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
              {guardando ? "Guardando..." : "Guardar Tematica"}
            </button>
          </div>
        </form>
      </div>
    );
  }

  // ────────────────────────────────────────────────
  // VISTA: LISTA (tarjetas)
  // ────────────────────────────────────────────────
  return (
    <div className="container-fluid mt-4 px-4 pb-4" style={{ maxWidth: 1200 }}>
      <div className="d-flex align-items-start justify-content-between mb-1">
        <div>
          <h2 className="fw-bold mb-1">Tematicas</h2>
          <p className="text-muted mb-0">Lista de Tematicas disponibles</p>
        </div>
        <button
          type="button"
          className="btn rounded-3 px-3 py-2 text-white fw-semibold d-flex align-items-center gap-2"
          style={{ backgroundColor: "#7c3aed" }}
          onClick={abrirNuevaTematica}
        >
          <FaPlus size={14} /> Nuevo Tematica
        </button>
      </div>

      <div className="position-relative mt-4 mb-4" style={{ maxWidth: 420 }}>
        <input
          type="text"
          className="form-control rounded-3 py-2 ps-3 pe-5"
          placeholder="Buscar tematica..."
          value={busqueda}
          onChange={cambiarBusqueda}
        />
        <FaSearch className="position-absolute text-muted" style={{ right: 16, top: "50%", transform: "translateY(-50%)" }} />
      </div>

      {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}

      {cargando ? (
        <p className="text-muted mb-0">Cargando...</p>
      ) : tematicasFiltradas.length === 0 ? (
        <p className="text-muted mb-0">
          {textoBusqueda ? "No se encontraron tematicas." : "Aún no hay tematicas registradas."}
        </p>
      ) : (
        <>
        <div className="row g-4">
          {tematicasPagina.map((t) => (
            <div className="col-12 col-sm-6 col-lg-3" key={t.id_tematica}>
              <div className="card h-100 border-0 shadow-sm rounded-4 overflow-hidden">
                {imagenesConError.includes(t.imagen_url || "default.jpg") ? (
                  <div
                    className="w-100 d-flex align-items-center justify-content-center text-muted"
                    style={{ height: 160, backgroundColor: "#f1f1f4" }}
                  >
                    <FaImage size={32} />
                  </div>
                ) : (
                  <img
                    src={t.imagen_url ? `${CARPETA_IMAGENES}${t.imagen_url}` : `${CARPETA_IMAGENES}default.jpg`}
                    alt={t.descripcion}
                    className="w-100"
                    style={{ height: 160, objectFit: "cover", backgroundColor: "#f1f1f4" }}
                    onError={() => marcarImagenConError(t.imagen_url || "default.jpg")}
                  />
                )}

                <div className="card-body d-flex flex-column">
                  <h5 className="fw-bold mb-1">{t.descripcion}</h5>
                  <p className="text-muted small mb-0">Desde</p>
                  <p className="fw-bold mb-3">S/ {Number(t.precio_base).toFixed(2)}</p>

                  <div className="d-flex align-items-center justify-content-between mt-auto">
                    <span className="d-flex align-items-center gap-2 fw-semibold small">
                      <span
                        className="rounded-circle"
                        style={{
                          width: 8,
                          height: 8,
                          display: "inline-block",
                          backgroundColor: t.estado === "Disponible" ? "#22c55e" : "#adb5bd",
                        }}
                      />
                      {t.estado === "Disponible" ? "Activo" : "Desactivado"}
                    </span>

                    <div className="d-flex gap-2">
                      <button
                        type="button"
                        className="btn btn-sm rounded-2"
                        style={{ backgroundColor: "#f6c343", color: "#1a1a1a" }}
                        title="Editar"
                        onClick={() => abrirEdicionTematica(t)}
                      >
                        <FaPen size={13} />
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm rounded-2"
                        style={{ backgroundColor: "#e0466f", color: "white" }}
                        title="Eliminar"
                        onClick={() => eliminarTematica(t)}
                      >
                        <FaTrash size={13} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {totalPaginas > 1 && (
          <div className="d-flex justify-content-center align-items-center gap-2 mt-4">
            <button
              type="button"
              className="btn btn-light rounded-3"
              disabled={paginaSegura === 1}
              onClick={() => setPagina(paginaSegura - 1)}
            >
              <FaChevronLeft size={12} />
            </button>

            {Array.from({ length: totalPaginas }, (_, i) => i + 1).map((num) => (
              <button
                key={num}
                type="button"
                className="btn rounded-3"
                style={
                  num === paginaSegura
                    ? { backgroundColor: "#7c3aed", color: "white" }
                    : { backgroundColor: "white", color: "#1a1a1a" }
                }
                onClick={() => setPagina(num)}
              >
                {num}
              </button>
            ))}

            <button
              type="button"
              className="btn btn-light rounded-3"
              disabled={paginaSegura === totalPaginas}
              onClick={() => setPagina(paginaSegura + 1)}
            >
              <FaChevronRight size={12} />
            </button>
          </div>
        )}
        </>
      )}
    </div>
  );
}

export default Tematicas;