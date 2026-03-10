#!/bin/bash
# Script para levantar los contenedores de Docker inyectando la versión de la aplicación.

# Extraemos la versión de git en el archivo (se ignorará en el nuevo commit)
echo "Generando archivo APP_VERSION.txt..."
git describe --tags --always > APP_VERSION.txt

echo "Versión inyectada:"
cat APP_VERSION.txt

# Construimos la imagen y/o levantamos los contenedores
echo "Construyendo la imagen Docker..."
docker compose build

echo "Deteniendo contenedores actuales..."
docker compose down

echo "Levantando contenedores en segundo plano..."
docker compose up -d

echo "¡Despliegue completado!"
