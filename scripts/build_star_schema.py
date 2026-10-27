from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SALES_PATH = ROOT / "02-data" / "raw" / "sales.csv"
PRODUCTS_PATH = ROOT / "02-data" / "raw" / "products.csv"
SCHEMA_PATH = ROOT / "03-work" / "sql" / "schema.sql"
DB_PATH = ROOT / "data" / "warehouse.db"

SALES_REQUIRED = {
    "order_id",
    "customer_id",
    "order_date",
    "category",
    "channel",
    "country",
    "city",
    "quantity",
    "unit_price",
    "discount_rate",
    "net_revenue",
    "cost",
    "payment_method",
    "device",
}
PRODUCTS_REQUIRED = {"product_id", "product_name", "category", "brand", "active"}


def _read_csv(path: Path, required_columns: set[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        missing = sorted(required_columns - set(reader.fieldnames))
        if missing:
            raise ValueError(f"{path.name} is missing columns: {missing}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"CSV has no data rows: {path}")
    return rows


def _load_and_validate_sales(path: Path) -> list[dict[str, Any]]:
    rows = _read_csv(path, SALES_REQUIRED)
    order_ids = [row["order_id"] for row in rows]
    if len(order_ids) != len(set(order_ids)):
        raise ValueError("Sales CSV contains duplicate order_id values.")

    validated: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, start=2):
        blanks = [column for column in SALES_REQUIRED if not (row.get(column) or "").strip()]
        if blanks:
            raise ValueError(f"Sales row {row_number} has blank required fields: {blanks}")

        try:
            order_date = date.fromisoformat(row["order_date"])
            quantity = int(row["quantity"])
            unit_price = float(row["unit_price"])
            discount_rate = float(row["discount_rate"])
            net_revenue = float(row["net_revenue"])
            cost = float(row["cost"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Sales row {row_number} has invalid date/numeric data.") from error

        if quantity <= 0:
            raise ValueError(f"Sales row {row_number}: quantity must be positive.")
        if unit_price < 0 or cost < 0 or net_revenue < 0:
            raise ValueError(f"Sales row {row_number}: amounts must be non-negative.")
        if not 0 <= discount_rate <= 0.20:
            raise ValueError(f"Sales row {row_number}: discount_rate outside 0..0.20.")
        expected_revenue = round(quantity * unit_price * (1 - discount_rate), 2)
        if abs(net_revenue - expected_revenue) > 0.011:
            raise ValueError(f"Sales row {row_number}: net_revenue formula mismatch.")

        validated.append(
            {
                **row,
                "parsed_date": order_date,
                "quantity_value": quantity,
                "unit_price_value": unit_price,
                "discount_rate_value": discount_rate,
                "net_revenue_value": net_revenue,
                "cost_value": cost,
                "gross_margin_value": round(net_revenue - cost, 2),
            }
        )
    return validated


def build_star_schema(
    sales_path: Path = SALES_PATH,
    products_path: Path = PRODUCTS_PATH,
    schema_path: Path = SCHEMA_PATH,
    db_path: Path = DB_PATH,
) -> dict[str, int]:
    sales = _load_and_validate_sales(sales_path)
    products = _read_csv(products_path, PRODUCTS_REQUIRED)
    for row_number, row in enumerate(products, start=2):
        blanks = [column for column in PRODUCTS_REQUIRED if not (row.get(column) or "").strip()]
        if blanks:
            raise ValueError(f"Products row {row_number} has blank fields: {blanks}")
        if row["active"].strip().lower() not in {"yes", "no"}:
            raise ValueError(f"Products row {row_number}: active must be Yes or No.")
    product_categories = {row["category"] for row in products}
    sales_categories = {row["category"] for row in sales}
    missing_categories = sorted(sales_categories - product_categories)
    if missing_categories:
        raise ValueError(f"Sales categories missing from product catalog: {missing_categories}")
    product_ids = [row["product_id"] for row in products]
    if len(product_ids) != len(set(product_ids)):
        raise ValueError("Products CSV contains duplicate product_id values.")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = schema_path.read_text(encoding="utf-8")
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_sql)

        dates = sorted({row["parsed_date"] for row in sales})
        customers = sorted({row["customer_id"] for row in sales})
        channels = sorted({row["channel"] for row in sales})
        categories = sorted({row["category"] for row in sales})
        geographies = sorted({(row["country"], row["city"]) for row in sales})
        payment_methods = sorted({row["payment_method"] for row in sales})
        devices = sorted({row["device"] for row in sales})

        date_keys = {value: int(value.strftime("%Y%m%d")) for value in dates}
        customer_keys = {value: index for index, value in enumerate(customers, start=1)}
        channel_keys = {value: index for index, value in enumerate(channels, start=1)}
        category_keys = {value: index for index, value in enumerate(categories, start=1)}
        geography_keys = {value: index for index, value in enumerate(geographies, start=1)}
        payment_keys = {value: index for index, value in enumerate(payment_methods, start=1)}
        device_keys = {value: index for index, value in enumerate(devices, start=1)}

        with connection:
            connection.executemany(
                "INSERT INTO dim_date VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        date_keys[value],
                        value.isoformat(),
                        value.year,
                        value.month,
                        (value.month - 1) // 3 + 1,
                        value.strftime("%B"),
                        value.strftime("%A"),
                    )
                    for value in dates
                ],
            )
            connection.executemany(
                "INSERT INTO dim_customer VALUES (?, ?)",
                [(customer_keys[value], value) for value in customers],
            )
            connection.executemany(
                "INSERT INTO dim_channel VALUES (?, ?)",
                [(channel_keys[value], value) for value in channels],
            )
            connection.executemany(
                "INSERT INTO dim_category VALUES (?, ?)",
                [(category_keys[value], value) for value in categories],
            )
            connection.executemany(
                "INSERT INTO dim_geography VALUES (?, ?, ?)",
                [
                    (geography_keys[value], value[0], value[1])
                    for value in geographies
                ],
            )
            connection.executemany(
                "INSERT INTO dim_payment_method VALUES (?, ?)",
                [(payment_keys[value], value) for value in payment_methods],
            )
            connection.executemany(
                "INSERT INTO dim_device VALUES (?, ?)",
                [(device_keys[value], value) for value in devices],
            )
            connection.executemany(
                """
                INSERT INTO fact_sales (
                    order_id, date_key, customer_key, channel_key, category_key,
                    geography_key, payment_method_key, device_key, quantity,
                    unit_price, discount_rate, net_revenue, cost, gross_margin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row["order_id"],
                        date_keys[row["parsed_date"]],
                        customer_keys[row["customer_id"]],
                        channel_keys[row["channel"]],
                        category_keys[row["category"]],
                        geography_keys[(row["country"], row["city"])],
                        payment_keys[row["payment_method"]],
                        device_keys[row["device"]],
                        row["quantity_value"],
                        row["unit_price_value"],
                        row["discount_rate_value"],
                        row["net_revenue_value"],
                        row["cost_value"],
                        row["gross_margin_value"],
                    )
                    for row in sales
                ],
            )

        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "fact_sales",
                "dim_date",
                "dim_customer",
                "dim_channel",
                "dim_category",
                "dim_geography",
                "dim_payment_method",
                "dim_device",
            )
        }
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Star schema foreign-key validation failed.")
        return counts
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the retail star schema in SQLite.")
    parser.add_argument("--sales", type=Path, default=SALES_PATH)
    parser.add_argument("--products", type=Path, default=PRODUCTS_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--db", type=Path, default=DB_PATH)
    args = parser.parse_args()

    try:
        counts = build_star_schema(args.sales, args.products, args.schema, args.db)
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    for table, count in counts.items():
        print(f"{table}: {count}")
    print(f"PASS - Star schema created at {args.db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
