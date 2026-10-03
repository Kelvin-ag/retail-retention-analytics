WITH counts AS (
    SELECT
        (
            SELECT COUNT(*)
            FROM {{ source('retail_raw', 'raw_retail_2009_2010') }}
        ) AS source_rows,
        (
            SELECT COUNT(*)
            FROM {{ ref('stg_retail_2009_2010') }}
        ) AS staging_rows
)

SELECT *
FROM counts
WHERE source_rows <> staging_rows