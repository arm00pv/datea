#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Set dummy env vars for collectstatic
export SECRET_KEY=dummy-secret-key-for-build
export DATABASE_URL=sqlite:///dummy.db

python inventory_management/manage.py collectstatic --no-input
