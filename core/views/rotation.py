from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.models import Player, TrainRotationEntry


@require_http_methods(["GET"])
def rotation_view(request):
    rotation = (
        TrainRotationEntry.objects
        .select_related("player")
        .order_by("position")
    )

    management_players = (
        Player.objects
        .filter(
            is_active=True,
            can_be_conductor=True,
            alliance_rank__in=[
                Player.AllianceRank.R4,
                Player.AllianceRank.R5,
            ],
            train_rotation_entry__isnull=True,
        )
        .order_by("-alliance_rank", "ingame_name")
    )

    return render(
        request,
        "rotation.html",
        {
            "rotation": rotation,
            "management_players": management_players,
        },
    )
