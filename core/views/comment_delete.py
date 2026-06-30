from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from core.models.db.comment import Comment
from core.models.db.player import Player


def get_safe_next_url(request) -> str:
    next_url = request.GET.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return reverse("home")


@require_http_methods(["GET"])
def comment_delete_view(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to delete comments.")

    comment = get_object_or_404(
        Comment.objects.prefetch_related("image_attachments__image"),
        id=id,
        deleted_at__isnull=True,
    )

    object_ref = comment.content_object
    object_type = "unknown"
    object_href = reverse("home")
    object_name = "Unknown object"

    if isinstance(object_ref, Player):
        object_type = "player"
        object_href = reverse("player_detail", args=[object_ref.id]) # pyright: ignore[reportAttributeAccessIssue]
        object_name = object_ref.ingame_name

    return render(
        request,
        "comment_delete.html",
        {
            "comment": comment,
            "target": {
                "type": object_type,
                "href": object_href,
                "name": object_name,
            },
            "next_url": get_safe_next_url(request),
        },
    )
