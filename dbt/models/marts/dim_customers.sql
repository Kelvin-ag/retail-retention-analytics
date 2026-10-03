WITH customer_ids AS (
    SELECT DISTINCT customer_id
    FROM {{ ref('int_retail_eligible') }}
    WHERE customer_id IS NOT NULL
      AND (is_paid_product_sale OR is_product_credit)
)

SELECT
    MD5('customer:' || customers.customer_id) AS customer_key,
    customers.customer_id,
    FALSE AS is_unknown,
    purchases.first_observed_purchase_date,
    purchases.cohort_month
FROM customer_ids AS customers
LEFT JOIN {{ ref('int_customer_first_purchase') }} AS purchases
    ON customers.customer_id = purchases.customer_id

UNION ALL

SELECT
    MD5('customer:unknown') AS customer_key,
    CAST(NULL AS VARCHAR) AS customer_id,
    TRUE AS is_unknown,
    CAST(NULL AS DATE) AS first_observed_purchase_date,
    CAST(NULL AS DATE) AS cohort_month