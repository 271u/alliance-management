from django.db import models

class PastUsername(models.Model):
    player = models.ForeignKey(
        "Player",
        on_delete=models.CASCADE,
        related_name="past_usernames",
    )

    ingame_name = models.CharField(max_length=100, db_index=True)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return self.ingame_name
