from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    checks = connection.execute("""
        WITH invoice_checks AS (
            SELECT
                invoice_id,
                COUNT(DISTINCT customer_id) AS customer_count,
                COUNT(*) FILTER (
                    WHERE customer_id IS NULL
                ) AS missing_customer_lines,
                COUNT(*) FILTER (
                    WHERE customer_id IS NOT NULL
                ) AS identified_customer_lines,
                COUNT(DISTINCT CAST(invoice_at AS DATE))
                    AS date_count,
                COUNT(DISTINCT country) AS country_count
            FROM analytics.int_retail_eligible
            WHERE is_paid_product_sale
            GROUP BY invoice_id
        )
        SELECT
            COUNT(*) AS qualifying_orders,
            COUNT(*) FILTER (
                WHERE customer_count > 1
            ) AS multiple_customer_orders,
            COUNT(*) FILTER (
                WHERE missing_customer_lines > 0
                  AND identified_customer_lines > 0
            ) AS mixed_customer_id_orders,
            COUNT(*) FILTER (
                WHERE date_count > 1
            ) AS multiple_date_orders,
            COUNT(*) FILTER (
                WHERE country_count > 1
            ) AS multiple_country_orders,
            COUNT(*) FILTER (
                WHERE customer_count = 0
            ) AS unidentified_orders
        FROM invoice_checks
    """).fetchdf()

    print("\nORDER GRAIN CHECK")
    print(checks.T.to_string(header=False))