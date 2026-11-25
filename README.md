# Roster Merge with local Ollama

## Try an unfamiliar roster with a local language model

After installing the Python dependencies below, start Ollama locally and run:

```sh
ollama pull qwen2.5:1.5b
python merge.py demo-llm baseline.xlsx
python suggest.py demo-llm/dispatch.xlsx --sheet Dispatch > proposal.json
cat proposal.json
# After checking each proposed source column:
python merge.py demo-llm combined_schedule.xlsx --approved-mapping proposal.json
```

The first run sends both dispatch rows to Review. Ollama receives only column
labels and proposes a JSON mapping. Check that Employee maps to Assigned
technician, Date to Duty day, Start to Clock in and End to Clock out before
applying. Both shifts should then appear in Shifts. This experiment covers
one new layout with separate date and time fields. A structurally valid
mapping can still be semantically wrong. Ambiguous or duplicate selections
are rejected; a human makes the final decision. The approved mapping is
scoped to the exact source filename, sheet and ordered headers.

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

The CLI creates or replaces the named output workbook. Use a distinct output filename. Unrecognized rows go to Review with the source values. Merging runs offline. Inference uses the local Ollama service. Nextcloud integration is a future experiment.

## Header mapping experiment

On an Ubuntu 24.04 VM with four vCPUs and 7.8 GiB RAM, Qwen2.5 1.5B
mapped 40/40 fields correctly across ten synthetic English header sets.
The small fixed synonym dictionary in evaluate.py mapped 20/40 fields.
The model took a median 3.66 seconds per request, including one cold request.
The dictionary was hand-written and deliberately limited. The cases are
synthetic and unambiguous, so these figures do not establish accuracy on real
workbooks, other languages, or ambiguous headers. Review every proposal.

Run `python evaluate.py` with Ollama running to repeat the experiment. It
writes evaluation/results.json. The committed file contains the original run.
