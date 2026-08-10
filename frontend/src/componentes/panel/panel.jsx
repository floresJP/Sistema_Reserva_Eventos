// componentes/panel.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaUsers, FaCalendarCheck, FaRegCreditCard, FaFileInvoiceDollar,
  FaCrown, FaFutbol, FaCog, FaMagic, FaSearch, FaChevronLeft, FaChevronRight,
} from "react-icons/fa";
import api from "../api/axios";

// Icono + color que rota para cada fila de "Proximas Reservas"
const ICONOS_RESERVA = [
  { icono: <FaCrown />, color: "#e91e8c" },
  { icono: <FaFutbol />, color: "#22a559" },
  { icono: <FaCog />, color: "#7c3aed" },
  { icono: <FaMagic />, color: "#e91e8c" },
];

// Traduce el "estado" que viene del backend a texto + color del badge
const ESTILO_ESTADO = {
  Confirmada:  { texto: "Confirmado", bg: "#e3f8ea", color: "#22a559" },
  Pendiente:   { texto: "Pendiente",  bg: "#fdf1de", color: "#e08a1e" },
  Completada:  { texto: "Completado", bg: "#e3f8ea", color: "#22a559" },
  Cancelada:   { texto: "Cancelado",  bg: "#fde3ea", color: "#e0466f" },
};

const DIAS_SEMANA = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
const MESES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

// Arma una matriz de semanas para pintar el calendario del mes dado
function generarMatrizCalendario(anio, mes) {
  const primerDia = new Date(anio, mes, 1).getDay();
  const totalDias = new Date(anio, mes + 1, 0).getDate();
  const celdas = [];
  for (let i = 0; i < primerDia; i++) celdas.push(null);   // relleno antes del dia 1
  for (let dia = 1; dia <= totalDias; dia++) celdas.push(dia);
  while (celdas.length % 7 !== 0) celdas.push(null);        // relleno al final
  const semanas = [];
  for (let i = 0; i < celdas.length; i += 7) semanas.push(celdas.slice(i, i + 7));
  return semanas;
}

// Circulo de color con un icono adentro (se reutiliza en tarjetas y filas)
function IconoCirculo({ icono, bg, color, size = 42 }) {
  return (
    <div
      className="d-flex align-items-center justify-content-center rounded-3 flex-shrink-0"
      style={{ width: size, height: size, backgroundColor: bg, color, fontSize: size * 0.42 }}
    >
      {icono}
    </div>
  );
}

function Panel() {
  const hoy = new Date();
  const navigate = useNavigate();
  const [clientes, setClientes] = useState([]);
  const [tematicas, setTematicas] = useState([]);
  const [reservas, setReservas] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [cuotas, setCuotas] = useState([]);
  const [cargando, setCargando] = useState(true);

  const [mesCalendario, setMesCalendario] = useState(hoy.getMonth());
  const [anioCalendario, setAnioCalendario] = useState(hoy.getFullYear());
  const [busqueda, setBusqueda] = useState("");

  const irMesAnterior = () => {
    if (mesCalendario === 0) {
      setMesCalendario(11);
      setAnioCalendario((a) => a - 1);
    } else {
      setMesCalendario((m) => m - 1);
    }
  };
  const irMesSiguiente = () => {
    if (mesCalendario === 11) {
      setMesCalendario(0);
      setAnioCalendario((a) => a + 1);
    } else {
      setMesCalendario((m) => m + 1);
    }
  };
  const irHoy = () => {
    setMesCalendario(hoy.getMonth());
    setAnioCalendario(hoy.getFullYear());
  };

  // Carga los 5 recursos en paralelo. allSettled evita que un solo
  // endpoint caido tumbe todo el panel (los demas igual se muestran).
  useEffect(() => {
    Promise.allSettled([
      api.get("/clientes"),
      api.get("/tematicas"),
      api.get("/reservas"),
      api.get("/pagos"),
      api.get("/cuotas"),
    ]).then(([resClientes, resTematicas, resReservas, resPagos, resCuotas]) => {
      setClientes(resClientes.status === "fulfilled" ? resClientes.value.data : []);
      setTematicas(resTematicas.status === "fulfilled" ? resTematicas.value.data : []);
      setReservas(resReservas.status === "fulfilled" ? resReservas.value.data : []);
      setPagos(resPagos.status === "fulfilled" ? resPagos.value.data : []);
      setCuotas(resCuotas.status === "fulfilled" ? resCuotas.value.data : []);
      setCargando(false);
    });
  }, []);

  // El backend solo guarda id_cliente/id_tematica en la reserva;
  // aqui se busca el nombre real para mostrarlo en pantalla.
  const nombreCliente = (id) => {
    const c = clientes.find((c) => c.id_cliente === id);
    return c ? `${c.nombre} ${c.apellido}` : id;
  };
  const nombreTematica = (id) => {
    const t = tematicas.find((t) => t.id_tematica === id);
    return t ? t.descripcion : id;
  };

  const esMismoMes = (fechaISO) => {
    const f = new Date(fechaISO + "T00:00:00");
    return f.getMonth() === hoy.getMonth() && f.getFullYear() === hoy.getFullYear();
  };

  // Metricas de las 4 tarjetas superiores
  const reservasEsteMes = reservas.filter((r) => esMismoMes(r.fecha_evento)).length;
  const pagosPendientes = pagos.filter((p) => p.estado_pago === "Pendiente").length;

  // Dinero REALMENTE cobrado este mes:
  // - pagos de 1 sola cuota que ya estan "Pagado" (se cobraron de una vez)
  // - + cada cuota individual ya marcada "Pagada" (para pagos con varias
  //   cuotas), usando la fecha_pago propia de esa cuota, no del pago padre
  const ingresosPagosUnicos = pagos
    .filter((p) => p.total_cuotas === 1 && p.estado_pago === "Pagado" && esMismoMes(p.fecha_pago))
    .reduce((suma, p) => suma + Number(p.monto_total), 0);

  const ingresosCuotasPagadas = cuotas
    .filter((c) => c.estado === "Pagada" && c.fecha_pago && esMismoMes(c.fecha_pago))
    .reduce((suma, c) => suma + Number(c.monto), 0);

  const ingresosEsteMes = ingresosPagosUnicos + ingresosCuotasPagadas;

  // Las 4 reservas mas cercanas a partir de hoy (futuras, ordenadas)
  const proximasReservas = [...reservas]
    .filter((r) => new Date(r.fecha_evento + "T00:00:00") >= new Date(hoy.toDateString()))
    .sort((a, b) => a.fecha_evento.localeCompare(b.fecha_evento))
    .slice(0, 4);

  // Buscador global: filtra clientes/tematicas/reservas por texto
  const textoBusqueda = busqueda.trim().toLowerCase();
  const buscando = textoBusqueda.length > 0;

  const resultadosClientes = buscando
    ? clientes.filter((c) =>
        `${c.nombre} ${c.apellido} ${c.dni} ${c.correo}`.toLowerCase().includes(textoBusqueda)
      ).slice(0, 5)
    : [];

  const resultadosTematicas = buscando
    ? tematicas.filter((t) => t.descripcion.toLowerCase().includes(textoBusqueda)).slice(0, 5)
    : [];

  const resultadosReservas = buscando
    ? reservas.filter((r) =>
        `${nombreCliente(r.id_cliente)} ${nombreTematica(r.id_tematica)} ${r.direccion}`
          .toLowerCase().includes(textoBusqueda)
      ).slice(0, 5)
    : [];

  const totalResultados = resultadosClientes.length + resultadosTematicas.length + resultadosReservas.length;

  // Datos del mini-calendario del mes visible
  const semanas = generarMatrizCalendario(anioCalendario, mesCalendario);
  const reservasPorDia = {};
  reservas.forEach((r) => {
    const f = new Date(r.fecha_evento + "T00:00:00");
    if (f.getMonth() === mesCalendario && f.getFullYear() === anioCalendario) {
      reservasPorDia[f.getDate()] = r.estado;
    }
  });

  const tarjetas = [
    { titulo: "Clientes", valor: clientes.length, sub: "Total Registrados", icono: <FaUsers />, bg: "#efe6fc", color: "#7c3aed" },
    { titulo: "Reservas", valor: reservasEsteMes, sub: "Este mes", icono: <FaCalendarCheck />, bg: "#e3f8ea", color: "#22a559" },
    { titulo: "Pagos pendientes", valor: pagosPendientes, sub: "Por cobrar", icono: <FaRegCreditCard />, bg: "#fdf1de", color: "#e08a1e" },
    { titulo: "Ingresos totales", valor: `S/ ${ingresosEsteMes.toLocaleString("es-PE")}`, sub: "Este mes", icono: <FaFileInvoiceDollar />, bg: "#e6eefc", color: "#3b6fe0" },
  ];

  return (
    <div className="container-fluid mt-4 px-4" style={{ maxWidth: 1200 }}>
      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h2 className="mb-0">Inicio</h2>
          <p className="text-muted mb-0">Datos del Inicio</p>
        </div>
        <div className="position-relative" style={{ maxWidth: 320, width: "100%" }}>
          <div className="input-group">
            <span className="input-group-text bg-white border-end-0"><FaSearch className="text-muted" /></span>
            <input
              type="text"
              className="form-control border-start-0"
              placeholder="Buscar en todo el sistema"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>

          {/* Panel flotante de resultados, solo visible mientras se escribe */}
          {buscando && (
            <div
              className="card shadow position-absolute w-100 mt-1 p-2"
              style={{ zIndex: 1000, maxHeight: 360, overflowY: "auto" }}
            >
              {totalResultados === 0 ? (
                <p className="text-muted small mb-0 p-2">Sin resultados para "{busqueda}".</p>
              ) : (
                <>
                  {resultadosClientes.length > 0 && (
                    <div className="mb-2">
                      <div className="text-muted small fw-semibold px-2">Clientes</div>
                      <div className="list-group list-group-flush">
                        {resultadosClientes.map((c) => (
                          <button
                            type="button"
                            key={c.id_cliente}
                            className="list-group-item list-group-item-action border-0 px-2 py-1 small"
                            onClick={() => { navigate("/clientes"); setBusqueda(""); }}
                          >
                            <span className="fw-semibold">{c.nombre} {c.apellido}</span>
                            <span className="text-muted"> — DNI {c.dni} — {c.correo}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {resultadosTematicas.length > 0 && (
                    <div className="mb-2">
                      <div className="text-muted small fw-semibold px-2">Temáticas</div>
                      <div className="list-group list-group-flush">
                        {resultadosTematicas.map((t) => (
                          <button
                            type="button"
                            key={t.id_tematica}
                            className="list-group-item list-group-item-action border-0 px-2 py-1 small"
                            onClick={() => { navigate("/tematicas"); setBusqueda(""); }}
                          >
                            <span className="fw-semibold">{t.descripcion}</span>
                            <span className="text-muted"> — S/ {t.precio_base}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {resultadosReservas.length > 0 && (
                    <div>
                      <div className="text-muted small fw-semibold px-2">Reservas</div>
                      <div className="list-group list-group-flush">
                        {resultadosReservas.map((r) => (
                          <button
                            type="button"
                            key={r.id_reserva}
                            className="list-group-item list-group-item-action border-0 px-2 py-1 small"
                            onClick={() => { navigate("/reservas"); setBusqueda(""); }}
                          >
                            <span className="fw-semibold">{nombreCliente(r.id_cliente)}</span>
                            <span className="text-muted"> — {nombreTematica(r.id_tematica)} — {r.fecha_evento}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 4 tarjetas de metricas */}
      <div className="row g-3 mb-4">
        {tarjetas.map((t) => (
          <div className="col-12 col-sm-6 col-lg-3" key={t.titulo}>
            <div className="card shadow-sm border-0 rounded-4 h-100 p-3">
              <div className="d-flex align-items-start">
                <IconoCirculo icono={t.icono} bg={t.bg} color={t.color} />
                <span className="ms-auto text-muted small">{t.titulo}</span>
              </div>
              <div className="fs-3 fw-bold mt-2">{t.valor}</div>
              <div className="text-muted small">{t.sub}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="row g-3">
        {/* Lista de proximas reservas */}
        <div className="col-12 col-lg-7">
          <div className="card shadow-sm border-0 rounded-4 h-100 p-3">
            <h5 className="mb-3">Proximas Reservas</h5>
            {cargando ? (
              <p className="text-muted">Cargando...</p>
            ) : proximasReservas.length === 0 ? (
              <p className="text-muted mb-0">
                Aún no hay reservas próximas (o el endpoint <code>/reservas</code> todavía no está conectado).
              </p>
            ) : (
              proximasReservas.map((r, i) => {
                const icono = ICONOS_RESERVA[i % ICONOS_RESERVA.length];
                const estado = ESTILO_ESTADO[r.estado] || ESTILO_ESTADO.Pendiente;
                const fecha = new Date(r.fecha_evento + "T00:00:00");
                return (
                  <div className="d-flex align-items-center py-2 border-bottom" key={r.id_reserva}>
                    <IconoCirculo icono={icono.icono} bg={`${icono.color}22`} color={icono.color} />
                    <div className="ms-3 flex-grow-1">
                      <div className="fw-semibold">{nombreCliente(r.id_cliente)}</div>
                      <div className="text-muted small">{nombreTematica(r.id_tematica)}</div>
                    </div>
                    <div className="text-end me-3 small text-muted" style={{ minWidth: 110 }}>
                      {fecha.toLocaleDateString("es-PE", { day: "2-digit", month: "short", year: "numeric" })}
                      <br />
                      {r.hora_inicio?.slice(0, 5)}
                    </div>
                    <span className="badge rounded-pill px-3 py-2 fw-semibold" style={{ backgroundColor: estado.bg, color: estado.color }}>
                      {estado.texto}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Mini calendario del mes */}
        <div className="col-12 col-lg-5">
          <div className="card shadow-sm border-0 rounded-4 h-100 p-3">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <button type="button" className="btn btn-sm btn-light" onClick={irMesAnterior} aria-label="Mes anterior">
                <FaChevronLeft />
              </button>
              <span className="fw-semibold" role="button" title="Volver a hoy" onClick={irHoy}>
                {MESES[mesCalendario]} {anioCalendario}
              </span>
              <button type="button" className="btn btn-sm btn-light" onClick={irMesSiguiente} aria-label="Mes siguiente">
                <FaChevronRight />
              </button>
            </div>
            <table className="table table-borderless mb-2" style={{ fontSize: "0.85rem" }}>
              <thead>
                <tr>
                  {DIAS_SEMANA.map((d) => <th key={d} className="text-muted small fw-normal text-center p-1">{d}</th>)}
                </tr>
              </thead>
              <tbody>
                {semanas.map((semana, i) => (
                  <tr key={i}>
                    {semana.map((dia, j) => {
                      const esHoy = dia === hoy.getDate() && mesCalendario === hoy.getMonth() && anioCalendario === hoy.getFullYear();
                      const estadoDia = dia ? reservasPorDia[dia] : null;
                      const colorEstado = estadoDia ? (ESTILO_ESTADO[estadoDia] || {}).color : null;
                      return (
                        <td key={j} className={`text-center p-1 ${esHoy ? "bg-dark text-white rounded-circle" : ""}`}
                            style={!esHoy && colorEstado ? { color: colorEstado, fontWeight: 600 } : undefined}>
                          {dia || ""}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="d-flex gap-3 small text-muted mt-2">
              <span><span className="d-inline-block rounded-circle me-1" style={{ width: 8, height: 8, backgroundColor: "#22a559" }} /> Confirmada</span>
              <span><span className="d-inline-block rounded-circle me-1" style={{ width: 8, height: 8, backgroundColor: "#e08a1e" }} /> Pendiente</span>
              <span><span className="d-inline-block rounded-circle me-1" style={{ width: 8, height: 8, backgroundColor: "#e0466f" }} /> Cancelada</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Panel;