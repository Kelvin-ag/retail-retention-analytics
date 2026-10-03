WITH expected AS (
    SELECT
        COUNT(*) AS line_count,
        SUM(net_product_revenue) AS revenue
    FROM {{ ref('int_retail_eligible') }}
    WHERE is_paid_product_sale OR is_product_credit
),

actual AS (
    SELECT
        COUNT(*) AS line_count,
        SUM(net_product_revenue) AS revenue
    FROM {{ ref('fct_order_lines') }}
)

SELECT actual.*
FROM actual
CROSS JOIN expected
WHERE actual.line_count <> expected.line_count
   OR actual.revenue IS DISTINCT FROM expected.revenue