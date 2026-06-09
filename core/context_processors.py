from core.models.db.player_sync_run import PlayerSyncRun


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
