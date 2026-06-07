#!/bin/sh

echo "Running database migrations..."
alembic upgrade head

echo "Starting Gunicorn..."
exec gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -w 4 \
    -b 0.0.0.0:8000