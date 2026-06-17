from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from core.views.health import healthz
from core.views.home import home
from core.views.login import login_start
from core.views.comment_delete import comment_delete_view
from core.views.rotation import rotation_view
from core.views.player_overview import player_overview_view
from core.views.player_search import player_search_view
from core.views.player_detail import player_detail_view
from core.views.api_player_get import api_players
from core.views.api_comment_add import api_comment_add
from core.views.api_comment_delete import api_comment_delete
from core.views.api_rotation_add import api_rotation_add
from core.views.api_rotation_update import api_rotation_update
from core.views.api_rotation_delete import api_rotation_delete
from core.views.audit_logs import audit_log_list

admin.site.site_header = settings.APP_NAME
admin.site.site_title = f"{settings.APP_NAME} admin"
admin.site.index_title = settings.APP_NAME


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),

    # Public custom login entry page
    path("login/", login_start, name="login"),

    # allauth URLs
    path("accounts/", include("allauth.urls")),

    # Protected by LoginRequiredMiddleware

    # User facing pages
    path("", home, name="home"),
    path("comments/delete/<str:id>", comment_delete_view, name="comment_delete"),
    path("rotation/", rotation_view, name="rotation"),
    path("players/", player_overview_view, name="players"),
    path("players/search/", player_search_view, name="player_search"),
    path('players/<int:id>', player_detail_view, name='player_detail'),
    path("audit-logs/", audit_log_list, name="audit_logs"),

    # API
    path("api/comment/add", api_comment_add, name="api_comment_add"),
    path("api/comment/delete/<int:id>", api_comment_delete, name="api_comment_delete"),
    path("api/rotation/add", api_rotation_add, name="api_rotation_add"),
    path("api/rotation/update", api_rotation_update, name="api_rotation_update"),
    path("api/rotation/delete", api_rotation_delete, name="api_rotation_delete"),
    path("api/players", api_players, name="api_players"),
]
