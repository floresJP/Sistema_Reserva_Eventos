# Sistema de Reserva de Eventos — Backend

API REST construida con **FastAPI** y **PostgreSQL** para gestionar clientes, temáticas, reservas, servicios adicionales, pagos y cuotas de una empresa de organización de eventos.

## Requisitos previos

- Python 3.11 o superior
- PostgreSQL 14 o superior (servidor corriendo localmente o accesible por red)
- pip

## 1. Clonar y ubicarse en el backend

```bash
git clone https://github.com/floresJP/Sistema_Reserva_Eventos.git
cd Sistema_Reserva_Eventos/backend
```

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si el proyecto todavía no incluye `requirements.txt`, instala manualmente:

```bash
pip install fastapi uvicorn[standard] psycopg2-binary pydantic python-dotenv
```

> **Nota:** estos pasos instalan las librerías directamente en tu instalación global de Python. Si más adelante quieres evitar conflictos con otros proyectos, se recomienda usar un entorno virtual (`python -m venv venv`), pero no es obligatorio para levantar este proyecto.

## 3. Crear la base de datos en PostgreSQL

Con `psql` o cualquier cliente (pgAdmin, DBeaver, etc.), crea la base de datos vacía:

```sql
CREATE DATABASE bd_sistema_reserva;
```

Las tablas (`cliente`, `tematica`, `reserva`, `servicio_adicional`, `pago`, `cuota`) **se crean automáticamente** al iniciar la aplicación (ver `config/base_datos.py`, función `inicializar()`), no es necesario ejecutar ningún script `.sql` a mano.

Si además quieres cargar los datos de prueba (10 clientes, 10 temáticas, reservas, pagos y cuotas de ejemplo), ejecuta el contenido de `script_postgre.md` (en la raíz del repo) sobre la base de datos ya creada:

```bash
psql -U postgres -d bd_sistema_reserva -f script_postgre.md
```

## 4. Configurar variables de entorno

El código en `config/base_datos.py` necesita las credenciales de la base de datos (host, puerto, nombre, usuario, contraseña), pero no las tiene escritas directamente — las busca en variables de entorno con `os.getenv(...)`.

**Qué hacer:**

1. Copia el archivo `.env.example` (incluido en `backend/`) y renómbralo a `.env`, en la misma carpeta `backend/`.
2. Complétalo con tus propios valores reales, por ejemplo:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bd_sistema_reserva
DB_USER=postgres
DB_PASSWORD=tu_password_de_postgres
```

`DB_NAME` debe coincidir con el nombre real de la base que creaste en el paso 3 (`bd_sistema_reserva`), no con el nombre de la carpeta del proyecto.

3. Instala `python-dotenv` (si no está en `requirements.txt`):

```bash
pip install python-dotenv
```

4. Verifica que `main.py` cargue el `.env` al inicio, **antes** de cualquier import que use `config/base_datos.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

El `.env` es personal de cada máquina (cada integrante del equipo pone su propia contraseña de PostgreSQL) y **nunca se sube al repositorio** — está listado en `.gitignore`. Solo se comparte `.env.example`, que no tiene datos reales.

## 5. Levantar el servidor

```bash
uvicorn main:app --reload
```

Por defecto queda disponible en `http://127.0.0.1:8000`.

## 6. Documentación interactiva

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: `GET http://127.0.0.1:8000/`

## 7. CORS

El backend permite peticiones desde el frontend en:

- `http://localhost:5173`
- `http://localhost:5174`
- `http://localhost:3000`

Si tu frontend corre en otro puerto, agrégalo en `allow_origins` dentro de `main.py`.

## Estructura del proyecto

```
backend/
├── main.py                  # Punto de entrada de la app FastAPI
├── config/
│   ├── base_datos.py        # Conexión a PostgreSQL y creación de tablas
│   ├── logger.py            # Singleton de logging en memoria
│   └── sistema_config.py    # Singleton de configuración general
├── modelos/                 # Entidades de dominio (Cliente, Reserva, Pago, etc.)
├── dao/                     # Acceso a datos (Data Access Object) por entidad
├── schemas/                 # Modelos Pydantic de entrada/salida (validación de la API)
├── routers/                 # Endpoints agrupados por recurso
└── validaciones/            # Validadores reutilizables y excepciones personalizadas
```

## Endpoints principales

| Recurso | Prefijo | Endpoints |
|---|---|---|
| Clientes | `/clientes` | `POST`, `GET`, `GET /{id}`, `GET /{id}/reservas`, `PUT /{id}`, `DELETE /{id}` |
| Temáticas | `/tematicas` | `POST`, `GET` (con filtro `?solo_disponibles=true`), `GET /{id}`, `PUT /{id}`, `DELETE /{id}` |
| Reservas | `/reservas` | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`, cambios de estado |
| Servicios adicionales | `/servicios-adicionales` | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}` |
| Pagos | `/pagos` | `POST`, `GET`, `GET /{id}`, generación de cuotas |
| Cuotas | `/cuotas` | `POST`, `GET`, `GET /pago/{id_pago}`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`, `PATCH /{id}/pagar` |

Para el detalle completo de parámetros, cuerpos de petición y respuestas, consulta `/docs` con el servidor corriendo.

## Notas técnicas

- Los IDs de cada entidad se generan automáticamente con formato `PREFIJO + 3 dígitos` (ej. `C001`, `R012`, `Q003`).
- Las cuotas de un pago se generan automáticamente al registrar el pago, repartiendo el monto total entre el número de cuotas indicado.
- Las validaciones de formato (DNI, teléfono, correo, fechas, horas, montos, etc.) están centralizadas en `validaciones/validadores.py` y se reutilizan tanto en los `schemas` de Pydantic como en la capa de acceso a datos.

## Nota sobre `\version-consola-inicial`

Esta carpeta contiene `Eventos_Reserva.py`, la **primera versión** del sistema: un prototipo de consola (sin FastAPI, sin servidor web) hecho antes de migrar a la arquitectura actual del backend (`routers`, `dao`, `modelos`, `schemas`, `validaciones`).

Se conserva solo como referencia del proceso de desarrollo. **No forma parte del backend evaluado** y no se ejecuta como parte de la aplicación (no está importado en `main.py`).

## Autor

AMPUERO - PASCACIO — Proyecto académico, IESTP "Argentina".