WITH expected AS (
    SELECT
        COUNT(*) AS row_count,
        SUM(net_product_revenue) AS revenue
    FROM {{ ref('int_retail_eligible') }}
    WHERE is_paid_product_sale OR is_product_credit
),

actual AS (
    SELECT
        COUNT(*) AS row_count,
        SUM(net_product_revenue) AS revenue
    FROM {{ ref('fct_order_lines') }}
)

SELECT 'row_count_changed' AS issue
FROM expected
CROSS JOIN actual
WHERE expected.row_count <> actual.row_count

UNION ALL

SELECT 'revenue_changed' AS issue
FROM expected
CROSS JOIN actual
WHERE expected.revenue IS DISTINCT FROM actual.revenue

UNION ALL

SELECT 'invalid_order_status' AS issue
WHERE EXISTS (
    SELECT 1
    FROM {{ ref('fct_order_lines') }}
    WHERE (
        is_paid_product_sale
        AND (
            order_customer_status IS NULL
            OR order_customer_status NOT IN (
                'first_observed',
                'returning',
                'reactivated',
                'unidentified'
            )
        )
    )
    OR (
        is_product_credit
        AND order_customer_status IS DISTINCT FROM 'not_applicable'
    )
)