import logging

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from core.helpers import JsonErrorMessage
from core.models.db.comment import Comment
from core.audit.comment import create_comment_deleted_audit_log


@require_http_methods(["DELETE"])
def api_comment_delete(request, id):
    if not request.user.is_staff:
        logging.error(
            "Failed to soft delete comment %s: User %s is not staff.",
            id,
            request.user,
        )
        return JsonErrorMessage("You are not allowed to delete this comment.", 403)

    try:
        comment = Comment.objects.get(
            id=id,
            deleted_at__isnull=True,
        )
    except Comment.DoesNotExist:
        logging.error(
            "Failed to execute comment deletion request for ID %s by %s: Comment not found.",
            id,
            request.user,
        )
        return JsonErrorMessage(f"Comment with ID {id} not found!", 404)

    comment.soft_delete(request.user)
    create_comment_deleted_audit_log(comment)

    logging.debug("Successfully soft deleted comment with id=%s", id)

    return HttpResponse(status=204)
