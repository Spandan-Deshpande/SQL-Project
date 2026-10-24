WITH history AS (
 SELECT order_id, asset_id, fault, day,
 LAG(day) OVER(PARTITION BY asset_id,fault ORDER BY day) AS prior_day
 FROM work_orders WHERE kind='Corrective'
)
SELECT *, CAST(julianday(day)-julianday(prior_day) AS INTEGER) AS days_since_prior
FROM history WHERE julianday(day)-julianday(prior_day) BETWEEN 1 AND 30
ORDER BY asset_id,day;
