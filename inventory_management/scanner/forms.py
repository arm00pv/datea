from django import forms
from .models import Item, Subscriber

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_number', 'name', 'quantity', 'expiration_date']

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
