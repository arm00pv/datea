from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('scanner/', include('scanner.urls')),
    path('', RedirectView.as_view(pattern_name='product_list', permanent=False)),
]