from django.contrib import admin
from django.urls import path, include

from core.views.home import home
from core.views.login import login_start
from core.views.rotation import rotation_view
from core.views.player_api import api_players

urlpatterns = [
    path("admin/", admin.site.urls),

    # Public custom login entry page
    path("login/", login_start, name="login"),

    # allauth URLs
    path("accounts/", include("allauth.urls")),

    # Protected by LoginRequiredMiddleware
    path("", home, name="home"),
    path("rotation/", rotation_view, name="rotation"),
    path("api/players", api_players, name="api_players"),
]
