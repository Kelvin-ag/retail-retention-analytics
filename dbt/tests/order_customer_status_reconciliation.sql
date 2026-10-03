WITH totals AS (
    SELECT
        COUNT(*) AS order_count,
        COUNT(DISTINCT invoice_id) AS distinct_orders,
        SUM(product_sales_value) AS sales_value,
        COUNT(*) FILTER (
            WHERE customer_status = 'first_observed'
        ) AS first_observed_orders
    FROM {{ ref('int_order_customer_status') }}
),

expected AS (
    SELECT
        COUNT(*) AS order_count,
        SUM(product_sales_value) AS sales_value,
        COUNT(DISTINCT customer_id) AS identified_customers
    FROM {{ ref('int_retail_orders') }}
)

SELECT totals.*
FROM totals
CROSS JOIN expected
WHERE totals.order_count <> expected.order_count
   OR totals.distinct_orders <> expected.order_count
   OR totals.sales_value IS DISTINCT FROM expected.sales_value
   OR totals.first_observed_orders <> expected.identified_customers