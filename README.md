# Proyecto Manhattan

> First we take Manhattan, then we take Berlin.

Manhattan es una aplicación web para gestionar los proyectos de Innovación Docente.
Está desarrollada con [Django](https://www.djangoproject.com/) 2, mucho ♥, bastante ☕ y un poco de magia 🧙.

## Requisitos

- Python 3.7 o superior. En Debian se puede instalar con el script `compile_python.sh`. En Ubuntu instalar los paquetes python3.7 libpython3.7-dev.
- [pip](https://pip.pypa.io/en/stable/installing/) (puede venir con la instalación de Python).
- [pipenv](https://github.com/pypa/pipenv) (se puede instalar con `sudo -H pip3 install pipenv`).
- Paquetes libxmlsec1-dev pkg-config
- Un SGBD aceptado por Django (vg PostgreSQL o MariaDB).
  Para MariaDB/MySQL instalar el paquete libmariadb-dev-compat o libmysqlclient-dev. La configuración deberá incluir:

  ```ini
  innodb_file_per_table
  innodb_file_format = Barracuda
  innodb_large_prefix
  innodb_default_row_format = dynamic
  ```

## Instalación

```shell
cd manhattan
pipenv --python 3.7 install --dev
```

## Configuración inicial

1. Configurar las bases de datos en el fichero `.env` y la sección `DATABASES` de `manhattan_project/settings.py`.
2. Configurar los datos para el correo, y la URL del sitio.
3. Configurar los datos para el _Single Sign On_ (SAML).
4. Ejecutar

    ```shell
    pipenv shell
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py loaddata seed
    ```

## Servidor web para desarrollo

```shell
pipenv shell
./manage.py runserver [<IP>[:<puerto>]]
```
