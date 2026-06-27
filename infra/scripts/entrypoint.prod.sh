#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    sleep 1
done

echo "PostgreSQL is ready. Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec "$@"