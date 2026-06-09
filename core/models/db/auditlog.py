from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        DELETED = "deleted", "Deleted"

    created_at = models.DateTimeField(auto_now_add=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )

    object_id = models.CharField(max_length=255)

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    object_repr = models.CharField(max_length=255)

    changes = models.JSONField(default=dict, blank=True)

    message = models.TextField(blank=True)

    path = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["action"]),
        ]

    @property
    def summary(self):
        if self.message:
            return self.message

        return f"{self.get_action_display()} {self.object_repr}" # pyright: ignore[reportAttributeAccessIssue]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} - {self.action} - {self.object_repr}"
