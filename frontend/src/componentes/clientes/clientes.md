# 📘 Manual Técnico del Módulo: Clientes

> **Proyecto:** Eventix - Sistema de Reserva de Eventos
>
> **Módulo:** Clientes
>
> **Versión:** 1.0
>
> **Tecnologías utilizadas:** React, Axios, Bootstrap, JavaScript, React Icons.

---

# 📖 Introducción

El módulo **Clientes** es la pantalla donde se administran los clientes registrados en Eventix.

A diferencia del Menu (que solo navega), este módulo sí conversa con el backend: pide la lista de clientes, permite crear uno nuevo, editar uno existente y eliminarlo.

Todo esto ocurre dentro de un único archivo, `clientes.jsx`, que en realidad se comporta como si fueran **dos pantallas en una**:

- La **lista** de clientes (tabla + buscador).
- El **formulario** (para crear o editar un cliente).

React decide cuál de las dos mostrar usando una sola variable de estado (`vista`), sin necesidad de crear una ruta nueva.

---

# 🎯 Objetivos del módulo

✔ Mostrar la lista de clientes que existen en la base de datos.

✔ Permitir buscar un cliente por nombre, apellido, DNI o correo.

✔ Permitir registrar un cliente nuevo.

✔ Permitir editar los datos de un cliente existente.

✔ Permitir eliminar un cliente.

✔ Avisar al usuario cuando algo sale mal (error de conexión, dato inválido, etc.).

✔ Reutilizar el mismo formulario tanto para crear como para editar.

---

# 📂 Estructura del módulo

```
clientes/
└── clientes.jsx
```

Todo (lógica + JSX) vive en un solo archivo. No tiene un `.css` propio porque toda la apariencia se resuelve con clases de **Bootstrap** y algunos `style={{ }}` puntuales para los colores de marca (morado `#7c3aed`, amarillo, rojo).

---

# 🛠 Tecnologías utilizadas

| Tecnología | Propósito |
|------------|-----------|
| React | Construcción del componente |
| useState | Guardar datos que cambian (clientes, formulario, vista, etc.) |
| useEffect | Pedir los clientes al backend apenas se abre la pantalla |
| Axios | Hacer las peticiones HTTP al backend (GET, POST, PUT, DELETE) |
| Bootstrap | Botones, tarjetas, tabla, formulario, grillas |
| React Icons | Iconos de lupa, lápiz, basurero y "+" |

---

# 📚 Importaciones

```jsx
import { useEffect, useState } from "react";
import { FaSearch, FaPen, FaTrash, FaPlus } from "react-icons/fa";
import api from "../api/axios";
```

### `useEffect` y `useState`

Son *Hooks* de React.

```
useState
↓
Guardar un dato que puede cambiar.
```

```
useEffect
↓
Ejecutar código automáticamente cuando el componente aparece en pantalla
(o cuando cierta información cambia).
```

### Iconos

`FaSearch`, `FaPen`, `FaTrash`, `FaPlus` son simplemente dibujos (lupa, lápiz, basurero, más) que React Icons entrega listos para usar como si fueran una etiqueta más.

### `api`

```jsx
import api from "../api/axios";
```

`api` es un "mensajero" ya configurado (en `componentes/api/axios.jsx`) que sabe la dirección del backend (`http://localhost:8000`). Gracias a esto, en vez de escribir la URL completa cada vez, simplemente se usa `api.get(...)`, `api.post(...)`, etc.

---

# 🧠 Estados del componente

```jsx
const [clientes, setClientes] = useState([]);
const [cargando, setCargando] = useState(true);
const [error, setError] = useState("");

const [vista, setVista] = useState("lista");
const [idEditando, setIdEditando] = useState(null);
const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
const [guardando, setGuardando] = useState(false);
const [errorFormulario, setErrorFormulario] = useState("");

const [busqueda, setBusqueda] = useState("");
```

Cada `useState` guarda **una sola cosa**. Analicémoslos uno por uno.

| Estado | ¿Para qué sirve? |
|---|---|
| `clientes` | La lista de clientes que llegó desde el backend. |
| `cargando` | `true` mientras se espera la respuesta del backend. |
| `error` | Mensaje de error si la lista no pudo cargar. |
| `vista` | Indica qué se muestra: `"lista"` o `"formulario"`. |
| `idEditando` | Si es `null`, se está creando un cliente nuevo. Si tiene un valor, se está editando ese cliente. |
| `formulario` | Los datos que el usuario está escribiendo (nombre, apellido, dni, teléfono, correo). |
| `guardando` | `true` mientras se espera la respuesta al guardar (crear/editar). |
| `errorFormulario` | Mensaje de error dentro del formulario (ej: correo duplicado). |
| `busqueda` | Lo que el usuario escribió en el buscador. |

### `FORMULARIO_VACIO`

```jsx
const FORMULARIO_VACIO = { nombre: "", apellido: "", dni: "", telefono: "", correo: "" };
```

Es una plantilla con todos los campos vacíos. Se usa para "limpiar" el formulario cuando se abre para crear un cliente nuevo, o cuando se cancela.

---

# 🌐 Dónde está el API realmente (y dónde no)

Esta es la parte más importante para entender el archivo: **no todo el archivo habla con el backend**. Solo tres funciones lo hacen.

## 1) `cargarClientes` → `GET /clientes`

```jsx
const cargarClientes = () => {
  api
    .get("/clientes")
    .then((res) => setClientes(res.data))
    .catch(() => setError("No se pudo cargar la lista de clientes."))
    .finally(() => setCargando(false));
};
```

- `api.get("/clientes")` → le pide al backend "dame todos los clientes".
- `.then(...)` → si respondió bien, guarda esos datos en `clientes`.
- `.catch(...)` → si falló (backend apagado, error de red), guarda un mensaje en `error`.
- `.finally(...)` → pase lo que pase, deja de mostrar "Cargando...".

## 2) `useEffect` → ejecuta `cargarClientes` una sola vez

```jsx
useEffect(() => {
  cargarClientes();
}, []);
```

El arreglo vacío `[]` significa: *"ejecuta esto una sola vez, apenas se muestra el componente en pantalla"*. Así es como la tabla ya aparece llena de clientes sin que el usuario tenga que hacer clic en nada.

## 3) `guardarCliente` → `POST /clientes` o `PUT /clientes/{id}`

```jsx
const guardarCliente = (e) => {
  e.preventDefault();
  setGuardando(true);
  setErrorFormulario("");

  const peticion = idEditando
    ? api.put(`/clientes/${idEditando}`, formulario)
    : api.post("/clientes", formulario);

  peticion
    .then(() => {
      cargarClientes();
      cancelarFormulario();
    })
    .catch((err) => {
      const detalle = err.response?.data?.detail;
      setErrorFormulario(detalle || "No se pudo guardar el cliente. Revisa los datos.");
    })
    .finally(() => setGuardando(false));
};
```

- `e.preventDefault()` → evita que el formulario recargue la página (comportamiento normal de HTML que aquí no queremos).
- El operador ternario decide **qué** petición mandar:
  - Si `idEditando` tiene un valor → estamos editando → `api.put(...)`.
  - Si `idEditando` es `null` → estamos creando → `api.post(...)`.
- Si sale bien: se vuelve a pedir la lista completa (`cargarClientes()`) para que la tabla se actualice, y se cierra el formulario (`cancelarFormulario()`).
- Si sale mal: el backend normalmente manda un mensaje de error (`err.response.data.detail`, por ejemplo "correo ya existe"), y ese mensaje se muestra en pantalla.
- `err.response?.data?.detail` usa el operador `?.` ("optional chaining"): significa *"si `response` existe, entra a `data`; si `data` existe, entra a `detail`; si en algún punto no existe nada, no explota, simplemente da `undefined`"*.

## 4) `eliminarCliente` → `DELETE /clientes/{id}`

```jsx
const eliminarCliente = (cliente) => {
  if (!window.confirm(`¿Eliminar a ${cliente.nombre} ${cliente.apellido}?`)) return;
  api
    .delete(`/clientes/${cliente.id_cliente}`)
    .then(() => cargarClientes())
    .catch((err) => {
      const detalle = err.response?.data?.detail;
      alert(detalle || "No se pudo eliminar el cliente.");
    });
};
```

- `window.confirm(...)` → abre la ventanita nativa del navegador preguntando "¿Estás seguro?". Si el usuario dice que no, la función se corta ahí mismo con `return`.
- Si confirma, se llama a `api.delete(...)` con el id del cliente.
- Si el backend lo elimina bien, se vuelve a cargar la lista.
- Si falla (por ejemplo, porque el cliente tiene reservas), se muestra el motivo con `alert(...)`.

---

# 🧩 Lo que NO es API (solo interfaz / JavaScript puro)

## Abrir el formulario para crear

```jsx
const abrirNuevoCliente = () => {
  setIdEditando(null);
  setFormulario(FORMULARIO_VACIO);
  setErrorFormulario("");
  setVista("formulario");
};
```

Solo cambia estados locales. No llama al backend. Deja `idEditando` en `null` para que `guardarCliente` sepa que debe hacer un `POST` (crear) y no un `PUT` (editar).

## Abrir el formulario para editar

```jsx
const abrirEdicionCliente = (cliente) => {
  setIdEditando(cliente.id_cliente);
  setFormulario({
    nombre: cliente.nombre,
    apellido: cliente.apellido,
    dni: cliente.dni,
    telefono: cliente.telefono,
    correo: cliente.correo,
  });
  setErrorFormulario("");
  setVista("formulario");
};
```

Tampoco llama al backend. Toma los datos que **ya están en pantalla** (los de la fila en la que se hizo clic) y los copia al formulario, además de guardar su `id_cliente` en `idEditando`.

## Cancelar

```jsx
const cancelarFormulario = () => {
  setVista("lista");
  setFormulario(FORMULARIO_VACIO);
  setIdEditando(null);
  setErrorFormulario("");
};
```

Vuelve a la vista de lista y limpia todo, sin tocar el backend.

## `cambiarCampo` (una función que devuelve otra función)

```jsx
const cambiarCampo = (campo) => (e) =>
  setFormulario((f) => ({ ...f, [campo]: e.target.value }));
```

Esta línea es la más "rara" a primera vista, pero se puede leer en partes:

```
cambiarCampo("nombre")
↓
Devuelve una función que, cuando el usuario escribe,
actualiza SOLO el campo "nombre" del formulario.
```

Así, en vez de escribir una función distinta para cada input (`onChange` para nombre, otra para apellido, otra para dni...), se reutiliza la misma fábrica de funciones:

```jsx
<input value={formulario.nombre} onChange={cambiarCampo("nombre")} />
<input value={formulario.telefono} onChange={cambiarCampo("telefono")} />
```

El `{ ...f, [campo]: e.target.value }` significa: *"copia todo lo que ya había en el formulario (`...f`), y solo cambia la propiedad que corresponde a `campo`"*. Los corchetes `[campo]` permiten usar el valor de la variable (`"nombre"`, `"dni"`, etc.) como el nombre de la propiedad a cambiar.

## Filtrado de la búsqueda

```jsx
const textoBusqueda = busqueda.trim().toLowerCase();
const clientesFiltrados = clientes.filter((c) =>
  `${c.nombre} ${c.apellido} ${c.dni} ${c.correo}`.toLowerCase().includes(textoBusqueda)
);
```

Esto ocurre **solo en el navegador**, con los datos que ya llegaron del backend. No se manda ninguna petición nueva mientras se escribe en el buscador.

- `.trim()` quita espacios sobrantes al inicio/final.
- `.toLowerCase()` pasa todo a minúsculas para que "Ana" y "ana" cuenten como lo mismo.
- `.filter(...)` recorre el arreglo `clientes` y se queda solo con los que cumplen la condición.
- El texto entre backticks (`` `${c.nombre} ${c.apellido}...` ``) junta varios campos en un solo string para poder buscar en todos a la vez.
- `.includes(...)` responde `true` o `false` según si el texto de búsqueda aparece dentro.

---

# 🖼️ Renderizado condicional (elegir qué pantalla mostrar)

```jsx
if (vista === "formulario") {
  return ( /* ... JSX del formulario ... */ );
}

return ( /* ... JSX de la lista ... */ );
```

Esta es la clave de que un solo archivo se comporte como dos pantallas:

```
vista === "formulario"
↓
Se muestra el formulario (crear o editar)
```

```
vista === "lista" (cualquier otro caso)
↓
Se muestra la tabla de clientes
```

React vuelve a ejecutar el componente completo cada vez que un estado cambia (por ejemplo, al hacer `setVista("formulario")`), y en esa nueva ejecución el `if` decide qué JSX devolver.

---

# 🧾 Analizando el formulario (crear / editar)

```jsx
<input
  type="text"
  className="form-control rounded-3 py-2"
  placeholder="Ingrese nombre"
  value={formulario.nombre}
  onChange={cambiarCampo("nombre")}
  required
/>
```

- `value={formulario.nombre}` → el input siempre muestra lo que hay guardado en el estado. A esto se le llama **input controlado**: React manda el valor, no el navegador.
- `onChange={cambiarCampo("nombre")}` → cada letra que se escribe actualiza el estado (ver sección anterior).
- `required` → el navegador no deja enviar el formulario si el campo está vacío.

El título y el subtítulo cambian según si se está creando o editando:

```jsx
<p className="text-muted mb-4">
  {idEditando ? "Edita los datos del cliente" : "Registra datos del cliente"}
</p>
```

Y el botón de guardar cambia de texto mientras espera respuesta del backend:

```jsx
{guardando ? "Guardando..." : "Guardar Cliente"}
```

---

# 📋 Analizando la parte de la lista (buscador + tabla)

```jsx
<div className="position-relative mt-4 mb-3" style={{ maxWidth: 420 }}>
  <input
    type="text"
    className="form-control rounded-3 py-2 ps-3 pe-5"
    placeholder="Buscar cliente..."
    value={busqueda}
    onChange={(e) => setBusqueda(e.target.value)}
  />
  <FaSearch className="position-absolute text-muted" style={{ right: 16, top: "50%", transform: "translateY(-50%)" }} />
</div>
```

- El input de búsqueda es controlado igual que los del formulario (`value` + `onChange`).
- El icono de lupa se dibuja **encima** del input gracias a `position-absolute` (de Bootstrap) más `right: 16` y `top: 50%` (para centrarlo verticalmente).

```jsx
<div className="card shadow-sm border-0 rounded-4 p-3">
  {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}

  {cargando ? (
    <p className="text-muted mb-0 p-3">Cargando...</p>
  ) : clientesFiltrados.length === 0 ? (
    <p className="text-muted mb-0 p-3">
      {textoBusqueda ? "No se encontraron clientes." : "Aún no hay clientes registrados."}
    </p>
  ) : (
    /* tabla */
  )}
</div>
```

Aquí hay **tres posibles resultados**, decididos en cadena:

```
¿Hay error?
↓ sí → se muestra la alerta roja arriba (pero igual se sigue evaluando lo de abajo)

¿Está cargando?
↓ sí → "Cargando..."
↓ no → sigue

¿La lista filtrada está vacía?
↓ sí → "No se encontraron clientes" o "Aún no hay clientes registrados"
        (el mensaje cambia según si el usuario estaba buscando algo o no)
↓ no → se muestra la tabla
```

```jsx
{clientesFiltrados.map((c) => (
  <tr key={c.id_cliente}>
    <td className="fw-semibold">{c.id_cliente}</td>
    <td>{c.dni}</td>
    ...
  </tr>
))}
```

`map()` recorre el arreglo `clientesFiltrados` y por cada cliente dibuja una fila (`<tr>`). El `key={c.id_cliente}` es obligatorio en React para que sepa distinguir una fila de otra cuando la lista cambia.

Los botones de acciones:

```jsx
<button onClick={() => abrirEdicionCliente(c)}><FaPen /></button>
<button onClick={() => eliminarCliente(c)}><FaTrash /></button>
```

El lápiz solo abre el formulario (no toca el API). El basurero sí llama al API (ver sección de `eliminarCliente`).

---

# 🗂️ Tabla resumen: ¿API o solo interfaz?

| Parte del código | ¿Llama al backend? |
|---|---|
| `useEffect` + `cargarClientes` | ✅ Sí — `GET /clientes` |
| `guardarCliente` | ✅ Sí — `POST` o `PUT /clientes` |
| `eliminarCliente` | ✅ Sí — `DELETE /clientes/{id}` |
| Buscador (`busqueda`, `clientesFiltrados`) | ❌ No — filtra en memoria |
| `abrirNuevoCliente` / `abrirEdicionCliente` | ❌ No — solo cambian de vista |
| `cancelarFormulario` | ❌ No — solo limpia estado |
| `cambiarCampo` | ❌ No — solo actualiza el formulario mientras se escribe |
| Tabla, tarjetas, mensajes de "Cargando..." | ❌ No — solo muestran datos que ya llegaron antes |

---

# 📚 Conceptos aprendidos

- `useState` y `useEffect`.
- Peticiones HTTP con Axios (`get`, `post`, `put`, `delete`).
- Promesas: `.then()`, `.catch()`, `.finally()`.
- Operador ternario.
- Operador de propagación (`...`) para copiar objetos.
- Propiedades computadas (`[campo]: valor`).
- Optional chaining (`?.`).
- Inputs controlados (`value` + `onChange`).
- Renderizado condicional (`if`, `? :`, `&&`).
- `map()` y la propiedad `key`.
- `window.confirm` y `alert`.
- Bootstrap (tarjetas, tablas, formularios, grillas).

---

# ❓ Posibles preguntas durante la exposición

### ¿Por qué todo está en un solo archivo, con un `if` para elegir la vista, en vez de dos componentes o dos rutas?

Porque ambas pantallas comparten los mismos datos (`clientes`, `formulario`) y es más simple mantener un solo componente pequeño que crear rutas nuevas para algo que en el fondo es "un formulario que aparece y desaparece".

### ¿Por qué `idEditando` decide entre crear y editar?

Porque así se reutiliza el mismo formulario para las dos acciones: si tiene un id, se edita ese cliente (`PUT`); si es `null`, se crea uno nuevo (`POST`).

### ¿Por qué el buscador no llama al backend cada vez que se escribe?

Porque ya tenemos todos los clientes cargados en memoria (`clientes`). Filtrar en el navegador es instantáneo y evita saturar al backend con una petición por cada letra escrita.

### ¿Qué pasa si el backend no está prendido?

`cargarClientes` cae en el `.catch()`, guarda un mensaje en `error`, y ese mensaje se muestra arriba de la tabla con una alerta roja de Bootstrap.

### ¿Por qué se usa `window.confirm` antes de eliminar?

Para evitar borrar un cliente por accidente con un solo clic.

---

# 🚀 Posibles mejoras futuras

- Validar los campos del formulario en el propio frontend antes de enviarlos (por ejemplo, formato de correo).
- Mostrar una notificación (toast) en vez de `alert()` para los errores.
- Agregar paginación si la lista de clientes crece mucho.
- Deshabilitar los botones de acción mientras se está guardando o eliminando.

---

# 📝 Conclusión

El módulo **Clientes** es el primer componente del sistema que realmente conversa con el backend: trae información real (`GET`), la modifica (`POST`/`PUT`) y la elimina (`DELETE`). Aun así, la mayor parte del código que se ve en pantalla (buscador, tabla, formulario) es interfaz simple que solo depende de los estados de React, y no del API.

Entender esta separación —qué parte llama al backend y qué parte solo dibuja información— es la clave para poder explicar el componente con confianza y para poder ampliarlo más adelante sin romper nada.