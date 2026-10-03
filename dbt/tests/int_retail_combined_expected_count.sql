SELECT COUNT(*) AS actual_rows
FROM {{ ref('int_retail_combined') }}
HAVING COUNT(*) <> 1044848