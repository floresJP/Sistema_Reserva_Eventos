import axios from "axios";

// Cambia esta URL si tu backend corre en otro host/puerto.
// (uvicorn api:app --reload, dentro de la carpeta backend/)
const api = axios.create({
baseURL: "http://localhost:8000",
});

export default api;
