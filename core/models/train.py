# core/models/train.py

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from .comment import Comment


class Train(models.Model):
    comments = GenericRelation(
        Comment,
        related_query_name="train",
    )

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
