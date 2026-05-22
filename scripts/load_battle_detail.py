import json
import sqlite3
from pathlib import Path

from parse_battle_detail import (
    parse_team_rows,
    parse_game_row,
    parse_player_rows,
    parse_hero_rows,
    parse_player_stats_rows,
)


def get_or_create_player(cursor, player_name: str, role: str | None) -> int:
    cursor.execute(
        "SELECT player_id FROM players WHERE player_name = ?",
        (player_name,),
    )
    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        "INSERT INTO players (player_name, role) VALUES (?, ?)",
        (player_name, role),
    )
    return cursor.lastrowid


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "kpl.db"
    json_path = project_root / "data" / "battle_detail.json"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    data = payload["data"]
    match_id = 2026031402

    teams = parse_team_rows(data)
    game = parse_game_row(data, match_id)
    players = parse_player_rows(data)
    heroes = parse_hero_rows(data)
    player_stats = parse_player_stats_rows(data)

    # Insert teams
    for team in teams:
        cursor.execute(
            """
            INSERT OR IGNORE INTO teams (team_id, team_name)
            VALUES (?, ?)
            """,
            (team["team_id"], team["team_name"]),
        )

    # Insert heroes
    for hero in heroes:
        cursor.execute(
            """
            INSERT OR IGNORE INTO heroes (hero_id, hero_name)
            VALUES (?, ?)
            """,
            (hero["hero_id"], hero["hero_name"]),
        )

    # Insert players and build name -> id map
    player_id_map = {}

    for player in players:
        player_id = get_or_create_player(
            cursor,
            player["player_name"],
            player["role"],
        )
        player_id_map[player["player_name"]] = player_id

    # Temporary: insert season and match manually
    cursor.execute(
        """
        INSERT OR IGNORE INTO seasons (season_id, season_name, year)
        VALUES (?, ?, ?)
        """,
        (1, "2026 KPL Spring", 2026),
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO matches
        (match_id, season_id, date, teamA_id, teamB_id, winner_team_id, best_of, patch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            match_id,
            1,
            "2026-03-14",
            10001,
            10008,
            game["winner_team_id"],
            5,
            None,
        ),
    )

    # Insert game
    cursor.execute(
        """
        INSERT OR IGNORE INTO games
        (game_id, match_id, game_number, winner_team_id, duration)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            game["game_id"],
            game["match_id"],
            game["game_number"],
            game["winner_team_id"],
            game["duration"],
        ),
    )

    # Insert player stats
    for stat in player_stats:
        player_id = player_id_map[stat["player_name"]]

        cursor.execute(
            """
            INSERT OR IGNORE INTO player_stats
            (game_id, player_id, team_id, hero_id, side, kills, deaths, assists, gold, win, is_mvp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stat["game_id"],
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

    conn.commit()
    conn.close()

    print("Battle detail loaded into SQLite successfully.")


if __name__ == "__main__":
    main()