"""Ask local Ollama to propose a column mapping for one worksheet."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

from openpyxl import load_workbook


FIELDS = ("Employee", "Date", "Start", "End")


def validate(headers, mapping):
    if not all(isinstance(h, str) and h.strip() for h in headers) or len(set(headers)) != len(headers):
        raise ValueError("Expected unique, nonempty text headers")
    if set(mapping) != set(FIELDS) or any(mapping[k] not in headers for k in FIELDS) or len(set(mapping.values())) != 4:
        raise ValueError("Expected four distinct source columns. Inspect the worksheet before proceeding.")


def propose(headers, model):
    schema = {"type": "object", "properties": {k: {"type": "string", "enum": [*headers, "UNSURE"]} for k in FIELDS},
              "required": list(FIELDS), "additionalProperties": False}
    payload = {"model": model, "stream": False, "format": schema,
               "options": {"temperature": 0, "num_ctx": 2048, "num_predict": 160},
               "prompt": "Match roster column labels to the employee name, shift date, start time and end time. "
                         "Copy each corresponding label exactly. Use UNSURE if unclear. Return JSON. Labels: " + json.dumps(headers)}
    req = Request("http://127.0.0.1:11434/api/generate", json.dumps(payload).encode(), {"Content-Type": "application/json"})
    with urlopen(req, timeout=180) as response:
        mapping = json.loads(json.load(response)["response"])
    validate(headers, mapping)
    return mapping


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--sheet", required=True)
    parser.add_argument("--model", default="qwen2.5:1.5b")
    args = parser.parse_args()
    book = load_workbook(args.workbook, read_only=True)
    try:
        headers = list(next(book[args.sheet].values))
        mapping = propose(headers, args.model)
        print(json.dumps(dict(file=args.workbook.name, sheet=args.sheet, headers=headers, model=args.model, mapping=mapping), indent=2))
    finally:
        book.close()
