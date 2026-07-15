from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from core.audit.rotation import (
    create_rotation_audit_log,
    rotation_order_snapshot,
)
from core.authorization.permissions import MANAGE_ROTATION
from core.models import Player, TrainRotationEntry
from core.models.db.auditlog import AuditLog


@permission_required(MANAGE_ROTATION, raise_exception=True)
@require_POST
def api_rotation_add(request: HttpRequest) -> HttpResponse:
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

    with transaction.atomic():
        current_entries = list(
            TrainRotationEntry.objects
            .select_for_update()
            .select_related("player")
            .order_by("position")
        )

        if any(entry.player_id == player.pk for entry in current_entries): # pyright: ignore[reportAttributeAccessIssue]
            messages.warning(
                request,
                f"{player.ingame_name} is already in the rotation.",
            )
            return redirect("rotation")

        old_order = rotation_order_snapshot(current_entries)

        next_position = (
            max(entry.position for entry in current_entries) + 1
            if current_entries
            else 1
        )

        TrainRotationEntry.objects.create(
            player=player,
            position=next_position,
        )

        create_rotation_audit_log(
            action=AuditLog.Action.CREATED,
            message=f"Added {player.ingame_name} to the train rotation.",
            old_order=old_order,
            new_order=[*old_order, player.ingame_name],
            extra_changes={
                "added_player": {
                    "old": None,
                    "new": player.ingame_name,
                },
                "added_player_id": {
                    "old": None,
                    "new": player.pk,
                },
            },
        )

    messages.success(
        request,
        f"Added {player.ingame_name} to the rotation.",
    )

    return redirect("rotation")
