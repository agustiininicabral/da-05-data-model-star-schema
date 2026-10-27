from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import pytest

from scripts.build_star_schema import (
    PRODUCTS_PATH,
    SALES_PATH,
    SCHEMA_PATH,
    build_star_schema,
)
from scripts.run_queries import execute_queries, run_queries


def test_star_schema_build_and_kpi_queries_reconcile(tmp_path: Path) -> None:
    database = tmp_path / "warehouse.db"
    counts = build_star_schema(db_path=database)

    assert counts["fact_sales"] == 3500
    assert counts["dim_customer"] == 877
    assert counts["dim_category"] == 6
    assert counts["dim_channel"] == 7
    assert counts["dim_date"] > 300
    assert counts["dim_geography"] > 10

    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        fact = connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT order_id), "
            "ROUND(SUM(net_revenue), 2), ROUND(SUM(gross_margin), 2) "
            "FROM fact_sales"
        ).fetchone()
        assert fact == (3500, 3500, 608810.14, 244734.87)

    results = run_queries(db_path=database)
    assert len(results) == 8
    monthly = next(rows for name, rows in results.items() if name.startswith("Q01"))
    cumulative = next(rows for name, rows in results.items() if name.startswith("Q07"))
    reconciliation = next(
        rows for name, rows in results.items() if name.startswith("Q08")
    )

    assert len(monthly) == 24
    assert float(cumulative[-1]["cumulative_revenue"]) == pytest.approx(
        608810.14, abs=0.01
    )
    assert reconciliation[0]["fact_rows"] == 3500
    assert reconciliation[0]["distinct_orders"] == 3500
    assert float(reconciliation[0]["revenue"]) == pytest.approx(608810.14, abs=0.01)


def test_builder_rejects_duplicate_order_ids(tmp_path: Path) -> None:
    duplicate_sales = tmp_path / "duplicate_sales.csv"
    with SALES_PATH.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        rows = list(reader)[:2]
    assert fields is not None
    rows[1]["order_id"] = rows[0]["order_id"]
    with duplicate_sales.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(ValueError, match="duplicate order_id"):
        build_star_schema(
            sales_path=duplicate_sales,
            products_path=PRODUCTS_PATH,
            schema_path=SCHEMA_PATH,
            db_path=tmp_path / "invalid.db",
        )


def test_query_runner_rejects_unnamed_sql() -> None:
    with sqlite3.connect(":memory:") as connection:
        with pytest.raises(ValueError, match="must start with"):
            execute_queries(connection, "SELECT 1;")
