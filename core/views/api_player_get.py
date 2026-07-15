from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.authorization.decorators import json_permission_required
from core.authorization.permissions import VIEW_PLAYERS
from core.models import Player


@json_permission_required(VIEW_PLAYERS)
@require_GET
def api_players(request):
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
