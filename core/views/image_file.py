from hashlib import sha256
from typing import TypeVar

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404
from django.utils.http import http_date, parse_http_date_safe, quote_etag
from django.views.decorators.http import require_GET

from core.models.db.comment import Comment
from core.models.db.image_attachment import ImageAttachment
from core.models.db.stored_image import StoredImage


ResponseT = TypeVar("ResponseT", bound=HttpResponseBase)


def user_can_view_image(user, image: StoredImage) -> bool:
    if not user.is_authenticated:
        return False

    if image.deleted_at is not None:
        return False

    if user.is_staff:
        return True

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


def build_image_etag(image: StoredImage) -> str:
    raw_etag = sha256(
        f"{image.id}:{image.size}:{image.created_at.isoformat()}".encode(),
    ).hexdigest()

    return quote_etag(raw_etag)


def image_was_not_modified(request, image: StoredImage, etag: str) -> bool:
    if_none_match = request.headers.get("If-None-Match")

    if if_none_match:
        client_etags = [value.strip() for value in if_none_match.split(",")]

        if etag in client_etags or "*" in client_etags:
            return True

    if_modified_since = request.headers.get("If-Modified-Since")

    if if_modified_since:
        modified_since_timestamp = parse_http_date_safe(if_modified_since)

        if modified_since_timestamp is not None:
            image_created_timestamp = int(image.created_at.timestamp())

            if image_created_timestamp <= modified_since_timestamp:
                return True

    return False


def add_image_cache_headers(
    response: ResponseT,
    image: StoredImage,
    etag: str,
) -> ResponseT:
    response["Cache-Control"] = "private, max-age=0, must-revalidate"
    response["ETag"] = etag
    response["Last-Modified"] = http_date(image.created_at.timestamp())
    response["X-Content-Type-Options"] = "nosniff"

    return response


@login_required
@require_GET
def image_file(request, image_id):
    image = get_object_or_404(StoredImage, id=image_id)

    if not user_can_view_image(request.user, image):
        return HttpResponseForbidden("You are not allowed to view this image.")

    etag = build_image_etag(image)

    if image_was_not_modified(request, image, etag):
        response = HttpResponse(status=304)
        return add_image_cache_headers(response, image, etag)

    try:
        image.file.open("rb")
    except FileNotFoundError:
        raise Http404("Image file not found.")

    response = FileResponse(
        image.file,
        content_type=image.mime_type,
        filename=image.original_filename,
    )

    return add_image_cache_headers(response, image, etag)
