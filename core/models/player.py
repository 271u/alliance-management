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

    last_war_id = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique player ID from Last War.",
    )

    strength = models.PositiveBigIntegerField(
        default=0,
        help_text="Strength of player"
    )

    is_active = models.BooleanField(default=True)

    is_member = models.BooleanField(
        default=False,
        help_text="True if player is currently member of this alliance."
    )

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

    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def strength_string(self):
        """Returns the strength formatted as a readable string (e.g., 15.92M)."""
        return f"{self.strength / 1_000_000:.2f}M"

    class Meta:
        ordering = ["ingame_name"]

    def __str__(self):
        return self.ingame_name
