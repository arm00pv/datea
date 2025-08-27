from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path("admin/", admin.site.urls),
    path('scanner/', include('scanner.urls')),  # Add this line
    path('', RedirectView.as_view(url='/scanner/', permanent=True)),
]
