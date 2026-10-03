WITH eligibility AS (
    SELECT
        *,
        (
            transaction_category = 'product_candidate'
            AND unit_price > 0
            AND quantity > 0
            AND NOT is_cancellation
        ) AS is_paid_product_sale,

        (
            transaction_category = 'product_candidate'
            AND unit_price > 0
            AND quantity < 0
            AND is_cancellation
        ) AS is_product_credit
    FROM {{ ref('int_retail_classified') }}
)

SELECT
    *,
    CASE
        WHEN is_paid_product_sale OR is_product_credit
            THEN signed_line_value
        ELSE 0
    END AS net_product_revenue
FROM eligibility