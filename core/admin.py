# core/admin.py

from django.contrib import admin
from .models.player import Player
from .models.auditlog import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "action",
        "content_type",
        "object_repr",
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
