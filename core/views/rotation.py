from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.models import Player, TrainRotationEntry


@login_required
@require_http_methods(["GET", "POST"])
def rotation_view(request):
    if request.method == "POST":
        player_id = request.POST.get("player")

        if not player_id:
            messages.error(request, "No player selected.")
            return redirect("rotation")

        player = get_object_or_404(
            Player,
            pk=player_id,
            is_active=True,
            can_be_conductor=True,
            alliance_rank__in=[
                Player.AllianceRank.R4,
                Player.AllianceRank.R5,
            ],
        )

        if TrainRotationEntry.objects.filter(player=player).exists():
            messages.warning(request, f"{player.ingame_name} is already in the rotation.")
            return redirect("rotation")

        with transaction.atomic():
            last_entry = (
                TrainRotationEntry.objects
                .select_for_update()
                .order_by("-position")
                .first()
            )

            next_position = 1

            if last_entry:
                next_position = last_entry.position + 1

            TrainRotationEntry.objects.create(
                player=player,
                position=next_position,
            )

        messages.success(request, f"Added {player.ingame_name} to the rotation.")
        return redirect("rotation")

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
