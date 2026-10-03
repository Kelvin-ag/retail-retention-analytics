WITH eligible_lines AS (
    SELECT
        stock_code,
        NULLIF(TRIM(description), '') AS product_description
    FROM {{ ref('int_retail_eligible') }}
    WHERE is_paid_product_sale OR is_product_credit
),

product_codes AS (
    SELECT DISTINCT stock_code
    FROM eligible_lines
),

description_counts AS (
    SELECT
        stock_code,
        product_description,
        COUNT(*) AS occurrences
    FROM eligible_lines
    WHERE product_description IS NOT NULL
    GROUP BY stock_code, product_description
),

ranked_descriptions AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY stock_code
            ORDER BY occurrences DESC, product_description ASC
        ) AS description_rank
    FROM description_counts
)

SELECT
    MD5('product:' || products.stock_code) AS product_key,
    products.stock_code,
    COALESCE(
        descriptions.product_description,
        'Description unavailable'
    ) AS product_description
FROM product_codes AS products
LEFT JOIN ranked_descriptions AS descriptions
    ON products.stock_code = descriptions.stock_code
   AND descriptions.description_rank = 1