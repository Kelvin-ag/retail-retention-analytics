SELECT *
FROM {{ ref('int_cohort_retention') }}
WHERE cohort_size <= 0
   OR purchasing_customers < 0
   OR purchasing_customers > cohort_size
   OR retention_rate IS NULL
   OR retention_rate < 0
   OR retention_rate > 1
   OR month_number < 0
   OR (
       month_number = 0
       AND purchasing_customers <> cohort_size
   )