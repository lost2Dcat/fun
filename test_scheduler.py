import tempfile
import unittest
from pathlib import Path

from scheduler import ScheduleManager


class ScheduleManagerTest(unittest.TestCase):
    def test_add_update_remove_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.json"
            m = ScheduleManager(db)
            task = m.add_task(
                title="任务A",
                owner="运营",
                channel="社群",
                start_at="2026-01-01 10:00",
                end_at="2026-01-01 12:00",
                priority="高",
                status="待开始",
                goal="目标",
                notes="备注",
            )
            self.assertEqual(task.id, 1)
            self.assertEqual(len(m.list_tasks()), 1)

            m.update_status(1, "进行中")
            self.assertEqual(m.list_tasks()[0].status, "进行中")

            m.remove_task(1)
            self.assertEqual(len(m.list_tasks()), 0)

    def test_seed_only_when_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.json"
            m = ScheduleManager(db)
            m.seed_template()
            self.assertEqual(len(m.list_tasks()), 2)
            m.seed_template()
            self.assertEqual(len(m.list_tasks()), 2)


if __name__ == "__main__":
    unittest.main()
