WITH spending_threshold AS (
    SELECT
        QUANTILE_CONT(
            monetary_sales_12m,
            {{ var('high_value_percentile') }}
        ) AS high_value_cutoff
    FROM {{ ref('int_customer_rfm') }}
    WHERE frequency_12m > 0
)

SELECT
    customers.*,
    threshold.high_value_cutoff,
    CASE
        WHEN frequency_12m = 0
            THEN 'Inactive in window'

        WHEN recency_days >= {{ var('at_risk_days') }}
             AND monetary_sales_12m >= threshold.high_value_cutoff
            THEN 'High-value at risk'

        WHEN recency_days >= {{ var('at_risk_days') }}
            THEN 'Other at risk'

        WHEN observed_tenure_days <= {{ var('recent_customer_days') }}
            THEN 'Recently first-observed'

        WHEN frequency_12m >= {{ var('repeat_order_threshold') }}
             AND monetary_sales_12m >= threshold.high_value_cutoff
            THEN 'High-value repeat'

        ELSE 'Other recent purchasers'
    END AS customer_segment
FROM {{ ref('int_customer_rfm') }} AS customers
CROSS JOIN spending_threshold AS threshold 