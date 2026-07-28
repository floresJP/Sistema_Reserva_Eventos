import Menu from './componentes/menu/menu';
import Panel from './componentes/panel/panel';
import Clientes from "./componentes/clientes/clientes";
import Reservas from "./componentes/reservas/reservas";
import Tematicas from "./componentes/tematicas/tematicas";
import Pagos from "./componentes/pagos/pagos";
import Cuotas from "./componentes/cuotas/cuotas";
import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <>
      <Menu />
      <Routes>

        <Route path="/inicio" element={<Panel />} />
        <Route path="/cliente" element={<Clientes />} />
        <Route path="/reserva" element={<Reservas />} />
        <Route path="/tematica" element={<Tematicas />} />
        <Route path="/pago" element={<Pagos />} />
        <Route path="/cuota" element={<Cuotas />} />

      </Routes>
    </>
  );
}

export default App;