# Pull base image from <https://hub.docker.com/_/python>
FROM python:3.12-slim-bookworm
LABEL maintainer="Enrique Matías Sánchez <quique@unizar.es>"

# Set environment variables
# Disable an automatic check for pip updates each time
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
# Don't write .pyc files
# All output to stdout will be flushed immediately
ENV PYTHONDONTWRITEBYTECODE 1 \
  PYTHONUNBUFFERED 1

# Install packages needed to run our application (not build deps)
#   fonts-ebgaramond-extra -- EB Garamond 12
#   fonts-liberation -- Fonts with the same metrics as Times, Arial and Courier
#   fonts-sil-gentium  -- Gentium
#   fonts-texgyre -- TeX Gyre Bonum (~ URW Bookman L) and TeX Gyre Pagella (~ URW Palladio L)
#   libgs9-common -- URWBookman
#   libmariadb3 -- for running database commands
#   libpcre3 -- for uWSGI internal routing support
#   xmlsec1 -- required for SAML auth
#   mime-support -- for mime types when serving static files
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  # fonts-ebgaramond-extra \
  # fonts-liberation \
  # fonts-sil-gentium \
  fonts-texgyre \
  # libgs9-common \
  libmariadb3 \
  libpcre3 \
  libxmlsec1-openssl \
  mime-support \
  pandoc \
  # Weasyprint:
  libcairo2 \
  libffi-dev \
  libgdk-pixbuf2.0-0 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  python3-cffi \
  shared-mime-info \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container image
COPY requirements.txt ./

# - Install the build dependencies needed
# - Run `pip install` to install the requirements
# - Then remove unneeded build deps (C compiler, etc)
# All in a single step, so that Docker caches it as a single layer.
RUN set -ex \
  && BUILD_DEPS=" \
  gcc \
  libmariadb-dev \
  libmariadb-dev-compat \
  libpcre3-dev \
  pkg-config" \
  && apt-get update \
  && apt-get install -y --no-install-recommends $BUILD_DEPS \
  && pip install --no-cache-dir -r requirements.txt \
  # && pip install gunicorn \
  && pip install uwsgi \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy your application code to the container image
# (make sure you create a .dockerignore file if any large files or directories should be excluded)
WORKDIR /code
COPY . /code

# Expose port 8005 - The WSGI server will listen on this port
EXPOSE 8005

# Add any static environment variables needed by Django or your settings file here:
# ENV DJANGO_SETTINGS_MODULE=my_project.settings.deploy

# Call collectstatic
RUN python3 manage.py collectstatic --no-input

## GUNICORN
# CMD exec gunicorn manhattan_project.wsgi:application --bind 0.0.0.0:8005 --workers 3

## uWSGI
# Avoid hr_read(): Connection reset by peer [plugins/http/http.c line 918]
# https://github.com/unbit/uwsgi/issues/1831
ENV UWSGI_BUFFER_SIZE=16384
# Tell uWSGI where to find your wsgi file:
ENV UWSGI_WSGI_FILE=manhattan_project/wsgi.py

# Base uWSGI configuration (use the appropriate UID and GID for your server):
ENV UWSGI_HTTP=:8005 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_UID=1501 UWSGI_GID=1501 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

# Number of uWSGI workers and threads per worker (customize as needed):
ENV UWSGI_WORKERS=4 UWSGI_THREADS=1

# uWSGI static file serving configuration (customize, or comment out if using Whitenoise or S3):
ENV UWSGI_STATIC_MAP="/static/=/code/staticfiles/" UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|pdf|map|txt) 86400"
ENV UWSGI_STATIC_MAP2="/media/=/code/" UWSGI_STATIC_EXPIRES_URI="/media/.*/.*/.*\.[a-f0-9]{12,}\.(png|jpg|jpeg|gif|svg) 3600"


# Deny invalid hosts before they get to Django (uncomment and change to your hostname(s)):
# ENV UWSGI_ROUTE_HOST="^(?!localhost:8005$) break:400"

# Uncomment after creating your docker-entrypoint.sh
ENTRYPOINT ["/code/docker-entrypoint.sh"]

# Start uWSGI
CMD ["uwsgi", "--show-config"]
