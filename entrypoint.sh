#!/bin/sh
set -e

export FLASK_APP=run.py

echo "Running database migrations..."
flask db upgrade

echo "Seeding initial data..."
python seed.py

echo "Starting application..."
exec "$@"
