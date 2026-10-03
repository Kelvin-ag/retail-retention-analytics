# Performance checks

Tested locally in Power BI Desktop.

- Revenue Overview: slowest observed visual was a card at 446 ms.
  - DAX query: 10 ms
  - Visual display: 83 ms
  - Other: 353 ms
- Other report pages: observed visual durations below 247 ms.
- No optimisation was required based on these observations.

These are local visual timings, not total page-load times or
Power BI Service performance guarantees.