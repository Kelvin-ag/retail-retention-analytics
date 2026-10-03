SELECT
    customers.customer_key,
    segments.snapshot_date,
    segments.window_start,
    segments.last_purchase_date,
    segments.recency_days,
    segments.observed_tenure_days,
    segments.frequency_12m,
    segments.monetary_sales_12m,
    segments.high_value_cutoff,
    segments.customer_segment
FROM {{ ref('int_customer_segments') }} AS segments
LEFT JOIN {{ ref('dim_customers') }} AS customers
    ON segments.customer_id = customers.customer_id