-- Calendar-dense input is validated by run.py. Early windows contain fewer than 7 days.
WITH daily AS (
 SELECT day,SUM(engine_hours) AS used,SUM(scheduled_hours) AS scheduled FROM asset_days GROUP BY day
)
SELECT day, ROUND(100.0*SUM(used) OVER(ORDER BY day ROWS 6 PRECEDING)
 /NULLIF(SUM(scheduled) OVER(ORDER BY day ROWS 6 PRECEDING),0),2) AS trailing_7_day_utilization_pct
FROM daily ORDER BY day;
