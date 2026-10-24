-- Service is assumed complete at end of day; count operating hours AFTER that day.
WITH last_service AS (
 SELECT asset_id,MAX(day) AS last_service_day FROM work_orders WHERE kind='Preventive' GROUP BY asset_id
), hours AS (
 SELECT a.asset_id,a.service_interval_hours,s.last_service_day,SUM(d.engine_hours) AS observed_hours
 FROM assets a LEFT JOIN last_service s USING(asset_id)
 LEFT JOIN daily_usage d ON d.asset_id=a.asset_id
 AND (s.last_service_day IS NULL OR d.day>s.last_service_day)
 GROUP BY a.asset_id
)
SELECT asset_id,last_service_day,ROUND(COALESCE(observed_hours,0),2) AS hours_since_service_or_start,
 service_interval_hours,
 CASE WHEN last_service_day IS NULL THEN 'History incomplete'
 WHEN COALESCE(observed_hours,0)>=service_interval_hours THEN 'Due'
 WHEN COALESCE(observed_hours,0)>=0.9*service_interval_hours THEN 'Due soon'
 ELSE 'Within interval' END AS service_status
FROM hours ORDER BY asset_id;
