from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Item
import datetime

class ItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.item = Item.objects.create(
            user=self.user,
            item_number="123456789012",
            name="Test Item",
            quantity=10,
            expiration_date=datetime.date.today() + datetime.timedelta(days=30)
        )

    def test_item_creation(self):
        self.assertEqual(self.item.item_number, "123456789012")
        self.assertEqual(self.item.name, "Test Item")
        self.assertEqual(self.item.quantity, 10)
        self.assertEqual(self.item.user, self.user)

    def test_item_str(self):
        self.assertEqual(str(self.item), "Test Item")

class ItemViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.item = Item.objects.create(
            user=self.user,
            item_number="123456789012",
            name="Test Item",
            quantity=10,
            expiration_date=datetime.date.today() + datetime.timedelta(days=30)
        )

    def test_item_list_view(self):
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Item")
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
            'expiration_date': datetime.date.today() + datetime.timedelta(days=60)
        }
        response = self.client.post(reverse('add_item'), data)
        self.assertEqual(response.status_code, 302) # Should redirect to item_list
        self.assertEqual(Item.objects.filter(user=self.user).count(), 2)
