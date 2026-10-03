SELECT
    invoice_id,
    stock_code,
    description,
    quantity,
    invoice_at,
    unit_price,
    customer_id,
    country,
    'Year 2009-2010' AS source_sheet
FROM {{ ref('stg_retail_2009_2010') }}
WHERE invoice_at < TIMESTAMP '2010-12-01'

UNION ALL

SELECT
    invoice_id,
    stock_code,
    description,
    quantity,
    invoice_at,
    unit_price,
    customer_id,
    country,
    'Year 2010-2011' AS source_sheet
FROM {{ ref('stg_retail_2010_2011') }}