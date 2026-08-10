# Sistema de Reserva de Eventos — Frontend

Aplicación web construida con **React + Vite**, que consume la API del backend (FastAPI) para gestionar clientes, temáticas, reservas, servicios adicionales, pagos y cuotas.

## Requisitos previos

- Node.js 18 o superior
- npm
- El **backend** de este proyecto debe estar corriendo (ver `backend/README.md`), ya que el frontend depende de su API.

## 1. Clonar y ubicarse en el frontend

```bash
git clone https://github.com/floresJP/Sistema_Reserva_Eventos.git
cd Sistema_Reserva_Eventos/frontend
```

## 2. Instalar dependencias

```bash
npm install
```

## 3. Configurar variables de entorno

El frontend necesita saber en qué URL está corriendo el backend. Esto se configura con una variable de entorno, no está escrito fijo en el código.

1. Copia el archivo `.env.example` y renómbralo a `.env`, en la misma carpeta `frontend/`.
2. Ajusta la URL si tu backend corre en otro host o puerto:

```env
VITE_API_URL=http://localhost:8000
```

Si no creas el `.env`, la app usa `http://localhost:8000` como valor de respaldo (ver `src/componentes/api/axios.jsx`), pero **para producción o si tu backend corre en otro puerto, es obligatorio definir esta variable**.

> Nota: en Vite, las variables de entorno visibles en el navegador deben empezar siempre con el prefijo `VITE_`.

El `.env` es local a cada máquina y **no se sube al repositorio** (está en `.gitignore`). Solo se comparte `.env.example`, sin datos reales.

## 4. Levantar la app en modo desarrollo

```bash
npm run dev
```

Por defecto queda disponible en `http://localhost:5173`.

## 5. Otros comandos disponibles

| Comando | Qué hace |
|---|---|
| `npm run dev` | Levanta el servidor de desarrollo con recarga en caliente |
| `npm run build` | Genera la build de producción en `dist/` |
| `npm run preview` | Sirve localmente la build de producción, para probarla |
| `npm run lint` | Corre ESLint sobre el proyecto |

## Estructura del proyecto

```
frontend/
├── public/
│   └── imagenes-tematica/     # Imágenes estáticas de cada temática de evento
├── src/
│   ├── assets/                 # Logos e imágenes propias de la app
│   ├── componentes/
│   │   ├── api/axios.jsx       # Instancia de axios configurada con VITE_API_URL
│   │   ├── clientes/           # Vista y lógica de Clientes
│   │   ├── cuotas/             # Vista y lógica de Cuotas
│   │   ├── menu/                # Barra de navegación / menú lateral
│   │   ├── pagos/               # Vista y lógica de Pagos
│   │   ├── panel/                # Panel principal / dashboard
│   │   ├── reservas/            # Vista y lógica de Reservas
│   │   └── tematicas/           # Vista y lógica de Temáticas
│   ├── App.jsx                  # Componente raíz, define las rutas
│   └── main.jsx                 # Punto de entrada de React
├── .env.example                 # Plantilla de variables de entorno
├── vite.config.js
└── package.json
```

## Conexión con el backend

Todas las llamadas a la API pasan por `src/componentes/api/axios.jsx`, que centraliza la URL base leída desde `VITE_API_URL`. Si necesitas apuntar a otro backend (por ejemplo, uno desplegado en la nube), solo cambia el valor en tu `.env` — no hace falta tocar ningún componente.

## Diseño de referencia

El diseño visual sigue el prototipo de Figma entregado en el classroom (layout, colores, tipografía, componentes y estados de cada vista).

## Autor

AMPUERO - PASCACIO — Proyecto académico, IESTP "Argentina".