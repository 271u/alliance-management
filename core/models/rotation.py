from django.core.validators import MinValueValidator
from django.db import models

from .player import Player


class TrainRotationEntry(models.Model):
    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name="train_rotation_entry",
    )

    position = models.PositiveIntegerField(
        unique=True,
        validators=[MinValueValidator(1)],
        help_text="1-based position in the train conductor rotation. The lowest position is next.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "player__ingame_name"]
        verbose_name = "train rotation entry"
        verbose_name_plural = "train rotation entries"

    def __str__(self):
        return f"{self.position}. {self.player.ingame_name}"
