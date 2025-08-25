from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from django.core.management import call_command
from .models import Product, Batch, Subscriber
import datetime
from io import StringIO

class ProductModelTest(TestCase):
    def test_product_creation(self):
        product = Product.objects.create(
            item_number="123",
            name="Test Product",
            total_on_hand=100,
            weekly_average_sales=10.5
        )
        self.assertEqual(product.name, "Test Product")

class BatchModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", item_number="123")
        self.batch = Batch.objects.create(
            product=self.product,
            quantity=50,
            expiration_date=datetime.date.today() + datetime.timedelta(days=30),
            is_steel=True
        )

    def test_batch_creation(self):
        self.assertEqual(self.batch.product, self.product)
        self.assertEqual(self.batch.quantity, 50)
        self.assertTrue(self.batch.is_steel)

class ViewTest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name="Product 1", item_number="1")
        self.batch1 = Batch.objects.create(product=self.product1, quantity=10, expiration_date=datetime.date.today() + datetime.timedelta(days=10))

    def test_product_list_view(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertTemplateUsed(response, 'scanner/product_list.html')

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', kwargs={'product_id': self.product1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertTemplateUsed(response, 'scanner/product_detail.html')

# NOTE: More tests for other views will be added in the dedicated testing phase.

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReminderCommandTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", item_number="1")
        self.expiring_batch = Batch.objects.create(
            product=self.product,
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
        self.assertIn('Test Product', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

class AuditCommandTest(TestCase):
    def test_audit_command_no_issues(self):
        product = Product.objects.create(name="Good Product", item_number="1", total_on_hand=20, weekly_average_sales=10)
        Batch.objects.create(product=product, quantity=20, expiration_date=datetime.date.today() + datetime.timedelta(days=30))

        out = StringIO()
        call_command('run_audit', stdout=out)
        self.assertIn('No products require an audit', out.getvalue())

    def test_audit_command_triggers_audit(self):
        product = Product.objects.create(name="Bad Product", item_number="2", total_on_hand=100, weekly_average_sales=1)
        Batch.objects.create(product=product, quantity=100, expiration_date=datetime.date.today() + datetime.timedelta(days=10))

        out = StringIO()
        call_command('run_audit', stdout=out)
        self.assertIn('The following products require an audit:', out.getvalue())
        self.assertIn('Bad Product', out.getvalue())
