SELECT
    COUNT(*) FILTER (
        WHERE is_unknown
    ) AS unknown_members,
    COUNT(*) FILTER (
        WHERE customer_id IS NULL
    ) AS null_customer_ids,
    COUNT(*) FILTER (
        WHERE is_unknown AND customer_id IS NULL
    ) AS valid_unknown_members
FROM {{ ref('dim_customers') }}
HAVING unknown_members <> 1
    OR null_customer_ids <> 1
    OR valid_unknown_members <> 1