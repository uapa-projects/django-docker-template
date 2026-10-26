#!/bin/sh

# Aplica las migraciones a la base de datos
python manage.py migrate --noinput

# Recolecta archivos estáticos
python manage.py collectstatic --noinput

# Ejecuta el comando principal (Gunicorn)
exec "$@"
