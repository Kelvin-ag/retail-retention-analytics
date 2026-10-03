WITH order_history AS (
    SELECT
        *,
        CASE
            WHEN customer_id IS NOT NULL THEN
                LAG(order_date) OVER (
                    PARTITION BY customer_id
                    ORDER BY order_date, invoice_id
                )
        END AS previous_order_date
    FROM {{ ref('int_retail_orders') }}
),

purchase_gaps AS (
    SELECT
        *,
        DATE_DIFF(
            'day',
            previous_order_date,
            order_date
        ) AS days_since_previous_order
    FROM order_history
)

SELECT
    *,
    CASE
        WHEN customer_id IS NULL THEN 'unidentified'
        WHEN previous_order_date IS NULL THEN 'first_observed'
        WHEN days_since_previous_order >= {{ var('reactivation_days') }} THEN 'reactivated'
        ELSE 'returning'
    END AS customer_status
FROM purchase_gaps