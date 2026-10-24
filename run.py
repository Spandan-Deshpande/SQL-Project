"""Rebuild the demonstration database and export every SQL analysis. Python 3.10+."""
from pathlib import Path
import csv
import random
import sqlite3
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parent

def build():
    rng = random.Random(2026)
    db = sqlite3.connect(':memory:')
    db.executescript((ROOT/'sql/01_schema.sql').read_text())
    db.executemany('INSERT INTO depots VALUES (?,?)',enumerate(['Bengaluru','Pune','Chennai','Hyderabad'],1))
    db.executemany('INSERT INTO assets VALUES (?,?,?,?)',[(i,(i-1)%4+1,'Demo diesel asset',500) for i in range(1,201)])
    db.executemany('INSERT INTO parts VALUES (?,?)',enumerate(['Filter','Seal','Belt','Sensor','Hose'],1))
    raw, orders, order_parts = [], [], []
    faults = ['Cooling','Fuel system','Electrical','Lubrication']
    for day_idx in range(180):
        day = str(date(2026,1,1)+timedelta(days=day_idx))
        for asset in range(1,201):
            downtime = 0
            if rng.random()<0.035:
                order_id = len(orders)+1
                kind = 'Preventive' if rng.random()<0.42 else 'Corrective'
                downtime = round(rng.uniform(0.5,3 if kind=='Preventive' else 8),2)
                orders.append((order_id,asset,day,kind,'Scheduled service' if kind=='Preventive' else rng.choice(faults),downtime,rng.randint(80000,600000)))
                for part in rng.sample(range(1,6),rng.randint(1,3)):
                    order_parts.append((order_id,part,rng.randint(1,3),rng.randint(25000,400000)))
            hours = round(rng.uniform(3,min(11,12-downtime)),2)
            raw.append((len(raw)+1,asset,day,hours))
    # Later valid replacements exercise deduplication without altering operating hours.
    for row in raw[:360]:
        raw.append((len(raw)+1,*row[1:]))
    # Invalid later records must never supersede valid observations.
    for row in raw[:120]:
        raw.append((len(raw)+1,row[1],row[2],-1))
    db.executemany('INSERT INTO staging_usage VALUES (?,?,?,?)',raw)
    db.executescript((ROOT/'sql/02_clean_usage.sql').read_text())
    db.executemany('INSERT INTO work_orders VALUES (?,?,?,?,?,?,?)',orders)
    db.executemany('INSERT INTO work_order_parts VALUES (?,?,?,?)',order_parts)
    db.executescript((ROOT/'sql/03_views.sql').read_text())
    validate(db)
    db.commit()
    return db

def validate(db):
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    assert db.execute('SELECT COUNT(*) FROM daily_usage').fetchone()[0] == 36000
    assert not db.execute('SELECT asset_id FROM daily_usage GROUP BY asset_id HAVING COUNT(*)<>180').fetchall()
    assert db.execute('SELECT COUNT(DISTINCT day) FROM daily_usage').fetchone()[0] == 180
    assert db.execute('SELECT COUNT(*) FROM asset_days WHERE engine_hours+downtime_hours>scheduled_hours+0.00001').fetchone()[0] == 0
    assert db.execute('SELECT COUNT(*) FROM asset_days').fetchone()[0] == 36000

def export(db):
    reports = ROOT/'reports'
    reports.mkdir(exist_ok=True)
    for query in sorted((ROOT/'sql/queries').glob('*.sql')):
        cursor = db.execute(query.read_text())
        with (reports/(query.stem+'.csv')).open('w',newline='',encoding='utf-8') as f:
            writer=csv.writer(f); writer.writerow([x[0] for x in cursor.description]); writer.writerows(cursor)
    orders = db.execute('SELECT COUNT(*) FROM work_orders').fetchone()[0]
    cost = db.execute('SELECT SUM(total_paise)/100.0 FROM order_costs').fetchone()[0]
    audit = db.execute('SELECT * FROM quality_audit').fetchone()
    summary = f'''# Reproduced results

All figures below describe a deterministic **synthetic** dataset, not Cummins operations.

- 200 assets across 4 depots, 180 days (January 1–June 29, 2026).
- {audit[0]:,} raw usage records; {audit[1]:,} rejected invalid rows; {audit[2]:,} superseded duplicate rows.
- {audit[3]:,} clean asset-day observations and {orders:,} work orders.
- INR {cost:,.2f} simulated maintenance expenditure; this is cost, not savings.
- Eight SQL analysis exports accompany this report.

Reproduce with `python run.py`, then `python -m unittest discover -s tests -v`.
'''
    (reports/'summary.md').write_text(summary,encoding='utf-8',newline='\n')
    build_dir=ROOT/'build'; build_dir.mkdir(exist_ok=True)
    with sqlite3.connect(build_dir/'fleet.db') as target:
        db.backup(target)
    print(summary)

if __name__=='__main__':
    with build() as connection:
        export(connection)
