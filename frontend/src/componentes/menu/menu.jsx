import "./menu.css";
import { NavLink } from "react-router-dom";
import { useState } from "react";
import {
  FaHome,
  FaUsers,
  FaCalendarCheck,
  FaPalette,
  FaCreditCard,
  FaFileInvoiceDollar,
} from "react-icons/fa";
import logo from "../../assets/imagenes/logo.png";
import logoTexto from "../../assets/imagenes/txt_logo.png";


const OPCIONES_MENU = [
  { ruta: "/inicio", icono: <FaHome size={20} />, texto: "Inicio" },
  { ruta: "/clientes", icono: <FaUsers size={20} />, texto: "Clientes" },
  { ruta: "/tematicas", icono: <FaPalette size={20} />, texto: "Tematicas" },
  { ruta: "/reservas", icono: <FaCalendarCheck size={20} />, texto: "Reserva" },
  { ruta: "/pagos", icono: <FaCreditCard size={20} />, texto: "Pagos" },
  { ruta: "/cuotas", icono: <FaFileInvoiceDollar size={20} />, texto: "Cuotas" },
];

function Menu() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`eventix-menu d-flex flex-column p-3 text-white ${collapsed ? "collapsed" : ""}`}>
      
      {/* Cabecera: Logo y botón */}
      <div className="d-flex align-items-center mb-4 mt-2">
        <button
          className="btn btn-link p-0 me-2"
          onClick={() => setCollapsed(!collapsed)}
          aria-label="Alternar barra lateral"
        >
          <img src={logo} alt="Eventix" height="34" />
        </button>
        <img src={logoTexto} alt="Eventix" height="60" className="hide-on-collapse" />
      </div>

          {/* <li>
              <NavLink to="/login" className="nav-link d-flex align-items-center px-3">
                <FaHome size={20} />
                <span className="ms-3 hide-on-collapse">Login</span>
              </NavLink>
          </li> */}
        
      <ul className="nav nav-pills flex-column mb-auto gap-2">
        {OPCIONES_MENU.map((opcion) => (
          <li key={opcion.ruta}>
            <NavLink to={opcion.ruta} className="nav-link d-flex align-items-center px-3">
              {opcion.icono}
              <span className="ms-3 hide-on-collapse">{opcion.texto}</span>
            </NavLink>
          </li>
        ))}
      </ul>

    </div>
  );
}

export default Menu;