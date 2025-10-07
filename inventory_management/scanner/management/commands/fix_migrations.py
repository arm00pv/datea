from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Fixes a broken migration state where tables are missing but migrations are recorded.'

    def handle(self, *args, **options):
        app_name = 'scanner'
        # Check for one of the tables that should exist.
        # Django creates table names as <app_name>_<model_name_lowercase>
        table_to_check = f'{app_name}_product'

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in cursor.fetchall()]

        if table_to_check not in tables:
            self.stdout.write(self.style.WARNING(f"Table '{table_to_check}' not found. This indicates a broken migration state."))
            self.stdout.write("Attempting to fix by resetting the app's migration history and re-running migrations.")

            with connection.cursor() as cursor:
                self.stdout.write(self.style.WARNING(f"Deleting stale migration records for app '{app_name}' from the 'django_migrations' table..."))
                cursor.execute("DELETE FROM django_migrations WHERE app = %s;", [app_name])
                self.stdout.write(self.style.SUCCESS("Stale migration records deleted."))

            self.stdout.write("Now, attempting to run the migrations again...")
            try:
                # Running migrate for the specific app
                call_command('migrate', app_name)
                self.stdout.write(self.style.SUCCESS(f"Successfully applied migrations for '{app_name}'. The tables should now be created."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred during the migration attempt: {e}"))
                self.stdout.write(self.style.WARNING("Please check the database and server logs for more details."))

        else:
            self.stdout.write(self.style.SUCCESS(f"Table '{table_to_check}' already exists. Database state appears to be correct."))