import os
import time
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.inventory_management.settings')

def check_db_connection():
    db_conn = None
    retries = 10
    while retries > 0:
        try:
            db_conn = connections['default']
            db_conn.cursor()
            print("Database is ready.")
            return
        except OperationalError:
            print("Database unavailable, waiting 1 second...")
            time.sleep(1)
        except psycopg2.OperationalError:
            print("Database unavailable (psycopg2), waiting 1 second...")
            time.sleep(1)
        retries -= 1

    print("Could not connect to database after 10 attempts. Exiting.")
    exit(1)


if __name__ == '__main__':
    check_db_connection()
