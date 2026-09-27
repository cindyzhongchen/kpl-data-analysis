import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

from parse_battle_detail import (
    parse_team_rows,
    parse_battle_row,
    parse_player_rows,
    parse_hero_rows,
    parse_player_stats_rows,
)

# Helper for extracting date from match id
def get_match_date(match_id: int) -> str:
    match_id_str = str(match_id)

    # Validate length
    if len(match_id_str) != 10:
        raise ValueError(
            f"Invalid match_id: {match_id}. Expected 10 digits."
        )

    # First 8 digits represent YYYYMMDD
    date_str = match_id_str[:8]

    try:
        date = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError(
            f"Invalid date inside match_id: {match_id}"
        )

    return date.strftime("%Y-%m-%d")


def get_or_create_player(cursor, player_name: str, role: str | None) -> int:
    cursor.execute(
        "SELECT player_id FROM players WHERE player_name = ?",
        (player_name,),
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO players (player_name, role)
        VALUES (?, ?)
        """,
        (player_name, role),
    )

    return cursor.lastrowid


def load_one_battle(cursor, data: dict, match_id: int) -> None:
    """
    Insert one battle and its related data into the database.

    The JSON has already been read by load_match().
    """

    teams = parse_team_rows(data)
    battle = parse_battle_row(data, match_id)
    players = parse_player_rows(data)
    heroes = parse_hero_rows(data)
    player_stats = parse_player_stats_rows(data)

    # Insert teams
    for team in teams:
        cursor.execute(
            """
            INSERT OR IGNORE INTO teams
            (team_id, team_name)
            VALUES (?, ?)
            """,
            (
                team["team_id"],
                team["team_name"],
            ),
        )

    # Insert heroes
    for hero in heroes:
        cursor.execute(
            """
            INSERT OR IGNORE INTO heroes
            (hero_id, hero_name)
            VALUES (?, ?)
            """,
            (
                hero["hero_id"],
                hero["hero_name"],
            ),
        )

    # Insert players and build player_name -> player_id map
    player_id_map = {}

    for player in players:
        player_id = get_or_create_player(
            cursor,
            player["player_name"],
            player["role"],
        )

        player_id_map[player["player_name"]] = player_id

    # Insert battle
    cursor.execute(
        """
        INSERT OR IGNORE INTO battles
        (battle_id, match_id, battle_number, winner_team_id, duration)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            battle["battle_id"],
            battle["match_id"],
            battle["battle_number"],
            battle["winner_team_id"],
            battle["duration"],
        ),
    )

    # Insert player stats
    for stat in player_stats:
        player_id = player_id_map[stat["player_name"]]

        cursor.execute(
            """
            INSERT OR IGNORE INTO player_stats
            (
                battle_id,
                player_id,
                team_id,
                hero_id,
                side,
                kills,
                deaths,
                assists,
                gold,
                win,
                is_mvp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stat["battle_id"],
                player_id,
                stat["team_id"],
                stat["hero_id"],
                stat["side"],
                stat["kills"],
                stat["deaths"],
                stat["assists"],
                stat["gold"],
                stat["win"],
                stat["is_mvp"],
            ),
        )


def load_match(cursor, json_files: list[Path], match_id: int) -> None:
    """
    Read all battle JSON files once, determine the BO5 winner,
    insert one match row, then insert each battle.
    """

    battles = []

    # Read every JSON file exactly once
    for json_path in json_files:
        with open(json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        data = payload["data"]

        teams = parse_team_rows(data)
        battle = parse_battle_row(data, match_id)

        battles.append({
            "json_path": json_path,
            "data": data,
            "teams": teams,
            "battle": battle,
        })

    # Get the two teams from the first battle
    team_a_id = battles[0]["teams"][0]["team_id"]
    team_b_id = battles[0]["teams"][1]["team_id"]

    # Count battle wins
    win_counts = {
        team_a_id: 0,
        team_b_id: 0,
    }

    for battle_info in battles:
        winner_team_id = battle_info["battle"]["winner_team_id"]
        win_counts[winner_team_id] += 1

    # Determine BO5 match winner
    match_winner_id = None

    for team_id, wins in win_counts.items():
        if wins >= 3:
            match_winner_id = team_id
            break

    if match_winner_id is None:
        raise ValueError(
            f"Could not determine winner for match {match_id}. "
            f"Battle wins: {win_counts}"
        )

    print(f"Battle wins: {win_counts}")
    print(f"Match winner team ID: {match_winner_id}")

    # Temporary season metadata
    cursor.execute(
        """
        INSERT OR IGNORE INTO seasons
        (season_id, season_name, year)
        VALUES (?, ?, ?)
        """,
        (
            1,
            "2026 KPL Spring",
            2026,
        ),
    )

    # Insert teams before match because matches references teams
    for team in battles[0]["teams"]:
        cursor.execute(
            """
            INSERT OR IGNORE INTO teams
            (team_id, team_name)
            VALUES (?, ?)
            """,
            (
                team["team_id"],
                team["team_name"],
            ),
        )

    # Insert exactly one match
    cursor.execute(
        """
        INSERT OR IGNORE INTO matches
        (
            match_id,
            season_id,
            date,
            teamA_id,
            teamB_id,
            winner_team_id,
            best_of,
            patch
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            match_id,
            1,                  # TODO: derive season
            get_match_date(match_id),
            team_a_id,
            team_b_id,
            match_winner_id,
            5,
            None,
        ),
    )

    # No reopening JSON files here.
    # Pass the data we already read to load_one_battle().
    for battle_info in battles:
        print(f"Loading {battle_info['json_path'].name}...")

        load_one_battle(
            cursor,
            battle_info["data"],
            match_id,
        )


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: "
            "python scripts/load_battle_detail.py <match_id>"
        )
        return

    match_id = int(sys.argv[1])

    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "kpl.db"

    match_dir = (
        project_root
        / "data"
        / "raw_battles"
        / str(match_id)
    )

    json_files = sorted(match_dir.glob("*.json"))

    if not json_files:
        print(
            f"No battle JSON files found for match {match_id}"
        )
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    load_match(
        cursor,
        json_files,
        match_id,
    )

    conn.commit()
    conn.close()

    print(
        f"Loaded match {match_id} with "
        f"{len(json_files)} battles successfully."
    )


if __name__ == "__main__":
    main()