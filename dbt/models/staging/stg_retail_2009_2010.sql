SELECT
    CAST("Invoice" AS VARCHAR) AS invoice_id,
    CAST("StockCode" AS VARCHAR) AS stock_code,
    CAST("Description" AS VARCHAR) AS description,
    CAST("Quantity" AS BIGINT) AS quantity,
    CAST("InvoiceDate" AS TIMESTAMP) AS invoice_at,
    CAST("Price" AS DECIMAL(18, 4)) AS unit_price,
    CAST("Customer ID" AS VARCHAR) AS customer_id,
    CAST("Country" AS VARCHAR) AS country
FROM {{ source('retail_raw', 'raw_retail_2009_2010') }}