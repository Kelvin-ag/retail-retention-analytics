SELECT
    cohort_month,
    activity_month,
    month_number,
    cohort_size,
    purchasing_customers
FROM {{ ref('int_cohort_retention') }}