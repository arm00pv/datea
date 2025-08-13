#!/bin/sh

# Exit on error
set -e

# Apply database migrations
python inventory_management/manage.py migrate

# Start the Gunicorn server
exec gunicorn inventory_management.inventory_management.wsgi:application --bind 0.0.0.0:8000
