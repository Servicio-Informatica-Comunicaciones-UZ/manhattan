Proyecto Manhattan
==================

> First we take Manhattan, then we take Berlin.

Manhattan es una aplicación web para gestionar los proyectos de Innovación Docente.
Está desarrollada con [Django](https://www.djangoproject.com/) 3, mucho ♥, bastante ☕ y un poco de magia 🧙.

Requisitos
----------

1. Python 3.8 o superior. En Debian o Ubuntu instalar los paquetes `python3.8-dev` y `python3-distutils`.
2. [pip](https://pip.pypa.io/en/stable/installing/), instalador de paquetes de Python.
   (Puede venir con la instalación de Python).
3. [pipenv](https://github.com/pypa/pipenv) para crear un entorno virtual para Python y facilitar el trabajo.

   Se puede instalar con `sudo -H pip3 install pipenv`.
4. Paquetes `fonts-texgyre`, `libxmlsec1-dev`, `pandoc` y `pkg-config`.
5. Un servidor de bases de datos aceptado por Django (vg PostgreSQL o MariaDB).

   En Debian/Ubuntu:  
   `apt install postgresql`  
   o  
   `apt install mariadb-server mariadb-client libmariadb-dev`  
   o  
   `apt install mysql-server mysql-client libmysqlclient-dev`

   En versiones antiguas de MariaDB/MySQL, la configuración deberá incluir, si es necesario:

   ```ini
   innodb_file_per_table = On  # Default on MariaDB >= 5.5
   innodb_file_format = Barracuda  # Deprecated in MariaDB 10.2
   innodb_large_prefix  # Deprecated on MariaDB 10.2, Removed in MariaDB 10.3.1
   innodb_default_row_format = dynamic  # Default on MariaDB >= 10.2.2
   ```

Instalación
-----------

```shell
git clone https://gitlab.unizar.es/InnovacionDocente/manhattan.git
cd manhattan
pipenv install [--dev]
```

Configuración inicial
---------------------

1. Crear una base de datos.  
   En MariaDB/MySQL sería algo así:

   ```sh
   sudo mysql -u root
   ```

   ```sql
   CREATE DATABASE nombre CHARACTER SET='utf8mb4' COLLATE utf8mb4_unicode_ci;
   GRANT ALL PRIVILEGES ON nombre.* TO usuario@localhost IDENTIFIED BY 'abretesesamo';
   quit
   ```

2. Copiar el fichero de ejemplo `.env-sample`.  Configurar las bases de datos en el fichero `.env`.
3. Copiar el fichero de ejemplo `manhattan_project/settings-sample.py`.  
   Configurar en `settings.py` los datos para el correo, y la URL del sitio (`SITE_URL`).
4. Configurar los datos para el _Single Sign On_ (SAML).
5. Ejecutar

    ```shell
    source .env
    pipenv shell
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py loaddata seed
    ```

6. Abrir la URL con el navegador web, autenticarse como superusuario y,
   en la interfaz de administración de Django, añadir usuarios al grupo `Gestores`
   (incluyendo al superusuario).
7. Activar a los usuarios gestores el atributo `is_staff` para que puedan acceder
   a la interfaz de administración.

Servidor web para desarrollo
----------------------------

```shell
pipenv shell
nohup ./manage.py run_huey &
./manage.py runserver [<IP>[:<puerto>]]
```

Podemos indicar que el superusuario pertenece al colectivo PAS, para que pueda crear proyectos:

```sql
UPDATE accounts_customuser
SET colectivos = '["PAS"]'
WHERE is_superuser = 1;
```

Nueva convocatoria
------------------

Se puede crear una nueva convocatoria desde la interfaz de administración (los usuarios gestores, además de pertenecer
al grupo `Gestores` deben tener activado el atributo `is_staff` para que puedan acceder a esta interfaz).

Se pueden clonar los programas y líneas de la convocatoria anterior con estas órdenes:

```sql
INSERT INTO indo_programa (nombre_corto, nombre_largo, max_ayuda, max_estudiantes, campos, requiere_visto_bueno_centro, convocatoria_id, requiere_visto_bueno_estudio)
SELECT nombre_corto, nombre_largo, max_ayuda, max_estudiantes, campos, requiere_visto_bueno_centro, convocatoria_id + 1, requiere_visto_bueno_estudio
FROM indo_programa
WHERE convocatoria_id = 2020
ORDER BY id
;

INSERT INTO indo_linea (nombre, programa_id)
SELECT l.nombre, p2.id
FROM indo_linea l
JOIN indo_programa p ON l.programa_id = p.id
JOIN indo_programa p2 ON p.nombre_corto = p2.nombre_corto
WHERE p.convocatoria_id = 2020 AND p2.convocatoria_id = p.convocatoria_id + 1
ORDER BY l.id
;
```
