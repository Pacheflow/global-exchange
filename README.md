# Global Exchange

## Entorno completo con Docker

No es necesario instalar Python ni PostgreSQL en la computadora. El entorno incluye:

- Django sobre Python 3.13.
- PostgreSQL 17 con almacenamiento persistente.
- Keycloak 26.7.2 conectado a PostgreSQL.
- Instalación automática de dependencias Python.
- Espera de disponibilidad y migraciones automáticas de Django.
- Importación automática del realm de Keycloak durante el primer inicio.

### Inicio rápido

1. Instalar e iniciar Docker Desktop.
2. Opcionalmente, copiar `.env.example` como `.env` y cambiar las contraseñas.
3. Desde la raíz del repositorio ejecutar:

   ```powershell
   docker compose up --build -d
   ```

4. Consultar el estado:

   ```powershell
   docker compose ps
   docker compose logs -f web
   ```

La aplicación queda en `http://localhost:8000` y Keycloak en
`http://localhost:8080`. PostgreSQL permanece aislado en la red interna de Docker
y no necesita ocupar el puerto `5432` de Windows.

Para ejecutar comandos Django no se usa el Python de Windows:

```powershell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test
docker compose exec web python manage.py createsuperuser
```

Para detener los contenedores conservando los datos:

```powershell
docker compose down
```

Los datos solo se eliminan si se solicita expresamente con
`docker compose down --volumes`.

## Integración con Keycloak

El contenedor importa automáticamente `keycloak/global-exchange-realm.json` durante
el primer inicio. El cliente `global-exchange-web` admite callbacks y logout en
`http://localhost:8000/*`.

Para utilizar la pantalla **Usuarios**, la cuenta autenticada necesita los roles
`view-users`, `query-users` y `manage-users` del cliente `realm-management`.

La selección de cliente lee el atributo multivalor `clientes` (o `client_ids`) del
token. El módulo de clientes puede poblarlo con sus identificadores sin acoplar la
interfaz a una implementación específica.
