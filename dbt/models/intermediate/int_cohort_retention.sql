WITH cohorts AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_size
    FROM {{ ref('int_customer_first_purchase') }}
    WHERE cohort_month < DATE '2011-12-01'
    GROUP BY cohort_month
),

months AS (
    SELECT CAST(month_start AS DATE) AS activity_month
    FROM GENERATE_SERIES(
        DATE '2009-12-01',
        DATE '2011-11-01',
        INTERVAL '1 month'
    ) AS calendar(month_start)
),

active_customers AS (
    SELECT
        cohort_month,
        activity_month,
        COUNT(DISTINCT customer_id) AS purchasing_customers
    FROM {{ ref('int_customer_monthly_activity') }}
    WHERE activity_month < DATE '2011-12-01'
    GROUP BY cohort_month, activity_month
)

SELECT
    cohorts.cohort_month,
    months.activity_month,
    DATE_DIFF(
        'month',
        cohorts.cohort_month,
        months.activity_month
    ) AS month_number,
    cohorts.cohort_size,
    COALESCE(active.purchasing_customers, 0) AS purchasing_customers,
    COALESCE(active.purchasing_customers, 0) * 1.0
        / cohorts.cohort_size AS retention_rate
FROM cohorts
CROSS JOIN months
LEFT JOIN active_customers AS active
    ON cohorts.cohort_month = active.cohort_month
   AND months.activity_month = active.activity_month
WHERE months.activity_month >= cohorts.cohort_month