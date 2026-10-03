WITH expected AS (
    SELECT
        COUNT(*) AS customers,
        SUM(frequency_12m) AS orders,
        SUM(monetary_sales_12m) AS sales
    FROM {{ ref('int_customer_segments') }}
),

actual AS (
    SELECT
        COUNT(*) AS customers,
        SUM(frequency_12m) AS orders,
        SUM(monetary_sales_12m) AS sales
    FROM {{ ref('fct_customer_snapshot') }}
)

SELECT actual.*
FROM actual
CROSS JOIN expected
WHERE actual.customers <> expected.customers
   OR actual.orders IS DISTINCT FROM expected.orders
   OR actual.sales IS DISTINCT FROM expected.sales