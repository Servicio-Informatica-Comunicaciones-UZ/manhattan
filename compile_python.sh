#!/bin/bash
# Script para descargar, compilar e instalar Python 3.7 en Debian/Ubuntu/Linux Mint

# Actualizar el sistema
apt update
apt -y upgrade

# Instalar las herramientas necesarias para compilar el código fuente de Python
apt install -y build-essential
apt install -y libbz2-dev libffi-dev libgdbm-dev liblzma-dev libncurses5-dev \
    libncursesw5-dev libnss3-dev libreadline-dev libsqlite3-dev libssl-dev tk-dev \
    uuid-dev zlib1g-dev

# Descargar y descomprimir Python
cd /usr/local/src
wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz
tar xzf Python-3.7.2.tgz

# Compilar e instalar Python
cd Python-3.7.2
./configure --enable-optimizations --with-ensurepip=install
make -j8
make altinstall
