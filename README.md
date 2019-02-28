Proyecto Manhattan
==================

> First we take Manhattan, then we take Berlin.

Manhattan es una aplicación web para gestionar los proyectos de Innovación Docente.
Está desarrollada con [Django](https://www.djangoproject.com/) 2 y mucho cariño ♥.


Requisitos
----------

* Python 3.7 o superior (el script `compile_python.sh` lo instala en Debian o Ubuntu).
* [pip](https://pip.pypa.io/en/stable/installing/) (puede venir con la instalación de Python).
* [pipenv](https://github.com/pypa/pipenv) (se puede instalar con `sudo -H pip3.7 install pipenv`).
* Paquetes libxmlsec1-dev pkg-config
* Un SGBD aceptado por Django (vg PostgreSQL o MariaDB).
  La configuración MariaDB/MySQL deberá incluir:
  ```
  innodb_file_per_table
  innodb_file_format = Barracuda
  innodb_large_prefix
  innodb_default_row_format = dynamic
  ```


Instalación
-----------

```shell
cd manhattan
pipenv --python 3.7 install --dev
```


Configuración inicial
---------------------

Configurar la base de datos en la sección `DATABASES` de `manhattan_project/settings.py`.
Configurar los datos para el _Single Sign On_ (SAML).

```shell
pipenv shell
./manage.py migrate
./manage.py createsuperuser
```


Ejecución
---------

```shell
pipenv shell
./manage.py runserver
```
