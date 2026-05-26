from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    class AllianceRank(models.IntegerChoices):
        R1 = 1, "R1"
        R2 = 2, "R2"
        R3 = 3, "R3"
        R4 = 4, "R4"
        R5 = 5, "R5"

    ingame_name = models.CharField(max_length=100, unique=True)

    alliance_rank = models.PositiveSmallIntegerField(
        choices=AllianceRank.choices,
        default=AllianceRank.R1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Alliance rank from 1 to 5. Higher means higher rank.",
    )

    is_active = models.BooleanField(default=True)

    can_be_conductor = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this player should be considered for train conductor rotation.",
    )

    can_be_vip = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this player can be selected as VIP / Guardian Defender.",
    )

    reliability_score = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Manual score from 1 to 5. Higher means more reliable.",
    )

    last_conductor_at = models.DateField(null=True, blank=True)
    last_vip_at = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ingame_name"]

    def __str__(self):
        return self.ingame_name
