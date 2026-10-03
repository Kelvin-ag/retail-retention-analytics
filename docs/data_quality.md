# Data Quality Decisions

| Issue | Rows affected | Decision | Justification |
| :--- | :---: | :--- | :--- |
| Overlapping source sheets | 22,523 | Use the first sheet before December 2010 and the second sheet from December 2010 onward. | All first-sheet records in the overlapping period have exact matching occurrences in the second sheet. |
| Missing customer IDs | 235,287 (22.52%) | Retain otherwise valid transactions in revenue; exclude from customer-level metrics. Financial impact under investigation. | Purchases contribute revenue even when the customer cannot be identified. |
| Negative-price bad-debt adjustments | 5; total -£158,676.14 | Exclude from product revenue and purchase metrics; retain for reconciliation. | Descriptions identify financial adjustments rather than product transactoins.
| Bad-debt adjustments (StockCode = B) | 6; net -£147,614.08 | Exclude all code B records from product revenue and purchase metrics; retain for reconciliation. | All six are labelled “Adjust bad debt”, including one positive adjustment.
| Manual entries (M/m) | 1,403; net -£82,935.57 | Separate from product revenue and purchase metrics; retain for reconciliation.<br> **Note** - Includes invoice 'C496350' a positive £373.57 entry on a cancellation invoice. Its purpose is unverified; handled under the existing manual-adjustment exclusion. | No identifiable product; sample includes apparent offsetting entries with inconsistent customer attribution. Business purpose cannot be verified.
| Zero-price records | 6,024; 70 with customer IDs | Retain for audit; exclude from paid-purchase activity and units sold. | Many descriptions suggest stock adjustments. Free items cannot reliably be distinguished from pricing errors. Revenue contribution is £0.
| Identical rows within combined data | 11,001 groups; 11,812 extra copies | Retain; assess the effect of removing extra copies on final product revenue. | No invoice-line identifier to distinguish legitimate repetitions from errors. Removing copies reduces raw signed value by £54,228.42.

# Validation Checks

| Check | Result | Action |
| :--- | :--- | :--- |
| Essential fields: invoice, stock code, date, quantity, price and country | No missing values across 1,044,848 combined rows | Add automated completeness tests in the transformation layer. |

**Working assumption:** Stock codes not classified as non-product or unresolved are treated as merchandise candidates. Eligibility rules determine whether their transactions contribute to product revenue and purchase activity. This classification has not been verified against an independent product catalogue.

> One row per product code, even when descriptions differ. It selects a reporting label; it does not establish an authoritative product name.