// componentes/tematicas.jsx
import { useEffect, useState } from "react";
import { FaSearch, FaPen, FaTrash, FaPlus, FaChevronLeft, FaChevronRight, FaImage } from "react-icons/fa";
import api from "../api/axios";

// ────────────────────────────────────────────────
// DETECCION DE IMAGEN POR PALABRAS CLAVE
// La imagen NO se guarda en la base de datos: se calcula en el
// frontend a partir del texto de la descripcion, cada vez que se
// muestra. Cada entrada define palabras clave (en minusculas, sin
// tildes) que, si aparecen en la descripcion, seleccionan ese
// archivo. Se evalua en orden y se usa la primera coincidencia.
// ────────────────────────────────────────────────
const CARPETA_IMAGENES = "/imagenes-tematica/";
const IMAGEN_POR_DEFECTO = "default.png";

const MAPA_PALABRAS_CLAVE = [
  { palabras: ["princesa"], archivo: "princesas.png" },
  { palabras: ["futbol"], archivo: "futbol.png" },
  { palabras: ["heroe", "superheroe"], archivo: "superheroes.png" },
  { palabras: ["dinosaurio"], archivo: "dinosaurios.png" },
  { palabras: ["pirata"], archivo: "piratas.png" },
  { palabras: ["espacio", "astronauta", "galaxia"], archivo: "espacio.png" },
  { palabras: ["globo", "cumple"], archivo: "globos.png" },
  { palabras: ["construccion"], archivo: "construccion.png" },
  { palabras: ["unicornio"], archivo: "unicornios.png" },
  { palabras: ["hada"], archivo: "hadas.png" },
  { palabras: ["robot"], archivo: "robots.png" },
  { palabras: ["safari", "animal", "selva"], archivo: "safari.png" },
  { palabras: ["oceano", "mar", "sirena"], archivo: "oceano.png" },
  { palabras: ["ninja"], archivo: "ninjas.png" },
  { palabras: ["circo"], archivo: "circo.png" },
  { palabras: ["granja"], archivo: "granja.png" },
  { palabras: ["jardin", "flores"], archivo: "jardin.png" },
  { palabras: ["mariposa"], archivo: "mariposas.png" },
  { palabras: ["arte", "pintura"], archivo: "arte.png" },
  { palabras: ["auto", "carro", "carrera"], archivo: "autos.png" },
  { palabras: ["bombero"], archivo: "bomberos.png" },
  { palabras: ["camping", "acampar"], archivo: "camping.png" },
  { palabras: ["cocina", "chef"], archivo: "cocina.png" },
  { palabras: ["estrella"], archivo: "estrellas.png" },
  { palabras: ["magia", "mago"], archivo: "magia.png" },
  { palabras: ["medico", "doctor"], archivo: "medicos.png" },
  { palabras: ["musica"], archivo: "musica.png" },
  { palabras: ["policia"], archivo: "policia.png" },
  { palabras: ["arcoiris"], archivo: "arcoiris.png" },
  { palabras: ["vaquero"], archivo: "vaqueros.png" },
  { palabras: ["baby"], archivo: "baby_shower.png" },
  { palabras: ["aniversario"], archivo: "aniversario romantico.png" },
  { palabras: ["guerreras"], archivo: "guerreras k'pop.png" },
  { palabras: ["oso"], archivo: "oso.png" },
  { palabras: ["holloween"], archivo: "Fiesta de Halloween infantil.png" },
  { palabras: ["15 años"], archivo: "15 años elegante.png" },
  { palabras: ["el hombre arana"], archivo: "el hombre arana.png" },
  { palabras: ["fiesta de graduacion universitaria"], archivo: "fiesta de graduacion universitaria.png" },
  ];


// Quita tildes para que "heroe" tambien coincida con "héroe", etc.
const normalizar = (texto) =>
  texto
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

const obtenerImagenSegunDescripcion = (descripcion) => {
  const texto = normalizar(descripcion || "");
  for (const entrada of MAPA_PALABRAS_CLAVE) {
    if (entrada.palabras.some((palabra) => texto.includes(palabra))) {
      return entrada.archivo;
    }
  }
  return null; // sin coincidencia => se usara la imagen por defecto
};

const PRECIO_MAXIMO = 50000;

const FORMULARIO_VACIO = { descripcion: "", precio_base: "", estado: "Disponible" };
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

  const guardarTematica = (e) => {
    e.preventDefault();
    setErrorFormulario("");

    const precioNumero = Number(formulario.precio_base);

    if (!formulario.precio_base || Number.isNaN(precioNumero) || precioNumero <= 0) {
      setErrorFormulario("Ingresa un precio base valido.");
      return;
    }
    if (precioNumero > PRECIO_MAXIMO) {
      setErrorFormulario(`El precio base no puede superar S/ ${PRECIO_MAXIMO.toLocaleString("es-PE")}.`);
      return;
    }

    setGuardando(true);

    const datosBase = {
      descripcion: formulario.descripcion,
      precio_base: precioNumero,
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
              <textarea
                className="form-control rounded-3 py-2"
                placeholder="Ingrese descripcion de la tematica"
                rows={4}
                maxLength={300}
                value={formulario.descripcion}
                onChange={cambiarCampo("descripcion")}
                required
              />
              <p className="text-muted small mt-1 mb-0">
                {formulario.descripcion.length}/300 caracteres. La imagen se elige sola segun
                palabras como "princesa", "futbol", "heroe", "oso", "cumple" o "espacio".
              </p>
            </div>
            <div className="col-12 col-md-6">
              <label className="form-label fw-semibold">Precio Base</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max={PRECIO_MAXIMO}
                className="form-control rounded-3 py-2"
                placeholder="0.00"
                value={formulario.precio_base}
                onChange={cambiarCampo("precio_base")}
                required
              />
              <p className="text-muted small mt-1 mb-0">
                Entre S/ 0.01 y S/ {PRECIO_MAXIMO.toLocaleString("es-PE")}.00
              </p>
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
          {tematicasPagina.map((t) => {
            const archivoImagen = obtenerImagenSegunDescripcion(t.descripcion) || IMAGEN_POR_DEFECTO;
            return (
            <div className="col-12 col-sm-6 col-lg-3" key={t.id_tematica}>
              <div className="card h-100 border-0 shadow-sm rounded-4 overflow-hidden">
                {imagenesConError.includes(archivoImagen) ? (
                  <div
                    className="w-100 d-flex align-items-center justify-content-center text-muted"
                    style={{ height: 160, backgroundColor: "#f1f1f4" }}
                  >
                    <FaImage size={32} />
                  </div>
                ) : (
                  <img
                    src={`${CARPETA_IMAGENES}${archivoImagen}`}
                    alt={t.descripcion}
                    className="w-100"
                    style={{ height: 160, objectFit: "cover", backgroundColor: "#f1f1f4" }}
                    onError={() => marcarImagenConError(archivoImagen)}
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
            );
          })}
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