WITH costs AS (
 SELECT depot_id,asset_id,SUM(total_paise) AS paise FROM asset_days GROUP BY depot_id,asset_id
), ranked AS (
 SELECT *,DENSE_RANK() OVER(PARTITION BY depot_id ORDER BY paise DESC) AS cost_rank FROM costs
)
SELECT p.name AS depot,asset_id,ROUND(paise/100.0,2) AS maintenance_inr,cost_rank
FROM ranked JOIN depots p USING(depot_id) WHERE cost_rank<=3 ORDER BY depot_id,cost_rank,asset_id;
