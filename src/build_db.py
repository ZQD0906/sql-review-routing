"""Load the generated CSVs into the local demo database."""

from pathlib import Path

import duckdb

TABLES = (
    "customers", "orders", "order_items", "order_payments",
    "order_reviews", "products", "sellers",
)

with duckdb.connect("data/mini.duckdb") as connection:
    connection.begin()
    for table in TABLES:
        path = Path("data/mini") / f"olist_{table}_dataset.csv"
        connection.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto(?, header=true)",
            [str(path)],
        )
    connection.commit()
print("Loaded the synthetic fixture into data/mini.duckdb.")
