# global-exchange

# HU-01 - Registro de usuario

## Descripción

El registro de usuarios se realiza mediante Keycloak como proveedor externo de identidad.

La aplicación Django no crea usuarios directamente, sino que redirige al usuario hacia el formulario de registro de Keycloak.

## Flujo de registro

1. El usuario accede a la opción de registro desde la aplicación.
2. Django genera la URL de registro de Keycloak.
3. El usuario completa sus datos en Keycloak.
4. Keycloak procesa la creación del usuario.
5. El usuario queda registrado en el Realm configurado.

## Configuración utilizada

- Proveedor de identidad: Keycloak
- Realm: `global-exchange`
- Cliente: `global-exchange-web`
- Flujo utilizado: OpenID Connect Authorization Code Flow

## Implementación

La lógica del registro se encuentra en:
usuarios/views.py



La función `registro()` genera la URL de registro de Keycloak utilizando la configuración definida en Django.

## Pruebas realizadas

Se implementaron pruebas automáticas para verificar:

- Existencia de la ruta de registro.
- Redirección hacia Keycloak.
- Uso del endpoint correcto.
- Uso del cliente configurado.
- Parámetros necesarios del flujo OpenID Connect.

Resultado:
7 tests ejecutados correctamente