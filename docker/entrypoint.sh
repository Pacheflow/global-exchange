#!/bin/sh

echo "Esperando PostgreSQL..."

python <<'PY'
import os
import time
import psycopg

config = {
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "host": os.environ["DB_HOST"],
    "port": os.environ.get("DB_PORT", "5432"),
}

for attempt in range(30):
    try:
        with psycopg.connect(**config):
            print("PostgreSQL disponible.")
            break
    except psycopg.OperationalError:
        if attempt == 29:
            raise
        time.sleep(1)
PY

echo "Aplicando migraciones..."

python manage.py migrate --noinput

exec "$@"