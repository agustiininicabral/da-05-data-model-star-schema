from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.db"
SQL_PATH = ROOT / "03-work" / "sql" / "02_star_schema_queries.sql"


def execute_queries(
    connection: sqlite3.Connection,
    sql_text: str,
) -> dict[str, list[dict[str, Any]]]:
    results: dict[str, list[dict[str, Any]]] = {}
    for statement in (part.strip() for part in sql_text.split(";")):
        if not statement:
            continue

        match = re.search(r"^\s*--\s*QUERY:\s*(.+)$", statement, flags=re.MULTILINE)
        if match is None:
            raise ValueError(
                "Every SQL statement must start with a '-- QUERY: name' comment."
            )

        query_name = match.group(1).strip()
        sql = "\n".join(
            line for line in statement.splitlines() if not line.strip().startswith("--")
        ).strip()
        if not sql:
            raise ValueError(f"Query {query_name!r} has no SQL statement.")
        if query_name in results:
            raise ValueError(f"Duplicate query name: {query_name!r}")

        cursor = connection.execute(sql)
        columns = [description[0] for description in cursor.description or []]
        results[query_name] = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if not results:
        raise ValueError("No named SQL queries were found.")
    return results


def run_queries(
    db_path: Path = DB_PATH,
    sql_path: Path = SQL_PATH,
) -> dict[str, list[dict[str, Any]]]:
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}. Build it first.")

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign-key validation failed.")
        results = execute_queries(connection, sql_path.read_text(encoding="utf-8"))

    print(f"Executed {len(results)} star-schema queries.")
    for name, rows in results.items():
        print(f"{name}: {len(rows)} result rows")
    return results


def main() -> int:
    try:
        run_queries()
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
