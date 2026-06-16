from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Player, TrainRotationEntry
from core.models.db.player_sync_run import PlayerSyncRun


def _format_strength(value) -> str:
    value = value or 0

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"{value / 1_000:.2f}K"

    return str(value)


@require_http_methods(["GET"])
def home(request):
    members = Player.objects.filter(is_member=True)
    non_members = Player.objects.filter(is_member=False)

    member_stats = members.aggregate(
        member_count=Count("id"),
        total_strength=Sum("strength"),
        average_strength=Avg("strength"),
        conductor_enabled_count=Count(
            "id",
            filter=Q(can_be_conductor=True),
        ),
        vip_enabled_count=Count(
            "id",
            filter=Q(can_be_vip=True),
        ),
    )

    active_comment_count = (
        members.aggregate(
            count=Count(
                "comments",
                filter=Q(comments__deleted_at__isnull=True),
            )
        )["count"]
        or 0
    )

    member_count = member_stats["member_count"] or 0
    total_strength = member_stats["total_strength"] or 0
    average_strength = member_stats["average_strength"] or 0

    rank_counts = {
        row["alliance_rank"]: row["count"]
        for row in members.values("alliance_rank").annotate(count=Count("id"))
    }

    rank_breakdown = []

    for rank_value, rank_label in reversed(Player.AllianceRank.choices):
        count = rank_counts.get(rank_value, 0)
        percentage = (count / member_count * 100) if member_count else 0

        rank_breakdown.append(
            {
                "label": rank_label,
                "count": count,
                "percentage": percentage,
            }
        )

    rotation_eligible_players = members.filter(
        is_active=True,
        can_be_conductor=True,
        alliance_rank__in=[
            Player.AllianceRank.R4,
            Player.AllianceRank.R5,
        ],
    )

    rotation_count = TrainRotationEntry.objects.count()
    rotation_eligible_count = rotation_eligible_players.count()
    rotation_missing_count = rotation_eligible_players.filter(
        train_rotation_entry__isnull=True,
    ).count()

    next_rotation_entries = (
        TrainRotationEntry.objects
        .select_related("player")
        .order_by("position")[:5]
    )

    top_players = members.order_by("-strength", "ingame_name")[:5]

    recent_joined_players = (
        members
        .filter(joined_at__isnull=False)
        .order_by("-joined_at")[:5]
    )

    recent_left_players = (
        non_members
        .filter(left_at__isnull=False)
        .order_by("-left_at")[:5]
    )

    latest_player_sync = (
        PlayerSyncRun.objects
        .order_by("-started_at")
        .first()
    )

    latest_successful_player_sync = (
        PlayerSyncRun.objects
        .filter(status=PlayerSyncRun.Status.SUCCESS)
        .order_by("-started_at")
        .first()
    )

    return render(
        request,
        "home.html",
        {
            "member_count": member_count,
            "non_member_count": non_members.count(),
            "total_player_count": Player.objects.count(),

            "total_strength": _format_strength(total_strength),
            "average_strength": _format_strength(average_strength),

            "conductor_enabled_count": member_stats["conductor_enabled_count"] or 0,
            "vip_enabled_count": member_stats["vip_enabled_count"] or 0,
            "active_comment_count": active_comment_count,

            "rank_breakdown": rank_breakdown,

            "rotation_count": rotation_count,
            "rotation_eligible_count": rotation_eligible_count,
            "rotation_missing_count": rotation_missing_count,
            "next_rotation_entries": next_rotation_entries,

            "top_players": top_players,
            "recent_joined_players": recent_joined_players,
            "recent_left_players": recent_left_players,

            "players_without_join_date_count": members.filter(joined_at__isnull=True).count(),
            "players_without_strength_count": members.filter(strength=0).count(),

            "latest_player_sync": latest_player_sync,
            "latest_successful_player_sync": latest_successful_player_sync,
        },
    )
