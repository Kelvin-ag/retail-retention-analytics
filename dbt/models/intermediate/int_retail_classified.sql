WITH normalised AS (
    SELECT
        *,
        UPPER(TRIM(stock_code)) AS stock_code_normalised,
        UPPER(TRIM(invoice_id)) LIKE 'C%' AS is_cancellation,
        quantity * unit_price AS signed_line_value
    FROM {{ ref('int_retail_combined') }}
)

SELECT
    transactions.*,
    CASE
        WHEN rules.stock_code IS NOT NULL
            THEN rules.transaction_category
        WHEN LEFT(transactions.stock_code_normalised, 5) = 'GIFT_'
            THEN 'gift_voucher'
        ELSE 'product_candidate'
    END AS transaction_category
FROM normalised AS transactions
LEFT JOIN {{ ref('stock_code_rules') }} AS rules
    ON transactions.stock_code_normalised = rules.stock_code