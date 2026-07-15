import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from core.models import TrainRotationEntry
from core.models.db.auditlog import AuditLog
from core.audit.rotation import create_rotation_audit_log, rotation_order_snapshot
from core.authorization.decorators import json_permission_required
from core.authorization.permissions import MANAGE_ROTATION


@json_permission_required(MANAGE_ROTATION)
@require_http_methods(["DELETE"])
def api_rotation_delete(request):
    try:
        body = request.body.decode("utf-8")
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON body."},
            status=400,
        )

    raw_player_id = data.get("id")

    if raw_player_id is None:
        return JsonResponse(
            {"success": False, "error": "Missing player id."},
            status=400,
        )

    try:
        player_id = int(raw_player_id)
    except (TypeError, ValueError):
        return JsonResponse(
            {"success": False, "error": "Invalid player id."},
            status=400,
        )

    with transaction.atomic():
        try:
            entry = (
                TrainRotationEntry.objects
                .select_for_update()
                .select_related("player")
                .get(player_id=player_id)
            )
        except TrainRotationEntry.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Rotation entry not found."},
                status=404,
            )

        old_entries = list(
            TrainRotationEntry.objects
            .select_for_update()
            .select_related("player")
            .order_by("position")
        )
        old_order = rotation_order_snapshot(old_entries)

        deleted_player_name = entry.player.ingame_name
        entry.delete()

        remaining_entries = list(
            TrainRotationEntry.objects
            .select_for_update()
            .select_related("player")
            .order_by("position")
        )

        if remaining_entries:
            temporary_position_offset = (
                max(entry.position for entry in remaining_entries)
                + len(remaining_entries)
                + 1
            )

            for index, remaining_entry in enumerate(remaining_entries, start=1):
                remaining_entry.position = temporary_position_offset + index

            TrainRotationEntry.objects.bulk_update(
                remaining_entries,
                ["position"],
            )

            for position, remaining_entry in enumerate(remaining_entries, start=1):
                remaining_entry.position = position

            TrainRotationEntry.objects.bulk_update(
                remaining_entries,
                ["position"],
            )

        new_order = rotation_order_snapshot(remaining_entries)

        create_rotation_audit_log(
            action=AuditLog.Action.DELETED,
            message=f"Removed {deleted_player_name} from the train rotation.",
            old_order=old_order,
            new_order=new_order,
            extra_changes={
                "removed_player": {
                    "old": deleted_player_name,
                    "new": None,
                },
                "removed_player_id": {
                    "old": player_id,
                    "new": None,
                },
            },
        )

    return JsonResponse(
        {
            "success": True,
            "deleted_player_id": player_id,
            "deleted_player_name": deleted_player_name,
        }
    )
