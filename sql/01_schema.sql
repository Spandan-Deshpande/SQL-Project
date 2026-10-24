PRAGMA foreign_keys = ON;
CREATE TABLE depots (depot_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE assets (
 asset_id INTEGER PRIMARY KEY, depot_id INTEGER NOT NULL REFERENCES depots,
 model TEXT NOT NULL, service_interval_hours INTEGER NOT NULL CHECK(service_interval_hours > 0)
);
-- Raw rows intentionally allow bad values so SQL can audit and reject them.
CREATE TABLE staging_usage (ingest_id INTEGER PRIMARY KEY, asset_id INTEGER, day TEXT, engine_hours REAL);
CREATE VIEW valid_usage AS
SELECT s.* FROM staging_usage s JOIN assets a USING(asset_id)
WHERE day BETWEEN '2026-01-01' AND '2026-06-29'
 AND date(day, '+0 days') = day AND engine_hours BETWEEN 0 AND 12;
CREATE TABLE daily_usage (
 asset_id INTEGER NOT NULL REFERENCES assets, day TEXT NOT NULL,
 engine_hours REAL NOT NULL CHECK(engine_hours BETWEEN 0 AND 12),
 scheduled_hours REAL NOT NULL DEFAULT 12 CHECK(scheduled_hours = 12),
 PRIMARY KEY(asset_id, day)
);
CREATE TABLE work_orders (
 order_id INTEGER PRIMARY KEY, asset_id INTEGER NOT NULL REFERENCES assets,
 day TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('Preventive','Corrective')),
 fault TEXT NOT NULL, downtime_hours REAL NOT NULL CHECK(downtime_hours BETWEEN 0 AND 12),
 labour_paise INTEGER NOT NULL CHECK(labour_paise >= 0),
 UNIQUE(asset_id, day), FOREIGN KEY(asset_id,day) REFERENCES daily_usage(asset_id,day)
);
CREATE TABLE parts (part_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE work_order_parts (
 order_id INTEGER NOT NULL REFERENCES work_orders, part_id INTEGER NOT NULL REFERENCES parts,
 quantity INTEGER NOT NULL CHECK(quantity > 0),
 unit_cost_paise INTEGER NOT NULL CHECK(unit_cost_paise >= 0),
 PRIMARY KEY(order_id,part_id)
);
CREATE INDEX orders_asset_kind_day ON work_orders(asset_id,kind,day);
