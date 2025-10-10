from django.contrib import admin
from django.urls import path, include
from scanner import views as scanner_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('scanner/', include('scanner.urls')),
    # Point the root URL directly to the search page view
    path('', scanner_views.search, name='home'),
]