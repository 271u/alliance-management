from dataclasses import dataclass
import datetime
import logging

from django.db import transaction
from django.utils import timezone

from core.models.past_username import PastUsername
from core.models.player import Player
from core.models.lastwartools_api import AllianceApiMember
from core.services.game_client import fetch_game_players


@dataclass
class PlayerSyncResult:
    created: int = 0
    left_alliance: int = 0
    joined_alliance: int = 0
    updated: int = 0
    unchanged: int = 0


def sync_players_from_game(*, dry_run: bool = False) -> PlayerSyncResult:
    logging.debug("Starting Player sync")
    result = PlayerSyncResult()

    now = timezone.now()

    game_players = fetch_game_players()
    logging.debug("Plaers returned by API: %d", len(game_players))
    game_player_ids = {game_player.uid for game_player in game_players}

    with transaction.atomic():
        for game_player in game_players:
            # Example expected shape:
            # {
            #     "game_id": "123456",
            #     "ingame_name": "Queen Nicole1",
            #     "rank": "R5",
            # }

            player = Player.objects.filter(last_war_id=game_player.uid).first()
            join_time = datetime.datetime.fromtimestamp(game_player.join_time / 1000, tz=datetime.UTC)

            if player is None:
                logging.debug("Player %s (UID %s): not found in database", game_player.name, game_player.uid)
                result.created += 1

                if not dry_run:
                    Player.objects.create(
                        ingame_name=game_player.name,
                        alliance_rank=game_player.rank,
                        last_war_id=game_player.uid,
                        strength=game_player.power,
                        is_member=True,
                        joined_at=join_time
                    )
                    logging.debug("Player %s (UID %s): created", game_player.name, game_player.uid)

                continue

            changed = False

            if player.ingame_name != game_player.name:
                logging.debug("Player %s (UID %s): changed their ingame name", game_player.name, game_player.uid)

                changed = True

                if not dry_run:
                    PastUsername.objects.get_or_create(
                        player=player,
                        ingame_name=player.ingame_name,
                    )
                    logging.debug("Player %s (UID %s): added past username (%s)", game_player.name, game_player.uid, player.ingame_name)


                    player.ingame_name = game_player.name

            if player.alliance_rank != game_player.rank:
                logging.debug("Player %s (UID %s): Alliance rank changed (%d -> %d)", game_player.name, game_player.uid, player.alliance_rank, game_player.rank)
                changed = True

                if not dry_run:
                    player.alliance_rank = game_player.rank
            
            if player.strength != game_player.power:
                logging.debug("Player %s (UID %s): strength changed (%d -> %d)", game_player.name, game_player.uid, player.strength, game_player.power)
                changed = True

                if not dry_run:
                    player.strength = game_player.power
            
            if player.joined_at != join_time:
                logging.debug("Player %s (UID %s): joined_at changed", game_player.name, game_player.uid)
                changed = True

                if not dry_run:
                    player.joined_at = join_time

            if player.is_member == False:
                logging.debug("Player %s (UID %s): is_member changed (%b -> %b)", game_player.name, game_player.uid)
                changed = True

                
                result.joined_alliance += 1
                if not dry_run:
                    player.is_member = True

            if changed:
                result.updated += 1

                if not dry_run:
                    player.save()
                    logging.debug("Player %s (UID %s): updated member in database", game_player.name, game_player.uid)
            else:
                result.unchanged += 1

        for existing_member in Player.objects.filter(is_member=True).exclude(last_war_id__in=game_player_ids):
            logging.debug("Player %s (UID %s): not in alliance anymore", existing_member.ingame_name, existing_member.last_war_id)
            result.left_alliance += 1

            if not dry_run:
                existing_member.is_member = False
                existing_member.left_at = now
                existing_member.save()
                logging.debug("Player %s (UID %s): updated member in database", existing_member.ingame_name, existing_member.last_war_id)

    return result
