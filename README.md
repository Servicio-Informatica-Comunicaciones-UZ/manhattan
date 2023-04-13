Proyecto Manhattan
==================

> First we take Manhattan, then we take Berlin.

Manhattan es una aplicación web para gestionar los proyectos de Innovación Docente.  
Está desarrollada con [Django](https://www.djangoproject.com/) 4, mucho ♥, bastante ☕
y un poco de magia 🧙.

Instalación sobre contenedores Docker
-------------------------------------

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

   Si el servidor en que se encuentra la base de datos es distinto a donde se alojará la aplicación,
   comprobar que desde la máquina de la aplicación se pueda acceder a la BD.

2. Clonar el repositorio Git.  
   `git clone https://gitlab.unizar.es/InnovacionDocente/manhattan.git .`
3. Copiar el fichero de ejemplo `.env-sample` a `.env`.
4. En el fichero `.env` configurar la clave secreta de Django, la conexión con la base de datos,
   la URL del sitio (`SITE_URL`), los datos para el correo electrónico, los datos para el _Single Sign On_ (SAML,
   los _web services_ de Gestión de Identidades, etc.  
   Si se está detrás de un proxy o balanceador, habilitar la opción `USE_X_FORWARDED_PORT`.  
   Si se usa SSL, habilitar las opciones `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE`.
5. En el fichero `Dockerfile` cambiar `UWSGI_UID` y `UWSGI_GID` al usuario y grupo que se desee.
   En el fichero `docker-compose.yml` cambiar el puerto `published` al que se desee.
6. Construir y levantar los contenedores:
   `docker-compose build && docker-compose up -d`
7. Crear el usuario administrador:

   ```bash
   docker-compose exec web ./manage.py createsuperuser
   docker-compose exec web ./manage.py loaddata seed
   ```

8. Entrar como administrador en la interfaz web, y añadir usuarios al grupo `Gestores`
   (incluyendo el superusuario).

9. Activar a los usuarios gestores el atributo `is_staff` para que puedan acceder
   a la interfaz de administración.

Instalación sobre hierro
------------------------

### Requisitos

1. **Python 3.8 o superior**. En Debian o Ubuntu:

   ```bash
    sudo apt-get install python3.9-dev python3-distutils
    ```

2. **[pip](https://pip.pypa.io/en/stable/installing/)**, instalador de paquetes de Python.
   (Puede venir con la instalación de Python).
3. **[pipenv](https://github.com/pypa/pipenv)** para crear un entorno virtual para Python y facilitar el trabajo.

   Se puede instalar con `sudo -H pip3 install pipenv`.
4. Paquetes `fonts-texgyre`, `libxmlsec1-dev`, `pandoc` y `pkg-config`.
5. **Un servidor de bases de datos** aceptado por Django (vg PostgreSQL o MariaDB).

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

### Instalación

```shell
git clone https://gitlab.unizar.es/InnovacionDocente/manhattan.git
cd manhattan
pipenv install [--dev]
```

### Configuración inicial

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

2. Copiar el fichero de ejemplo `.env-sample` a `.env`.
3. En el fichero `.env` configurar la clave secreta de Django, la conexión con la base de datos,
   la URL del sitio (`SITE_URL`), los datos para el correo electrónico, los datos para el _Single Sign On_ (SAML,
   los _web services_ de Gestión de Identidades, etc.  
   Si se está detrás de un proxy o balanceador, habilitar la opción `USE_X_FORWARDED_PORT`.  
   Si se usa SSL, habilitar las opciones `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE`.
4. Ejecutar

    ```shell
    source .env
    pipenv shell
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py loaddata seed
    ```

5. Abrir la URL con el navegador web, autenticarse como superusuario y,
   en la interfaz de administración de Django, añadir usuarios al grupo `Gestores`
   (incluyendo al superusuario).
6. Activar a los usuarios gestores el atributo `is_staff` para que puedan acceder
   a la interfaz de administración.

### Servidor web para desarrollo

```shell
source .env
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

Se puede crear una nueva convocatoria desde la interfaz de administración
(los usuarios gestores, además de pertenecer al grupo `Gestores` deben tener activado
el atributo `is_staff` para que puedan acceder a esta interfaz).

Se pueden clonar los maestros de la convocatoria anterior con estas órdenes SQL:

```sql
-- Programas
INSERT INTO indo_programa (nombre_corto, nombre_largo, max_ayuda, max_estudiantes,
  campos, requiere_visto_bueno_centro, convocatoria_id, requiere_visto_bueno_estudio)
SELECT nombre_corto, nombre_largo, max_ayuda, max_estudiantes, campos,
  requiere_visto_bueno_centro, convocatoria_id + 1, requiere_visto_bueno_estudio
FROM indo_programa
WHERE convocatoria_id = 2023  -- Reemplazar 2023 por la última convocatoria.
ORDER BY id;
-- WARNING: Si se añaden nuevos programas, hay que actualizar el método `Proyecto.get_unidad_planificacion()`.

-- Líneas
INSERT INTO indo_linea (nombre, programa_id)
SELECT l.nombre, p2.id
FROM indo_linea l
JOIN indo_programa p ON l.programa_id = p.id
JOIN indo_programa p2 ON p.nombre_corto = p2.nombre_corto
WHERE p.convocatoria_id = 2023  -- Reemplazar 2023 por la última convocatoria.
  AND p2.convocatoria_id = p.convocatoria_id + 1
ORDER BY p2.id, l.id;

-- Rúbrica evaluación ACPUA
-- Si se añaden o quitan programas de la convocatoria, actualizar manualmente el campo `programas`
INSERT INTO indo_criterio (parte, peso, descripcion, tipo, convocatoria_id, programas)
SELECT parte, peso, descripcion, tipo, convocatoria_id + 1, programas
FROM indo_criterio
WHERE convocatoria_id = 2023  -- Reemplazar 2023 por la última convocatoria.
ORDER BY parte, peso;

-- Opciones de la rúbrica
INSERT INTO indo_opcion (puntuacion, descripcion, criterio_id)
SELECT o.puntuacion, o.descripcion, c2.id
FROM indo_opcion o
JOIN indo_criterio c1 ON o.criterio_id = c1.id
JOIN indo_criterio c2 ON c1.parte = c2.parte AND c1.peso = c2.peso
WHERE c1.convocatoria_id = 2023  -- Reemplazar 2023 por la última convocatoria.
  AND c2.convocatoria_id = c1.convocatoria_id + 1
ORDER BY c2.id, o.puntuacion;

-- Apartados memoria
INSERT INTO indo_memoriaapartado (numero, descripcion, convocatoria_id)
SELECT numero, descripcion, convocatoria_id + 1
FROM indo_memoriaapartado
WHERE convocatoria_id = 2023  -- Reemplazar 2023 por la última convocatoria.
ORDER BY numero;

-- Subapartados memoria
INSERT INTO indo_memoriasubapartado (peso, descripcion, ayuda, tipo, apartado_id)
SELECT peso, s.descripcion, ayuda, tipo, a2.id
FROM indo_memoriasubapartado s
JOIN indo_memoriaapartado a1 ON s.apartado_id = a1.id
JOIN indo_memoriaapartado a2 ON a1.numero = a2.numero
WHERE a1.convocatoria_id = 2023  -- Reemplazar 2023 por la última convocatoria.
  AND a2.convocatoria_id = a1.convocatoria_id + 1
ORDER BY a2.id, peso;
```
