#!/bin/sh
set -e

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    echo "Apply database migrations"
    sleep 1
    python manage.py migrate --noinput
fi

# Obtener UID/GID del entorno o usar 1501 por defecto
TARGET_UID=${UWSGI_UID:-1501}
TARGET_GID=${UWSGI_GID:-1501}

# Ajustar permisos si se ejecuta como root
if [ "$(id -u)" = '0' ]; then
    echo "Ajustando permisos de carpetas de datos (media y cola) para el usuario $TARGET_UID:$TARGET_GID..."
    chown -R $TARGET_UID:$TARGET_GID /code/media /code/cola
    touch /code/cola/huey.log
    chown $TARGET_UID:$TARGET_GID /code/cola/huey.log
fi

# Ejecutar el worker de Huey en segundo plano como usuario configurado
echo "Lanzando el worker de Huey como usuario $TARGET_UID..."
nohup python -c "import os; os.setgid($TARGET_GID); os.setuid($TARGET_UID); os.execlp('python', 'python', 'manage.py', 'run_huey')" > /code/cola/huey.log 2>&1 &

exec "$@"
