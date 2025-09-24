from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import Product, Batch, Subscriber
from .forms import ProductForm, BatchForm, SubscriberForm

def product_list(request):
    products = Product.objects.all()
    return render(request, 'scanner/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    today = date.today()
    batches_with_predictions = []

    for batch in product.batches.all():
        days_to_expiration = (batch.expiration_date - today).days
        if days_to_expiration > 0:
            predicted_sales = (product.weekly_average_sales / 7) * days_to_expiration
            is_at_risk = batch.quantity > predicted_sales
        else:
            predicted_sales = 0
            is_at_risk = batch.quantity > 0

        batches_with_predictions.append({
            'batch': batch,
            'days_to_expiration': days_to_expiration,
            'predicted_sales': predicted_sales,
            'is_at_risk': is_at_risk,
        })

    return render(request, 'scanner/product_detail.html', {
        'product': product,
        'batches_with_predictions': batches_with_predictions,
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
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(item_number__icontains=query) | Q(name__icontains=query)
        )
    else:
        products = Product.objects.none()
    return render(request, 'scanner/search_results.html', {'products': products, 'query': query})

def view_barcode(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'scanner/view_barcode.html', {'product': product})

def expiration_prediction(request):
    batches = Batch.objects.select_related('product').all()
    today = date.today()
    predictions = []

    for batch in batches:
        days_to_expiration = (batch.expiration_date - today).days
        if days_to_expiration > 0:
            predicted_sales = (batch.product.weekly_average_sales / 7) * days_to_expiration
            is_at_risk = batch.quantity > predicted_sales
        else:
            predicted_sales = 0
            is_at_risk = batch.quantity > 0

        predictions.append({
            'batch': batch,
            'days_to_expiration': days_to_expiration,
            'predicted_sales': predicted_sales,
            'is_at_risk': is_at_risk,
        })

    return render(request, 'scanner/expiration_prediction.html', {'predictions': predictions})
