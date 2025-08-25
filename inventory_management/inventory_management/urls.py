from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # Import this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scanner/', include('scanner.urls')),
    # Add this line to redirect the root URL to the scanner app
    path('', RedirectView.as_view(url='/templates/', permanent=True)),
]
