# core/admin.py

from django.contrib import admin

from .models.auditlog import AuditLog
from .models.player import Player
from .models.rotation import TrainRotationEntry


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "action",
        "content_type",
        "object_repr",
        "message",
        "path",
        "ip_address",
    )

    list_filter = (
        "action",
        "content_type",
        "created_at",
    )

    search_fields = (
        "object_repr",
        "message",
        "actor__username",
        "actor__email",
        "path",
    )

    readonly_fields = (
        "created_at",
        "actor",
        "action",
        "content_type",
        "object_id",
        "object_repr",
        "message",
        "changes",
        "path",
        "ip_address",
    )

    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

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


@admin.register(TrainRotationEntry)
class TrainRotationEntryAdmin(admin.ModelAdmin):
    list_display = (
        "position",
        "player",
        "player_alliance_rank",
        "player_is_active",
        "player_can_be_conductor",
        "updated_at",
    )

    list_select_related = ("player",)

    list_filter = (
        "player__alliance_rank",
        "player__is_active",
        "player__can_be_conductor",
    )

    search_fields = (
        "player__ingame_name",
        "player__notes",
    )

    ordering = ("position", "player__ingame_name")

    autocomplete_fields = ("player",)

    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Rank", ordering="player__alliance_rank")
    def player_alliance_rank(self, obj):
        return obj.player.get_alliance_rank_display()

    @admin.display(boolean=True, description="Active", ordering="player__is_active")
    def player_is_active(self, obj):
        return obj.player.is_active

    @admin.display(
        boolean=True,
        description="Can be conductor",
        ordering="player__can_be_conductor",
    )
    def player_can_be_conductor(self, obj):
        return obj.player.can_be_conductor
