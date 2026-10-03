| Metric | Working definition |
| :--- | :--- |
| **Net product revenue** | Signed value of qualifying product sales and product credits, recognised on their recorded dates. Excludes delivery, standalone discount entries and other non-product categories. Report standalone discounts separately. This measure is net of product credits, but before standalone discounts. |
| **Orders** | Count distinct non-cancellation invoices containing at least one eligible product line with Quantity > 0 and Price > 0. Exclude non-product codes according to our documented classification rules. Credit notes do not count as new orders. |
| **Active customers** | Distinct identified customers with at least one valid purchase in the selected period. |
| **Orders per customer** | Purchase orders from identified customers ÷ active customers. |
| **Average order value** | Net product revenue ÷ purchase orders within the selected period. Returns are recognised on their recorded date. |
| **Repeat purchase rate** | Identified customers with at least two purchase orders in the selected period ÷ active customers in that period. |
| **Acquisition cohort** | Month of a customer’s first observed valid purchase in the dataset; not necessarily their first-ever purchase. |
| **Monthly cohort retention** | Customers from a cohort purchasing in a given subsequent month ÷ original cohort size. Only show months we can fully observe. |

## Scope Rules

- Compare January – November 2011 against January – November 2010, subject to checking coverage.
- Keep valid sales without customer IDs in total revenue, but exclude them from customer counts, cohorts and repeat-purchase measures.
- Use identified-customer revenue and orders consistently when breaking revenue into customers × orders per customer × average order value.
- Define “at risk” after examining purchase intervals; any threshold will be an explicit assumption.

## Customer Purchase Status
| Status | Definition |
| :--- | :--- |
| First observed | The customer’s earliest qualifying paid order in the available data. |
| Returning | A later qualifying paid order occurring fewer than 90 days after the previous qualifying paid order. |
| Reactivated | A later qualifying paid order occurring 90 or more days after the previous qualifying paid order. |
| Unidentified | A qualifying paid order without a customer ID; status cannot be determined. |

## Implementation Notes
- Calculate history across the full dataset before filtering reporting dates.
- Use calendar-day gaps. For multiple orders on the same date, use invoice ID as a deterministic tie-breaker; this does not establish their actual time order.
- Classify each order separately. A customer can contribute revenue to more than one status during a quarter.
- This breakdown initially uses paid product sales before credits. Keep credits separate because we haven’t linked them to original purchase orders; sales plus signed credits reconcile to net product revenue.
- Reactivation uses a provisional 90-day purchase gap. Tested alternatives of 60 and 120 days materially change the classified sales share.

## Customer Segmentation

- Snapshot: start of 1 December 2011; include purchases through
  30 November 2011 only.
- Population: identified customers with at least one qualifying
  paid purchase before the snapshot.
- Recency: calendar days between the latest qualifying purchase
  date and 1 December 2011, using all available prior history.
- Frequency: qualifying paid orders from 1 December 2010
  up to, but excluding, 1 December 2011.
- Monetary value: product sales value from those same orders,
  before credits. This is not net revenue or profit.
- Customers with earlier purchases but none in that 12-month
  window remain included with frequency and monetary value of zero.
- No transactions on or after the snapshot date are used.
- Segments describe this snapshot only; they must not be treated
  as the customer's historical status on every transaction.
- ONS 21st August 2026 release and series code J596

| Segment | Rules |
| :--- | :--- |
| Inactive in window | No paid orders in the 12-month window |
| High-value at risk | Recency ≥ 90 days and spending ≥ the window purchasers’ 75th percentile |
| Other at risk | Recency ≥ 90 days |
| Recently first-observed | Observed tenure ≤ 30 days |
| High-value repeat | At least 4 orders and spending ≥ the 75th percentile |
| Other recent purchasers | All remaining customers |