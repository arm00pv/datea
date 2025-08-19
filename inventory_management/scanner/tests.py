from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from django.core.management import call_command
from .models import Item, Subscriber
import datetime
from io import StringIO

class ItemModelTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            item_number="123456789012",
            name="Test Item",
            quantity=10,
            expiration_date=datetime.date.today() + datetime.timedelta(days=30)
        )

    def test_item_creation(self):
        self.assertEqual(self.item.item_number, "123456789012")
        self.assertEqual(self.item.name, "Test Item")
        self.assertEqual(self.item.quantity, 10)

    def test_item_str(self):
        self.assertEqual(str(self.item), "Test Item")

    def test_duplicate_item_number_allowed(self):
        Item.objects.create(
            item_number="123456789012",
            name="Test Item 2",
            quantity=5,
            expiration_date=datetime.date.today() + datetime.timedelta(days=60)
        )
        self.assertEqual(Item.objects.count(), 2)

    def test_is_steel_default(self):
        self.assertFalse(self.item.is_steel)

class SubscriberModelTest(TestCase):
    def setUp(self):
        self.subscriber = Subscriber.objects.create(email='test@example.com')

    def test_subscriber_creation(self):
        self.assertEqual(self.subscriber.email, 'test@example.com')

    def test_subscriber_str(self):
        self.assertEqual(str(self.subscriber), 'test@example.com')

class ViewTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            item_number="123456789012",
            name="Test Item",
            quantity=10,
            expiration_date=datetime.date.today() + datetime.timedelta(days=30),
            is_steel=False
        )
        self.steel_item = Item.objects.create(
            item_number="steel_item",
            name="Steel Item",
            quantity=1,
            expiration_date=datetime.date.today() + datetime.timedelta(days=3),
            is_steel=True
        )

    def test_item_list_view(self):
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Item")
        self.assertContains(response, "Steel Item")
        self.assertContains(response, "Floor")
        self.assertContains(response, "Steel")
        self.assertTemplateUsed(response, 'scanner/item_list.html')

    def test_add_item_view_get(self):
        response = self.client.get(reverse('add_item'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scanner/add_item.html')

    def test_add_item_view_post(self):
        data = {
            'item_number': '987654321098',
            'name': 'New Test Item',
            'quantity': 5,
            'expiration_date': datetime.date.today() + datetime.timedelta(days=60),
            'is_steel': True
        }
        response = self.client.post(reverse('add_item'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Item.objects.count(), 3)
        new_item = Item.objects.get(item_number='987654321098')
        self.assertTrue(new_item.is_steel)

    def test_expiring_soon_view(self):
        response = self.client.get(reverse('expiring_soon'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test Item")
        self.assertContains(response, "Steel Item")
        self.assertTemplateUsed(response, 'scanner/expiring_soon.html')

    def test_subscribe_view_get(self):
        response = self.client.get(reverse('subscribe'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scanner/subscribe.html')

    def test_subscribe_view_post(self):
        data = {'email': 'new_subscriber@example.com'}
        response = self.client.post(reverse('subscribe'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_search_view(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scanner/search.html')

    def test_search_results_view(self):
        response = self.client.get(reverse('search_results', kwargs={'upc': '123456789012'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Item")
        self.assertTemplateUsed(response, 'scanner/search_results.html')

    def test_view_barcode_view(self):
        response = self.client.get(reverse('view_barcode', kwargs={'item_id': self.item.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Barcode for: Test Item")
        self.assertTemplateUsed(response, 'scanner/view_barcode.html')

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReminderCommandTest(TestCase):
    def setUp(self):
        self.expiring_item = Item.objects.create(
            item_number="expiring",
            name="Expiring Item",
            quantity=1,
            expiration_date=datetime.date.today() + datetime.timedelta(days=3)
        )
        self.subscriber = Subscriber.objects.create(email='test@example.com')

    def test_send_reminders_command(self):
        out = StringIO()
        call_command('send_reminders', stdout=out)
        self.assertIn('Successfully sent reminder email to 1 subscribers.', out.getvalue())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Expiring Items Reminder')
        self.assertIn('Expiring Item', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
