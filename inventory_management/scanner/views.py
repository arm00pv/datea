from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from django.views.decorators.cache import cache_page
from .models import Product, Batch, Subscriber
from .forms import ProductForm, BatchForm, SubscriberForm

@cache_page(60 * 15)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'scanner/product_list.html', {'products': products})

@cache_page(60 * 15)
def product_detail(request, product_id):
    # Use prefetch_related to efficiently fetch all batches for the product
    # and their related product in a single query.
    product = get_object_or_404(Product.objects.prefetch_related('batches'), pk=product_id)

    # The logic is now in the model, so we can pass the batches directly.
    return render(request, 'scanner/product_detail.html', {
        'product': product,
        'batches': product.batches.all(),
    })

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'scanner/add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'scanner/edit_product.html', {'form': form, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'scanner/product_confirm_delete.html', {'product': product})

def add_batch(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.product = product
            batch.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = BatchForm(initial={'product': product})
    return render(request, 'scanner/add_batch.html', {'form': form, 'product': product})

def edit_batch(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    product = batch.product
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = BatchForm(instance=batch)
    return render(request, 'scanner/edit_batch.html', {'form': form, 'batch': batch})

def delete_batch(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    product_id = batch.product.id
    if request.method == 'POST':
        batch.delete()
        return redirect('product_detail', product_id=product_id)
    return render(request, 'scanner/batch_confirm_delete.html', {'batch': batch})

def expiring_soon(request):
    seven_days_from_now = date.today() + timedelta(days=7)
    expiring_batches = Batch.objects.filter(expiration_date__lte=seven_days_from_now)
    return render(request, 'scanner/expiring_soon.html', {'batches': expiring_batches})

def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = SubscriberForm()
    return render(request, 'scanner/subscribe.html', {'form': form})

from django.db.models import Q

def search(request):
    """
    Displays the search form and scanner interface.
    """
    return render(request, 'scanner/search.html')

def search_results(request):
    """
    Displays search results based on a query.
    """
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(item_number__icontains=query) | Q(name__icontains=query)
        )
    else:
        # If no query, show all products
        products = Product.objects.all()
    return render(request, 'scanner/search_results.html', {'products': products, 'query': query})

def view_barcode(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'scanner/view_barcode.html', {'product': product})

@cache_page(60 * 15)
def expiration_prediction(request):
    # The logic is now in the model, so we can just fetch the batches.
    # We use select_related to avoid N+1 queries when accessing product details.
    batches = Batch.objects.select_related('product').all()

    return render(request, 'scanner/expiration_prediction.html', {'batches': batches})
