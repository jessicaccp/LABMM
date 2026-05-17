#!/usr/bin/env bash
set -e

echo "Removing existing database..."
rm -f instance/labmm.db

echo "Running migrations..."
flask db upgrade

echo "Seeding database..."
python seed.py

echo "Done."
