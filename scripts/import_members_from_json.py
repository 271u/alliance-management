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
        help="Mark existing players as inactive if they are not present in the JSON file.",
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
    from core.models.player import Player

    data = load_json(args.json_file)
    members = get_members(data)

    seen_names: set[str] = set()
    created_count = 0
    updated_count = 0
    skipped_count = 0

    with transaction.atomic():
        for member in members:
            name = clean_name(member.get("name"))

            if not name:
                skipped_count += 1
                print("Skipping member without name:", member)
                continue

            try:
                rank = clean_rank(member.get("rank"))
            except (TypeError, ValueError) as error:
                skipped_count += 1
                print(f"Skipping {name!r}: {error}")
                continue

            seen_names.add(name)

            if args.dry_run:
                existing = Player.objects.filter(ingame_name=name).first()

                if existing:
                    print(
                        f"Would update: {name} "
                        f"rank {existing.alliance_rank} -> {rank}, "
                        f"is_active=True"
                    )
                    updated_count += 1
                else:
                    print(f"Would create: {name} rank {rank}")
                    created_count += 1

                continue

            player, created = Player.objects.update_or_create(
                ingame_name=name,
                defaults={
                    "alliance_rank": rank,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                print(f"Created: {player.ingame_name} rank {player.alliance_rank}")
            else:
                updated_count += 1
                print(f"Updated: {player.ingame_name} rank {player.alliance_rank}")

        deactivated_count = 0

        if args.deactivate_missing:
            missing_players = Player.objects.exclude(ingame_name__in=seen_names)

            if args.dry_run:
                deactivated_count = missing_players.filter(is_active=True).count()
                for player in missing_players.filter(is_active=True):
                    print(f"Would deactivate: {player.ingame_name}")
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
    print(f"Skipped: {skipped_count}")

    if args.deactivate_missing:
        print(f"Deactivated missing players: {deactivated_count}")

    if args.dry_run:
        print("Dry run only. No database changes were written.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
