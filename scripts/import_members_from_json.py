#!/usr/bin/env python

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import alliance members from a JSON API response into the Django database."
    )

    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the alliance response JSON file.",
    )

    parser.add_argument(
        "--settings",
        default="config.settings",
        help="Django settings module. Defaults to config.settings.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show what would change without writing to the database.",
    )

    parser.add_argument(
        "--deactivate-missing",
        action="store_true",
        help="Mark existing Last War players as inactive if they are not present in the JSON file.",
    )

    return parser.parse_args()


def setup_django(settings_module: str) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    import django

    django.setup()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file does not exist: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Expected the JSON root to be an object.")

    return data


def get_members(data: dict[str, Any]) -> list[dict[str, Any]]:
    members = data.get("members")

    if not isinstance(members, list):
        raise ValueError("Expected JSON to contain a top-level 'members' list.")

    return members


def clean_uid(raw_uid: Any) -> str:
    if raw_uid is None:
        return ""

    return str(raw_uid).strip()


def clean_name(raw_name: Any) -> str:
    if raw_name is None:
        return ""

    return str(raw_name).strip()


def clean_rank(raw_rank: Any) -> int:
    rank = int(raw_rank)

    if rank < 1 or rank > 5:
        raise ValueError(f"Invalid alliance rank: {rank}. Expected 1 to 5.")

    return rank


def main() -> int:
    args = parse_args()
    setup_django(args.settings)

    from django.db import transaction
    from django.db.models import Q
    from core.models.player import Player

    data = load_json(args.json_file)
    members = get_members(data)

    seen_last_war_ids: set[str] = set()

    created_count = 0
    updated_count = 0
    linked_count = 0
    skipped_count = 0

    with transaction.atomic():
        for member in members:
            uid = clean_uid(member.get("uid"))
            name = clean_name(member.get("name"))

            if not uid:
                skipped_count += 1
                print("Skipping member without uid:", member)
                continue

            if not name:
                skipped_count += 1
                print(f"Skipping member {uid!r} without name:", member)
                continue

            if uid in seen_last_war_ids:
                skipped_count += 1
                print(f"Skipping duplicate uid in JSON: {uid} ({name})")
                continue

            try:
                rank = clean_rank(member.get("rank"))
            except (TypeError, ValueError) as error:
                skipped_count += 1
                print(f"Skipping {name!r} ({uid}): {error}")
                continue

            seen_last_war_ids.add(uid)

            existing_by_uid = Player.objects.filter(last_war_id=uid).first()

            if existing_by_uid:
                conflicting_name_owner = (
                    Player.objects
                    .filter(ingame_name=name)
                    .exclude(pk=existing_by_uid.pk)
                    .first()
                )

                if conflicting_name_owner:
                    skipped_count += 1
                    print(
                        f"Skipping {name!r} ({uid}): name is already used by "
                        f"player id={conflicting_name_owner.pk} "
                        f"with last_war_id={conflicting_name_owner.last_war_id!r}"
                    )
                    continue

                if args.dry_run:
                    print(
                        f"Would update by uid: {uid} "
                        f"name {existing_by_uid.ingame_name!r} -> {name!r}, "
                        f"rank {existing_by_uid.alliance_rank} -> {rank}, "
                        f"is_active=True"
                    )
                    updated_count += 1
                    continue

                old_name = existing_by_uid.ingame_name

                existing_by_uid.ingame_name = name
                existing_by_uid.alliance_rank = rank
                existing_by_uid.is_active = True
                existing_by_uid.save(
                    update_fields=[
                        "ingame_name",
                        "alliance_rank",
                        "is_active",
                        "updated_at",
                    ]
                )

                updated_count += 1
                print(
                    f"Updated by uid: {uid} "
                    f"{old_name!r} -> {existing_by_uid.ingame_name!r}, "
                    f"rank {existing_by_uid.alliance_rank}"
                )
                continue

            existing_by_name_without_uid = (
                Player.objects
                .filter(ingame_name=name)
                .filter(Q(last_war_id__isnull=True) | Q(last_war_id=""))
                .first()
            )

            if existing_by_name_without_uid:
                if args.dry_run:
                    print(
                        f"Would link existing player by name: {name!r} "
                        f"last_war_id None -> {uid}, "
                        f"rank {existing_by_name_without_uid.alliance_rank} -> {rank}, "
                        f"is_active=True"
                    )
                    linked_count += 1
                    continue

                existing_by_name_without_uid.last_war_id = uid
                existing_by_name_without_uid.alliance_rank = rank
                existing_by_name_without_uid.is_active = True
                existing_by_name_without_uid.save(
                    update_fields=[
                        "last_war_id",
                        "alliance_rank",
                        "is_active",
                        "updated_at",
                    ]
                )

                linked_count += 1
                print(
                    f"Linked existing player: {name} "
                    f"last_war_id={uid}, rank {existing_by_name_without_uid.alliance_rank}"
                )
                continue

            conflicting_name_owner = Player.objects.filter(ingame_name=name).first()

            if conflicting_name_owner:
                skipped_count += 1
                print(
                    f"Skipping {name!r} ({uid}): name is already used by "
                    f"player id={conflicting_name_owner.pk} "
                    f"with last_war_id={conflicting_name_owner.last_war_id!r}"
                )
                continue

            if args.dry_run:
                print(f"Would create: {name} uid {uid} rank {rank}")
                created_count += 1
                continue

            player = Player.objects.create(
                last_war_id=uid,
                ingame_name=name,
                alliance_rank=rank,
                is_active=True,
            )

            created_count += 1
            print(
                f"Created: {player.ingame_name} "
                f"last_war_id={player.last_war_id}, rank {player.alliance_rank}"
            )

        deactivated_count = 0

        if args.deactivate_missing:
            missing_players = (
                Player.objects
                .filter(last_war_id__isnull=False)
                .exclude(last_war_id="")
                .exclude(last_war_id__in=seen_last_war_ids)
            )

            if args.dry_run:
                deactivated_count = missing_players.filter(is_active=True).count()

                for player in missing_players.filter(is_active=True):
                    print(
                        f"Would deactivate: {player.ingame_name} "
                        f"last_war_id={player.last_war_id}"
                    )
            else:
                deactivated_count = missing_players.filter(is_active=True).update(
                    is_active=False
                )

        if args.dry_run:
            transaction.set_rollback(True)

    print()
    print("Import finished.")
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")
    print(f"Linked existing players: {linked_count}")
    print(f"Skipped: {skipped_count}")

    if args.deactivate_missing:
        print(f"Deactivated missing players: {deactivated_count}")

    if args.dry_run:
        print("Dry run only. No database changes were written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
