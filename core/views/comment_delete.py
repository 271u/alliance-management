from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from core.models.db.player import Player
from core.models.db.comment import Comment


@require_http_methods(["GET"])
def comment_delete_view(request, id):
    next_url = request.GET.get("next")
    



    comment = get_object_or_404(Comment, id=id)
    object_ref = comment.content_object
    object_type = ""
    object_href = ""
    object_name = ""

    if isinstance(object_ref, Player):
        object_type = "player"
        object_href = f"/players/{object_ref.id}" # type: ignore
        object_name = object_ref.ingame_name

    return render(
        request,
        "comment_delete.html",
        {
            "comment": comment,
            "target": {
                "type": object_type,
                "href": object_href,
                "name": object_name
            },
            "next_url": next_url
        },
    )
