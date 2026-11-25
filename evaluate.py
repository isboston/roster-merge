"""Compare header mapping approaches on a small synthetic set."""
import json
import time
from pathlib import Path
from suggest import FIELDS, propose

CASES = [
    ["Employee", "Date", "Start", "End"],
    ["Clock out", "Assigned technician", "Clock in", "Duty day"],
    ["Staff member", "Shift date", "Start time", "End time"],
    ["Worker", "Workday", "From", "Until"],
    ["Name", "Date of duty", "Shift begins", "Shift finishes"],
    ["Agent", "Calendar date", "Beginning", "Ending"],
    ["Team member", "Day", "In", "Out"],
    ["On-call person", "Service date", "Duty starts", "Duty ends"],
    ["Personnel", "Scheduled date", "Arrival", "Departure"],
    ["Employee name", "Shift day", "Time in", "Time out"],
]
EXPECTED = [(1, 3, 2, 0) if i == 1 else (0, 1, 2, 3) for i in range(len(CASES))]
SYNONYMS = {
    "Employee": {"employee", "employee name", "staff member", "name", "worker"},
    "Date": {"date", "shift date", "shift day", "day", "workday"},
    "Start": {"start", "start time", "clock in", "time in", "from"},
    "End": {"end", "end time", "clock out", "time out", "until"},
}


def dictionary(headers):
    return {field: next((header for header in headers if header.lower() in SYNONYMS[field]), None) for field in FIELDS}


def run():
    results = []
    for number, (headers, indexes) in enumerate(zip(CASES, EXPECTED), 1):
        expected = dict(zip(FIELDS, (headers[i] for i in indexes)))
        baseline = dictionary(headers)
        started = time.monotonic()
        try:
            prediction = propose(headers, "qwen2.5:1.5b")
            error = None
        except Exception as exc:
            prediction, error = {}, str(exc)
        elapsed = round(time.monotonic() - started, 2)
        results.append({"case": number, "headers": headers, "expected": expected, "dictionary": baseline,
                        "llm": prediction, "llm_seconds": elapsed, "error": error})
        print(f"Case {number}: {sum(prediction.get(k) == v for k, v in expected.items())}/4 in {elapsed}s", flush=True)
    Path("evaluation").mkdir(exist_ok=True)
    Path("evaluation/results.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    run()
