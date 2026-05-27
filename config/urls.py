from django.contrib import admin
from django.urls import path, include

from core.views.home import home
from core.views.login import login_start
from core.views.rotation import rotation_view
from core.views.api_player_get import api_players
from core.views.api_rotation_add import api_rotation_add
from core.views.api_rotation_update import api_rotation_update
from core.views.api_rotation_delete import api_rotation_delete

urlpatterns = [
    path("admin/", admin.site.urls),

    # Public custom login entry page
    path("login/", login_start, name="login"),

    # allauth URLs
    path("accounts/", include("allauth.urls")),

    # Protected by LoginRequiredMiddleware
    path("", home, name="home"),
    path("rotation/", rotation_view, name="rotation"),
    path("api/rotation/add", api_rotation_add, name="api_rotation_add"),
    path("api/rotation/update", api_rotation_update, name="api_rotation_update"),
    path("api/rotation/delete", api_rotation_delete, name="api_rotation_delete"),
    path("api/players", api_players, name="api_players"),
]
