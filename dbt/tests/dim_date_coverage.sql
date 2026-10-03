SELECT
    MIN(date_key) AS first_date,
    MAX(date_key) AS last_date,
    COUNT(DISTINCT date_key) AS distinct_dates
FROM {{ ref('dim_date') }}
HAVING MIN(date_key) IS DISTINCT FROM DATE '2009-01-01'
    OR MAX(date_key) IS DISTINCT FROM DATE '2011-12-31'
    OR COUNT(DISTINCT date_key) <> 1095