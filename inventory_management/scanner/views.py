from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import Item, Category
from .forms import ItemForm, SubscriberForm, CustomUserCreationForm, CategoryForm
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import csv
from django.http import HttpResponse, JsonResponse
import requests
import json

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
@cache_page(60 * 15)
def dashboard(request):
    stats = Item.objects.filter(user=request.user).aggregate(
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

@login_required
def item_list(request):
    items = Item.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    query = request.GET.get('query')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort_by', 'name')
    direction = request.GET.get('direction', 'asc')

    if query:
        items = items.filter(name__icontains=query)

    if category_id:
        items = items.filter(category__id=category_id)

    if direction == 'desc':
        sort_by = f'-{sort_by}'
    items = items.order_by(sort_by)

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'scanner/item_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'sort_by': sort_by,
        'direction': direction
    })

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect('item_list')
    else:
        form = ItemForm(user=request.user)
    return render(request, 'scanner/add_item.html', {'form': form})

@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item, user=request.user)
    return render(request, 'scanner/edit_item.html', {'form': form})

@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'scanner/delete_item_confirm.html', {'item': item})

@login_required
def expiring_soon_list(request):
    items = Item.objects.filter(user=request.user, expiration_date__lte=date.today() + timedelta(days=7))
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scanner/item_list.html', {'page_obj': page_obj})

@login_required
def low_stock_list(request):
    items = Item.objects.filter(user=request.user, quantity__lte=5)
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

@login_required
def setup_test_data(request):
    Item.objects.filter(user=request.user).delete()
    Category.objects.filter(user=request.user).delete()

    dairy = Category.objects.create(user=request.user, name='Dairy')
    bakery = Category.objects.create(user=request.user, name='Bakery')

    Item.objects.create(user=request.user, item_number='1', name='Milk', quantity=1, expiration_date=date.today() + timedelta(days=3), category=dairy)
    Item.objects.create(user=request.user, item_number='2', name='Eggs', quantity=12, expiration_date=date.today() + timedelta(days=10), category=dairy)
    Item.objects.create(user=request.user, item_number='3', name='Bread', quantity=1, expiration_date=date.today() + timedelta(days=1), category=bakery)
    return redirect('item_list')

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'

    writer = csv.writer(response)
    writer.writerow(['Item Number', 'Name', 'Quantity', 'Entry Date', 'Expiration Date'])

    items = Item.objects.filter(user=request.user).values_list('item_number', 'name', 'quantity', 'entry_date', 'expiration_date')
    for item in items:
        writer.writerow(item)

    return response

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'scanner/category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'scanner/add_category.html', {'form': form})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'scanner/edit_category.html', {'form': form})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'scanner/delete_category_confirm.html', {'category': category})

@login_required
def lookup_upc(request):
    upc = request.GET.get('upc')
    if not upc:
        return JsonResponse({'error': 'UPC not provided'}, status=400)

    try:
        response = requests.get(f'https://api.upcitemdb.com/prod/trial/lookup?upc={upc}')
        response.raise_for_status()
        data = response.json()

        if data.get('items'):
            return JsonResponse({'title': data['items'][0].get('title', '')})
        else:
            return JsonResponse({'title': ''})

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def bulk_scan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            for item_data in items:
                Item.objects.create(
                    user=request.user,
                    item_number=item_data['item_number'],
                    name=item_data['name'],
                    quantity=1 # Default quantity
                )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'scanner/bulk_scan.html')

@login_required
def chart_data(request):
    category_data = Item.objects.filter(user=request.user).values('category__name').annotate(count=Count('id'))
    stock_data = Item.objects.filter(user=request.user).values('name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    category_chart = {
        'labels': [data['category__name'] if data['category__name'] else "Uncategorized" for data in category_data],
        'data': [data['count'] for data in category_data],
    }

    stock_chart = {
        'labels': [data['name'] for data in stock_data],
        'data': [data['total_quantity'] for data in stock_data],
    }

    return JsonResponse({
        'category_chart': category_chart,
        'stock_chart': stock_chart,
    })
