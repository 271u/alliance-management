from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from core.models.db.comment import Comment
from core.models.db.image_attachment import ImageAttachment
from core.models.db.stored_image import StoredImage


def user_can_view_image(user, image: StoredImage) -> bool:
    if not user.is_authenticated:
        return False

    if image.deleted_at is not None:
        return False

    if user.is_staff:
        return True

    if image.deleted_at is not None:
        return False

    comment_content_type = ContentType.objects.get_for_model(Comment)

    comment_attachment_object_ids = ImageAttachment.objects.filter(
        image=image,
        content_type=comment_content_type,
    ).values_list("object_id", flat=True)

    comment_ids: list[int] = []

    for object_id in comment_attachment_object_ids:
        try:
            comment_ids.append(int(object_id))
        except ValueError:
            continue

    return Comment.objects.filter(
        id__in=comment_ids,
        deleted_at__isnull=True,
    ).exists()


@login_required
@require_GET
def image_file(request, image_id):
    image = get_object_or_404(StoredImage, id=image_id)

    if not user_can_view_image(request.user, image):
        return HttpResponseForbidden("You are not allowed to view this image.")

    try:
        image.file.open("rb")
    except FileNotFoundError:
        raise Http404("Image file not found.")

    return FileResponse(
        image.file,
        content_type=image.mime_type,
        filename=image.original_filename,
    )
