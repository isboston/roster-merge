from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from openpyxl import load_workbook
from merge import merge


class DemoTest(unittest.TestCase):
    def test_demo(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "combined.xlsx"
            merge(Path(__file__).parent / "examples", output)
            wb = load_workbook(output)
            try:
                shifts = list(wb["Shifts"].values)[1:]
                conflicts = list(wb["Conflicts"].values)[1:]
                review = list(wb["Review"].values)[1:]
                self.assertEqual(len(shifts), 11)
                self.assertEqual(len(conflicts), 1)
                self.assertEqual(conflicts[0][:3], ("Avery Vale", datetime(2026,12,1,14), datetime(2026,12,1,16)))
                self.assertEqual(set(conflicts[0][3::3]), {"support.xlsx", "infrastructure.xlsx"})
                self.assertIn(("Morgan Reed", datetime(2026,12,1,20), datetime(2026,12,2,8)), [r[:3] for r in shifts])
                self.assertEqual(len(review), 1)
                self.assertEqual(review[0][:3], ("operations.xlsx", "Operations", 5))
                self.assertIn("Night", review[0][-1])
                self.assertEqual(len({r[3:] for r in shifts} | {r[:3] for r in review}), 12)
            finally:
                wb.close()
