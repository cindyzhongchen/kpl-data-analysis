import sqlite3
from pathlib import Path

# checks database contents
def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "kpl.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = [
        "teams",
        "players",
        "heroes",
        "matches",
        "games",
        "player_stats",
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        print(f"{table}: {count} rows")

    conn.close()


if __name__ == "__main__":
    main()