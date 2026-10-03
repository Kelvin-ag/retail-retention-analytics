WITH order_totals AS (
    SELECT
        COUNT(*) AS order_count,
        SUM(product_line_count) AS line_count,
        SUM(product_sales_value) AS sales_value
    FROM {{ ref('int_retail_orders') }}
),

line_totals AS (
    SELECT
        COUNT(DISTINCT invoice_id) AS order_count,
        COUNT(*) AS line_count,
        SUM(signed_line_value) AS sales_value
    FROM {{ ref('int_retail_eligible') }}
    WHERE is_paid_product_sale
)

SELECT
    orders.order_count,
    orders.line_count,
    orders.sales_value
FROM order_totals AS orders
CROSS JOIN line_totals AS lines
WHERE orders.order_count <> lines.order_count
   OR orders.line_count <> lines.line_count
   OR orders.sales_value IS DISTINCT FROM lines.sales_value