import os
import sys
import time
import psycopg2
import django

def main():
    # Add the project directory to the Python path
    # This is the directory that contains manage.py
    project_path = os.path.join(os.path.dirname(__file__), 'inventory_management')
    sys.path.append(project_path)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')

    django.setup()

    from django.db import connections
    from django.db.utils import OperationalError

    print("Waiting for database...")

    db_conn = None
    retries = 10
    while retries > 0:
        try:
            db_conn = connections['default']
            db_conn.cursor()
            print("Database available!")
            break
        except (OperationalError, psycopg2.OperationalError):
            print("Database unavailable, waiting 1 second...")
            time.sleep(1)
        retries -= 1

    if not db_conn:
        print("Could not connect to database after 10 attempts. Exiting.")
        sys.exit(1)

if __name__ == '__main__':
    main()
