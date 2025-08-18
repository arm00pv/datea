from django.shortcuts import render, redirect
from datetime import date, timedelta
from .models import Item
from .forms import ItemForm, SubscriberForm


def item_list(request):
    items = Item.objects.all()
    return render(request, 'scanner/item_list.html', {'items': items})


def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'scanner/add_item.html', {'form': form})

def expiring_soon(request):
    seven_days_from_now = date.today() + timedelta(days=7)
    expiring_items = Item.objects.filter(expiration_date__lte=seven_days_from_now)
    return render(request, 'scanner/expiring_soon.html', {'items': expiring_items})

def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list') # Or a success page
    else:
        form = SubscriberForm()
    return render(request, 'scanner/subscribe.html', {'form': form})

def setup_test_data(request):
    Item.objects.all().delete() # Clear existing data
    Item.objects.create(item_number='1', name='Milk', quantity=1, expiration_date=date.today() + timedelta(days=3))
    Item.objects.create(item_number='2', name='Eggs', quantity=12, expiration_date=date.today() + timedelta(days=10))
    Item.objects.create(item_number='3', name='Bread', quantity=1, expiration_date=date.today() + timedelta(days=1))
    return redirect('item_list')
