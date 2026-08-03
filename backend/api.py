from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.base_datos import inicializar
from routers.cliente import router as cliente_router
from routers.tematica import router as tematica_router
from routers.reserva import router as reserva_router

app = FastAPI(
    title="Sistema de Reserva de Eventos — Eventix",
    description="API REST sobre el mismo PostgreSQL, DAO y validadores que usa la app de consola.",
    version="1.0",
)

# Sin esto, el navegador bloquea las peticiones que hace el frontend
# (localhost:5173) hacia el backend (localhost:8000), porque son
# puertos distintos y el navegador los trata como orígenes distintos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def crear_tablas():
    inicializar()

app.include_router(cliente_router)
app.include_router(tematica_router)
app.include_router(reserva_router)

@app.get("/", tags=["Salud"])
def salud():
    return {"estado": "ok", "sistema": "Eventix API"}