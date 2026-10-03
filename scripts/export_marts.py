from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"
EXPORTS = PROJECT_ROOT / "data" / "exports"

EXPORTS.mkdir(parents=True, exist_ok=True)

TABLES = [
    "dim_date",
    "dim_customers",
    "dim_products",
    "fct_order_lines",
    "fct_customer_snapshot",
    "fct_cohort_retention",
]

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    for table in TABLES:
        destination = EXPORTS / f"{table}.parquet"
        temporary = EXPORTS / f"{table}.tmp.parquet"

        source = connection.table(f"analytics.{table}")
        source_count = source.count("*").fetchone()[0]

        source.write_parquet(
            str(temporary),
            compression="snappy",
        )

        exported = connection.read_parquet(str(temporary))
        exported_count = exported.count("*").fetchone()[0]

        if source_count != exported_count:
            raise ValueError(f"Row count mismatch: {table}")

        if source.columns != exported.columns or source.types != exported.types:
            raise ValueError(f"Column or type mismatch: {table}")

        temporary.replace(destination)

        size_mb = destination.stat().st_size / (1024 * 1024)
        print(f"{table}: {exported_count:,} rows | {size_mb:.2f} MB")

print("\nAll six exports completed and checked.")