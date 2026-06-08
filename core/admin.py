# core/admin.py

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from django.utils import timezone
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html

from .models.auditlog import AuditLog
from .models.player import Player
from .models.past_username import PastUsername
from .models.rotation import TrainRotationEntry
from .models.comment import Comment



class PastUsernameInline(admin.TabularInline):
    model = PastUsername
    extra = 0
    fields = ("ingame_name", "recorded_at")
    readonly_fields = ("recorded_at",)
    show_change_link = True


class CommentInline(GenericTabularInline):
    model = Comment
    extra = 0

    fields = (
        "text",
        "created_by",
        "created_at",
        "updated_at",
        "deleted_at",
        "deleted_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "deleted_by",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(deleted_at__isnull=True)


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
        "is_member",
        "is_active",
        "can_be_conductor",
        "can_be_vip",
        "reliability_score",
        "last_conductor_at",
        "last_vip_at",
    )

    list_filter = (
        "alliance_rank",
        "is_member",
        "is_active",
        "can_be_conductor",
        "can_be_vip",
        "reliability_score",
    )

    search_fields = ("ingame_name", "notes")

    ordering = ("ingame_name",)

    readonly_fields = ("created_at", "updated_at")
    inlines = [
        PastUsernameInline,
        CommentInline
    ]

@admin.register(PastUsername)
class PastUsernameAdmin(admin.ModelAdmin):
    list_display = ("ingame_name", "player", "recorded_at")
    list_filter = ("recorded_at",)
    search_fields = ("ingame_name", "player__ingame_name")
    autocomplete_fields = ("player",)
    readonly_fields = ("recorded_at",)
    ordering = ("-recorded_at",)

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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "short_text",
        "referenced_object_link",
        "content_type",
        "created_by",
        "created_at",
        "is_deleted",
        "deleted_by",
        "deleted_at",
    )

    list_filter = (
        "content_type",
        "created_at",
        "deleted_at",
    )

    search_fields = (
        "text",
        "created_by__username",
        "created_by__email",
        "deleted_by__username",
        "deleted_by__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "deleted_by",
    )

    ordering = ("-created_at",)

    list_select_related = (
        "content_type",
        "created_by",
        "deleted_by",
    )

    @admin.display(description="Text")
    def short_text(self, obj):
        return obj.text[:80]

    @admin.display(description="Referenced object")
    def referenced_object_link(self, obj):
        referenced_object = obj.content_object

        if referenced_object is None:
            return "-"

        app_label = obj.content_type.app_label
        model_name = obj.content_type.model

        admin_url_name = f"admin:{app_label}_{model_name}_change"

        try:
            url = reverse(admin_url_name, args=[obj.object_id])
        except NoReverseMatch:
            return str(referenced_object)

        return format_html(
            '<a href="{}">{}</a>',
            url,
            referenced_object,
        )

    @admin.display(boolean=True, description="Deleted")
    def is_deleted(self, obj):
        return obj.deleted_at is not None
