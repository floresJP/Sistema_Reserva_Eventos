import Menu from './componentes/menu/menu';
import Panel from './componentes/panel/panel';
import Clientes from "./componentes/clientes/clientes";
import Reservas from "./componentes/reservas/reservas";
import Tematicas from "./componentes/tematicas/tematicas";
import Pagos from "./componentes/pagos/pagos";
import Cuotas from "./componentes/cuotas/cuotas";
import { Routes, Route, Navigate} from 'react-router-dom';

function App() {
  return (
    <div className="d-flex">
      <Menu />
      <main className="flex-grow-1">
        <Routes>
          <Route path="/" element={<Navigate to="/inicio" replace />} /> 
          <Route path="/inicio" element={<Panel />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/reservas" element={<Reservas />} />
          <Route path="/tematicas" element={<Tematicas />} />
          <Route path="/pagos" element={<Pagos />} />
          <Route path="/cuotas" element={<Cuotas />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;