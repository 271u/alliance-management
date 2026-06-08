from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Player


@require_http_methods(["GET"])
def player_detail_view(request, id):
    error_message = ""

    try:
        player = Player.objects.get(id=id)
        comments = player.comments.filter(deleted_at__isnull=True)
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
            "error_message": error_message
        },
    )
