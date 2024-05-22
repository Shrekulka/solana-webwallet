FROM python:3.12-slim-bookworm

# Установка зависимостей
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG USER=user
ARG USER_UID=1001
ARG PROJECT_NAME=web
ARG GUNICORN_PORT=8000
ARG GUNICORN_WORKERS=2
# the value is in seconds
ARG GUNICORN_TIMEOUT=60
ARG GUNICORN_LOG_LEVEL=info
# ARG DJANGO_BASE_DIR=/$PROJECT_NAME
ARG DJANGO_BASE_DIR=/usr/src/$PROJECT_NAME
ARG DJANGO_STATIC_ROOT=/var/www/static
ARG DJANGO_MEDIA_ROOT=/var/www/media
ARG DJANGO_SQLITE_DIR=/sqlite
# The superuser with the data below will be created only if there are no users in the database!
ARG DJANGO_SUPERUSER_USERNAME=admin
ARG DJANGO_SUPERUSER_PASSWORD=qwerty987
ARG DJANGO_SUPERUSER_EMAIL=admin@example.com
ARG DJANGO_DEV_SERVER_PORT=8000

ENV \
    USER=$USER \
    USER_UID=$USER_UID \
    PROJECT_NAME=$PROJECT_NAME \
    GUNICORN_PORT=$GUNICORN_PORT \
    GUNICORN_WORKERS=$GUNICORN_WORKERS \
    GUNICORN_TIMEOUT=$GUNICORN_TIMEOUT \
    GUNICORN_LOG_LEVEL=$GUNICORN_LOG_LEVEL \
    DJANGO_BASE_DIR=$DJANGO_BASE_DIR \
    DJANGO_STATIC_ROOT=$DJANGO_STATIC_ROOT \
    DJANGO_MEDIA_ROOT=$DJANGO_MEDIA_ROOT \
    DJANGO_SQLITE_DIR=$DJANGO_SQLITE_DIR \
    DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME \
    DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD \
    DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL \
    DJANGO_DEV_SERVER_PORT=$DJANGO_DEV_SERVER_PORT \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# # вывод из python будет отправлен прямо в терминал без предварительной буферизации
# ENV PYTHONUNBUFFERED 1
# # Python не будет пытаться создавать файлы .pyc
# ENV PYTHONDONTWRITEBYTECODE 1

# Создание и переход в рабочую директорию
WORKDIR $DJANGO_BASE_DIR

COPY ./compose/docker-entrypoint.sh /docker-entrypoint.sh
COPY ./compose/docker-cmd.sh /docker-cmd.sh
COPY $PROJECT_NAME $DJANGO_BASE_DIR

# Install latest su-exec
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libc-dev wget; \
    rm -rf /var/lib/apt/lists/*; \
    wget -O /usr/local/bin/su-exec.c https://raw.githubusercontent.com/ncopa/su-exec/master/su-exec.c; \
    gcc -Wall /usr/local/bin/su-exec.c -o/usr/local/bin/su-exec; \
    chown root:root /usr/local/bin/su-exec; \
    chmod 0755 /usr/local/bin/su-exec; \
    rm /usr/local/bin/su-exec.c; \
    apt-get purge -y --auto-remove gcc libc-dev wget

# Копирование зависимостей проекта и установка их
COPY ./requirements/requirements.txt $DJANGO_BASE_DIR
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта в контейнер
COPY . $DJANGO_BASE_DIR

# User
RUN chmod +x /docker-entrypoint.sh /docker-cmd.sh; \
    mkdir -p $DJANGO_STATIC_ROOT $DJANGO_MEDIA_ROOT; \
    adduser --shell /bin/bash --disabled-password --uid $USER_UID $USER; \
    chown -R $USER:$USER $DJANGO_BASE_DIR $DJANGO_STATIC_ROOT $DJANGO_MEDIA_ROOT;

# ENTRYPOINT ["/entrypoint.sh"]

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/docker-cmd.sh"]

EXPOSE $GUNICORN_PORT
