# Row-level security demonstration

Role: UK_Only

- Order lines are restricted to United Kingdom.
- Identified customers are accessible only when all their
  recorded order lines are UK-based.
- The shared unknown customer remains accessible, but its
  non-UK order lines are excluded.
- Customer snapshots include only qualifying identified UK customers.
- Global cohort-retention totals are blocked because they
  cannot be recalculated by country from the existing summary.

Validation: tested locally using Power BI Desktop's View as.
Retention visuals are blank under UK_Only and return after
exiting the role test.

Limitations: UK-specific retention is not implemented.
Power BI Service role assignment has not been tested.
Publish to web requires a separate copy without RLS.