from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    # customer status
    summary = connection.execute("""
        WITH status_totals AS (
            SELECT
                EXTRACT(YEAR FROM order_date)::INTEGER AS year,
                customer_status,
                COUNT(*) AS order_count,
                COUNT(DISTINCT customer_id) AS identified_customers,
                SUM(product_sales_value) AS sales_value
            FROM analytics.int_order_customer_status
            WHERE (
                order_date >= DATE '2010-01-01'
                AND order_date < DATE '2010-12-01'
            ) OR (
                order_date >= DATE '2011-01-01'
                AND order_date < DATE '2011-12-01'
            )
            GROUP BY 1, 2
        )

        SELECT
            year,
            customer_status,
            order_count,
            identified_customers,
            ROUND(sales_value, 2) AS product_sales_value,
            ROUND(
                100.0 * sales_value
                / SUM(sales_value) OVER (PARTITION BY year),
                2
            ) AS share_of_all_product_sales_pct
        FROM status_totals
        ORDER BY year, customer_status
    """).fetchdf()

    print("\nCUSTOMER STATUS — JANUARY–NOVEMBER")
    print(summary.to_string(index=False))

    # inspecting customer reactivation span
    sensitivity = connection.execute("""
        WITH thresholds AS (
            SELECT *
            FROM (VALUES (60), (90), (120)) AS t(threshold_days)
        ),

        orders AS (
            SELECT *
            FROM analytics.int_order_customer_status
            WHERE customer_id IS NOT NULL
              AND (
                  (order_date >= DATE '2010-01-01'
                   AND order_date < DATE '2010-12-01')
                  OR
                  (order_date >= DATE '2011-01-01'
                   AND order_date < DATE '2011-12-01')
              )
        )

        SELECT
            EXTRACT(YEAR FROM order_date)::INTEGER AS year,
            threshold_days,
            COUNT(*) FILTER (
                WHERE days_since_previous_order >= threshold_days
            ) AS reactivated_orders,
            ROUND(SUM(
                CASE
                    WHEN days_since_previous_order >= threshold_days
                    THEN product_sales_value
                    ELSE 0
                END
            ), 2) AS reactivated_sales,
            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN days_since_previous_order >= threshold_days
                        THEN product_sales_value
                        ELSE 0
                    END
                ) / SUM(product_sales_value),
                2
            ) AS share_of_identified_sales_pct
        FROM orders
        CROSS JOIN thresholds
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).fetchdf()

    print("\nREACTIVATION THRESHOLD SENSITIVITY")
    print(sensitivity.to_string(index=False))