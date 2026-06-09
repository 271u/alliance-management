from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from core.models.db.player import Player

@require_http_methods(["GET"])
def api_players(request):
    return _api_players_get(request)


def _api_players_get(request):
    players = Player.objects.filter(is_active=True).order_by(
        "-alliance_rank",
        "ingame_name",
    )

    data = [
        {
            "id": player.pk,
            "ingame_name": player.ingame_name,
            "alliance_rank": player.alliance_rank,
            "alliance_rank_display": Player.AllianceRank(player.alliance_rank).label,
            "can_be_conductor": player.can_be_conductor,
            "can_be_vip": player.can_be_vip,
            "reliability_score": player.reliability_score,
            "last_conductor_at": player.last_conductor_at.isoformat()
            if player.last_conductor_at
            else None,
            "last_vip_at": player.last_vip_at.isoformat()
            if player.last_vip_at
            else None,
        }
        for player in players
    ]

    return JsonResponse(
        {
            "count": len(data),
            "players": data,
        }
    )
