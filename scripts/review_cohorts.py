from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    customer_check = connection.execute("""
        SELECT
            (SELECT COUNT(*)
             FROM analytics.int_customer_first_purchase)
                AS cohort_customers,

            (SELECT COUNT(DISTINCT customer_id)
             FROM analytics.int_retail_orders
             WHERE customer_id IS NOT NULL)
                AS identified_purchasing_customers
    """).fetchdf()

    print("\nCUSTOMER COUNT CHECK")
    print(customer_check.to_string(index=False))

    cohorts = connection.execute("""
        SELECT
            cohort_month,
            COUNT(*) AS cohort_size
        FROM analytics.int_customer_first_purchase
        GROUP BY cohort_month
        ORDER BY cohort_month
    """).fetchdf()

    print("\nCOHORT DISTRIBUTION")
    print(cohorts.to_string(index=False))

    # inspect retention at months 0, 1, 3 and 6
    retention = connection.execute("""
        SELECT
            cohort_month,
            MAX(cohort_size) AS cohort_size,
            ROUND(100 * MAX(
                CASE WHEN month_number = 0 THEN retention_rate END
            ), 2) AS month_0_pct,
            ROUND(100 * MAX(
                CASE WHEN month_number = 1 THEN retention_rate END
            ), 2) AS month_1_pct,
            ROUND(100 * MAX(
                CASE WHEN month_number = 3 THEN retention_rate END
            ), 2) AS month_3_pct,
            ROUND(100 * MAX(
                CASE WHEN month_number = 6 THEN retention_rate END
            ), 2) AS month_6_pct
        FROM analytics.int_cohort_retention
        GROUP BY cohort_month
        ORDER BY cohort_month
    """).fetchdf()

    print("\nCOHORT RETENTION (%)")
    print(retention.to_string(index=False))

    # retention calculation using orders
    independent_check = connection.execute("""
        WITH first_purchase AS (
            SELECT
                customer_id,
                MIN(order_date) AS first_date
            FROM analytics.int_retail_orders
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        ),

        october_cohort AS (
            SELECT customer_id
            FROM first_purchase
            WHERE first_date >= DATE '2011-10-01'
              AND first_date < DATE '2011-11-01'
        ),

        november_buyers AS (
            SELECT DISTINCT customer_id
            FROM analytics.int_retail_orders
            WHERE order_date >= DATE '2011-11-01'
              AND order_date < DATE '2011-12-01'
              AND customer_id IS NOT NULL
        )

        SELECT
            COUNT(*) AS cohort_size,
            COUNT(buyers.customer_id) AS returning_customers,
            ROUND(
                100.0 * COUNT(buyers.customer_id) / COUNT(*),
                2
            ) AS month_1_pct
        FROM october_cohort AS cohort
        LEFT JOIN november_buyers AS buyers
            ON cohort.customer_id = buyers.customer_id
    """).fetchdf()

    print("\nOCTOBER 2011 — DIRECT ORDER CHECK")
    print(independent_check.to_string(index=False))