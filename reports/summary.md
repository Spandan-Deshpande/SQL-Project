# Reproduced results

All figures below describe a deterministic **synthetic** dataset, not Cummins operations.

- 200 assets across 4 depots, 180 days (January 1–June 29, 2026).
- 36,480 raw usage records; 120 rejected invalid rows; 360 superseded duplicate rows.
- 36,000 clean asset-day observations and 1,219 work orders.
- INR 14,406,841.44 simulated maintenance expenditure; this is cost, not savings.
- Eight SQL analysis exports accompany this report.

Reproduce with `python run.py`, then `python -m unittest discover -s tests -v`.
