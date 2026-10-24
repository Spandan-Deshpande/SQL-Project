SELECT p.name AS depot, COUNT(DISTINCT d.asset_id) AS assets,
 ROUND(100.0*(SUM(scheduled_hours)-SUM(downtime_hours))/NULLIF(SUM(scheduled_hours),0),2) AS availability_pct,
 ROUND(SUM(total_paise)/100.0,2) AS maintenance_inr,
 ROUND(SUM(total_paise)/100.0/NULLIF(SUM(engine_hours),0),2) AS inr_per_engine_hour
FROM asset_days d JOIN depots p USING(depot_id) GROUP BY p.depot_id ORDER BY maintenance_inr DESC;
