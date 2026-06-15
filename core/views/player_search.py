from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Player

@require_http_methods(["GET"])
def player_search_view(request):
    query = request.GET.get("q", "").strip()

    if query:
        players = Player.objects.filter(Q(ingame_name__icontains=query)).order_by("ingame_name")
    else:
        players = None


    return render(request, "player_search.html", {
        "players": players,
        "query": query,
    })
