#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python inventory_management/manage.py collectstatic --no-input
