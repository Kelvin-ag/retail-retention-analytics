from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    customers = connection.execute("""
        SELECT
            COUNT(*) AS dimension_rows,
            COUNT(*) FILTER (
                WHERE is_unknown
            ) AS unknown_members,
            COUNT(*) FILTER (
                WHERE NOT is_unknown
                  AND first_observed_purchase_date IS NOT NULL
            ) AS purchasing_customers,
            COUNT(*) FILTER (
                WHERE NOT is_unknown
                  AND first_observed_purchase_date IS NULL
            ) AS credit_only_customers
        FROM analytics.dim_customers
    """).fetchdf()

    print("\nCUSTOMER DIMENSION CHECK")
    print(customers.T.to_string(header=False))