SELECT
    lines.invoice_id,
    CAST(lines.invoice_at AS DATE) AS date_key,
    customers.customer_key,
    products.product_key,
    lines.country,
    lines.quantity,
    lines.unit_price,
    lines.is_paid_product_sale,
    lines.is_product_credit,
    lines.net_product_revenue,
    lines.source_sheet,
    CASE
        WHEN lines.is_paid_product_sale
            THEN order_status.customer_status
        ELSE 'not_applicable'
    END AS order_customer_status

FROM {{ ref('int_retail_eligible') }} AS lines

LEFT JOIN {{ ref('dim_customers') }} AS customers
    ON lines.customer_id IS NOT DISTINCT FROM customers.customer_id

LEFT JOIN {{ ref('dim_products') }} AS products
    ON lines.stock_code = products.stock_code

LEFT JOIN {{ ref('int_order_customer_status') }} AS order_status
    ON lines.invoice_id = order_status.invoice_id
    AND lines.is_paid_product_sale

WHERE lines.is_paid_product_sale OR lines.is_product_credit