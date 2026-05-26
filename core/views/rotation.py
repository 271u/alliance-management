from django.shortcuts import render
from core.models.player import Player



def rotation(request):
    management_players = Player.objects.filter(
        is_active=True,
        alliance_rank__gte=Player.AllianceRank.R4,
    ).order_by("-alliance_rank", "ingame_name")

    return render(
        request,
        "rotation.html",
        {
            "management_players": management_players,
        },
    )
