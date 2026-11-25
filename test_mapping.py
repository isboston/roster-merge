import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from openpyxl import load_workbook
from merge import merge


class DispatchTest(unittest.TestCase):
    def test_recorded_local_proposal(self):
        folder = Path(__file__).parent / "demo-llm"
        proposal = json.loads((folder / "observed.json").read_text())
        with TemporaryDirectory() as directory:
            output = Path(directory) / "out.xlsx"
            for mapping, counts in [(None, (0, 2)), (proposal, (2, 0))]:
                merge(folder, output, mapping)
                book = load_workbook(output)
                try:
                    self.assertEqual(tuple(book[s].max_row - 1 for s in ("Shifts", "Review")), counts)
                    if mapping:
                        row = list(book["Shifts"].values)[1]
                        self.assertEqual((row[0], row[1].hour, row[2].hour), ("Evan Birch", 9, 17))
                finally:
                    book.close()
            with self.assertRaisesRegex(ValueError, "headers have changed"):
                merge(folder, output, dict(proposal, headers=[]))
