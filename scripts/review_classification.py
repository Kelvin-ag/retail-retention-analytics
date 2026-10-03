from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    summary = connection.execute("""
        SELECT
            transaction_category,
            COUNT(*) AS row_count,
            ROUND(SUM(signed_line_value), 2) AS signed_value,
            COUNT(*) FILTER (
                WHERE unit_price = 0
            ) AS zero_price_rows,
            COUNT(*) FILTER (
                WHERE customer_id IS NULL
            ) AS missing_customer_rows
        FROM analytics.int_retail_classified
        GROUP BY transaction_category
        ORDER BY row_count DESC
    """).fetchdf()

    print("\nCLASSIFICATION SUMMARY")
    print(summary.to_string(index=False))

    reconciliation = connection.execute("""
        SELECT
            (SELECT SUM(quantity * unit_price)
             FROM analytics.int_retail_combined) AS before_value,

            (SELECT SUM(signed_line_value)
             FROM analytics.int_retail_classified) AS after_value
    """).fetchdf()

    print("\nVALUE RECONCILIATION")
    print(reconciliation.to_string(index=False))