from django.core.management.base import BaseCommand

from core.services.player_sync import sync_players_from_game


class Command(BaseCommand):
    help = "Sync players from the game into the local database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch and compare players without writing changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        result = sync_players_from_game(dry_run=dry_run)

        self.stdout.write(
            self.style.SUCCESS(
                f"Player sync completed. "
                f"created={result.created}, "
                f"updated={result.updated}, "
                f"unchanged={result.unchanged}, "
                f"joined_alliance={result.joined_alliance}, "
                f"left_alliance={result.left_alliance}"
            )
        )
