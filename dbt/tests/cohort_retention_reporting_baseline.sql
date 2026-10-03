SELECT COUNT(*) AS actual_rows
FROM {{ ref('fct_cohort_retention') }}
HAVING COUNT(*) <> 300