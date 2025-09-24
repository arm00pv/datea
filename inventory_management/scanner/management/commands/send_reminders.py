from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from scanner.models import Batch, Subscriber
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Sends email reminders for items that are about to expire.'

    def handle(self, *args, **options):
        self.stdout.write('Sending reminders...')

        seven_days_from_now = date.today() + timedelta(days=7)
        expiring_batches = Batch.objects.filter(expiration_date__lte=seven_days_from_now)

        if expiring_batches.exists():
            subject = 'Expiring Items Reminder'
            message = 'The following items are expiring soon:\n\n'
            for batch in expiring_batches:
                message += f'- {batch.product.name} (expires on {batch.expiration_date})\n'

            subscribers = Subscriber.objects.all()
            recipient_list = [s.email for s in subscribers]

            if recipient_list:
                send_mail(
                    subject,
                    message,
                    'from@example.com',
                    recipient_list,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully sent reminder email to {len(recipient_list)} subscribers.'))
            else:
                self.stdout.write(self.style.WARNING('No subscribers to send reminders to.'))
        else:
            self.stdout.write(self.style.SUCCESS('No items are expiring soon.'))
