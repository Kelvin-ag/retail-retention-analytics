WITH before_segmentation AS (
    SELECT
        COUNT(*) AS customer_count,
        SUM(frequency_12m) AS order_count,
        SUM(monetary_sales_12m) AS sales_value
    FROM {{ ref('int_customer_rfm') }}
),

after_segmentation AS (
    SELECT
        COUNT(*) AS customer_count,
        SUM(frequency_12m) AS order_count,
        SUM(monetary_sales_12m) AS sales_value
    FROM {{ ref('int_customer_segments') }}
)

SELECT after_segmentation.*
FROM before_segmentation
CROSS JOIN after_segmentation
WHERE before_segmentation.customer_count
          <> after_segmentation.customer_count
   OR before_segmentation.order_count
          IS DISTINCT FROM after_segmentation.order_count
   OR before_segmentation.sales_value
          IS DISTINCT FROM after_segmentation.sales_value