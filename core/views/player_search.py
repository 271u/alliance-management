from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core.authorization.permissions import VIEW_PLAYERS
from core.models import Player


@permission_required(VIEW_PLAYERS, raise_exception=True)
@require_GET
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
