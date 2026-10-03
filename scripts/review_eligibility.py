from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    summary = connection.execute("""
        SELECT
            CASE
                WHEN is_paid_product_sale THEN 'Product sales'
                WHEN is_product_credit THEN 'Product credits'
                ELSE 'Excluded'
            END AS treatment,
            COUNT(*) AS row_count,
            SUM(signed_line_value) AS signed_value,
            SUM(net_product_revenue) AS product_revenue
        FROM analytics.int_retail_eligible
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    print("\nELIGIBILITY SUMMARY")
    print(summary.to_string(index=False))

    checks = connection.execute("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE is_paid_product_sale AND is_product_credit
            ) AS conflicting_flags,
            COUNT(*) FILTER (
                WHERE is_paid_product_sale IS NULL
                   OR is_product_credit IS NULL
            ) AS missing_flags,
            SUM(net_product_revenue) AS net_product_revenue,
            SUM(signed_line_value - net_product_revenue)
                AS excluded_signed_value,
            (SELECT SUM(signed_line_value)
             FROM analytics.int_retail_classified)
                - SUM(signed_line_value) AS value_difference
        FROM analytics.int_retail_eligible
    """).fetchdf()

    print("\nELIGIBILITY CHECKS")
    print(checks.T.to_string(header=False))