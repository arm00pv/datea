from django import forms
from .models import Item, Subscriber

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_number', 'name', 'quantity', 'expiration_date']
        widgets = {
            'item_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
