from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from scanner import views as scanner_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("scanner.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name="logout"),
    path("accounts/register/", scanner_views.SignUpView.as_view(), name="register"),
]
