SELECT
    (SELECT COUNT(*)
     FROM {{ ref('int_retail_combined') }}) AS combined_rows,

    (SELECT COUNT(*)
     FROM {{ ref('int_retail_classified') }}) AS classified_rows

WHERE combined_rows <> classified_rows