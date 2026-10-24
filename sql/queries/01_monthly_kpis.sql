SELECT substr(day,1,7) AS month, COUNT(*) AS asset_days,
 ROUND(100.0*(SUM(scheduled_hours)-SUM(downtime_hours))/NULLIF(SUM(scheduled_hours),0),2) AS availability_pct,
 ROUND(100.0*SUM(engine_hours)/NULLIF(SUM(scheduled_hours),0),2) AS utilization_pct,
 ROUND(SUM(total_paise)/100.0,2) AS maintenance_inr,
 ROUND(SUM(total_paise)/100.0/NULLIF(SUM(engine_hours),0),2) AS inr_per_engine_hour
FROM asset_days GROUP BY month ORDER BY month;
