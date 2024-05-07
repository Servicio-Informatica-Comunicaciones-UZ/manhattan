#!/bin/sh
set -e

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    echo "Apply database migrations"
    sleep 1
    python manage.py migrate --noinput
fi

# Ejecutar el worker de Huey en segundo plano - ¿Sería mejor crear un contenedor independiente?
echo "Lanzando el worker de Huey"
nohup python manage.py run_huey &

exec "$@"
