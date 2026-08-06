# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.base_datos import inicializar
from routers import cliente, tematica, reserva, servicio_adicional, pago, cuota

# ------------------------------------------------------------
# APLICACION FASTAPI - Sistema de Reserva de Eventos
# Genera documentacion automatica en /docs (Swagger UI) y /redoc.
# ------------------------------------------------------------

app = FastAPI(
    title="Sistema de Reserva de Eventos",
    version="1.0",
    description="API REST para gestion de clientes, tematicas, reservas, "
    "servicios adicionales, pagos y cuotas",
)

# ------------------------------------------------------------
# CORS: permite que React (localhost:5173,5174 o 3000) consuma esta API
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
                "http://localhost:5174", 
                "http://localhost:5173",
                "http://localhost:3000"
                ],
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas en PostgreSQL si no existen, al arrancar la aplicacion.
inicializar()

# Registra los endpoints de cada router.
# Ej: /clientes (prefix del router) + /{id_cliente} = GET /clientes/{id_cliente}
app.include_router(cliente.router)
app.include_router(tematica.router)
app.include_router(reserva.router)
app.include_router(servicio_adicional.router)
app.include_router(pago.router)
app.include_router(cuota.router)


# Endpoint raiz - health check para verificar que la API esta activa.
@app.get("/")
def inicio():
    return {
        "mensaje": "API Sistema de Reserva de Eventos",
        "version": "1.0",
        "docs": "/docs",
    }
    

# Documentación automática:

# Swagger UI: http://127.0.0.1:8000/docs

# ReDoc: http://127.0.0.1:8000/redoc