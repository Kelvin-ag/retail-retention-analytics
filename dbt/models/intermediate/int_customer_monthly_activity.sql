WITH monthly_orders AS (
    SELECT
        customer_id,
        CAST(DATE_TRUNC('month', order_date) AS DATE)
            AS activity_month,
        COUNT(*) AS order_count,
        SUM(product_sales_value) AS product_sales_value
    FROM {{ ref('int_retail_orders') }}
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id, activity_month
)

SELECT
    activity.customer_id,
    activity.activity_month,
    cohort.cohort_month,
    DATE_DIFF(
        'month',
        cohort.cohort_month,
        activity.activity_month
    ) AS months_since_first_purchase,
    activity.order_count,
    activity.product_sales_value
FROM monthly_orders AS activity
LEFT JOIN {{ ref('int_customer_first_purchase') }} AS cohort
    ON activity.customer_id = cohort.customer_id