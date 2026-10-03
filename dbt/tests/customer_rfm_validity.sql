SELECT *
FROM {{ ref('int_customer_rfm') }}
WHERE window_start >= snapshot_date
   OR last_purchase_date >= snapshot_date
   OR first_observed_purchase_date > last_purchase_date
   OR recency_days < 1
   OR observed_tenure_days < recency_days
   OR frequency_12m < 0
   OR monetary_sales_12m < 0
   OR (frequency_12m = 0 AND monetary_sales_12m <> 0)
   OR (frequency_12m > 0 AND monetary_sales_12m <= 0)