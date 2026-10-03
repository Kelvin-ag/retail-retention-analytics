from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_ROOT / "data" / "retail.duckdb"

with duckdb.connect(str(DATABASE), read_only=True) as connection:
    # understanding total revenue growth
    growth = connection.execute("""
        SELECT
            EXTRACT(YEAR FROM invoice_at)::INTEGER AS year,
            ROUND(SUM(net_product_revenue), 2)
                AS net_product_revenue,
            ROUND(SUM(
                CASE WHEN customer_id IS NOT NULL
                     THEN net_product_revenue ELSE 0 END
            ), 2) AS identified_revenue,
            ROUND(SUM(
                CASE WHEN customer_id IS NULL
                     THEN net_product_revenue ELSE 0 END
            ), 2) AS unidentified_revenue,
            COUNT(DISTINCT CASE
                WHEN is_paid_product_sale THEN invoice_id
            END) AS paid_orders,
            COUNT(DISTINCT CASE
                WHEN is_paid_product_sale
                 AND customer_id IS NOT NULL
                THEN invoice_id
            END) AS identified_orders,
            COUNT(DISTINCT CASE
                WHEN is_paid_product_sale THEN customer_id
            END) AS active_customers
        FROM analytics.int_retail_eligible
        WHERE (
            invoice_at >= TIMESTAMP '2010-01-01'
            AND invoice_at < TIMESTAMP '2010-12-01'
        ) OR (
            invoice_at >= TIMESTAMP '2011-01-01'
            AND invoice_at < TIMESTAMP '2011-12-01'
        )
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    print("\nJANUARY–NOVEMBER COMPARISON")
    print(growth.to_string(index=False))

    # understanding unidentified revenue increase
    monthly = connection.execute("""
        SELECT
            CAST(DATE_TRUNC('month', invoice_at) AS DATE)
                AS revenue_month,
            ROUND(SUM(net_product_revenue), 2) AS revenue,
            ROUND(SUM(
                CASE WHEN customer_id IS NULL
                     THEN net_product_revenue ELSE 0 END
            ), 2) AS unidentified_revenue,
            ROUND(
                100.0 * SUM(
                    CASE WHEN customer_id IS NULL
                         THEN net_product_revenue ELSE 0 END
                ) / NULLIF(SUM(net_product_revenue), 0),
                2
            ) AS unidentified_revenue_pct
        FROM analytics.int_retail_eligible
        WHERE invoice_at >= TIMESTAMP '2010-01-01'
          AND invoice_at < TIMESTAMP '2011-12-01'
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    print("\nMONTHLY CUSTOMER-ID COVERAGE")
    print(monthly.to_string(index=False))

    # splitting unidentified revenue
    unidentified_check = connection.execute("""
        SELECT
            EXTRACT(YEAR FROM invoice_at)::INTEGER AS year,
            COUNT(DISTINCT CASE
                WHEN is_paid_product_sale THEN invoice_id
            END) AS unidentified_orders,
            ROUND(SUM(
                CASE WHEN is_paid_product_sale
                     THEN signed_line_value ELSE 0 END
            ), 2) AS product_sales_value,
            ROUND(SUM(
                CASE WHEN is_product_credit
                     THEN signed_line_value ELSE 0 END
            ), 2) AS product_credit_value,
            ROUND(SUM(net_product_revenue), 2) AS net_revenue
        FROM analytics.int_retail_eligible
        WHERE customer_id IS NULL
          AND (
              (invoice_at >= TIMESTAMP '2010-01-01'
               AND invoice_at < TIMESTAMP '2010-12-01')
              OR
              (invoice_at >= TIMESTAMP '2011-01-01'
               AND invoice_at < TIMESTAMP '2011-12-01')
          )
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()

    print("\nUNIDENTIFIED SALES AND CREDITS — JANUARY–NOVEMBER")
    print(unidentified_check.to_string(index=False))

    # checking revenue spread
    order_distribution = connection.execute("""
        WITH ranked_orders AS (
            SELECT
                EXTRACT(YEAR FROM order_date)::INTEGER AS year,
                product_sales_value,
                ROW_NUMBER() OVER (
                    PARTITION BY EXTRACT(YEAR FROM order_date)
                    ORDER BY product_sales_value DESC, invoice_id
                ) AS value_rank
            FROM analytics.int_retail_orders
            WHERE customer_id IS NULL
              AND (
                  (order_date >= DATE '2010-01-01'
                   AND order_date < DATE '2010-12-01')
                  OR
                  (order_date >= DATE '2011-01-01'
                   AND order_date < DATE '2011-12-01')
              )
        )
        SELECT
            year,
            ROUND(MEDIAN(product_sales_value), 2)
                AS median_order_value,
            ROUND(MAX(product_sales_value), 2)
                AS largest_order_value,
            ROUND(
                100.0 * SUM(
                    CASE WHEN value_rank <= 10
                         THEN product_sales_value ELSE 0 END
                ) / SUM(product_sales_value),
                2
            ) AS top_10_sales_pct
        FROM ranked_orders
        GROUP BY year
        ORDER BY year
    """).fetchdf()

    print("\nUNIDENTIFIED ORDER DISTRIBUTION")
    print(order_distribution.to_string(index=False))