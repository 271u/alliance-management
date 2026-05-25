from django.contrib import admin
from django.urls import path, include

from core.views import home, login_start

urlpatterns = [
    path("admin/", admin.site.urls),

    # Public custom login entry page
    path("login/", login_start, name="login"),

    # allauth URLs
    path("accounts/", include("allauth.urls")),

    # Protected by LoginRequiredMiddleware
    path("", home, name="home"),
]
