# Documentación de uso de Inteligencia Artificial

**Proyecto:** Global Exchange  
**Sprint:** Sprint 1 — HU-01 a HU-16  
**Integrante:** Axel Pacheco

---

## 1. Objetivo de esta documentación

Este documento registra el uso de herramientas de Inteligencia Artificial como apoyo durante el desarrollo, integración, depuración y validación del proyecto **Global Exchange**, correspondiente al **Sprint 1 (HU-01 a HU-16)**.

La Inteligencia Artificial fue utilizada principalmente para analizar problemas técnicos, comprender errores, revisar alternativas de implementación, orientar la integración con Keycloak, apoyar la revisión de pruebas automatizadas, analizar configuraciones de Docker y PostgreSQL, asistir en procedimientos de Git y colaborar en la preparación de la documentación del proyecto.

Las decisiones finales, ejecución de comandos, incorporación de cambios, pruebas y validaciones fueron realizadas sobre el proyecto real por el equipo.

---

## 2. Alcance del Sprint 1

El trabajo documentado corresponde al alcance del Sprint 1, comprendido por las historias de usuario **HU-01 a HU-16**.

Durante el desarrollo se trabajaron principalmente aspectos relacionados con:

- registro y verificación de usuarios;
- autenticación mediante Keycloak;
- integración OIDC y PKCE;
- gestión de accesos y roles;
- operaciones administrativas relacionadas con usuarios y roles;
- gestión de clientes;
- asociación entre usuarios y clientes;
- selección del cliente;
- control de permisos;
- validación y pruebas del sistema.

Las funcionalidades correspondientes a sprints posteriores no fueron consideradas parte del objetivo de esta entrega.

---

## 3. Herramientas de Inteligencia Artificial utilizadas

Durante el desarrollo se utilizaron principalmente:

- **ChatGPT**, como asistente para análisis, diagnóstico, revisión técnica, planificación de pruebas y documentación.
- **Codex / agente de código**, como asistente para inspección del repositorio, ejecución de comandos, análisis de código, corrección de errores y validación mediante pruebas.

Las herramientas fueron utilizadas como apoyo al desarrollo y no como sustituto de la revisión del equipo.

---

# 4. Registro de consultas y usos relevantes

## Consulta 1 – Análisis del alcance del Sprint

**Objetivo**

Utilizar IA para determinar qué funcionalidades debían formar parte del Sprint 1 y evitar incorporar funcionalidades pertenecientes a sprints posteriores.

**Pregunta / tarea realizada**

> Analizar el sistema de Global Exchange y determinar qué funcionalidades corresponden al Sprint 1, considerando las HU-01 a HU-16, y qué funcionalidades deben quedar fuera del alcance de esta entrega.

**Orientación obtenida**

Se recomendó diferenciar entre funcionalidades ya existentes parcialmente en el sistema y aquellas que realmente debían presentarse como parte del Sprint 1.

También se identificó la necesidad de priorizar la estabilidad funcional y evitar modificaciones innecesarias del menú, diseño y funcionalidades de otros sprints.

**Aplicación en el proyecto**

Esta orientación permitió mantener el foco en HU-01 a HU-16 y evitar agregar funcionalidades que no fueran necesarias para esta entrega.

---

## Consulta 2 – Integración de Django con Keycloak

**Objetivo**

Comprender y revisar la integración entre Django y Keycloak.

**Pregunta / tarea realizada**

> Revisar cómo debía funcionar la autenticación de Global Exchange utilizando Keycloak y cómo debía comunicarse Django con el proveedor de identidad.

**Orientación obtenida**

Se revisó la separación de responsabilidades entre Django y Keycloak:

- Keycloak administra la identidad y autenticación.
- Django administra la lógica propia de la aplicación.
- OIDC se utiliza para el flujo de autenticación.
- PKCE protege el flujo de autorización.
- Los roles proporcionados por Keycloak pueden utilizarse para determinar permisos dentro de la aplicación.

**Aplicación en el proyecto**

La orientación fue utilizada para revisar y validar el funcionamiento del login, callback, sesiones y autorización basada en roles.

---

## Consulta 3 – Roles y control de acceso

**Objetivo**

Analizar el comportamiento esperado para usuarios con diferentes roles.

**Pregunta / tarea realizada**

> Revisar cómo debe funcionar el acceso de usuarios con diferentes roles y qué debe ocurrir cuando un usuario autenticado intenta acceder a una operación para la que no tiene permisos.

**Orientación obtenida**

Se diferenció entre:

- usuario no autenticado;
- usuario autenticado sin permisos suficientes;
- usuario autenticado con el rol requerido.

También se revisó el uso de respuestas HTTP apropiadas:

- `401 Unauthorized` para solicitudes sin autenticación válida;
- `403 Forbidden` para usuarios autenticados sin autorización suficiente.

**Aplicación en el proyecto**

Estos criterios fueron utilizados para validar las restricciones de acceso de las funcionalidades de usuarios y clientes.

---

## Consulta 4 – Operaciones administrativas de Keycloak

**Objetivo**

Revisar la comunicación de Django con la API administrativa de Keycloak.

**Pregunta / tarea realizada**

> Analizar cómo debe obtener Django un token administrativo para realizar operaciones sobre usuarios y roles mediante Keycloak.

**Orientación obtenida**

Se revisó el uso de un cliente administrativo separado y el flujo de credenciales de cliente para obtener un token destinado a operaciones administrativas.

También se revisó que los secretos administrativos se mantuvieran mediante variables de entorno y no fueran incorporados al repositorio.

**Aplicación en el proyecto**

Esta orientación fue utilizada para implementar y revisar las operaciones administrativas relacionadas con usuarios y roles.

---

## Consulta 5 – Diagnóstico de errores en `usuarios/views.py`

**Objetivo**

Analizar errores encontrados durante la ejecución y revisión del código de usuarios.

**Pregunta / tarea realizada**

> Revisar el error encontrado en `usuarios/views.py`, determinar su causa y proponer una corrección sin modificar innecesariamente el comportamiento existente.

**Orientación obtenida**

Se analizó el código existente para localizar la causa del problema y se priorizó una corrección localizada.

Se evitó modificar OIDC, PKCE, Keycloak, frontend u otras funcionalidades que no estuvieran relacionadas con el problema.

**Aplicación en el proyecto**

La corrección fue incorporada y posteriormente validada mediante la suite automatizada de pruebas.

---

## Consulta 6 – Problemas de tipado en `usuarios/tests.py`

**Objetivo**

Resolver diagnósticos de Pylance/Pyright sin alterar el comportamiento de las pruebas.

**Pregunta / tarea realizada**

> Corregir los errores de tipado de `usuarios/tests.py` utilizando los tipos reales de Django siempre que sea posible y evitando soluciones artificiales.

**Orientación obtenida**

Se revisó inicialmente una solución basada en Protocols personalizados y posteriormente se determinó que dicha solución era una sobreabstracción.

Se priorizó el uso de los tipos reales de Django y `typing.cast()` únicamente en puntos concretos donde era necesario.

También se revisó la compatibilidad con:

- `assertRedirects()`;
- `assertContains()`;
- `assertNotContains()`;
- `response.status_code`;
- `response.url`;
- `response.json()`;
- `response.context`;
- `response.cookies`.

**Aplicación en el proyecto**

Los diagnósticos de `usuarios/tests.py` fueron corregidos sin modificar las assertions ni el comportamiento de las pruebas.

---

## Consulta 7 – Validación de respuestas de Keycloak

**Objetivo**

Analizar problemas de robustez en `usuarios/keycloak.py`.

**Pregunta / tarea realizada**

> Revisar qué puede ocurrir si la respuesta de Keycloak al solicitar el token administrativo es inválida, no contiene `access_token` o contiene un `expires_in` incorrecto.

**Orientación obtenida**

Se recomendó validar explícitamente la respuesta antes de utilizar sus valores.

Se contemplaron:

- respuesta que no sea un diccionario;
- ausencia de `access_token`;
- `access_token` vacío o con tipo incorrecto;
- `expires_in` no convertible a entero.

**Aplicación en el proyecto**

Se incorporaron las validaciones correspondientes utilizando el `KeycloakError` existente.

La modificación fue posteriormente verificada mediante las pruebas automatizadas.

---

# 5. Diagnóstico de Docker y PostgreSQL

## Consulta 8 – Error al ejecutar las pruebas desde Windows

**Problema encontrado**

Al ejecutar:

```powershell
python manage.py test
se obtuvo:

Got an error creating the test database:
se ha denegado el permiso para crear la base de datos

Análisis realizado

Se utilizó IA para determinar a qué servidor PostgreSQL estaba conectándose Django.

La comprobación mostró que la ejecución directa desde Windows utilizaba:

host: localhost
port: 5432

y que la conexión correspondía a una instalación local de PostgreSQL.

También se verificó la configuración del PostgreSQL utilizado por Docker.

Solución

Se determinó que las pruebas debían ejecutarse dentro del contenedor de Django para utilizar el PostgreSQL definido por Docker Compose:

docker compose exec web python manage.py test

Resultado

La suite se ejecutó correctamente:

Found 96 test(s).

Ran 96 tests

OK

Destroying test database for alias 'default'...
6. Validación del ambiente de desarrollo
Consulta 9 – Verificación del entorno Docker

Objetivo

Comprobar que los servicios necesarios para el desarrollo estuvieran correctamente montados y funcionando.

Se revisaron:

Django;
PostgreSQL;
Keycloak;
Mailpit;
healthchecks;
migraciones;
dependencias;
configuración de Docker.

Se utilizaron comprobaciones como:

docker compose ps
docker compose config --quiet
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web pip check

Resultado

Los servicios principales quedaron en estado healthy y las verificaciones no reportaron problemas.

7. Ambiente de producción
Consulta 10 – Cumplimiento del requisito AMB

Objetivo

Determinar si el proyecto cumplía el requisito de disponer de ambientes de desarrollo y producción montados y funcionando.

Pregunta / tarea realizada

Auditar el repositorio y determinar si existen ambientes de desarrollo y producción montados y funcionando, sin modificar funcionalidades del Sprint 1.

Análisis realizado

La auditoría inicial determinó que el proyecto disponía de un ambiente de desarrollo basado en Docker Compose, pero no tenía inicialmente una configuración de producción separada.

Se determinó que era necesario diferenciar ambos ambientes.

Aplicación en el proyecto

Se implementó una configuración productiva separada mediante:

compose.prod.yaml;
.env.production.example;
Gunicorn;
WhiteNoise;
configuración productiva de Django;
DEBUG=False;
variables de entorno para secretos;
PostgreSQL con persistencia independiente;
Keycloak configurado para producción;
imagen sin bind mount del código.

La configuración productiva fue levantada y probada de manera independiente del ambiente de desarrollo.

Resultado

Se verificó que tanto el ambiente de desarrollo como el de producción podían ser montados y ejecutados correctamente.

8. Validación de pruebas automatizadas
Consulta 11 – Auditoría de la suite

Objetivo

Comprobar que las modificaciones realizadas no hubieran roto funcionalidades existentes del sistema.

Se solicitó analizar los resultados de las pruebas después de las correcciones realizadas.

Resultado

La suite completa del proyecto obtuvo:

Found 96 test(s).

Ran 96 tests

OK

También se verificó:

System check identified no issues (0 silenced).

Las migraciones fueron verificadas mediante:

No changes detected

Y las dependencias mediante:

No broken requirements found.
9. Revisión del alcance antes de la entrega

Durante el cierre del Sprint 1 se utilizó IA para revisar que las modificaciones realizadas no introdujeran funcionalidades innecesarias.

Se establecieron como criterios:

mantener el alcance en HU-01 a HU-16;
no implementar funcionalidades de sprints posteriores;
no modificar el menú sin necesidad;
no realizar cambios visuales que no fueran necesarios;
no modificar OIDC/PKCE sin una causa concreta;
no agregar abstracciones innecesarias;
validar las modificaciones mediante pruebas.

Cuando una propuesta de IA implicaba modificaciones innecesarias o fuera del alcance, se revisó, simplificó o descartó.

10. Principales aportes de la IA

La Inteligencia Artificial fue utilizada principalmente para:

analizar errores de Django;
analizar problemas de tipado;
revisar la integración con Keycloak;
comprender OIDC y PKCE;
analizar autorización basada en roles;
revisar operaciones administrativas de Keycloak;
diagnosticar problemas de PostgreSQL y Docker;
orientar la ejecución de pruebas;
revisar configuraciones de desarrollo y producción;
apoyar procedimientos de Git;
revisar el alcance del Sprint 1;
apoyar la documentación técnica.
11. Validación humana y responsabilidad sobre el código

Las respuestas y propuestas generadas por las herramientas de IA no fueron incorporadas automáticamente.

Cada modificación fue revisada por el equipo y, cuando correspondía, validada mediante:

ejecución del sistema;
pruebas automatizadas;
comprobaciones de Django;
comprobaciones de Docker;
revisión de configuración;
pruebas manuales;
revisión de cambios mediante Git.

Las propuestas que modificaban innecesariamente el proyecto, introducían funcionalidades fuera del alcance o generaban una complejidad innecesaria fueron descartadas o simplificadas.

La responsabilidad final sobre el código, las decisiones técnicas, las pruebas y la entrega corresponde al equipo del proyecto.

12. Resultado final

El uso de Inteligencia Artificial permitió acelerar el análisis de problemas técnicos y apoyar distintas etapas del desarrollo del Sprint 1.

La IA fue utilizada como herramienta de asistencia y revisión, mientras que la implementación y validación final fueron realizadas sobre el proyecto real.

Como resultado de la validación final se obtuvo:

96/96 pruebas automatizadas correctas.
Django check sin problemas.
Migraciones sin cambios pendientes.
Dependencias sin conflictos.
Ambiente de desarrollo funcionando.
Ambiente de producción montado y validado.
Integración con Keycloak verificada.
Cambios revisados antes del cierre de la entrega.

El alcance documentado corresponde al Sprint 1 — HU-01 a HU-16.