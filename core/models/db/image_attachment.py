from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .stored_image import StoredImage


class ImageAttachment(models.Model):
    image = models.ForeignKey(
        StoredImage,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    attached_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="image_attachments",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.image} attached to {self.content_type}:{self.object_id}"
