# core/admin.py

from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "ingame_name",
        "alliance_rank",
        "is_active",
        "can_be_conductor",
        "can_be_vip",
        "reliability_score",
        "last_conductor_at",
        "last_vip_at",
    )

    list_filter = (
        "alliance_rank",
        "is_active",
        "can_be_conductor",
        "can_be_vip",
        "reliability_score",
    )

    search_fields = ("ingame_name", "notes")

    ordering = ("ingame_name",)

    readonly_fields = ("created_at", "updated_at")
