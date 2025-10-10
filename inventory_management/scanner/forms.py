from django import forms
from .models import Product, Batch, Subscriber

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['item_number', 'name', 'total_on_hand', 'weekly_average_sales']
        widgets = {
            'item_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'total_on_hand': forms.NumberInput(attrs={'class': 'form-control'}),
            'weekly_average_sales': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'quantity', 'expiration_date', 'is_steel']
        labels = {
            'is_steel': 'Steel',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_steel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
