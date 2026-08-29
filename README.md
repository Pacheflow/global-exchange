# global-exchange

## Verificación de correo de usuarios (HU-02)

La aplicación utiliza Keycloak como proveedor de identidad para gestionar el registro y la verificación de correo de los usuarios.

## Configuración implementada

- Realm configurado: `global-exchange`
- Verificación de correo habilitada en Keycloak.
- Servidor SMTP configurado mediante Mailpit.
- Host SMTP: `mailpit`
- Puerto SMTP: `1025`
- Correo remitente: `noreply@globalexchange.com`

## Flujo de verificación

1. El usuario inicia el registro desde la aplicación.
2. Django redirige el proceso de registro hacia Keycloak.
3. Keycloak crea la cuenta del usuario.
4. Keycloak envía un correo de verificación.
5. El usuario abre el enlace recibido.
6. La cuenta queda marcada como verificada.

## Entorno de pruebas

Los correos enviados por Keycloak pueden visualizarse mediante Mailpit:
http://localhost:8025

## Configuración persistente

La configuración del Realm se encuentra exportada en:
keycloak/global-exchange-realm.json

y es cargada automáticamente mediante Docker Compose:


docker compose up -d