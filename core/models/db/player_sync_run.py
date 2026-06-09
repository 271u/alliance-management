from django.db import models


class PlayerSyncRun(models.Model):
  class Status(models.TextChoices):
    RUNNING = "running", "Running"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"

  status = models.CharField(
    max_length=20,
    choices=Status.choices,
    default=Status.RUNNING,
  )

  message = models.TextField(blank=True)

  created_count = models.PositiveIntegerField(default=0)
  updated_count = models.PositiveIntegerField(default=0)
  joined_count = models.PositiveIntegerField(default=0)
  left_count = models.PositiveIntegerField(default=0)

  started_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  finished_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    ordering = ["-started_at"]
    verbose_name = "Player sync run"
    verbose_name_plural = "Player sync runs"

  def __str__(self):
    return f"Player sync run #{self.id} - {self.status}" # pyright: ignore[reportAttributeAccessIssue]
