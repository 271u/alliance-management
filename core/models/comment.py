from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .player import Player

class Comment(models.Model):
    content = models.CharField()

    player = models.ForeignKey("player", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ingame_name"]
