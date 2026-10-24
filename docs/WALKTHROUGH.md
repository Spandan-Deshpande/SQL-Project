# Fleet Maintenance Analytics — technical walkthrough

**Maintainer: Spandan Mukesh Deshpande**

## Overview

This project models a small equipment fleet and uses SQL to analyze service costs, availability, repeated faults, and preventive-service thresholds. It has six core relational tables and a staging table. The demonstration contains 36,000 asset-day observations generated deterministically. Eight SQL queries produce CSV reports.

The central correctness issue is table grain: an order may contain several parts. Joining those lines directly to daily usage would multiply usage and labour values. The order_costs view first aggregates parts per order; asset_days then preserves one row per asset/day.

## Trace one record

1. A raw usage observation enters staging_usage with an ingestion sequence.
2. valid_usage rejects unknown assets, invalid dates, and hours outside 0–12.
3. ROW_NUMBER orders valid records by descending ingestion sequence within asset/day.
4. The winning observation enters daily_usage.
5. Work orders reference that asset/day. Parts costs aggregate into order_costs.
6. asset_days joins usage and order totals without changing grain.
7. The monthly query sums the facts before computing ratios.

## Formulas

- Availability = 100 × (scheduled hours − downtime hours) / scheduled hours.
- Utilization = 100 × engine hours / scheduled hours.
- Maintenance cost = labour + sum(quantity × historical unit part price).
- Cost per operating hour = maintenance cost / engine hours.
- Repeat fault = the same asset and fault category observed 1–30 days after its previous corrective order.

Ratios use aggregate numerators and denominators, not averages of per-asset percentages. NULLIF protects against zero denominators.

## Query design

- ROW_NUMBER chooses exactly one valid observation per asset/day.
- LAG finds the previous matching failure, without a self-join.
- DENSE_RANK keeps tied cost positions in each depot's top three ranks.
- A cumulative SUM creates a Pareto report ordered by descending cost, with a stable fault-name tie break.
- ROWS 6 PRECEDING creates a seven-row rolling window. It only equals seven days when dates are dense.
- LEFT JOIN retains days without work orders; COALESCE turns absent cost and downtime into zero.

## Validation

The suite verifies quality accounting, referential integrity, join grain, cost reconciliation, latest-valid-row handling, 30-day repeat boundaries, absent service history, zero-hour denominators, and query execution. The CI report check verifies deterministic output.

## Possible extensions

Store start/end timestamps and merge overlapping downtime intervals before aggregation. Use actual shift calendars. Add incremental loads, meter-reset detection, currency handling, and observed service history. PostgreSQL would support a larger multi-user deployment, but SQLite is sufficient for this demonstration.

## Experimenting with the analysis

The repeat-fault window in `sql/queries/04_repeat_faults.sql` is 30 days. Changing it to 14 days gives a stricter definition of recurrence. Compare the exported rows to see which events disappear.

Service thresholds come from `assets.service_interval_hours`. Different intervals change the service-due report without changing the maintenance history.

After modifying a business rule, rebuild the reports, inspect the affected outputs and run the test suite. Update the committed reports only when the differences match the intended change.
