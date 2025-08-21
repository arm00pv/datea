from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:product_id>/add_batch/', views.add_batch, name='add_batch'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('batch/<int:batch_id>/edit/', views.edit_batch, name='edit_batch'),
    path('batch/<int:batch_id>/delete/', views.delete_batch, name='delete_batch'),
    path('expiring-soon/', views.expiring_soon, name='expiring_soon'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('search/', views.search, name='search'),
    path('search/<str:upc>/', views.search_results, name='search_results'),
    path('product/<int:product_id>/barcode/', views.view_barcode, name='view_barcode'),
]
