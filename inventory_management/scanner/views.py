from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from .models import Item
from .forms import ItemForm

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

@login_required
def item_list(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'scanner/item_list.html', {'items': items})

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'scanner/add_item.html', {'form': form})
