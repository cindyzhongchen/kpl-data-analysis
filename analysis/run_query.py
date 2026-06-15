import sys
import sqlite3
from pathlib import Path

import pandas as pd


def load_query(query_path: Path) -> str:
    with open(query_path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python analysis/run_query.py <query_name>")
        print("Example: python analysis/run_query.py top_avg_kills")
        return

    query_name = sys.argv[1]

    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "kpl.db"
    query_path = project_root / "sql" / f"{query_name}.sql"

    if not query_path.exists():
        print(f"Query file not found: {query_path}")
        return

    conn = sqlite3.connect(db_path)
    query = load_query(query_path)

    df = pd.read_sql_query(query, conn)
    conn.close()

    print(df)


if __name__ == "__main__":
    main()