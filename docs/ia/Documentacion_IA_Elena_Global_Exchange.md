# Documentación de uso de Inteligencia Artificial
**Integrante:** Elena Ramírez   

---

## 1. Objetivo de esta documentación

Este documento registra el uso de Inteligencia Artificial como herramienta de apoyo durante el desarrollo de las historias de usuario asignadas en el proyecto **Global Exchange**.

La IA fue utilizada principalmente para comprender requisitos, orientar la configuración de Keycloak, revisar decisiones de integración entre Django y Keycloak, resolver errores de configuración y dependencias, apoyar el uso de Git y la resolución de conflictos, diseñar y revisar pruebas automatizadas y verificar criterios de aceptación.

Las decisiones finales, ejecución de comandos, configuración del entorno, pruebas y validaciones fueron realizadas sobre el proyecto real.

---

## 2. Historias de usuario trabajadas

- **HU-01 – Registrar Usuario**
- **HU-02 – Verificar Usuario**
- **HU-03 – Iniciar Sesión**
- **HU-04 – Gestionar Accesos**
- **HU-08 – Asignar Rol**

---

## 3. Registro de consultas realizadas a la IA

### Consulta 1 – Interpretación de las historias de usuario

**Pregunta realizada**

> ¿Puedes ayudarme a entender qué tengo que implementar en las historias de usuario que me corresponden y qué parte debería manejar Keycloak?

**Respuesta / orientación obtenida**

Se identificó que la autenticación, verificación de correo, inicio de sesión, gestión de roles y asignación de roles debían apoyarse en el proveedor externo de identidad, en este caso **Keycloak**.

Se separaron las responsabilidades de la siguiente forma: Django se encarga de la aplicación y sus endpoints; Keycloak administra identidad, autenticación, sesiones y roles; y los permisos de la aplicación se determinan utilizando los roles entregados por Keycloak.

**Aplicación en el proyecto**

Esta orientación se utilizó como base para implementar HU-01, HU-02, HU-03, HU-04 y HU-08.

---

### Consulta 2 – Configuración de registro de usuarios en Keycloak

**Pregunta realizada**

> ¿Cómo puedo configurar el registro de usuarios para que una persona pueda crear su propia cuenta desde Keycloak?

**Respuesta / orientación obtenida**

Se indicó habilitar el registro de usuarios dentro del realm correspondiente y utilizar el flujo de registro de Keycloak en lugar de implementar directamente el manejo de contraseñas desde Django.

**Aplicación en el proyecto**

Se configuró el flujo de auto-registro en Keycloak para la **HU-01 – Registrar Usuario**.

---

### Consulta 3 – Verificación de correo electrónico

**Pregunta realizada**

> ¿Cómo hago para que después del registro el usuario tenga que verificar su correo?

**Respuesta / orientación obtenida**

Se explicó que Keycloak dispone de la opción de verificación de correo y que esta funcionalidad debía integrarse al flujo de registro. También se revisó la utilización del servidor de correo configurado para el entorno de desarrollo.

**Aplicación en el proyecto**

La configuración se utilizó para completar la **HU-02 – Verificar Usuario**.

---

### Consulta 4 – Inicio de sesión con Keycloak

**Pregunta realizada**

> ¿Cómo debería implementar el inicio de sesión entre Django y Keycloak?

**Respuesta / orientación obtenida**

Se recomendó utilizar el flujo estándar de OpenID Connect: **Authorization Code Flow con PKCE**.

El flujo trabajado fue:

1. Django redirige al usuario hacia Keycloak.
2. Keycloak autentica al usuario.
3. Keycloak redirige al callback configurado.
4. Django procesa la respuesta.
5. Se obtiene y valida la información del usuario.
6. Se crea la sesión correspondiente en la aplicación.

**Aplicación en el proyecto**

Esta orientación se utilizó para implementar la **HU-03 – Iniciar Sesión**.

---

### Consulta 5 – Roles que debía manejar el sistema

**Pregunta realizada**

> ¿Qué roles debería crear en Keycloak según los requisitos del proyecto?

**Respuesta / orientación obtenida**

Se identificaron los siguientes roles de negocio:

- `USUARIO`
- `CAJERO`
- `ANALISTA_CAMBIARIO`
- `ADMINISTRADOR`

También se diferenció al usuario visitante, que no posee una sesión autenticada.

**Aplicación en el proyecto**

Los roles fueron creados como **Realm Roles** en Keycloak y utilizados posteriormente para controlar accesos.

---

### Consulta 6 – Cómo obtener los roles del usuario autenticado

**Pregunta realizada**

> ¿Cómo puedo saber desde Django qué roles tiene el usuario que inició sesión en Keycloak?

**Respuesta / orientación obtenida**

Se revisó la lectura de los roles presentes en la información entregada por Keycloak y el almacenamiento de los roles necesarios dentro de la sesión de Django. Además, se trabajó sobre la validación segura del token JWT recibido desde Keycloak.

**Aplicación en el proyecto**

Se incorporó la identificación de roles durante el login para la **HU-04 – Gestionar Accesos**.

---

### Consulta 7 – Protección de vistas según autenticación y rol

**Pregunta realizada**

> ¿Cómo hago para que una vista solo pueda ser utilizada por usuarios autenticados o por un administrador?

**Respuesta / orientación obtenida**

Se propuso implementar decoradores reutilizables para verificar que exista una sesión OIDC válida, comprobar que el usuario posea un rol determinado, devolver `401 Unauthorized` cuando no exista autenticación y devolver `403 Forbidden` cuando exista autenticación pero no autorización.

**Aplicación en el proyecto**

Se implementaron decoradores de autorización utilizados para proteger los endpoints de acuerdo con los roles del usuario.

---

### Consulta 8 – Validación real de HU-04

**Pregunta realizada**

> ¿Cómo puedo comprobar que la gestión de accesos realmente funciona y no solamente pasa los tests?

**Respuesta / orientación obtenida**

Se recomendó realizar pruebas utilizando usuarios reales de Keycloak con diferentes roles.

**Aplicación en el proyecto**

Se realizaron pruebas manuales con un usuario que poseía `ADMINISTRADOR` y `CAJERO`, y con un usuario sin roles de negocio. El administrador pudo acceder correctamente al endpoint protegido y el usuario sin privilegios recibió una respuesta de acceso denegado.

---

## 4. HU-08 – Asignar Rol

### Consulta 9 – Diseño de la HU-08

**Pregunta realizada**

> Para la HU-08, ¿cómo debería hacer para que un administrador asigne un rol a otro usuario?

**Respuesta / orientación obtenida**

Se determinó que la asignación debía realizarse mediante la **Keycloak Admin REST API**, ya que el criterio de aceptación indicaba que la operación debía ejecutarse a través del proveedor externo de identidad.

La solución propuesta consistió en crear un cliente confidencial exclusivo para operaciones administrativas.

**Aplicación en el proyecto**

Se creó el cliente `global-exchange-admin` con **Service Accounts** habilitado.

---

### Consulta 10 – Permisos del cliente administrativo

**Pregunta realizada**

> ¿Qué permisos tengo que darle al cliente `global-exchange-admin`?

**Respuesta / orientación obtenida**

Se determinó utilizar permisos específicos de `realm-management`, evitando conceder privilegios innecesarios:

- `manage-users`
- `view-users`
- `view-realm`

**Aplicación en el proyecto**

El Service Account del cliente administrativo recibió esos permisos para poder consultar usuarios, consultar roles y modificar asignaciones.

---

### Consulta 11 – Autenticación contra la Admin API

**Pregunta realizada**

> ¿Cómo obtiene Django un token para utilizar la API administrativa de Keycloak?

**Respuesta / orientación obtenida**

Se indicó utilizar el flujo `client_credentials` con `KEYCLOAK_ADMIN_CLIENT_ID` y `KEYCLOAK_ADMIN_CLIENT_SECRET`.

El secreto debía permanecer únicamente en el archivo `.env` local y no debía incorporarse al repositorio.

**Aplicación en el proyecto**

Se implementó la función encargada de obtener el token administrativo y se documentaron las variables en `.env.example` sin incluir secretos.

---

### Consulta 12 – Funciones necesarias para asignar roles

**Pregunta realizada**

> ¿Qué funciones debería tener el servicio de Keycloak para completar la HU-08?

**Respuesta / orientación obtenida**

Se dividió la implementación en funciones para obtener token administrativo, buscar usuario por identificador, buscar un rol, obtener los roles actuales del usuario, comprobar si el usuario ya posee un rol y asignar el rol mediante Keycloak.

**Aplicación en el proyecto**

Estas operaciones fueron implementadas en el servicio de integración con Keycloak.

---

### Consulta 13 – Validación de roles duplicados

**Pregunta realizada**

> ¿Cómo evito que el administrador asigne dos veces el mismo rol?

**Respuesta / orientación obtenida**

Antes de realizar la asignación se debía consultar el listado actual de roles del usuario. Si el rol ya estaba asignado, la operación debía rechazarse.

**Aplicación en el proyecto**

La implementación devuelve el error `El usuario ya posee ese rol.` y no vuelve a realizar la asignación.

---

### Consulta 14 – Endpoint para HU-08

**Pregunta realizada**

> ¿Cómo debería ser el endpoint de Django para asignar el rol?

**Respuesta / orientación obtenida**

Se diseñó un endpoint `POST` protegido por el rol `ADMINISTRADOR`.

Ruta implementada:

`POST /usuarios/asignar-rol/`

El cuerpo esperado contiene:

```json
{
  "usuario_id": "identificador-del-usuario",
  "rol": "CAJERO"
}
```

El endpoint valida autenticación, rol administrador, JSON válido, existencia de `usuario_id`, existencia de `rol`, existencia del usuario en Keycloak, existencia del rol, rol permitido por el sistema, ausencia de asignación duplicada y resultado de la operación contra Keycloak.

---

### Consulta 15 – Pruebas automatizadas de HU-08

**Pregunta realizada**

> ¿Qué pruebas debería hacer para comprobar que HU-08 cumple los criterios?

**Respuesta / orientación obtenida**

Se definieron pruebas para verificar:

- usuario no autenticado → `401`;
- usuario autenticado sin rol administrador → `403`;
- administrador válido → asignación correcta;
- rol previamente asignado → operación rechazada.

**Aplicación en el proyecto**

Las pruebas fueron incorporadas a la suite automatizada de Django.

---

### Consulta 16 – Aplicación inmediata de un rol nuevo

**Pregunta realizada**

> Si asigno un rol en Keycloak, ¿el usuario obtiene el permiso inmediatamente?

**Respuesta / orientación obtenida**

Se aclaró que Keycloak actualiza la asignación inmediatamente, pero una sesión de Django ya iniciada puede conservar los roles que fueron obtenidos durante el login. Por lo tanto, el usuario obtiene los permisos correspondientes cuando recibe un nuevo token o vuelve a iniciar sesión.

**Aplicación en el proyecto**

Esta consideración se tuvo en cuenta al verificar el criterio de aceptación correspondiente a la aplicación de permisos.

---

## 5. Uso de Git y resolución de conflictos

### Consulta 17 – Integración de HU-08 con `develop`

**Pregunta realizada**

> Mi Pull Request tiene conflictos con `develop`. ¿Cómo puedo resolverlos sin perder mi implementación?

**Respuesta / orientación obtenida**

Se siguió un proceso de integración controlado: actualizar referencias remotas, integrar `origin/develop`, identificar archivos en conflicto, preservar los cambios nuevos de `develop`, reincorporar únicamente la funcionalidad de HU-08, verificar que no quedaran marcadores de conflicto y ejecutar toda la suite de pruebas antes del commit.

**Aplicación en el proyecto**

Se resolvieron conflictos en diferentes momentos sobre `.env.example`, `usuarios/tests.py`, `usuarios/urls.py` y `usuarios/views.py`.

---

### Consulta 18 – Verificación de conflictos resueltos

**Pregunta realizada**

> ¿Cómo puedo comprobar que ya no quedaron conflictos dentro de los archivos?

**Respuesta / orientación obtenida**

Se utilizaron los siguientes comandos:

```powershell
git diff --check
```

```powershell
Select-String -Path usuarios/urls.py,usuarios/views.py -Pattern "<<<<<<<|=======|>>>>>>>"
```

Si no se obtiene salida, no quedan marcadores de conflicto ni errores de espacios detectados por Git.

**Aplicación en el proyecto**

Ambos comandos finalizaron sin resultados, permitiendo marcar los archivos como resueltos.

---

## 6. Resolución de errores del entorno

### Consulta 19 – Error `No module named 'material'`

**Problema encontrado**

Al ejecutar `python manage.py test` se obtuvo:

```text
ModuleNotFoundError: No module named 'material'
```

**Pregunta realizada**

> ¿Por qué aparece este error después de integrar los últimos cambios de `develop`?

**Respuesta / orientación obtenida**

Se comprobó primero si la dependencia estaba declarada en `requirements.txt` mediante:

```powershell
Select-String -Path requirements.txt -Pattern "django-material|material"
```

El archivo contenía:

```text
django-material @ git+https://github.com/viewflow/django-material.git@80dc63d05677a7714ec95a5230acc643af994fda
```

Por lo tanto, no correspondía modificar el código ni instalar un paquete diferente. El entorno virtual local simplemente no tenía instaladas todavía las nuevas dependencias incorporadas por `develop`.

La solución fue ejecutar:

```powershell
python -m pip install -r requirements.txt
```

**Aplicación en el proyecto**

Luego de instalar las dependencias, Django volvió a iniciar correctamente.

---

## 7. Verificación final

Después de resolver los conflictos e instalar las dependencias actualizadas, se ejecutó:

```powershell
python manage.py test
```

Resultado:

```text
Found 65 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................................................................
----------------------------------------------------------------------
Ran 65 tests in 1.480s

OK
Destroying test database for alias 'default'...
```

También se ejecutó:

```powershell
python manage.py check
```

Resultado:

```text
System check identified no issues (0 silenced).
```

Finalmente, los cambios fueron enviados a la rama `feature/hu-08-asignar-rol` y el Pull Request de HU-08 quedó sin conflictos para ser integrado a `develop`.

---

## 8. Principales aportes de la IA

La IA funcionó como herramienta de apoyo para analizar problemas, revisar alternativas y orientar procedimientos técnicos. Los aportes principales fueron la explicación de OpenID Connect y del flujo Authorization Code con PKCE, la configuración conceptual de Keycloak, el diseño de control de acceso basado en roles, el uso de la Keycloak Admin REST API, el diseño de validaciones de HU-08, la definición de casos de prueba, la orientación en comandos Git, la resolución de conflictos entre ramas, el diagnóstico de dependencias faltantes y la revisión de los resultados de las pruebas.

---

## 9. Validación humana y responsabilidad sobre el código

Las respuestas proporcionadas por la IA no fueron incorporadas automáticamente al proyecto.

Cada propuesta fue contrastada mediante ejecución sobre el entorno local, pruebas automatizadas, pruebas manuales con Keycloak, revisión de errores, revisión de los criterios de aceptación e integración mediante Git y Pull Requests.

La responsabilidad sobre las decisiones finales, configuración y código entregado corresponde a la integrante del proyecto.

---

## 10. Resultado

El uso de IA permitió acelerar la comprensión de herramientas y resolver problemas técnicos durante el Sprint 1, principalmente en la integración entre **Django, Keycloak y Git**.

La implementación fue verificada mediante la suite completa del proyecto, obteniendo como resultado final:

**65 pruebas ejecutadas correctamente y 0 errores reportados por `python manage.py check`.**
