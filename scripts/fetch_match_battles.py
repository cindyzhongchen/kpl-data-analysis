import json
import sys              # provides access to command-line arguments
import time             # allows us to pause between requests/retries
from pathlib import Path

import requests         # for HTTP requests


MATCH_BATTLES_URL = "https://prod.comp.smoba.qq.com/leaguesite/match/battles/open"
BATTLE_DETAIL_URL = "https://prod.comp.smoba.qq.com/leaguesite/battle/open"


def fetch_json(url: str, params: dict, max_retries: int = 3) -> dict:
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()  # converts JSON response into Python dictionary

        except requests.RequestException as e:
            print(
                f"Request failed "
                f"(attempt {attempt}/{max_retries}): {e}"
            )

            if attempt < max_retries:
                wait_time = attempt * 2
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/fetch_match_battles.py <match_id>")
        return

    match_id = sys.argv[1]

    project_root = Path(__file__).resolve().parent.parent

    output_dir = (
        project_root
        / "data"
        / "raw_battles"
        / match_id
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch list of battles belonging to this match
    match_payload = fetch_json(
        MATCH_BATTLES_URL,
        {"match_id": match_id},
    )

    battles = match_payload["results"]

    print(f"Found {len(battles)} battles for match {match_id}")

    # Fetch each individual battle
    for battle in battles:
        battle_id = battle["battle_id"]
        battle_seq = battle["battle_seq"]

        print(f"Fetching battle {battle_seq}: {battle_id}...")

        output_path = (
            output_dir
            / f"battle_{battle_seq:02d}_{battle_id}.json"
        )

        # Don't download battles we already have
        if output_path.exists():
            print(
                f"Skipping battle {battle_seq} "
                "(already downloaded)"
            )
            continue

        battle_payload = fetch_json(
            BATTLE_DETAIL_URL,
            {"battle_id": battle_id},
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                battle_payload,
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"Saved {output_path}")

        # Wait one second before requesting the next battle
        time.sleep(1)

    print("Done.")


if __name__ == "__main__":
    main()