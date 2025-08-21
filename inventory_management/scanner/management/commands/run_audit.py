from django.core.management.base import BaseCommand
from scanner.models import Product
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Runs an audit to find products at risk of expiring before they are sold.'

    def handle(self, *args, **options):
        self.stdout.write('Running inventory audit...')

        today = date.today()
        audit_products = []

        for product in Product.objects.all():
            if product.weekly_average_sales > 0:
                weeks_of_stock = product.total_on_hand / product.weekly_average_sales
            else:
                # If there are no sales, any stock is at risk if it expires.
                # Set a very high weeks_of_stock to force an audit if there is an expiration date.
                weeks_of_stock = float('inf') if product.total_on_hand > 0 else 0

            earliest_exp_batch = product.batches.order_by('expiration_date').first()

            if earliest_exp_batch:
                days_to_expiry = (earliest_exp_batch.expiration_date - today).days
                weeks_to_expiry = days_to_expiry / 7

                # Condition 1: Predicted to not sell out before expiry.
                sells_out_in_time = weeks_of_stock <= weeks_to_expiry

                # Condition 2: Expires in less than 20 days.
                expires_soon = days_to_expiry < 20

                if not sells_out_in_time and expires_soon:
                    audit_products.append(product)

        if audit_products:
            self.stdout.write(self.style.WARNING('The following products require an audit:'))
            for product in audit_products:
                self.stdout.write(f'- {product.name} (UPC: {product.item_number})')
        else:
            self.stdout.write(self.style.SUCCESS('No products require an audit at this time.'))
