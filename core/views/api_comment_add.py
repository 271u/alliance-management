import logging

from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from core.models.player import Player
from core.models.comment_api import ApiCommentModel
from core.helpers import JsonErrorMessage

@require_http_methods(["POST"])
def api_comment_add(request):
    return _api_comment_post(request)


def add_player_comment(comment: ApiCommentModel, commenter: str) -> HttpResponse:
    try:
        player = Player.objects.get(id=comment.target_id)
    except Player.DoesNotExist:
        return JsonErrorMessage(f"Player with ID {comment.target_id} not found", 400)

    try: 
        player.comments.create(
            text=comment.message,
            created_by=commenter,
        )
    except Exception as e:
        logging.error(f"Failed to create new comment (by={commenter},playerId={comment.target_id}): {e}")
        return JsonErrorMessage(f"Failed to add comment")
    
    logging.debug(f"New comment for playerId={comment.target_id} by {commenter}")

    return HttpResponse(status=201)



def _api_comment_post(request):

    try:
        result = ApiCommentModel.model_validate_json(request.body)
    except ValueError:
        return JsonErrorMessage("Message body invalid", 400)
    
    match result.target_type:
        case "player":
            return add_player_comment(result, request.user)
        case _:
            return JsonErrorMessage("Message body invalid", 400)
