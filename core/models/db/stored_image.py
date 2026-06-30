from __future__ import annotations

import uuid
from pathlib import Path
from typing import cast

from django.conf import settings
from django.db import models
from django.utils import timezone


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def stored_image_upload_to(instance: models.Model, filename: str) -> str:
    stored_image = cast("StoredImage", instance)

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        extension = ""

    now = timezone.now()
    return f"images/{now:%Y/%m/%d}/{stored_image.id}{extension}"


class StoredImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    file = models.ImageField(upload_to=stored_image_upload_to)

    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField(help_text="Original uploaded file size in bytes.")
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_images",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_images",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.original_filename

    def soft_delete(self, user=None) -> None:
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["deleted_at", "deleted_by"])
