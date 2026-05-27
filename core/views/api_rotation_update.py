import json

from django.db import transaction
from django.db.models import Max
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from core.models import TrainRotationEntry


@require_http_methods(["POST"])
def api_rotation_update(request: HttpRequest) -> HttpResponse:
    try:
        update_items = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body."},
            status=400,
        )

    if not isinstance(update_items, list):
        return JsonResponse(
            {"error": "Expected a list of rotation entries."},
            status=400,
        )

    player_ids: list[int] = []

    for item in update_items:
        if not isinstance(item, dict):
            return JsonResponse(
                {"error": "Each rotation entry must be an object."},
                status=400,
            )

        player_id = item.get("id")

        if isinstance(player_id, str) and player_id.isdigit():
            player_id = int(player_id)

        if not isinstance(player_id, int):
            return JsonResponse(
                {"error": "Each rotation entry needs a numeric id."},
                status=400,
            )

        player_ids.append(player_id)

    if len(player_ids) != len(set(player_ids)):
        return JsonResponse(
            {"error": "Duplicate player ids are not allowed."},
            status=400,
        )

    with transaction.atomic():
        entries = list(
            TrainRotationEntry.objects
            .select_for_update()
            .select_related("player")
            .all()
        )

        entries_by_player_id = {
            entry.player.id: entry # pyright: ignore[reportAttributeAccessIssue]
            for entry in entries
        }

        existing_player_ids = set(entries_by_player_id.keys())
        submitted_player_ids = set(player_ids)

        if submitted_player_ids != existing_player_ids:
            return JsonResponse(
                {
                    "error": "Submitted rotation does not match current rotation.",
                    "missing_ids": sorted(existing_player_ids - submitted_player_ids),
                    "unknown_ids": sorted(submitted_player_ids - existing_player_ids),
                },
                status=400,
            )

        max_position = (
            TrainRotationEntry.objects
            .aggregate(max_position=Max("position"))
            ["max_position"]
            or 0
        )

        for index, entry in enumerate(entries, start=1):
            entry.position = max_position + index

        TrainRotationEntry.objects.bulk_update(
            entries,
            ["position"],
        )

        reordered_entries: list[TrainRotationEntry] = []

        for position, player_id in enumerate(player_ids, start=1):
            entry = entries_by_player_id[player_id]
            entry.position = position
            reordered_entries.append(entry)

        TrainRotationEntry.objects.bulk_update(
            reordered_entries,
            ["position"],
        )

    return JsonResponse(
        {"success": True},
        status=200,
    )
