import os
import requests
import logging
from core.models.api.lastwartools_api import AllianceApiResponse, AllianceApiMember


def fetch_game_players() -> list[AllianceApiMember]:

    api_url = os.getenv("LASTWAR_TOOLS_BASEURL", "https://api.lastwar.tools").strip().rstrip("/")
    api_token = os.getenv("LASTWAR_TOOLS_APIKEY", "").strip()
    alliance_id = os.getenv("LASTWAR_TOOLS_ALLIANCEID", "").strip()

    query_params={
        "sort_by": "power",
        "descending": "true",
        "session_key": ""
    }

    url = f"{api_url}/alliance/{alliance_id}/members"

    response = requests.get(
        url,
        headers={
            "X-API-Key": api_token,
            "Accept": "application/json",
        },
        params=query_params,
        timeout=30,
    )
    try:
        response.raise_for_status()
    
    except requests.HTTPError as e:
        logging.error(f"got non-success code from {url} ({response.status_code}): {e}")
        raise e

    try:
        result = AllianceApiResponse.model_validate_json(response.text)
    except ValueError as e:
        logging.error("failed to parse response from API: %s", e)
        raise e

    return result.members

    
