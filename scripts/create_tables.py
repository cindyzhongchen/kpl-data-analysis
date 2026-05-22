import sqlite3
from pathlib import Path                                            


def main() -> None:
    # Make sure the data folder exists
    project_root = Path(__file__).resolve().parent.parent           # find project path
    data_dir = project_root / "data"                                # create folder
    data_dir.mkdir(exist_ok=True)

    db_path = data_dir / "kpl.db"                                  

    conn = sqlite3.connect(db_path)                                 # connect data base
    cursor = conn.cursor()                                          

    # Turn on foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")                     

    # Create tables
    cursor.executescript (
        """
        CREATE TABLE IF NOT EXISTS seasons (
            season_id INTEGER PRIMARY KEY,
            season_name TEXT NOT NULL,
            year INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL UNIQUE,
            role TEXT CHECK (role IN ('对抗路', '打野', '中路', '发育路', '游走'))
        );

        CREATE TABLE IF NOT EXISTS heroes (
            hero_id INTEGER PRIMARY KEY,
            hero_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            season_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            teamA_id INTEGER NOT NULL,
            teamB_id INTEGER NOT NULL,
            winner_team_id INTEGER NOT NULL,
            best_of INTEGER NOT NULL,
            patch TEXT,
            FOREIGN KEY (season_id) REFERENCES seasons(season_id),
            FOREIGN KEY (teamA_id) REFERENCES teams(team_id),
            FOREIGN KEY (teamB_id) REFERENCES teams(team_id),
            FOREIGN KEY (winner_team_id) REFERENCES teams(team_id)
        );

        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            match_id INTEGER NOT NULL,
            game_number INTEGER NOT NULL,
            winner_team_id INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            FOREIGN KEY (match_id) REFERENCES matches(match_id),
            FOREIGN KEY (winner_team_id) REFERENCES teams(team_id)
        );

        CREATE TABLE IF NOT EXISTS player_stats (
            game_id TEXT NOT NULL,
            player_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            hero_id INTEGER NOT NULL,
            side TEXT NOT NULL CHECK (side IN ('red', 'blue')),
            kills INTEGER NOT NULL DEFAULT 0,
            deaths INTEGER NOT NULL DEFAULT 0,
            assists INTEGER NOT NULL DEFAULT 0,
            gold INTEGER,
            win INTEGER NOT NULL CHECK (win IN (0, 1)),
            is_mvp INTEGER NOT NULL CHECK (is_mvp IN (0, 1)),
            PRIMARY KEY (game_id, player_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (hero_id) REFERENCES heroes(hero_id)
        );
        """
    )

    conn.commit()
    conn.close()

    print(f"Database created successfully at: {db_path}")


if __name__ == "__main__":
    main()