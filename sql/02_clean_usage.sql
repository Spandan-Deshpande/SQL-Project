-- Validate first, then retain the most recently ingested VALID row per asset/day.
INSERT INTO daily_usage(asset_id, day, engine_hours)
SELECT asset_id, day, engine_hours FROM (
 SELECT *, ROW_NUMBER() OVER(PARTITION BY asset_id, day ORDER BY ingest_id DESC) AS rn
 FROM valid_usage
) WHERE rn = 1;
