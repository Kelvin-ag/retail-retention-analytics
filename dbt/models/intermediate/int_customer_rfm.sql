WITH settings AS (
    SELECT
        CAST('{{ var("customer_snapshot_date") }}' AS DATE)
            AS snapshot_date,
        CAST('{{ var("customer_window_start") }}' AS DATE)
            AS window_start
),

customer_metrics AS (
    SELECT
        orders.customer_id,
        settings.snapshot_date,
        settings.window_start,
        MIN(orders.order_date) AS first_observed_purchase_date,
        MAX(orders.order_date) AS last_purchase_date,

        COUNT(*) FILTER (
            WHERE orders.order_date >= settings.window_start
        ) AS frequency_12m,

        SUM(
            CASE
                WHEN orders.order_date >= settings.window_start
                    THEN orders.product_sales_value
                ELSE 0
            END
        ) AS monetary_sales_12m

    FROM {{ ref('int_retail_orders') }} AS orders
    CROSS JOIN settings
    WHERE orders.customer_id IS NOT NULL
      AND orders.order_date < settings.snapshot_date
    GROUP BY
        orders.customer_id,
        settings.snapshot_date,
        settings.window_start
)

SELECT
    *,
    DATE_DIFF(
        'day', last_purchase_date, snapshot_date
    ) AS recency_days,
    DATE_DIFF(
        'day', first_observed_purchase_date, snapshot_date
    ) AS observed_tenure_days
FROM customer_metrics