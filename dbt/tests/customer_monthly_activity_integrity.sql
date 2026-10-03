SELECT
    customer_id,
    activity_month
FROM {{ ref('int_customer_monthly_activity') }}
GROUP BY customer_id, activity_month
HAVING COUNT(*) <> 1
    OR COUNT(cohort_month) <> COUNT(*)
    OR MIN(months_since_first_purchase) < 0