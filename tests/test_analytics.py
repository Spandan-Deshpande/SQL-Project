import sqlite3
import unittest
from run import build, ROOT

class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = build()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_quality_accounting(self):
        self.assertEqual(self.db.execute("SELECT * FROM quality_audit").fetchone(),
                         (36480,120,360,36000))

    def test_foreign_keys(self):
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_no_join_fanout(self):
        expected = self.db.execute("SELECT SUM(engine_hours) FROM daily_usage").fetchone()[0]
        actual = self.db.execute("SELECT SUM(engine_hours) FROM asset_days").fetchone()[0]
        self.assertAlmostEqual(expected,actual)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM asset_days").fetchone()[0],36000)

    def test_cost_reconciliation(self):
        labour = self.db.execute("SELECT SUM(labour_paise) FROM work_orders").fetchone()[0]
        parts = self.db.execute("SELECT SUM(quantity*unit_cost_paise) FROM work_order_parts").fetchone()[0]
        actual = self.db.execute("SELECT SUM(total_paise) FROM asset_days").fetchone()[0]
        self.assertEqual(labour+parts,actual)

    def test_latest_valid_record_wins(self):
        db = sqlite3.connect(":memory:")
        db.executescript((ROOT/"sql/01_schema.sql").read_text())
        db.execute("INSERT INTO depots VALUES(1,'Test')")
        db.execute("INSERT INTO assets VALUES(1,1,'Test',500)")
        db.executemany("INSERT INTO staging_usage VALUES(?,?,?,?)",[
            (1,1,'2026-01-01',3),(2,1,'2026-01-01',7),
            (3,1,'2026-01-01',-1),(4,999,'2026-01-01',4),
            (5,1,'2026-02-30',5)])
        db.executescript((ROOT/"sql/02_clean_usage.sql").read_text())
        self.assertEqual(db.execute("SELECT engine_hours FROM daily_usage").fetchall(),[(7.0,)])
        db.close()

    def test_repeat_fault_boundary(self):
        db=sqlite3.connect(":memory:")
        db.execute("CREATE TABLE work_orders(order_id,asset_id,fault,day,kind)")
        db.executemany("INSERT INTO work_orders VALUES(?,?,?,?,?)",[
            (1,1,'Cooling','2026-01-01','Corrective'),
            (2,1,'Cooling','2026-01-31','Corrective'),
            (3,1,'Cooling','2026-03-03','Corrective')])
        rows=db.execute((ROOT/"sql/queries/04_repeat_faults.sql").read_text()).fetchall()
        self.assertEqual([r[0] for r in rows],[2])
        self.assertEqual(rows[0][-1],30)
        db.close()

    def test_missing_service_history_is_not_assumed_current(self):
        db=sqlite3.connect(":memory:")
        db.executescript((ROOT/"sql/01_schema.sql").read_text())
        db.execute("INSERT INTO depots VALUES(1,'Test')")
        db.execute("INSERT INTO assets VALUES(1,1,'Test',500)")
        db.execute("INSERT INTO daily_usage VALUES(1,'2026-01-01',0,12)")
        row=db.execute((ROOT/"sql/queries/06_service_due.sql").read_text()).fetchone()
        self.assertEqual(row[-1],"History incomplete")
        db.close()

    def test_zero_engine_hours_produce_null_cost_rate(self):
        db=sqlite3.connect(":memory:")
        db.execute("CREATE TABLE asset_days(day,scheduled_hours,downtime_hours,engine_hours,total_paise)")
        db.execute("INSERT INTO asset_days VALUES('2026-01-01',12,0,0,500)")
        row=db.execute((ROOT/"sql/queries/01_monthly_kpis.sql").read_text()).fetchone()
        self.assertIsNone(row[-1])
        db.close()

    def test_all_queries_execute(self):
        for path in (ROOT/"sql/queries").glob("*.sql"):
            with self.subTest(query=path.name):
                self.assertTrue(self.db.execute(path.read_text()).description)

if __name__=="__main__":
    unittest.main()
