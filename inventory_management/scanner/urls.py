from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('add/', views.add_item, name='add_item'),
    path('expiring-soon/', views.expiring_soon, name='expiring_soon'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('search/', views.search, name='search'),
    path('search/<str:upc>/', views.search_results, name='search_results'),
    path('item/<int:item_id>/barcode/', views.view_barcode, name='view_barcode'),
    path('setup-test-data/', views.setup_test_data, name='setup_test_data'),
]
