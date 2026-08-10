import axios from "axios";

// La URL del backend viene de la variable de entorno VITE_API_URL,
// definida en el archivo .env (ver .env.example). Si no está definida,
// usa http://localhost:8000 como valor de respaldo para desarrollo local.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export default api;