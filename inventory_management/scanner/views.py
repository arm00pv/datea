from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import Item
from .forms import ItemForm, SubscriberForm
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def dashboard(request):
    stats = Item.objects.aggregate(
        total_items=Count('id'),
        expiring_soon_count=Count('id', filter=Q(expiration_date__lte=date.today() + timedelta(days=7))),
        low_stock_count=Count('id', filter=Q(quantity__lte=5))
    )

    context = {
        'total_items': stats['total_items'],
        'expiring_soon_count': stats['expiring_soon_count'],
        'low_stock_count': stats['low_stock_count'],
    }
    return render(request, 'scanner/dashboard.html', context)

def item_list(request):
    items = Item.objects.all()
    query = request.GET.get('query')
    sort_by = request.GET.get('sort_by', 'name')
    direction = request.GET.get('direction', 'asc')

    if query:
        items = items.filter(name__icontains=query)

    if direction == 'desc':
        sort_by = f'-{sort_by}'
    items = items.order_by(sort_by)

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'scanner/item_list.html', {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'direction': direction
    })


def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'scanner/add_item.html', {'form': form})

def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'scanner/edit_item.html', {'form': form})

def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'scanner/delete_item_confirm.html', {'item': item})

def expiring_soon_list(request):
    items = Item.objects.filter(expiration_date__lte=date.today() + timedelta(days=7))
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scanner/item_list.html', {'page_obj': page_obj})

def low_stock_list(request):
    items = Item.objects.filter(quantity__lte=5)
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scanner/item_list.html', {'page_obj': page_obj})

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
