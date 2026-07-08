from django.conf import settings

from core.models.db.player_sync_run import PlayerSyncRun

def app_metadata(request):
    return {
        "APP_NAME": settings.APP_NAME,
        "APP_VERSION": settings.APP_VERSION,
        "APP_SOURCE_URL": settings.APP_SOURCE_URL,
    }

def player_sync_status(request):
    latest_player_sync = (
        PlayerSyncRun.objects
        .order_by("-started_at")
        .first()
    )

    latest_successful_player_sync = (
        PlayerSyncRun.objects
        .filter(status="success")
        .order_by("-started_at")
        .first()
    )

    return {
        "latest_player_sync": latest_player_sync,
        "latest_successful_player_sync": latest_successful_player_sync,
    }


def app_branding(request):
    return {
        "app_name": settings.APP_NAME,
    }
