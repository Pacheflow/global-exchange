# Documentación de uso de Inteligencia Artificial

**Integrante:** Elias Hirano

## 1. Objetivo de esta documentación

Este documento registra el uso de Inteligencia Artificial como herramienta de apoyo durante el desarrollo de las historias de usuario relacionadas con la gestión de clientes del proyecto **Global Exchange**.

La IA fue utilizada principalmente para comprender los requisitos de las historias de usuario, aclarar dudas sobre Django y PostgreSQL, revisar la estructura del módulo de clientes, orientar la creación de pruebas, verificar criterios de aceptación y apoyar el uso de Git, Docker y la resolución de conflictos.

Las decisiones finales, modificaciones realizadas, ejecución de comandos y validaciones fueron realizadas sobre el proyecto real.

---

## 2. Historias de usuario trabajadas

- **HU-09 – Registrar Cliente**
- **HU-10 – Consultar Cliente**
- **HU-11 – Editar Cliente**
- **HU-12 – Dar de Baja Cliente**
- **HU-13 – Segmentar Cliente**

---

## 3. Registro de consultas realizadas a la IA

### Consulta 1 – Interpretación de las historias de usuario

**Pregunta realizada**

> ¿Me puedes ayudar a entender qué debería hacer en cada una de mis historias HU-09 a HU-13 y cómo se relacionan entre sí?

**Respuesta / orientación obtenida**

Se separaron las funcionalidades principales del módulo de clientes: registrar, consultar, modificar información, realizar una baja lógica y asignar una categoría comercial.

También se recomendó trabajar las historias sobre un mismo modelo `Cliente`, agregando los formularios, vistas y rutas necesarias según cada funcionalidad.

**Aplicación en el proyecto**

Esta orientación fue utilizada para organizar el desarrollo del módulo `clientes` y trabajar las historias de manera progresiva.

---

### Consulta 2 – Datos necesarios para representar un cliente

**Pregunta realizada**

> ¿Qué campos debería tener el modelo Cliente teniendo en cuenta los requisitos que tenemos?

**Respuesta / orientación obtenida**

Se revisaron los datos requeridos para representar un cliente, entre ellos:

- nombre o razón social;
- tipo de persona;
- documento;
- estado;
- categoría;
- fecha de registro.

También se revisó qué campos debían ser obligatorios y cuáles podían tener valores predeterminados.

**Aplicación en el proyecto**

Se utilizó esta estructura como referencia para revisar el modelo `Cliente`.

---

### Consulta 3 – Tipo de dato del documento

**Pregunta realizada**

> ¿Conviene guardar el documento del cliente como número o como texto?

**Respuesta / orientación obtenida**

Se analizó que el documento no necesariamente debía limitarse únicamente a números, ya que determinados identificadores pueden incluir otros caracteres.

Por esa razón, se recomendó mantenerlo como un campo de texto y controlar que no se repita.

**Aplicación en el proyecto**

El campo `documento` se mantuvo como texto y con restricción de unicidad.

---

### Consulta 4 – Registro de clientes

**Pregunta realizada**

> Para registrar un cliente en Django, ¿qué partes necesito además del modelo?

**Respuesta / orientación obtenida**

Se explicó la relación básica entre:

- modelo;
- `ModelForm`;
- vista;
- URL;
- template.

La vista recibe el formulario, verifica los datos ingresados y, si son válidos, guarda el cliente en la base de datos.

**Aplicación en el proyecto**

Se utilizó este flujo como guía para revisar la implementación de la **HU-09 – Registrar Cliente**.

---

### Consulta 5 – Validación de documentos duplicados

**Pregunta realizada**

> ¿Cómo puedo evitar que se registren dos clientes con el mismo documento?

**Respuesta / orientación obtenida**

Se indicó que la restricción de unicidad podía definirse desde el propio modelo para que Django también la validara mediante el formulario.

**Aplicación en el proyecto**

Se verificó que intentar registrar un documento existente fuera rechazado.

---

### Consulta 6 – Consulta y búsqueda de clientes

**Pregunta realizada**

> ¿Cómo puedo hacer para listar los clientes y permitir buscar uno por nombre?

**Respuesta / orientación obtenida**

Se explicó que podía obtenerse el listado mediante el ORM de Django y aplicar un filtro cuando el usuario ingresara un término de búsqueda.

Se recomendó utilizar una búsqueda que no dependiera de mayúsculas o minúsculas.

**Aplicación en el proyecto**

La orientación se utilizó para verificar la **HU-10 – Consultar Cliente**, incluyendo el listado y búsqueda por nombre.

---

### Consulta 7 – Edición de clientes

**Pregunta realizada**

> ¿Puedo reutilizar el formulario de registro para editar un cliente o necesito hacer otro completamente distinto?

**Respuesta / orientación obtenida**

Se explicó que un `ModelForm` puede reutilizarse indicando la instancia existente que se desea modificar.

De esta forma se evita duplicar lógica innecesariamente.

**Aplicación en el proyecto**

Se utilizó este funcionamiento para la **HU-11 – Editar Cliente**.

---

### Consulta 8 – Baja lógica de clientes

**Pregunta realizada**

> El requisito dice dar de baja al cliente, ¿conviene eliminarlo de la base de datos o cambiar su estado?

**Respuesta / orientación obtenida**

Se revisó el concepto de baja lógica. En lugar de eliminar físicamente el registro, se recomendó modificar su estado de `ACTIVO` a `INACTIVO`.

Esto permite conservar la información histórica del cliente.

**Aplicación en el proyecto**

La **HU-12 – Dar de Baja Cliente** fue implementada conservando el registro y modificando únicamente su estado.

---

### Consulta 9 – Segmentación de clientes

**Pregunta realizada**

> ¿Cómo puedo manejar categorías como Minorista, Corporativo y VIP sin escribirlas directamente dentro de cada cliente?

**Respuesta / orientación obtenida**

Se recomendó representar las categorías mediante un modelo independiente y relacionarlo con `Cliente`.

Esto permite administrar las categorías de forma separada y que varios clientes puedan utilizar una misma categoría.

**Aplicación en el proyecto**

La solución se utilizó para la **HU-13 – Segmentar Cliente**.

---

### Consulta 10 – Categorías iniciales

**Pregunta realizada**

> ¿Cómo hago para que Minorista, Corporativo y VIP existan automáticamente cuando se prepara la base de datos?

**Respuesta / orientación obtenida**

Se revisó el uso de una migración de datos para crear categorías iniciales de forma controlada.

También se recomendó evitar crear registros duplicados si la migración se ejecutaba nuevamente.

**Aplicación en el proyecto**

Se incorporó la migración `0002_categorias_iniciales`.

---

## 4. Pruebas del módulo

### Consulta 11 – Casos de prueba

**Pregunta realizada**

> ¿Qué cosas debería probar para asegurarme de que mis historias de clientes funcionan correctamente?

**Respuesta / orientación obtenida**

Se recomendó verificar tanto los casos correctos como situaciones inválidas, por ejemplo:

- creación de clientes;
- documento duplicado;
- campos obligatorios;
- consulta y búsqueda;
- edición;
- baja lógica;
- asignación de categoría;
- cambio de categoría.

**Aplicación en el proyecto**

Se ampliaron las pruebas automatizadas del módulo hasta cubrir las funcionalidades principales de HU-09 a HU-13.

---

### Consulta 12 – Diferencia entre pruebas automáticas y manuales

**Pregunta realizada**

> Si mis tests pasan, ¿igual tengo que probar las páginas desde el navegador?

**Respuesta / orientación obtenida**

Se explicó que las pruebas automatizadas verifican el comportamiento del código, mientras que las pruebas manuales permiten comprobar el flujo completo desde la interfaz.

**Aplicación en el proyecto**

Además de las pruebas automatizadas, se probaron manualmente:

- registro;
- consulta;
- búsqueda;
- edición;
- segmentación;
- baja lógica.

---

## 5. Integración con Git

### Consulta 13 – Actualizar la rama sin perder cambios

**Pregunta realizada**

> Mi grupo actualizó `develop`. ¿Cómo puedo traer esos cambios a mi rama sin perder lo que hice en clientes?

**Respuesta / orientación obtenida**

Se recomendó actualizar primero las referencias remotas y realizar la integración desde la propia rama de trabajo.

También se explicó que un conflicto de Git no significa que se haya perdido código, sino que determinadas diferencias deben resolverse manualmente.

**Aplicación en el proyecto**

Se integró `origin/develop` dentro de `feature/hu-09-registrar-cliente` antes de preparar el Pull Request.

---

### Consulta 14 – Conflictos de Git

**Pregunta realizada**

> ¿Cómo puedo saber qué parte de un archivo pertenece a cada rama cuando Git me muestra un conflicto?

**Respuesta / orientación obtenida**

Se explicaron los marcadores:

```text
<<<<<<<
=======
>>>>>>>
```

y que debía conservarse el contenido necesario de cada lado antes de eliminar dichos marcadores.

**Aplicación en el proyecto**

Se revisaron conflictos existentes en archivos del proyecto y se verificó que no quedaran marcadores antes de continuar.

---

### Consulta 15 – Verificar que no queden conflictos

**Pregunta realizada**

> ¿Hay alguna forma de comprobar que no quedaron marcas de conflicto escondidas en algún archivo?

**Respuesta / orientación obtenida**

Se utilizó una búsqueda de los marcadores de conflicto dentro del repositorio y también:

```powershell
git diff --check
```

para detectar posibles problemas antes de realizar el commit.

**Aplicación en el proyecto**

Las comprobaciones terminaron sin errores antes de subir los cambios.

---

## 6. Docker y entorno de desarrollo

### Consulta 16 – Error al levantar Docker

**Pregunta realizada**

> Docker Compose me muestra un error al leer `compose.yaml`. ¿Cómo puedo saber qué está causando el problema?

**Respuesta / orientación obtenida**

Se revisó el archivo y se detectó que contenía marcas de conflicto de Git que habían quedado dentro del contenido.

También se revisaron otros archivos relacionados con la infraestructura para comprobar si existía el mismo problema.

**Aplicación en el proyecto**

Se corrigieron los conflictos y posteriormente se validó nuevamente la configuración de Docker.

---

### Consulta 17 – Mailpit y Keycloak

**Pregunta realizada**

> Keycloak está configurado para usar Mailpit, pero Docker no tiene ese servicio. ¿Necesito agregarlo?

**Respuesta / orientación obtenida**

Se revisó la configuración existente y se comprobó que Keycloak utilizaba `mailpit` como servidor SMTP.

Se explicó que, para que esa configuración funcionara dentro de Docker, el servicio debía estar disponible en la misma red.

**Aplicación en el proyecto**

Se incorporó Mailpit al entorno y se volvió a levantar Docker para verificar la integración.

---

### Consulta 18 – Verificación de los contenedores

**Pregunta realizada**

> ¿Cómo puedo saber si Django, PostgreSQL, Keycloak y Mailpit realmente levantaron bien?

**Respuesta / orientación obtenida**

Se recomendó comprobar el estado de los contenedores después de ejecutar Docker Compose.

**Aplicación en el proyecto**

Se verificó que los servicios principales estuvieran iniciados correctamente y en estado saludable.

---

## 7. Verificación final

### Consulta 19 – Migraciones dentro de Docker

**Pregunta realizada**

> ¿Cómo puedo comprobar que las migraciones de mi módulo también están aplicadas dentro de Docker?

**Respuesta / orientación obtenida**

Se utilizó:

```powershell
docker compose exec web python manage.py showmigrations clientes
```

**Resultado obtenido**

```text
clientes
 [X] 0001_initial
 [X] 0002_categorias_iniciales
```

---

### Consulta 20 – Ejecutar los tests desde Docker

**Pregunta realizada**

> ¿Cómo puedo comprobar que los tests funcionan también usando el entorno Docker del grupo?

**Respuesta / orientación obtenida**

Se utilizó:

```powershell
docker compose exec web python manage.py test clientes
```

**Resultado obtenido**

```text
Found 20 test(s).
....................
Ran 20 tests

OK
```

---

## 8. Preparación del Pull Request

### Consulta 21 – Rama destino del Pull Request

**Pregunta realizada**

> ¿El Pull Request de mi rama debería ir a `main` o a `develop`?

**Respuesta / orientación obtenida**

De acuerdo con el flujo de trabajo utilizado por el equipo, las ramas `feature` debían integrarse primero en `develop`.

**Aplicación en el proyecto**

Se creó el Pull Request:

```text
feature/hu-09-registrar-cliente
        ↓
develop
```

con el título:

```text
feat: implementar gestión de clientes HU-09 a HU-13
```

---

## 9. Principales aportes de la IA

La Inteligencia Artificial fue utilizada principalmente para resolver dudas durante el desarrollo, comprender conceptos de Django, revisar la estructura de las historias de usuario, proponer casos de prueba, interpretar errores, orientar el uso de Git y Docker y verificar que las funcionalidades desarrolladas correspondieran con los requisitos establecidos.

La IA también fue utilizada como apoyo durante la preparación y validación del Pull Request.

---

## 10. Validación humana y responsabilidad sobre el código

Las respuestas proporcionadas por la IA fueron utilizadas como orientación y no como sustitución de la revisión del proyecto.

Cada propuesta fue comprobada sobre el entorno real mediante ejecución de comandos, revisión del código, pruebas automatizadas, pruebas manuales, validación de migraciones y revisión del funcionamiento mediante Docker.

Las decisiones finales y los cambios incorporados al repositorio fueron revisados antes de ser enviados al Pull Request.

---

## 11. Resultado

Al finalizar la revisión del módulo de clientes:

- Las migraciones `0001_initial` y `0002_categorias_iniciales` se encontraban aplicadas.
- Se ejecutaron **20 pruebas automatizadas correctamente**.
- Se realizaron pruebas manuales de HU-09 a HU-13.
- El entorno Docker fue verificado.
- El Pull Request fue creado desde la rama de clientes hacia `develop`.
