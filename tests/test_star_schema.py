from __future__ import annotations

import sqlite3

from scripts.build_star_schema import build_star_schema


def test_star_schema_preserves_fact_grain_and_source_metrics() -> None:
    result = build_star_schema()

    assert result["source_sales_rows"] == 3500
    assert result["source_products_rows"] == 500
    assert result["fact_sales_rows"] == 3500
    assert result["distinct_fact_orders"] == 3500
    assert result["source_revenue"] == result["fact_revenue"] == 608810.14
    assert result["source_cost"] == result["fact_cost"] == 364075.27
    assert result["gross_margin"] == 244734.87


def test_star_schema_has_complete_dimensions_and_valid_keys() -> None:
    result = build_star_schema()
    counts = result["dimension_counts"]

    assert counts["dim_date"] == 731
    assert counts["dim_customer"] == 877
    assert counts["dim_category"] == 6
    assert counts["dim_channel"] == 7
    assert counts["dim_geography"] > 0
    assert counts["dim_payment_method"] > 0
    assert counts["dim_device"] > 0
    assert result["foreign_key_errors"] == 0
    assert result["duplicate_orders"] == 0
    assert result["unmatched_categories"] == 0
