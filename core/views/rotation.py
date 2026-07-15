from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core.authorization.permissions import (
    MANAGE_ROTATION,
    VIEW_ROTATION,
)
from core.models import Player, TrainRotationEntry


@permission_required(VIEW_ROTATION, raise_exception=True)
@require_GET
def rotation_view(request):
    can_manage_rotation = request.user.has_perm(MANAGE_ROTATION)

    rotation = (
        TrainRotationEntry.objects
        .select_related("player")
        .order_by("position")
    )

    management_players = Player.objects.none()

    if can_manage_rotation:
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
            "can_manage_rotation": can_manage_rotation,
        },
    )
