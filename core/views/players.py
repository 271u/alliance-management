from django.db.models import Count, Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Player


@require_http_methods(["GET"])
def player_view(request):
    show_others = True if request.GET.get("others") == "true" else False

    players = (
        Player.objects
        .filter(is_member=(not show_others))
        .annotate(
            active_comment_count=Count(
                "comments",
                filter=Q(comments__deleted_at__isnull=True),
            )
        )
        .order_by("-alliance_rank", "ingame_name")
    )

    return render(
        request,
        "players.html",
        {
            "players": players,
            "show_others": show_others
        },
    )
