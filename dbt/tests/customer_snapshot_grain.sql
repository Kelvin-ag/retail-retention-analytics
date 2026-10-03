SELECT
    customer_key,
    snapshot_date
FROM {{ ref('fct_customer_snapshot') }}
GROUP BY customer_key, snapshot_date
HAVING COUNT(*) > 1