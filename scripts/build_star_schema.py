from __future__ import annotations

import csv
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SALES_PATH = ROOT / "02-data" / "raw" / "sales.csv"
PRODUCTS_PATH = ROOT / "02-data" / "raw" / "products.csv"
SCHEMA_PATH = ROOT / "03-work" / "sql" / "01_core_queries.sql"
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DIMENSIONS = (
    "dim_date",
    "dim_customer",
    "dim_category",
    "dim_channel",
    "dim_geography",
    "dim_payment_method",
    "dim_device",
)


def load_csv(connection: sqlite3.Connection, path: Path, table: str) -> int:
    if not IDENTIFIER.fullmatch(table):
        raise ValueError(f"Unsafe table name: {table!r}")

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames
        if not columns or any(not IDENTIFIER.fullmatch(column) for column in columns):
            raise ValueError(f"CSV has a missing header or unsupported columns: {path}")
        rows = list(reader)

    definitions = ", ".join(f'"{column}" TEXT' for column in columns)
    names = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    connection.execute(f'CREATE TABLE "{table}" ({definitions})')
    connection.executemany(
        f'INSERT INTO "{table}" ({names}) VALUES ({placeholders})',
        [[row.get(column) for column in columns] for row in rows],
    )
    return len(rows)


def build_star_schema(
    sales_path: Path = SALES_PATH,
    products_path: Path = PRODUCTS_PATH,
    schema_path: Path = SCHEMA_PATH,
) -> dict[str, Any]:
    with sqlite3.connect(":memory:") as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        sales_rows = load_csv(connection, sales_path, "sales")
        products_rows = load_csv(connection, products_path, "products")
        connection.executescript(schema_path.read_text(encoding="utf-8"))

        fact = connection.execute(
            """
            SELECT COUNT(*), ROUND(SUM(net_revenue), 2), ROUND(SUM(cost), 2),
                   COUNT(DISTINCT order_id)
            FROM fact_sales
            """
        ).fetchone()
        source_revenue = connection.execute(
            "SELECT ROUND(SUM(CAST(net_revenue AS REAL)), 2) FROM sales"
        ).fetchone()[0]
        source_cost = connection.execute(
            "SELECT ROUND(SUM(CAST(cost AS REAL)), 2) FROM sales"
        ).fetchone()[0]
        dimension_counts = {
            table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in DIMENSIONS
        }
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        duplicate_orders = connection.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT order_id FROM fact_sales
                GROUP BY order_id HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]
        unmatched_categories = connection.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT DISTINCT category FROM sales
                EXCEPT
                SELECT DISTINCT category FROM products
            )
            """
        ).fetchone()[0]

    fact_rows, revenue, cost, distinct_orders = fact
    result = {
        "source_sales_rows": sales_rows,
        "source_products_rows": products_rows,
        "fact_sales_rows": fact_rows,
        "distinct_fact_orders": distinct_orders,
        "source_revenue": source_revenue,
        "fact_revenue": revenue,
        "source_cost": source_cost,
        "fact_cost": cost,
        "gross_margin": round((revenue or 0) - (cost or 0), 2),
        "dimension_counts": dimension_counts,
        "foreign_key_errors": len(foreign_key_errors),
        "duplicate_orders": duplicate_orders,
        "unmatched_categories": unmatched_categories,
    }
    return result


def main() -> int:
    try:
        result = build_star_schema()
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    checks_pass = (
        result["source_sales_rows"] == result["fact_sales_rows"]
        and result["fact_sales_rows"] == result["distinct_fact_orders"]
        and result["source_revenue"] == result["fact_revenue"]
        and result["source_cost"] == result["fact_cost"]
        and result["foreign_key_errors"] == 0
        and result["duplicate_orders"] == 0
        and result["unmatched_categories"] == 0
    )
    if not checks_pass:
        print("ERROR: Star schema validation failed.", file=sys.stderr)
        return 1

    print("PASS - Star schema loaded and validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
