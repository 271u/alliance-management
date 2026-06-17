#!/bin/sh
set -eu

interval="${PLAYER_SYNC_INTERVAL_SECONDS:-10800}"
initial_delay="${PLAYER_SYNC_INITIAL_DELAY_SECONDS:-120}"

echo "Player sync worker starting."
echo "Initial delay: ${initial_delay}s"
echo "Interval: ${interval}s"

sleep "$initial_delay"

while true; do
  echo "Running player sync at $(date -Iseconds)"

  if python manage.py sync_players; then
    echo "Player sync completed at $(date -Iseconds)"
  else
    echo "Player sync failed at $(date -Iseconds)" >&2
  fi

  sleep "$interval"
done
