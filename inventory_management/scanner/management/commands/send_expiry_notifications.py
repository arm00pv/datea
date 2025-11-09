from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from ...models import Item, Subscriber

class Command(BaseCommand):
    help = 'Sends notifications for items expiring soon.'

    def handle(self, *args, **options):
        seven_days_from_now = timezone.now().date() + timedelta(days=7)
        expiring_items = Item.objects.filter(expiration_date__lte=seven_days_from_now)
        subscribers = Subscriber.objects.all()

        if expiring_items.exists() and subscribers.exists():
            subject = 'Inventory Alert: Items Expiring Soon'
            html_message = render_to_string('scanner/email/expiry_notification.html', {'items': expiring_items})
            recipient_list = [s.email for s in subscribers]

            send_mail(subject, '', 'noreply@inventory.com', recipient_list, html_message=html_message)
            self.stdout.write(self.style.SUCCESS('Successfully sent expiry notifications.'))
        else:
            self.stdout.write(self.style.SUCCESS('No expiring items or subscribers.'))
