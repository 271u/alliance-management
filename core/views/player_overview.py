from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.authorization.permissions import VIEW_PLAYERS
from core.models import Player


@permission_required(VIEW_PLAYERS, raise_exception=True)
@require_http_methods(["GET"])
def player_overview_view(request):
    show_others = request.GET.get("others") == "true"

    players = (
        Player.objects
        .filter(is_member=not show_others)
        .annotate(
            active_comment_count=Count(
                "comments",
                filter=Q(comments__deleted_at__isnull=True),
            )
        )
        .order_by("-alliance_rank", "ingame_name")
    )

    template_name = (
        "non_member_overview.html"
        if show_others
        else "member_overview.html"
    )

    return render(
        request,
        template_name,
        {
            "players": players,
            "show_others": show_others,
        },
    )
