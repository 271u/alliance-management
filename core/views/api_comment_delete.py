import logging

from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from core.models.db.comment import Comment
from core.models.api.comment_api import ApiCommentModel
from core.helpers import JsonErrorMessage

@require_http_methods(["DELETE"])
def api_comment_delete(request, id):

    try:
        comment = Comment.objects.get(
            id=id,
            deleted_at__isnull=True,
        )
    except Comment.DoesNotExist:
        logging.error(f"Failed to execute comment deletion request for ID {id} by {request.user}: Comment not found")
        return JsonErrorMessage(f"Comment with ID {id} not found!")
    
    if not request.user.is_staff:
        logging.error(f"Failed to soft delete comment {id}: User {request.user} is not staff!")
        return JsonErrorMessage("You are not allowed to delete this comment.", 403)

    comment.soft_delete(request.user)

    logging.debug(f"Successfully soft deleted comment with id={id}")

    return HttpResponse(status=204)
