from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('items/', views.item_list, name='item_list'),
    path('add/', views.add_item, name='add_item'),
    path('edit/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('expiring-soon/', views.expiring_soon_list, name='expiring_soon_list'),
    path('low-stock/', views.low_stock_list, name='low_stock_list'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('setup-test-data/', views.setup_test_data, name='setup_test_data'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
]
