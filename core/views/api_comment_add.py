import logging

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from PIL import Image, UnidentifiedImageError

from core.helpers import JsonErrorMessage
from core.models.db.image_attachment import ImageAttachment
from core.models.db.player import Player
from core.models.db.stored_image import StoredImage
from core.audit.comment import create_comment_created_audit_log


ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class ImageValidationError(ValueError):
    pass


def validate_uploaded_image(uploaded_file):
    max_size_bytes = settings.COMMENT_IMAGE_MAX_SIZE_MB * 1024 * 1024

    if uploaded_file.size > max_size_bytes:
        raise ImageValidationError(
            f"{uploaded_file.name} is too large. Maximum size is {settings.COMMENT_IMAGE_MAX_SIZE_MB} MB."
        )

    if uploaded_file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ImageValidationError(
            f"{uploaded_file.name} is not an allowed image type. Allowed: JPG, PNG, WEBP."
        )

    try:
        uploaded_file.seek(0)

        with Image.open(uploaded_file) as image:
            image.verify()

        uploaded_file.seek(0)

        with Image.open(uploaded_file) as image:
            width, height = image.size

    except (UnidentifiedImageError, OSError):
        raise ImageValidationError(f"{uploaded_file.name} is not a valid image.")
    finally:
        uploaded_file.seek(0)

    if width * height > settings.COMMENT_IMAGE_MAX_PIXELS:
        raise ImageValidationError(f"{uploaded_file.name} is too large in pixel dimensions.")

    return width, height


def add_player_comment(request) -> HttpResponse:
    try:
        target_id = int(request.POST.get("target_id", ""))
    except ValueError:
        return JsonErrorMessage("target_id must be a number", 400)

    message = request.POST.get("message", "").strip()
    images = request.FILES.getlist("images")

    if len(message) < 3:
        return JsonErrorMessage("Comment must contain at least 3 characters", 400)

    if len(images) > settings.COMMENT_IMAGE_MAX_FILES:
        return JsonErrorMessage(
            f"You can upload at most {settings.COMMENT_IMAGE_MAX_FILES} images per comment.",
            400,
        )

    try:
        player = Player.objects.get(id=target_id)
    except Player.DoesNotExist:
        return JsonErrorMessage(f"Player with ID {target_id} not found", 400)

    validated_images = []

    for image in images:
        try:
            width, height = validate_uploaded_image(image)
        except ImageValidationError as error:
            return JsonErrorMessage(str(error), 400)

        validated_images.append((image, width, height))

    try:
        with transaction.atomic():
            comment = player.comments.create(
                text=message,
                created_by=request.user,
            )

            for image, width, height in validated_images:
                stored_image = StoredImage.objects.create(
                    file=image,
                    original_filename=image.name[:255],
                    mime_type=image.content_type or "application/octet-stream",
                    size=image.size,
                    width=width,
                    height=height,
                    uploaded_by=request.user,
                )

                ImageAttachment.objects.create(
                    image=stored_image,
                    content_object=comment,
                    attached_by=request.user,
                )

            create_comment_created_audit_log(comment)

    except Exception as error:
        logging.error(
            "Failed to create new comment (by=%s, playerId=%s): %s",
            request.user,
            target_id,
            error,
        )
        return JsonErrorMessage("Failed to add comment")

    logging.debug("New comment for playerId=%s by %s", target_id, request.user)

    return HttpResponse(status=201)


@require_http_methods(["POST"])
def api_comment_add(request):
    target_type = request.POST.get("target_type", "")

    match target_type:
        case "player":
            return add_player_comment(request)
        case _:
            return JsonErrorMessage("Message body invalid", 400)
