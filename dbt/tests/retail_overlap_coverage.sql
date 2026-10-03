SELECT *
FROM {{ ref('stg_retail_2009_2010') }}
WHERE invoice_at >= TIMESTAMP '2010-12-01'

EXCEPT ALL

SELECT *
FROM {{ ref('stg_retail_2010_2011') }}