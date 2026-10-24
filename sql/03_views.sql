-- Aggregate the one-to-many parts table before joining to work orders.
CREATE VIEW order_costs AS
SELECT w.*, w.labour_paise + COALESCE(p.parts_paise,0) AS total_paise
FROM work_orders w LEFT JOIN (
 SELECT order_id, SUM(quantity*unit_cost_paise) AS parts_paise
 FROM work_order_parts GROUP BY order_id
) p USING(order_id);
-- One row per asset/day: prevents parts rows from multiplying hours or labour.
CREATE VIEW asset_days AS
SELECT d.*, a.depot_id, COALESCE(w.downtime_hours,0) AS downtime_hours,
 COALESCE(w.total_paise,0) AS total_paise
FROM daily_usage d JOIN assets a USING(asset_id)
LEFT JOIN order_costs w ON w.asset_id=d.asset_id AND w.day=d.day;
CREATE VIEW quality_audit AS
SELECT (SELECT COUNT(*) FROM staging_usage) AS raw_rows,
 (SELECT COUNT(*) FROM staging_usage)-(SELECT COUNT(*) FROM valid_usage) AS rejected_rows,
 (SELECT COUNT(*) FROM valid_usage)-(SELECT COUNT(*) FROM daily_usage) AS superseded_rows,
 (SELECT COUNT(*) FROM daily_usage) AS accepted_rows;
