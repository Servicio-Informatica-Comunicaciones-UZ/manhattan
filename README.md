# Proyecto Manhattan

> First we take Manhattan, then we take Berlin.

Manhattan es una aplicación web para gestionar los proyectos de Innovación Docente.
Está desarrollada con [Django](https://www.djangoproject.com/) 3, mucho ♥, bastante ☕ y un poco de magia 🧙.

## Requisitos

1. Python 3.7 o superior. En Debian o Ubuntu instalar los paquetes `python3.7-dev` y `python3-distutils`.
2. [pip](https://pip.pypa.io/en/stable/installing/), instalador de paquetes de Python. (Puede venir con la instalación de Python).
3. [pipenv](https://github.com/pypa/pipenv) para crear un entorno virtual para Python y facilitar el trabajo.

   Se puede instalar con `sudo -H pip3 install pipenv`.
4. Paquetes `libxmlsec1-dev`, `pandoc` y `pkg-config`.
5. Un servidor de bases de datos aceptado por Django (vg PostgreSQL o MariaDB).

   Para MariaDB/MySQL instalar el paquete `libmariadb-dev` o `libmysqlclient-dev`.

   En versiones antiguas de MariaDB/MySQL, la configuración deberá incluir, si es necesario:

   ```ini
   innodb_file_per_table = On  # Default on MariaDB >= 5.5
   innodb_file_format = Barracuda  # Deprecated in MariaDB 10.2
   innodb_large_prefix  # Deprecated on MariaDB 10.2, Removed in MariaDB 10.3.1
   innodb_default_row_format = dynamic  # Default on MariaDB >= 10.2.2
   ```

## Instalación

```shell
git clone https://gitlab.unizar.es/InnovacionDocente/manhattan.git
cd manhattan
pipenv install [--dev]
```

## Configuración inicial

1. Crear una base de datos.  
   En MariaDB/MySQL sería algo así:

   ```sh
   sudo mysql -u root
   ```

   ```sql
   CREATE DATABASE nombre CHARACTER SET = 'utf8mb4' COLLATE utf8mb4_unicode_ci;
   GRANT ALL PRIVILEGES ON nombre.* TO usuario@localhost IDENTIFIED BY 'abretesesamo';
   quit
   ```

2. Copiar los ficheros de ejemplo `.env-sample` y `manhattan_project/settings-sample.py`.  Configurar las bases de datos en el fichero `.env` y la sección `DATABASES` de `settings.py`.
3. Configurar en `settings.py` los datos para el correo, y la URL del sitio (`SITE_URL`).
4. Configurar los datos para el _Single Sign On_ (SAML).
5. Ejecutar

    ```shell
    source .env
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

Abrir la URL con el navegador web, autenticarse como superusuario y, en la interfaz de administración de Django, añadir al superusuario al grupo `Gestores`.
