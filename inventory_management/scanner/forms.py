from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Subscriber, Category

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_number', 'name', 'category', 'quantity', 'expiration_date']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ItemForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
