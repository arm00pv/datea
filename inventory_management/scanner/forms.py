from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Subscriber

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_number', 'name', 'quantity', 'expiration_date']

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
