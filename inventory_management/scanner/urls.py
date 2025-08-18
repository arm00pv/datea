from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('add/', views.add_item, name='add_item'),
    path('expiring-soon/', views.expiring_soon, name='expiring_soon'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('setup-test-data/', views.setup_test_data, name='setup_test_data'),
]
