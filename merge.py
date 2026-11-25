"""Merge supported English duty rosters into an auditable XLSX workbook."""
import argparse
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


def parse(row):
    if "Engineer" in row:
        name = row["Engineer"]
        start, end = (datetime.fromisoformat(str(row[key])) for key in ("Shift starts", "Shift ends"))
    else:
        if "Employee" in row:
            name, day, first, last = (row[key] for key in ("Employee", "Date", "Start", "End"))
        else:
            name, day, window = (row[key] for key in ("Duty officer", "Service date", "Time window"))
            if "-" not in str(window):
                raise ValueError(f"Missing explicit start and end: {window}")
            first, last = window.split("-", 1)
        day = day.date() if isinstance(day, datetime) else date.fromisoformat(str(day))
        start, end = (datetime.combine(day, time.fromisoformat(str(value).strip())) for value in (first, last))
        if end < start:
            end += timedelta(days=1)
    if not isinstance(name, str) or not name.strip() or end <= start:
        raise ValueError("Missing employee or invalid shift duration")
    return name.strip(), start, end


def merge(folder, output):
    files = sorted(p for p in folder.glob("*.xlsx") if p.resolve() != output.resolve() and not p.name.startswith("~$"))
    if not files:
        raise ValueError("Input folder contains no XLSX files")
    book = Workbook()
    shifts = book.active
    shifts.title = "Shifts"
    conflicts = book.create_sheet("Conflicts")
    review = book.create_sheet("Review")
    shifts.append(["Employee", "Start", "End", "File", "Sheet", "Row"])
    conflicts.append(["Employee", "Overlap start", "Overlap end", "First file", "First sheet", "First row", "Second file", "Second sheet", "Second row"])
    review.append(["File", "Sheet", "Row", "Reason", "Source values"])
    people = defaultdict(list)
    for path in files:
        source = load_workbook(path, read_only=True)
        try:
            for sheet in source:
                rows = sheet.values
                headers = next(rows, ())
                for number, values in enumerate(rows, 2):
                    if all(v is None for v in values):
                        continue
                    ref = (path.name, sheet.title, number)
                    try:
                        name, start, end = parse(dict(zip(headers, values)))
                    except (ValueError, KeyError, TypeError) as error:
                        review.append([*ref, str(error), " | ".join(map(str, values))])
                        continue
                    people[name].append((start, end, ref))
        finally:
            source.close()
    for name, entries in sorted(people.items()):
        active = []
        for start, end, ref in sorted(entries):
            shifts.append([name, start, end, *ref])
            active = [entry for entry in active if entry[1] > start]
            for _, previous_end, previous_ref in active:
                conflicts.append([name, start, min(end, previous_end), *previous_ref, *ref])
            active.append((start, end, ref))
    for sheet in book:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="17465A")
        for cells in sheet.columns:
            for cell in cells:
                if cell.data_type == "f":
                    cell.data_type = "s"
            sheet.column_dimensions[get_column_letter(cells[0].column)].width = min(65, max(len(str(c.value)) for c in cells) + 4)
    with NamedTemporaryFile(dir=output.parent, suffix=".xlsx", delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        book.save(temporary)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    merge(args.folder, args.output)
