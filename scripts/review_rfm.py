from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    population = connection.execute("""
        SELECT
            COUNT(*) AS total_customers,
            COUNT(*) FILTER (
                WHERE frequency_12m = 0
            ) AS no_purchases_in_window,
            COUNT(*) FILTER (
                WHERE frequency_12m > 0
            ) AS purchased_in_window,
            SUM(frequency_12m) AS total_orders_12m,
            ROUND(SUM(monetary_sales_12m), 2) AS total_sales_12m
        FROM analytics.int_customer_rfm
    """).fetchdf()

    print("\nRFM POPULATION")
    print(population.T.to_string(header=False))

    # customer rfm distribution
    distribution = connection.execute("""
        SELECT
            'Recency: all customers (days)' AS metric,
            QUANTILE_CONT(recency_days, 0.25) AS p25,
            MEDIAN(recency_days) AS p50,
            QUANTILE_CONT(recency_days, 0.75) AS p75,
            MAX(recency_days) AS maximum
        FROM analytics.int_customer_rfm

        UNION ALL

        SELECT
            'Frequency: window purchasers (orders)',
            QUANTILE_CONT(frequency_12m, 0.25),
            MEDIAN(frequency_12m),
            QUANTILE_CONT(frequency_12m, 0.75),
            MAX(frequency_12m)
        FROM analytics.int_customer_rfm
        WHERE frequency_12m > 0

        UNION ALL

        SELECT
            'Monetary: window purchasers (GBP)',
            QUANTILE_CONT(monetary_sales_12m, 0.25),
            MEDIAN(monetary_sales_12m),
            QUANTILE_CONT(monetary_sales_12m, 0.75),
            MAX(monetary_sales_12m)
        FROM analytics.int_customer_rfm
        WHERE frequency_12m > 0
    """).fetchdf()

    print("\nRFM DISTRIBUTIONS")
    print(distribution.round(2).to_string(index=False))

    # customer historical spending
    segments = connection.execute("""
        WITH segment_totals AS (
            SELECT
                customer_segment,
                COUNT(*) AS customers,
                SUM(frequency_12m) AS paid_orders_12m,
                SUM(monetary_sales_12m) AS sales_12m,
                MEDIAN(recency_days) AS median_recency_days
            FROM analytics.int_customer_segments
            GROUP BY customer_segment
        )

        SELECT
            customer_segment,
            customers,
            ROUND(
                100.0 * customers / SUM(customers) OVER (),
                2
            ) AS customer_share_pct,
            paid_orders_12m,
            ROUND(sales_12m, 2) AS historical_sales_12m,
            ROUND(
                100.0 * sales_12m
                / NULLIF(SUM(sales_12m) OVER (), 0),
                2
            ) AS sales_share_pct,
            median_recency_days
        FROM segment_totals
        ORDER BY sales_12m DESC
    """).fetchdf()

    print("\nCUSTOMER SEGMENTS — SNAPSHOT 1 DECEMBER 2011")
    print(segments.to_string(index=False))

    # change in spending of high value at risk customers
    risk_sensitivity = connection.execute("""
        WITH thresholds AS (
            SELECT *
            FROM (VALUES (60), (90), (120)) AS t(inactivity_days)
        )

        SELECT
            inactivity_days,
            COUNT(*) AS high_value_at_risk_customers,
            ROUND(SUM(monetary_sales_12m), 2)
                AS historical_sales_12m
        FROM analytics.int_customer_segments
        CROSS JOIN thresholds
        WHERE frequency_12m > 0
          AND monetary_sales_12m >= high_value_cutoff
          AND recency_days >= inactivity_days
        GROUP BY inactivity_days
        ORDER BY inactivity_days
    """).fetchdf()

    print("\nHIGH-VALUE AT-RISK SENSITIVITY")
    print(risk_sensitivity.to_string(index=False))