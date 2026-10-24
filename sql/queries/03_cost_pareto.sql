WITH costs AS (
 SELECT fault, SUM(total_paise) AS paise FROM order_costs WHERE kind='Corrective' GROUP BY fault
)
SELECT fault, ROUND(paise/100.0,2) AS cost_inr,
 ROUND(100.0*SUM(paise) OVER(ORDER BY paise DESC, fault ROWS UNBOUNDED PRECEDING)
 /NULLIF(SUM(paise) OVER(),0),2) AS cumulative_cost_pct
FROM costs ORDER BY paise DESC, fault;
