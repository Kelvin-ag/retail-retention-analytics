SELECT
    invoice_id,
    MIN(customer_id) AS customer_id,
    MIN(CAST(invoice_at AS DATE)) AS order_date,
    MIN(country) AS country,
    COUNT(*) AS product_line_count,
    SUM(quantity) AS units_purchased,
    SUM(signed_line_value) AS product_sales_value
FROM {{ ref('int_retail_eligible') }}
WHERE is_paid_product_sale
GROUP BY invoice_id