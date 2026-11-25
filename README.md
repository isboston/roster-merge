# Roster Merge

Combine duty schedules from three departments into one Excel workbook. Every shift links back through its source filename, worksheet name and row number. The included schedules are fictional.

## Run the demo

With Python 3.12 and venv installed, run from the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python merge.py examples combined_schedule.xlsx
python -m unittest -v
```

Open the result in ONLYOFFICE or Excel. The Shifts tab contains 11 timed assignments. Conflicts shows Avery Vale assigned to two teams on December 1, 2026 from 14:00 to 16:00. Jules Hart changes teams at 16:00 without an overlap. Review preserves Sky Lane's unspecified Night shift for a human decision.

## Input contract

Place source XLSX files in a single directory. Each worksheet uses the first row for headers and one assignment per following row. The three supported header sets match the workbooks in examples. Columns may be reordered. Use exact employee names, one shared local time zone, ISO dates and 24-hour times. A time window ending earlier than it starts crosses midnight. Explicit start and end timestamps must already contain the correct dates.

The CLI creates or replaces the named output workbook. Use a distinct output filename. Unrecognized rows go to Review with the source values. This version uses deterministic rules and runs offline after dependency installation. Nextcloud integration and model-assisted mapping of unfamiliar headers are future experiments.
