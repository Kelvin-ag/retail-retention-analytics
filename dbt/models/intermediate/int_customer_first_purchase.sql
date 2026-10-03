SELECT
    customer_id,
    MIN(order_date) AS first_observed_purchase_date,
    CAST(
        DATE_TRUNC('month', MIN(order_date)) AS DATE
    ) AS cohort_month
FROM {{ ref('int_retail_orders') }}
WHERE customer_id IS NOT NULL
GROUP BY customer_id