# 📘 Manual Técnico del Módulo: Menu (Sidebar)

> **Proyecto:** Eventix - Sistema de Reserva de Eventos
>
> **Módulo:** Menu (Sidebar)
>
> **Versión:** 1.0
>
> **Tecnologías utilizadas:** React, React Router DOM, Bootstrap, CSS, JavaScript, React Icons.

---

# 📖 Introducción

El módulo **Menu** corresponde a la barra de navegación lateral (Sidebar) de la aplicación **Eventix**.

Su principal responsabilidad es permitir que el usuario pueda desplazarse entre los diferentes módulos del sistema de una forma rápida, intuitiva y organizada.

Además de mostrar las opciones de navegación, este componente incorpora un comportamiento dinámico que permite expandir o contraer el menú según las necesidades del usuario, optimizando el espacio disponible en pantalla.

Durante el desarrollo de este módulo se aplicaron conceptos fundamentales de React, JavaScript, React Router, Bootstrap y CSS, los cuales serán explicados a lo largo de este documento.

---

# 🎯 Objetivos del módulo

Este componente fue diseñado con los siguientes objetivos.

✔ Mostrar un menú lateral organizado.

✔ Facilitar la navegación entre los diferentes módulos del sistema.

✔ Informar visualmente al usuario cuál página se encuentra activa.

✔ Optimizar el espacio disponible permitiendo colapsar el menú.

✔ Reducir la repetición de código mediante renderizado dinámico.

✔ Mantener una estructura escalable y fácil de mantener.

✔ Separar correctamente la lógica del diseño.

---

# 📂 Estructura del módulo

```

menu/

├── menu.jsx
└── menu.css

```

## menu.jsx

Contiene toda la lógica del componente.

Entre sus responsabilidades se encuentran:

- Construcción del menú.
- Definición de rutas.
- Estado del menú.
- Eventos del usuario.
- Renderizado dinámico.
- Comunicación con React Router.

---

## menu.css

Contiene exclusivamente la apariencia visual.

Entre sus responsabilidades se encuentran:

- Colores.
- Tamaños.
- Espaciados.
- Animaciones.
- Transiciones.
- Estado visual del menú.
- Adaptación cuando el menú cambia de tamaño.

Una buena práctica en React consiste en mantener separada la lógica del diseño.

```

menu.jsx

↓

¿Qué hace?

```

```

menu.css

↓

¿Cómo se ve?

```

Esta separación facilita el mantenimiento del proyecto.

---

# 🛠 Tecnologías utilizadas

Durante el desarrollo del componente se emplearon las siguientes tecnologías.

| Tecnología | Propósito |
|------------|-----------|
| React | Construcción del componente |
| React Router DOM | Navegación entre páginas |
| JavaScript | Lógica del menú |
| Bootstrap | Distribución y organización visual |
| CSS | Diseño personalizado |
| React Icons | Iconografía del sistema |

---

# 📚 Librerías importadas

## Importación del CSS

```jsx
import "./menu.css";
```

Esta línea importa el archivo de estilos correspondiente al componente.

Todo el diseño del menú se encuentra separado del archivo JavaScript.

Esto permite modificar colores, tamaños o animaciones sin alterar la lógica del componente.

---

## React Router

```jsx
import { NavLink } from "react-router-dom";
```

### ¿Qué es React Router?

React Router es una biblioteca que permite construir aplicaciones con múltiples páginas sin necesidad de recargar completamente el navegador.

En una página HTML tradicional ocurre lo siguiente.

```

Usuario

↓

Hace clic

↓

El navegador vuelve a cargar toda la página.

```

Con React Router el comportamiento cambia.

```

Usuario

↓

Hace clic

↓

React cambia únicamente el componente necesario.

```

Esto produce una navegación mucho más rápida y mejora la experiencia del usuario.

---

### ¿Qué es NavLink?

`NavLink` es un componente especializado para crear enlaces de navegación.

Ejemplo.

```jsx
<NavLink to="/clientes">
Clientes
</NavLink>
```

Cuando el usuario hace clic sobre este botón, React Router muestra automáticamente el componente asociado a la ruta `/clientes`.

---

### ¿Qué significa la propiedad "to"?

```jsx
to="/clientes"
```

La propiedad **to** indica el destino al que navegará el usuario.

Puede entenderse como una dirección.

```

to="/inicio"

↓

Ir a Inicio

```

```

to="/pagos"

↓

Ir a Pagos

```

---

### ¿Por qué usamos NavLink y no una etiqueta `<a>`?

En HTML normalmente escribiríamos.

```html
<a href="/clientes">Clientes</a>
```

Sin embargo, esta etiqueta obliga al navegador a recargar completamente la página.

En cambio.

```jsx
<NavLink to="/clientes">
```

permite cambiar únicamente el contenido necesario.

La aplicación se comporta como un software de escritorio.

---

### ¿Qué diferencia existe entre Link y NavLink?

Ambos sirven para navegar.

La diferencia principal es que `NavLink` reconoce automáticamente cuál página está abierta.

Por ejemplo.

```

🏠 Inicio

👤 Clientes

💳 Pagos

```

Si el usuario entra en Clientes.

React detecta la ruta.

```

/clientes

```

y automáticamente agrega la clase.

```

active

```

Después CSS cambia el color del botón.

Gracias a esto el usuario siempre sabe dónde se encuentra.

---

## useState

```jsx
import { useState } from "react";
```

React posee herramientas especiales llamadas Hooks.

Uno de ellos es `useState`.

Su función consiste en almacenar información que puede cambiar durante la ejecución del programa.

Podemos dividir la palabra.

```

use

↓

Usar

```

```

State

↓

Estado

```

Por lo tanto.

```

useState

↓

Usar un estado.

```

---

# 🧠 ¿Qué es un estado?

Un estado es una información que puede cambiar mientras la aplicación está funcionando.

Ejemplos.

Una puerta.

```

Cerrada

↓

Abierta

```

Una lámpara.

```

Apagada

↓

Encendida

```

Nuestro menú funciona exactamente igual.

```

Expandido

↓

Colapsado

```

React necesita recordar cuál de esos estados está activo.

Para ello utilizamos `useState`.

---

# ⚛️ Analizando el estado del menú

```jsx
const [collapsed, setCollapsed] = useState(false);
```

Esta línea parece complicada al principio, pero realmente puede dividirse en tres partes.

## collapsed

Es la variable donde React almacena el estado actual.

Puede contener únicamente dos valores.

```

true

```

o

```

false

```

---

## setCollapsed

Es la función encargada de modificar el estado.

Ejemplo.

```jsx
setCollapsed(true);
```

El menú pasa al estado colapsado.

```jsx
setCollapsed(false);
```

El menú vuelve a expandirse.

---

## useState(false)

Indica el valor inicial.

Cuando la aplicación inicia.

```

collapsed

↓

false

```

Es decir.

```

El menú comienza expandido.

```

---

# 🔄 Cambio de estado

Cuando el usuario hace clic sobre el logotipo ocurre la siguiente instrucción.

```jsx
onClick={() => setCollapsed(!collapsed)}
```

El operador `!` significa **negar**.

Su función consiste en invertir un valor booleano.

Ejemplo.

```

false

↓

true

```

```

true

↓

false

```

Cada clic cambia el estado del menú.

Es exactamente igual que un interruptor de luz.

```

OFF

↓

ON

↓

OFF

↓

ON

```

Este mecanismo permite que un único botón abra y cierre el menú.

---

# 🎨 Aplicación dinámica de clases

```jsx
className={`eventix-menu ${collapsed ? "collapsed" : ""}`}
```

Esta línea utiliza un operador ternario.

Puede leerse de la siguiente forma.

```

¿collapsed es true?

```

Sí.

```

Agregar la clase

collapsed

```

No.

```

No agregar ninguna clase.

```

Es importante entender que React no modifica el CSS.

Lo único que hace es agregar o quitar clases.

Posteriormente CSS interpreta esas clases para cambiar el diseño visual.

---
---

# 📦 Organización de las opciones del menú

Antes de mostrar los botones del menú, se creó una constante llamada `OPCIONES\_MENU`.

```jsx
const OPCIONES_MENU = [
  { ruta: "/inicio", icono: <FaHome size={20} />, texto: "Inicio" },
  { ruta: "/clientes", icono: <FaUsers size={20} />, texto: "Clientes" },
  { ruta: "/reservas", icono: <FaCalendarCheck size={20} />, texto: "Reserva" },
  { ruta: "/tematicas", icono: <FaPalette size={20} />, texto: "Tematicas" },
  { ruta: "/pagos", icono: <FaCreditCard size={20} />, texto: "Pagos" },
  { ruta: "/cuotas", icono: <FaFileInvoiceDollar size={20} />, texto: "Cuotas" },
];
```

A simple vista parece una lista de datos, pero en realidad representa la información necesaria para construir cada botón del menú.

Cada elemento del arreglo es un **objeto** de JavaScript.

Por ejemplo:

```jsx
{
    ruta: "/clientes",
    icono: <FaUsers size={20} />,
    texto: "Clientes"
}
```

Este objeto indica que existirá un botón con las siguientes características:

| Propiedad | Significado |
|-----------|-------------|
| `ruta` | Dirección a la que navegará el usuario. |
| `icono` | Icono que se mostrará junto al texto. |
| `texto` | Nombre visible del botón. |

---

# 💡 ¿Por qué utilizar un arreglo?

Una de las reglas más importantes en programación es **evitar repetir código**.

Supongamos que no existiera `OPCIONES\_MENU`.

Tendríamos que escribir algo parecido a esto:

```jsx
<li>
    <NavLink ...>Inicio</NavLink>
</li>

<li>
    <NavLink ...>Clientes</NavLink>
</li>

<li>
    <NavLink ...>Reservas</NavLink>
</li>

<li>
    <NavLink ...>Pagos</NavLink>
</li>
```

Aunque funciona, presenta varios problemas.

- El código es muy largo.
- Es difícil de mantener.
- Agregar una nueva opción implica copiar y pegar nuevamente todo el bloque.

Por esta razón se decidió almacenar únicamente los datos en un arreglo.

Posteriormente React construye automáticamente todos los botones.

Este enfoque sigue el principio **DRY (Don't Repeat Yourself)**, cuyo objetivo es evitar la repetición innecesaria de código.

---

# 🔄 Renderizado dinámico mediante `map()`

Una vez creado el arreglo `OPCIONES\_MENU`, necesitamos recorrerlo.

Para ello utilizamos el método:

```jsx
.map()
```

Su función consiste en recorrer cada elemento del arreglo y ejecutar una acción por cada uno.

Podemos imaginarlo así.

```
OPCIONES_MENU

│

├── Inicio

├── Clientes

├── Reservas

├── Temáticas

├── Pagos

└── Cuotas
```

Cuando React ejecuta `.map()` hace el siguiente recorrido.

```
Primer objeto

↓

Crear botón Inicio

↓

Segundo objeto

↓

Crear botón Clientes

↓

Tercer objeto

↓

Crear botón Reservas

↓

...

↓

Último objeto

↓

Crear botón Cuotas
```

Al finalizar el recorrido, React habrá construido automáticamente todos los botones del menú.

---

# 📖 Analizando el código

```jsx
{OPCIONES_MENU.map((opcion) => (
```

Esta línea puede traducirse al español de la siguiente manera:

> Recorre cada objeto almacenado dentro de `OPCIONES\_MENU` y guárdalo temporalmente en una variable llamada `opcion`.

La variable `opcion` cambia automáticamente durante cada recorrido.

Por ejemplo.

Primera vuelta.

```jsx
opcion
```

contiene

```jsx
{
ruta:"/inicio",
texto:"Inicio"
}
```

Segunda vuelta.

```jsx
opcion
```

contiene

```jsx
{
ruta:"/clientes",
texto:"Clientes"
}
```

Tercera vuelta.

```jsx
{
ruta:"/reservas",
texto:"Reservas"
}
```

Y así sucesivamente.

---

# 🔑 ¿Por qué usamos `key`?

```jsx
<li key={opcion.ruta}>
```

Cuando React crea muchos elementos mediante `.map()`, necesita identificar cada uno de ellos.

Para ello utiliza la propiedad `key`.

Podemos compararla con el DNI de una persona.

Dos personas pueden llamarse igual.

Pero jamás tendrán el mismo DNI.

React utiliza `key` exactamente para lo mismo.

Le permite reconocer rápidamente cuál elemento cambió.

Gracias a esto mejora considerablemente el rendimiento de la aplicación.

---

# 🌐 Construcción de cada botón

Dentro del recorrido encontramos el siguiente código.

```jsx
<NavLink
    to={opcion.ruta}
    className="nav-link d-flex align-items-center px-3"
>
```

En este punto React sustituye automáticamente los valores.

Por ejemplo.

Primera vuelta.

```jsx
to="/inicio"
```

Segunda vuelta.

```jsx
to="/clientes"
```

Tercera vuelta.

```jsx
to="/reservas"
```

De esta manera un único bloque de código genera todos los botones.

---

# 🖼 ¿Cómo aparecen los iconos?

Observemos esta línea.

```jsx
{opcion.icono}
```

Cada objeto ya posee un icono.

Ejemplo.

```jsx
icono:<FaUsers size={20}/>
```

Cuando React encuentra:

```jsx
{opcion.icono}
```

simplemente inserta el componente correspondiente.

Resultado.

```
👤 Clientes
```

En la siguiente vuelta.

```
🏠 Inicio
```

Después.

```
💳 Pagos
```

No es necesario escribir un icono diferente para cada botón.

---

# 📝 ¿Por qué utilizamos un `<span>`?

```jsx
<span className="ms-3 hide-on-collapse">
```

El texto se encuentra dentro de un `<span>` por dos razones.

## Primera

Aplicar margen.

```css
ms-3
```

Genera un pequeño espacio entre el icono y el texto.

Sin este margen ambos elementos quedarían demasiado juntos.

---

## Segunda

Ocultar el texto.

La clase

```css
hide-on-collapse
```

permite ocultar únicamente el texto cuando el menú cambia de tamaño.

Los iconos permanecen visibles.

Gracias a esto el usuario continúa identificando cada módulo incluso con el menú reducido.

---

# 🚀 Bootstrap utilizado

Durante la construcción del componente se utilizaron diversas clases utilitarias de Bootstrap.

Estas clases permiten crear interfaces rápidamente sin escribir grandes cantidades de CSS.

| Clase | Explicación |
|--------|-------------|
| d-flex | Activa Flexbox. |
| flex-column | Organiza los elementos de arriba hacia abajo. |
| p-3 | Agrega padding general. |
| mt-2 | Margen superior. |
| mb-4 | Margen inferior. |
| me-2 | Margen derecho. |
| text-white | Cambia el color del texto a blanco. |
| nav | Define un menú de navegación. |
| nav-pills | Estilo de navegación de Bootstrap. |
| gap-2 | Espacio automático entre elementos. |
| btn | Convierte el elemento en botón. |
| btn-link | Elimina el aspecto tradicional del botón. |
| align-items-center | Centra verticalmente los elementos. |

Bootstrap reduce considerablemente la cantidad de CSS necesaria para construir interfaces.

---

# 🎨 Análisis del archivo `menu.css`

Mientras que React controla el comportamiento del menú, CSS controla completamente su apariencia.

Podemos resumirlo así.

```
React

↓

¿Qué debe ocurrir?

```

```
CSS

↓

¿Cómo debe verse?
```

---

## Contenedor principal

```css
.eventix-menu{
width:250px;
min-height:100vh;
background-color:#171733;
transition:width .3s ease;
}
```

Esta clase representa el contenedor principal del menú.

### width

```css
width:250px;
```

Define el ancho inicial del menú.

Cuando la aplicación inicia, el menú aparece completamente expandido.

---

### min-height

```css
min-height:100vh;
```

Hace que el menú tenga como mínimo el mismo alto que la ventana del navegador.

```
100vh

↓

100% del alto visible de la pantalla.
```

---

### background-color

```css
background-color:#171733;
```

Define el color de fondo del menú.

El color oscuro fue seleccionado para mejorar el contraste con el texto y los iconos.

---

### transition

```css
transition:width .3s ease;
```

Hace que el cambio de tamaño sea gradual.

Sin esta propiedad el menú cambiaría de tamaño de forma instantánea.

Con ella se obtiene una animación suave.
---

# 📏 Menú colapsado

Cuando el usuario presiona el botón del logotipo, React cambia el estado `collapsed`.

Si el estado cambia a `true`, React agrega automáticamente la clase:

```css
collapsed
```

Esta clase es detectada por CSS.

```css
.eventix-menu.collapsed {
    width: 80px;
}
```

## ¿Qué ocurre aquí?

Cuando el menú posee la clase `collapsed`, su ancho cambia.

Antes del clic:

```
┌──────────────────────────────┐
│🏠 Inicio                     │
│👤 Clientes                   │
│📅 Reservas                   │
│💳 Pagos                      │
└──────────────────────────────┘

250px
```

Después del clic:

```
┌─────────┐
│🏠        │
│👤        │
│📅        │
│💳        │
└─────────┘

80px
```

No fue necesario modificar el ancho utilizando JavaScript.

React únicamente agregó la clase.

CSS realizó todo el cambio visual.

---

# 👀 Ocultar elementos automáticamente

Cuando el menú se reduce de tamaño, el texto ya no tiene suficiente espacio.

Por esa razón utilizamos la siguiente regla.

```css
.eventix-menu.collapsed .hide-on-collapse{
    display:none;
}
```

Esta instrucción puede leerse así.

> Busca todos los elementos que tengan la clase **hide-on-collapse**, pero únicamente cuando el menú tenga también la clase **collapsed**.

En nuestro componente esa clase fue aplicada en dos lugares.

```jsx
<img
className="hide-on-collapse"
/>
```

y

```jsx
<span className="hide-on-collapse">
```

Por eso desaparecen:

✔ El nombre de Eventix.

✔ El texto de cada botón.

Mientras que los iconos permanecen visibles.

Visualmente sucede esto.

Antes.

```
🏠 Inicio

👤 Clientes

📅 Reservas
```

Después.

```
🏠

👤

📅
```

Esta decisión mejora el aprovechamiento del espacio sin perder la funcionalidad del menú.

---

# 🎨 Personalización de los botones

Todos los botones del menú utilizan la siguiente regla.

```css
.eventix-menu .nav-link{

color:#e5e5f0;

border-radius:10px;

transition:background .2s;

}
```

Analicemos cada propiedad.

---

## Color

```css
color:#e5e5f0;
```

Define el color inicial del texto.

Se eligió un tono gris muy claro para mantener un buen contraste con el fondo oscuro.

---

## Border Radius

```css
border-radius:10px;
```

Redondea las esquinas del botón.

Sin esta propiedad los botones tendrían un aspecto completamente rectangular.

Con ella el diseño resulta más moderno y agradable para el usuario.

---

## Transition

```css
transition:background .2s;
```

Hace que el cambio de color no ocurra de forma instantánea.

Cuando el usuario mueve el cursor sobre un botón, el cambio ocurre suavemente durante 0.2 segundos.

Esto mejora la experiencia visual.

---

# 🖱 Estado Hover

Cuando el usuario coloca el cursor encima de un botón, CSS activa automáticamente el pseudoestado:

```css
:hover
```

Nuestro código es.

```css
.eventix-menu .nav-link:hover{

background-color:rgba(255,255,255,.1);

color:white;

}
```

Visualmente ocurre.

```
Cursor fuera

↓

Color normal

↓

Cursor encima

↓

Fondo ligeramente iluminado
```

Este pequeño efecto indica al usuario que el botón puede seleccionarse.

---

# 📍 Estado Active

Cuando el usuario entra en una página determinada, `NavLink` agrega automáticamente la clase.

```css
active
```

Posteriormente CSS aplica.

```css
.eventix-menu .nav-link.active{

background-color:#7c3aed;

color:white;

font-weight:600;

}
```

Esto provoca tres cambios.

### Cambio de color

```css
background-color:#7c3aed;
```

Pinta el botón de color morado.

---

### Cambio del texto

```css
color:white;
```

El texto cambia completamente a blanco para aumentar el contraste.

---

### Fuente

```css
font-weight:600;
```

Hace que el texto sea ligeramente más grueso.

Esto ayuda al usuario a identificar rápidamente cuál opción está seleccionada.

---

# 🔄 Comunicación entre React y CSS

Una de las características más importantes de este módulo es que React y CSS trabajan juntos.

Cada uno tiene responsabilidades diferentes.

```
React

↓

Controla la lógica

```

```
CSS

↓

Controla el diseño
```

El flujo completo del programa es el siguiente.

```
Usuario hace clic

        │

        ▼

onClick()

        │

        ▼

setCollapsed()

        │

        ▼

React cambia el estado

        │

        ▼

React vuelve a renderizar

        │

        ▼

Agrega la clase "collapsed"

        │

        ▼

CSS detecta la clase

        │

        ▼

Reduce el ancho

        │

        ▼

Oculta los textos

        │

        ▼

Ejecuta la animación
```

Todo este proceso ocurre en apenas unos milisegundos.

El usuario únicamente observa una transición suave.

---

# 💡 Decisiones de diseño

Durante el desarrollo de este componente se tomaron varias decisiones importantes.

## Utilizar un arreglo

En lugar de escribir manualmente cada botón, se decidió almacenar la información dentro de un arreglo de objetos.

Esto facilita agregar nuevos módulos.

---

## Utilizar `map()`

Permite recorrer automáticamente todas las opciones del menú.

Reduce la cantidad de código repetido.

---

## Utilizar `NavLink`

Además de navegar entre páginas, identifica automáticamente cuál ruta se encuentra activa.

---

## Separar JSX y CSS

La lógica permanece dentro de `menu.jsx`.

El diseño permanece dentro de `menu.css`.

Esto facilita el mantenimiento del proyecto.

---

## Mantener visibles los iconos

Cuando el menú se colapsa únicamente desaparece el texto.

Los iconos permanecen visibles para que el usuario continúe identificando cada módulo.

---

## Utilizar Bootstrap

Bootstrap fue utilizado para reducir la cantidad de CSS necesario y acelerar el desarrollo de la interfaz.

---

# 📚 Conceptos aprendidos

Durante la construcción de este módulo se aplicaron los siguientes conceptos.

- Componentes de React.
- Hooks.
- useState.
- Eventos (`onClick`).
- Operador lógico `!`.
- Operador ternario.
- Renderizado dinámico.
- Arreglos de objetos.
- Método `map()`.
- Propiedad `key`.
- React Router.
- NavLink.
- Bootstrap.
- Flexbox.
- Selectores CSS.
- Pseudoestados (`:hover`).
- Clases dinámicas.
- Animaciones mediante `transition`.
- Organización modular de un proyecto React.

---

# ❓ Posibles preguntas durante la exposición

### ¿Por qué utilizaste `useState`?

Porque necesitaba guardar el estado del menú y permitir que React actualizara automáticamente la interfaz cuando ese estado cambiara.

---

### ¿Por qué utilizaste `map()`?

Porque evita repetir código. Todas las opciones del menú tienen la misma estructura y solo cambian sus datos.

---

### ¿Por qué utilizaste un arreglo de objetos?

Porque facilita agregar, eliminar o modificar opciones sin alterar la estructura del componente.

---

### ¿Por qué utilizaste `NavLink`?

Porque además de permitir la navegación, identifica automáticamente la ruta activa y agrega la clase `active`.

---

### ¿Por qué separaste JSX y CSS?

Porque sigue el principio de separación de responsabilidades. La lógica y el diseño pueden mantenerse y modificarse de forma independiente.

---

### ¿Por qué utilizaste Bootstrap?

Porque proporciona clases reutilizables para construir interfaces de manera más rápida, limpia y consistente.

---

### ¿Qué ventaja tiene que el menú sea colapsable?

Permite aprovechar mejor el espacio disponible en pantallas pequeñas y mejora la experiencia del usuario sin perder la funcionalidad del menú.

---

# 🚀 Posibles mejoras futuras

Este módulo puede ampliarse en versiones posteriores.

Algunas mejoras serían:

- Agregar submenús desplegables.
- Incorporar animaciones más avanzadas.
- Adaptar automáticamente el menú para dispositivos móviles.
- Permitir cambiar entre tema claro y oscuro.
- Mostrar notificaciones o indicadores dentro del menú.
- Controlar los permisos de acceso según el tipo de usuario.

---

# 📝 Conclusión

El componente **Menu** constituye uno de los elementos principales de la interfaz de Eventix, ya que proporciona un acceso rápido y organizado a los diferentes módulos del sistema.

Durante su desarrollo se aplicaron conceptos fundamentales de React, JavaScript, React Router, Bootstrap y CSS, siguiendo principios como la reutilización de código, la separación de responsabilidades y la organización modular.

Gracias al uso de `useState`, el menú puede cambiar dinámicamente entre un estado expandido y colapsado. Mediante `map()` se evita la repetición de código al generar automáticamente las opciones de navegación. Por su parte, `NavLink` facilita la navegación y resalta la página activa, mientras que CSS se encarga de la presentación visual y de las animaciones.

El resultado es un componente reutilizable, escalable y fácil de mantener, que puede crecer junto con el resto del proyecto sin requerir modificaciones importantes en su estructura.