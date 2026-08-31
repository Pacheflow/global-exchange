# Documentación técnica del frontend — Global Exchange

**Proyecto:** Global Exchange  
**Alcance documentado:** frontend web implementado hasta Sprint 1  
**Rama relevada:** `develop`  
**Fecha de actualización:** 31 de agosto de 2026  
**Tecnologías principales:** Django Templates, Django Material, Django Cotton, HTML5, CSS3 y JavaScript

---

## 1. Objetivo

Este documento describe la arquitectura, las decisiones de diseño y el funcionamiento técnico del frontend de Global Exchange. El alcance comprende:

- Landing pública de la casa de cambios.
- Registro, verificación de correo, inicio y cierre de sesión mediante Keycloak.
- Layout autenticado con sidebar.
- Dashboard principal.
- Gestión visual de usuarios y roles.
- CRUD, segmentación, selección y asignación de clientes.
- Sistema de diseño, componentes, interacciones y comportamiento responsive.

El frontend utiliza renderizado del lado del servidor. Django prepara el contexto, evalúa permisos y genera HTML mediante templates. JavaScript se reserva para interacciones puntuales y no constituye una aplicación SPA.

---

## 2. Arquitectura general

```text
Navegador
   |
   | HTTP / HTML / CSS / JavaScript
   v
Django
   |-- templates/usuarios/       Landing, layout, dashboard y usuarios
   |-- clientes/templates/       Pantallas del módulo de clientes
   |-- static/css/app.css        Sistema visual y responsive
   |-- static/js/app.js          Interacciones de interfaz
   |
   +--> Keycloak                 Identidad, autenticación y roles
   +--> PostgreSQL               Clientes, categorías y asignaciones
   +--> Mailpit                  Correo de verificación en desarrollo
```

### 2.1 Responsabilidades por capa

| Capa | Responsabilidad |
|---|---|
| Templates Django | Estructura semántica, composición de pantallas y renderizado condicional por sesión o rol. |
| Django Material | Componentes Material para formularios, botones, tarjetas, tipografía e iconografía. |
| Django Cotton | Sintaxis de componentes reutilizables mediante etiquetas `c-*`. |
| CSS del proyecto | Tokens, layouts, estados, responsive y adaptación de Django Material a la identidad visual. |
| JavaScript | Menús, ripple, confirmaciones, dropdown de perfil, mensajes y conversor demostrativo. |
| Vistas Django | Contexto de pantalla, validación, autorización y coordinación con Keycloak/PostgreSQL. |
| Keycloak | Registro, credenciales, correo verificado, identidad y roles globales. |
| PostgreSQL | Información comercial de clientes, categorías y relaciones usuario-cliente. |

---

## 3. Organización de archivos

```text
global-exchange/
|-- templates/usuarios/
|   |-- base.html                 Layout común público/autenticado
|   |-- home.html                 Landing y conversor informativo
|   |-- dashboard.html            Panel autenticado
|   |-- user_list.html            Listado de usuarios
|   |-- user_form.html            Alta y edición de usuarios
|   |-- forbidden.html            Respuesta visual HTTP 403
|   `-- client_select.html        Selector alternativo de cliente
|-- clientes/templates/clientes/
|   |-- consultar.html            Búsqueda, tabla y acciones
|   |-- registrar.html            Alta de cliente
|   |-- editar.html               Edición de cliente
|   |-- baja.html                 Confirmación de baja lógica
|   |-- segmentar.html            Categoría comercial
|   |-- asignaciones.html         Usuarios autorizados por cliente
|   `-- partials/form_fields.html Campos reutilizables
|-- static/
|   |-- css/app.css               Estilos y design tokens
|   `-- js/app.js                 Comportamiento de interfaz
|-- usuarios/
|   |-- views.py                  Vistas OIDC, dashboard y usuarios
|   |-- decorators.py             Protección por autenticación/roles
|   |-- keycloak.py               Cliente de Keycloak Admin API
|   `-- services/keycloak.py      Validación JWT y sesión OIDC
`-- clientes/
    |-- views.py                  Casos de uso del módulo
    |-- forms.py                  Formularios Django
    `-- models.py                 Cliente, categoría y asignación
```

---

## 4. Layout y navegación

El template raíz es `templates/usuarios/base.html`. Este archivo determina el layout según la existencia de `request.session.kc_user`.

### 4.1 Experiencia pública

Una sesión no autenticada recibe:

- Header público fijo durante el desplazamiento.
- Navegación hacia Personas, Empresas y Plataforma.
- Subnavegación hacia conversor, cotizaciones, servicios y presentación institucional.
- Acciones visibles de inicio de sesión y registro.
- Footer institucional.

El público puede consultar información general y usar el conversor demostrativo, pero no puede realizar operaciones ni acceder a módulos internos.

### 4.2 Experiencia autenticada

Una sesión autenticada recibe un `app-shell` compuesto por:

- Sidebar sticky en escritorio.
- Logo y acceso al inicio.
- Accesos a Inicio, Usuarios y Clientes.
- Indicador del cliente seleccionado.
- Identidad del usuario y cierre de sesión.
- Header compacto con menú de icono en dispositivos móviles.
- Área principal compartida por todas las pantallas.

El enlace **Usuarios** solo se renderiza para `ADMINISTRADOR`. Los permisos también se validan en backend; ocultar el enlace no es el mecanismo de seguridad.

### 4.3 Navegación activa

Los templates utilizan `request.resolver_match` y `aria-current="page"` para identificar la sección activa. Esto proporciona:

- Estado visual consistente.
- Información semántica para tecnologías de asistencia.
- Independencia respecto de JavaScript para marcar la ruta actual.

---

## 5. Pantallas implementadas

### 5.1 Landing pública

La landing contiene:

1. Hero institucional con propuesta de valor.
2. Conversor informativo USD, EUR, BRL y PYG.
3. Cotizaciones de compra y venta de referencia.
4. Servicios principales.
5. Presentación institucional.
6. CTA para autenticarse antes de operar.

Las tasas se encuentran actualmente definidas en la vista y en `static/js/app.js`. Son valores demostrativos y no consumen todavía un servicio de cotizaciones en tiempo real.

### 5.2 Dashboard

El dashboard muestra:

- Saludo generado desde los claims de Keycloak.
- Dropdown de perfil en la esquina superior derecha.
- Cierre de sesión desde el dropdown.
- Acción para seleccionar o cambiar cliente.
- Panel horizontal de monedas.
- Estado del contexto de cliente.
- Acciones rápidas según el rol.

La obtención del nombre usa la siguiente prioridad:

1. `given_name`.
2. `name`.
3. `preferred_username`.
4. Texto de respaldo `Usuario`.

Esto evita imprimir expresiones de template como texto literal o mostrar un encabezado vacío.

### 5.3 Gestión de usuarios

El módulo permite al administrador:

- Listar identidades de Keycloak.
- Crear usuarios.
- Editar nombre, apellido, correo y estado.
- Asignar o modificar roles globales.
- Dar de baja de manera lógica deshabilitando la identidad.

La información no se duplica en Django: las identidades se consultan y modifican mediante Keycloak Admin REST API.

### 5.4 Gestión de clientes

El módulo permite:

- Registrar personas físicas o jurídicas.
- Buscar por nombre o razón social.
- Editar datos.
- Dar de baja lógicamente.
- Asignar una categoría comercial.
- Seleccionar un cliente como contexto de trabajo.
- Deseleccionar o cambiar el cliente activo.
- Asignar identidades Keycloak a un cliente.
- Quitar asignaciones.

Las acciones de tabla se presentan como botones de icono con `title`, `aria-label` y tooltip visual. Esto reduce ruido en tablas sin perder comprensión ni accesibilidad.

---

## 6. Matriz de rutas y permisos

| Pantalla o acción | Ruta | Roles permitidos |
|---|---|---|
| Landing | `/` | Público |
| Iniciar sesión | `/login/` | Público |
| Registrarse | `/registro/` | Público |
| Callback OIDC | `/callback/` | Flujo iniciado |
| Dashboard | `/panel/` | Todos los roles de negocio |
| Listar usuarios | `/usuarios/` | `ADMINISTRADOR` |
| Crear usuario | `/usuarios/nuevo/` | `ADMINISTRADOR` |
| Editar usuario | `/usuarios/<id>/editar/` | `ADMINISTRADOR` |
| Dar de baja usuario | `/usuarios/<id>/baja/` | `ADMINISTRADOR` |
| Consultar clientes | `/clientes/consultar/` | Todos los roles de negocio |
| Registrar cliente | `/clientes/registrar/` | `ADMINISTRADOR` |
| Editar cliente | `/clientes/editar/<id>/` | `ADMINISTRADOR` |
| Dar de baja cliente | `/clientes/baja/<id>/` | `ADMINISTRADOR` |
| Segmentar cliente | `/clientes/segmentar/<id>/` | `ADMINISTRADOR`, `ANALISTA_CAMBIARIO` |
| Seleccionar/deseleccionar | `/clientes/seleccionar/<id>/`, `/clientes/deseleccionar/` | Todos los roles de negocio con acceso al cliente |
| Asignar usuarios | `/clientes/<id>/usuarios/` | `ADMINISTRADOR` |

Roles globales reconocidos:

- `USUARIO`
- `CAJERO`
- `ANALISTA_CAMBIARIO`
- `ADMINISTRADOR`

Permisos dentro de un cliente:

- `RESPONSABLE`
- `OPERADOR`
- `CONSULTA`

Los primeros determinan acceso global a módulos. Los segundos describen el alcance de la relación con un cliente y quedan persistidos en `UsuarioCliente`.

---

## 7. Integración del frontend con Keycloak

### 7.1 Protocolo utilizado

Se implementa OpenID Connect Authorization Code Flow con PKCE S256.

```text
Usuario -> /login/ o /registro/
        -> Django crea state + code_verifier + code_challenge
        -> Keycloak autentica o registra
        -> /callback/?code=...&state=...
        -> Django valida state y canjea el código
        -> Django valida firma y claims del JWT
        -> Django crea la sesión
        -> Dashboard
```

### 7.2 Controles aplicados

- `state` aleatorio para mitigar CSRF en OAuth/OIDC.
- Comparación segura mediante `secrets.compare_digest`.
- Estado de un solo uso y con expiración configurable.
- PKCE con SHA-256.
- Validación de algoritmo RS256.
- Validación de firma mediante JWKS de Keycloak.
- Validación de `issuer`, expiración, sujeto y cliente autorizado.
- Requisito `email_verified=true`.
- Rotación de la clave de sesión con `cycle_key()`.
- Cookies HTTP-only y opciones Secure/SameSite configurables.

### 7.3 Datos conservados en sesión

| Clave | Contenido |
|---|---|
| `oidc_authenticated` | Indicador interno de autenticación validada. |
| `oidc_user` | Identificador, username y correo normalizados. |
| `kc_user` | Claims recibidos desde Keycloak. |
| `roles` | Roles de negocio filtrados. |
| `oidc_expires_at` | Expiración de la sesión alineada con el token. |
| `kc_access_token` | Access token para el flujo actual. |
| `kc_id_token` | ID token usado como pista al cerrar sesión. |
| `selected_client` | Identificador y nombre del cliente activo. |

Las contraseñas nunca son almacenadas ni procesadas por el frontend de Django durante el login normal.

### 7.4 Verificación de correo

Keycloak envía el mensaje mediante SMTP a Mailpit en desarrollo. El acceso local es:

```text
http://localhost:8025
```

Mientras `emailVerified` sea falso, el token es rechazado y no se establece sesión. Esta condición implementa el requisito de verificación por correo.

---

## 8. Integración con Django Material

La dependencia se instala desde `requirements.txt` y la aplicación `material` está registrada en `INSTALLED_APPS`.

El layout carga:

```html
material/fonts/roboto/fonts.css
material/fonts/material-symbols/index.css
material/css/unpoly.min.css
material/css/material.css
material/js/unpoly.js
material/js/material.js
```

También se utiliza `django-cotton`, que habilita componentes declarativos como:

```html
<c-card.outlined>...</c-card.outlined>
<c-button.filled type="submit" icon="save">Guardar</c-button.filled>
<c-forms.text.outlined name="email">Correo</c-forms.text.outlined>
```

### 8.1 Estrategia de adopción

La interfaz combina:

- Componentes nativos de Django Material en formularios y tarjetas.
- HTML semántico para elementos específicos del dominio.
- Clases propias para unificar apariencia y dimensiones.
- Material Symbols para iconografía.
- Una capa de interacción propia para aplicar ripple a enlaces que funcionan como botones.

No se utiliza React Material UI. Django Material cumple una función equivalente dentro de la arquitectura server-side de Django.

---

## 9. Sistema de diseño

Los tokens se encuentran al inicio de `static/css/app.css`.

### 9.1 Colores principales

| Token | Valor | Uso |
|---|---:|---|
| `--color-ink` | `#111218` | Botones y texto de énfasis. |
| `--color-text` | `#292c33` | Texto principal. |
| `--color-muted` | `#686c78` | Texto secundario. |
| `--color-border` | `#e3e5e8` | Bordes y divisores. |
| `--color-canvas` | `#f6f7f8` | Fondo neutro. |
| `--color-surface` | `#ffffff` | Tarjetas y superficies. |
| `--color-navy` | `#0a115c` | Identidad de landing y foco. |
| `--color-blue-soft` | `#d5e7ff` | Estados suaves e iconos. |
| `--color-gold` | `#f1ba08` | Acento de marca. |
| `--color-green` | `#469d73` | Estados exitosos. |
| `--color-danger` | `#b53543` | Acciones destructivas y errores. |

### 9.2 Espaciado y dimensiones

- Ancho máximo de contenido: `1120px`.
- Padding horizontal responsive: `clamp(20px, 4vw, 48px)`.
- Padding vertical de pantalla: `clamp(40px, 6vw, 72px)`.
- Altura estándar de botones: `44px`.
- Padding horizontal estándar de botones: `20px`.
- Radio estándar de botones: `10px`.
- Radios de superficie: 10, 14 y 20 px.

Las pantallas de dashboard, usuarios y clientes comparten estos valores para mantener alineación, densidad y ritmo visual.

### 9.3 Estados interactivos

Los controles contemplan:

- `hover`: cambio de fondo, borde o elevación.
- `focus-visible`: anillo perceptible para navegación por teclado.
- `active`: reducción de escala o cambio de tono.
- `disabled`: reducción de contraste y bloqueo funcional cuando corresponde.
- Ripple posicionado desde el punto de pulsación.
- Confirmación previa para acciones sensibles.

---

## 10. JavaScript de interfaz

`static/js/app.js` implementa únicamente comportamiento progresivo:

### 10.1 Menú responsive

- Alterna la clase `open`.
- Actualiza icono `menu/close`.
- Mantiene `aria-expanded`, `aria-label` y `title` sincronizados.

### 10.2 Capa Material y ripple

- Identifica botones, enlaces de navegación y acciones de tabla.
- Agrega la clase `material-interactive`.
- Calcula las coordenadas de la pulsación.
- CSS dibuja el efecto desde el punto real de interacción.

### 10.3 Dropdown de perfil

- Usa `<details>` y `<summary>` como base accesible.
- Cierra al hacer clic fuera.
- Cierra con `Escape` y devuelve el foco al disparador.

### 10.4 Confirmaciones y mensajes

- Los formularios con `data-confirm` solicitan confirmación antes del envío.
- Los mensajes flash se retiran visualmente después de cinco segundos.

### 10.5 Conversor demostrativo

- Convierte entre PYG, USD, EUR y BRL.
- Utiliza `Intl.NumberFormat("es-PY")`.
- Permite intercambiar moneda origen/destino.
- No realiza llamadas de red ni inicia operaciones reales.

El contenido esencial, la navegación y los formularios siguen funcionando con renderizado Django; JavaScript mejora la experiencia sin concentrar reglas de autorización.

---

## 11. Clientes: selección, segmentación y asignación

### 11.1 Selección de cliente

Seleccionar un cliente no modifica el registro. Guarda en sesión:

```python
{
    "id": cliente.id,
    "name": cliente.nombre_razon_social,
}
```

El contexto se refleja en sidebar, dashboard y tabla. Puede cambiarse seleccionando otro cliente o eliminarse mediante **Dejar de seleccionar**.

Un usuario no administrador solo puede seleccionar clientes con una asignación activa vinculada a su `sub` de Keycloak.

### 11.2 Segmentación

La segmentación asigna una `CategoriaCliente` con finalidad comercial. Permite clasificar clientes sin alterar sus credenciales ni permisos. La edición está habilitada para administrador y analista cambiario.

### 11.3 Asignación usuario-cliente

La entidad `UsuarioCliente` vincula:

- Identificador inmutable del usuario en Keycloak.
- Username de referencia.
- Cliente de Django.
- Rol dentro del cliente.
- Estado y fecha de asignación.

Esta separación evita confundir los roles globales de plataforma con los permisos contextuales de cada cliente.

---

## 12. Formularios, validación y feedback

- Los formularios mutables utilizan `POST` y token CSRF.
- Django Forms valida los campos del módulo de clientes.
- Las operaciones de usuarios validan datos antes de llamar a Keycloak.
- Los errores permanecen asociados a la pantalla o campo correspondiente.
- Los resultados exitosos se comunican mediante Django Messages.
- Las bajas son lógicas para preservar trazabilidad.
- Las asignaciones eliminadas no modifican la identidad Keycloak.

---

## 13. Responsive y accesibilidad

### 13.1 Responsive

El CSS utiliza `clamp`, CSS Grid, Flexbox y media queries. Los principales cambios son:

- Sidebar de escritorio reemplazado por header móvil.
- Menú desplegable controlado por icono.
- Columnas de formularios convertidas en una sola columna.
- Tablas con desplazamiento horizontal cuando es necesario.
- Conversor adaptado a una disposición vertical.
- Acciones rápidas y tarjetas reorganizadas según el ancho.

### 13.2 Accesibilidad incorporada

- Documento declarado en español.
- Enlace **Saltar al contenido**.
- Regiones `<header>`, `<nav>`, `<main>`, `<aside>` y `<footer>`.
- `aria-label` para acciones representadas únicamente por iconos.
- `aria-current` en navegación activa.
- Texto oculto `.sr-only` para encabezados sin etiqueta visible.
- Foco visible para teclado.
- Cierre del dropdown mediante `Escape`.
- Feedback de mensajes con `role="status"`.
- Iconos decorativos marcados con `aria-hidden="true"`.

---

## 14. Ejecución y verificación

### 14.1 Levantar el entorno

```powershell
docker compose up --build -d
```

Servicios disponibles:

| Servicio | Dirección |
|---|---|
| Aplicación Django | `http://localhost:8000` |
| Keycloak | `http://localhost:8080` |
| Mailpit | `http://localhost:8025` |

### 14.2 Ejecutar pruebas

```powershell
docker compose exec web python manage.py test
```

### 14.3 Verificar configuración Django

```powershell
docker compose exec web python manage.py check
```

### 14.4 Archivos que deben revisarse al modificar UI

1. `templates/usuarios/base.html` si cambia navegación o layout.
2. Template específico de la pantalla.
3. `static/css/app.css` para estilos y responsive.
4. `static/js/app.js` solo si se requiere una interacción del navegador.
5. Vista y pruebas correspondientes si cambia el contexto o la autorización.

---

## 15. Criterios para extender el frontend

Para conservar la consistencia actual:

1. Extender siempre `usuarios/base.html`.
2. Utilizar `.workspace` para las pantallas internas estándar.
3. Reutilizar `.workspace-header`, `.page-intro`, `.surface` y `.form-surface`.
4. Usar tokens CSS antes de introducir valores nuevos.
5. Mantener botones en 44 px de alto, 20 px de padding y 10 px de radio.
6. Preferir componentes `c-button`, `c-card` y `c-forms` cuando exista equivalencia.
7. Añadir `aria-label` y tooltip a acciones de solo icono.
8. Proteger la vista en backend aunque la acción se oculte en el template.
9. Utilizar `POST` con CSRF para acciones que cambian estado.
10. Incorporar pruebas para permisos, errores y caminos exitosos.

---

## 16. Estado actual y límites conocidos

### Implementado

- Landing responsive con navegación fija.
- Login, registro, logout y verificación de correo con Keycloak.
- Sesión segura con OIDC Authorization Code + PKCE.
- UI diferenciada para visitante y usuario autenticado.
- Sidebar responsive y navegación por iconos.
- Dashboard de estilo plataforma cambiaria.
- Gestión de usuarios y roles desde Keycloak.
- CRUD y baja lógica de clientes.
- Segmentación de clientes.
- Selección de contexto de cliente.
- Asignación de usuarios Keycloak a clientes.
- Componentes Django Material y efectos de interacción Material.
- Protección visual y backend por roles.

### Pendiente para una etapa transaccional

- Fuente dinámica de cotizaciones.
- Persistencia de operaciones de cambio.
- Cálculo de comisiones y confirmación de tasa.
- Historial transaccional.
- Aplicación efectiva de `RESPONSABLE`, `OPERADOR` y `CONSULTA` sobre operaciones futuras.
- Pipeline de assets para producción y servidor WSGI/ASGI productivo.

Estos puntos no invalidan el alcance visual y de administración del Sprint 1; delimitan funcionalidades posteriores del producto.

---

## 17. Resumen técnico

El frontend de Global Exchange se encuentra construido como una aplicación Django server-rendered. `base.html` concentra la estructura de navegación y selecciona automáticamente la experiencia pública o autenticada. Django Material y Django Cotton aportan componentes reutilizables; `app.css` define un sistema visual propio y uniforme; `app.js` agrega interacción progresiva.

La identidad se delega completamente en Keycloak y la sesión solo se crea después de verificar criptográficamente el token, su emisor, vigencia, cliente y correo confirmado. Los roles globales controlan el acceso a las pantallas y la relación `UsuarioCliente` restringe qué clientes puede consultar o seleccionar cada identidad. De este modo, presentación, autenticación, autorización y datos comerciales permanecen desacoplados, pero integrados en un único flujo de usuario.
