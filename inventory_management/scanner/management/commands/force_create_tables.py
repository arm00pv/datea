from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Force creates the necessary tables for the scanner app by executing raw SQL. This is a workaround for persistent migration issues.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting forceful table creation for the 'scanner' app..."))

        # Raw SQL for creating the tables. This is generated from `python manage.py sqlmigrate scanner 0001`.
        # Using `CREATE TABLE IF NOT EXISTS` makes this command safe to run multiple times.
        sql_commands = """
        CREATE TABLE IF NOT EXISTS `scanner_product` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `item_number` varchar(100) NOT NULL UNIQUE,
            `name` varchar(200) NOT NULL,
            `total_on_hand` integer NOT NULL,
            `weekly_average_sales` double precision NOT NULL
        );
        CREATE TABLE IF NOT EXISTS `scanner_subscriber` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `email` varchar(254) NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS `scanner_batch` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `quantity` integer NOT NULL,
            `expiration_date` date NOT NULL,
            `is_steel` bool NOT NULL,
            `entry_date` date NOT NULL,
            `product_id` integer NOT NULL
        );
        ALTER TABLE `scanner_batch` ADD CONSTRAINT `scanner_batch_product_id_fk_scanner_product_id`
        FOREIGN KEY (`product_id`) REFERENCES `scanner_product` (`id`);
        """

        try:
            with connection.cursor() as cursor:
                # Split commands and execute them one by one
                for command in sql_commands.split(';'):
                    if command.strip():
                        self.stdout.write(f"Executing: {command.strip()[:70]}...")
                        cursor.execute(command)
            self.stdout.write(self.style.SUCCESS("All tables for the 'scanner' app created or verified successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during table creation: {e}"))
            self.stdout.write(self.style.WARNING("Please check the database and server logs for more details."))

        self.stdout.write(self.style.WARNING("Now, attempting to fake the initial migration to sync Django's records..."))
        try:
            from django.core.management import call_command
            call_command('migrate', 'scanner', '0001', fake=True)
            self.stdout.write(self.style.SUCCESS("Django's migration records have been successfully synced."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while faking the migration: {e}"))
            self.stdout.write(self.style.WARNING("You may need to run `python manage.py migrate scanner 0001 --fake` manually."))