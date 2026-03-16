import json
from pathlib import Path


def parse_team_rows(data: dict) -> list[dict]:
    rows = []
    for camp_key in ["camp1", "camp2"]:
        camp = data[camp_key]

        # create a new dictionary and add it to list rows
        rows.append({
            "team_id": int(camp["team_id"]),
            "team_name": camp["team_name"],
        })
    return rows


def parse_game_row(data: dict, match_id: int) -> dict:
    win_camp = data["win_camp"]
    winner_team_id = int(data[f"camp{win_camp}"]["team_id"])

    return {
        "game_id": data["battle_id"],
        "match_id": match_id,
        "game_number": data["battle_seq"],
        "winner_team_id": winner_team_id,
        "duration": data["game_duration"] // 1000,  # seconds
    }


def parse_player_rows(data: dict) -> list[dict]:
    seen = set() # using hash table cause search has a time complexity of O(1)
    rows = []

    for p in data["battle_player_list"]:
        player_name = p["player_name"]
        role = p.get("position_desc")

        if player_name not in seen:
            rows.append({
                "player_name": player_name,
                "role": role,
            })
            seen.add(player_name)

    return rows


def parse_hero_rows(data: dict) -> list[dict]:
    seen = set()
    rows = []

    for p in data["battle_player_list"]:
        hero_id = int(p["hero_id"])
        hero_name = p["hero_name"]

        if hero_id not in seen:
            rows.append({
                "hero_id": hero_id,
                "hero_name": hero_name,
            })
            seen.add(hero_id)

    return rows


def parse_player_stats_rows(data: dict) -> list[dict]:
    rows = []
    game_id = data["battle_id"]
    win_camp = data["win_camp"]

    for p in data["battle_player_list"]:
        camp = int(p["camp"])

        rows.append({
            "game_id": game_id,
            "player_name": p["player_name"],   # later we'll map this to player_id
            "team_id": int(p["team_id"]),
            "hero_id": int(p["hero_id"]),
            "side": "blue" if camp == 1 else "red",
            "kills": int(p["kill_num"]),
            "deaths": int(p["death_num"]),
            "assists": int(p["assist_num"]),
            "gold": int(p["gold"]),
            "win": 1 if camp == win_camp else 0,
            "is_mvp": int(p["is_mvp"]),
        })

    return rows


def main() -> None:
    # put your raw JSON in data/battle_detail.json first
    project_root = Path(__file__).resolve().parent.parent   # 项目根目录
    json_path = project_root / "data" / "battle_detail.json"

    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    data = payload["data"]

    match_id = 2026031402  # temporary hardcoded value

    teams = parse_team_rows(data)
    game = parse_game_row(data, match_id)
    players = parse_player_rows(data)
    heroes = parse_hero_rows(data)
    player_stats = parse_player_stats_rows(data)

    print("=== GAME ===")
    print(game)

    print("\n=== TEAMS ===")
    for row in teams:
        print(row)

    print("\n=== PLAYERS ===")
    for row in players:
        print(row)

    print("\n=== HEROES ===")
    for row in heroes:
        print(row)

    print("\n=== PLAYER STATS ===")
    for row in player_stats:
        print(row)


if __name__ == "__main__":
    main()