#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to read secrets (Docker Secrets compatibility)
file_env() {
    local var="$1"
    local fileVar="${var}_FILE"
    local def="${2:-}"
    if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
        echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
        exit 1
    fi
    local val="$def"
    if [ "${!var:-}" ]; then
        val="${!var}"
    elif [ "${!fileVar:-}" ]; then
        val="$(< "${!fileVar}")"
    fi
    export "$var"="$val"
    unset "$fileVar"
}

# Load secrets
file_env 'POSTGRES_PASSWORD'
file_env 'REDIS_PASSWORD'

# Wait for Postgres to be ready
if [ "$DATABASE_HOST" = "db" ]; then
    echo "Waiting for PostgreSQL..."
    while ! nc -z $DATABASE_HOST 5432; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Run migrations automatically on startup
echo "Running Database Migrations..."
python manage.py migrate

# Collect static files (puts them in the volume for Nginx)
echo "Collecting Static Files..."
python manage.py collectstatic --noinput

# Exec the container's main process (CMD in Dockerfile)
exec "$@"