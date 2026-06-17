from django.db.models import Count, Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Player


@require_http_methods(["GET"])
def player_search_view(request):
    query = request.GET.get("q", "").strip()

    if query:
        players = (
            Player.objects
            .filter(ingame_name__icontains=query)
            .annotate(
                active_comment_count=Count(
                    "comments",
                    filter=Q(comments__deleted_at__isnull=True),
                    distinct=True,
                )
            )
            .order_by("ingame_name")
        )
    else:
        players = None

    return render(
        request,
        "player_search.html",
        {
            "players": players,
            "query": query,
        },
    )
