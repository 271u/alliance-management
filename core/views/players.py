from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Player


@require_http_methods(["GET"])
def player_view(request):
    players = (
        Player.objects
        .filter(is_member=True)
        .order_by("-alliance_rank", "ingame_name")
    )

    return render(
        request,
        "players.html",
        {
            "players": players
        },
    )
