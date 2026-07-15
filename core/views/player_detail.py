from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core.authorization.permissions import VIEW_PLAYERS
from core.models import Player


@permission_required(VIEW_PLAYERS, raise_exception=True)
@require_GET
def player_detail_view(request, id):
    error_message = ""

    try:
        player = Player.objects.get(id=id)
        comments = player.comments.filter(
            deleted_at__isnull=True,
        ).prefetch_related("image_attachments__image")
    except Player.DoesNotExist:
        error_message = f"Player with ID {id} not found."
        player = None
        comments = None

    return render(
        request,
        "player_detail.html",
        {
            "player": player,
            "comments": comments,
        },
    )
