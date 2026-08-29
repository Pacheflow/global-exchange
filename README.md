# Global Exchange

Frontend Django del Sprint 1 con autenticación OpenID Connect mediante Keycloak.

## Puesta en marcha

1. Copiar `.env.example` a `.env` y completar las credenciales locales.
2. Iniciar Keycloak: `docker compose up -d`.
3. El contenedor importa automáticamente `keycloak/global-exchange-realm.json` al primer inicio.
4. Instalar dependencias: `pip install -r requirements.txt`.
5. Ejecutar migraciones: `python manage.py migrate`.
6. Iniciar Django: `python manage.py runserver`.
7. Abrir `http://localhost:8000/`.

El cliente `global-exchange-web` ya admite callbacks y logout en `http://localhost:8000/*`.
Para usar la pantalla **Usuarios**, la cuenta autenticada necesita roles del cliente
`realm-management`: `view-users`, `query-users` y `manage-users`.

La selección de cliente lee el atributo multivalor `clientes` (o `client_ids`) del token
de usuario. El módulo de clientes puede poblar ese atributo con sus identificadores sin
acoplar las pantallas a un modelo todavía inexistente.

## Pruebas

`python manage.py test`
