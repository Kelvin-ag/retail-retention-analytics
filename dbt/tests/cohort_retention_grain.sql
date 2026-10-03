SELECT
    cohort_month,
    activity_month
FROM {{ ref('fct_cohort_retention') }}
GROUP BY cohort_month, activity_month
HAVING COUNT(*) > 1