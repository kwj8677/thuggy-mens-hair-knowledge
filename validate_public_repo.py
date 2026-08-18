from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "README.md",
    "canonical/entity.json",
    "schema/localbusiness.jsonld",
    "guides/barber-menshair-spectrum.md",
    "guides/mens-hair-style-decision-guide.md",
    "guides/specialty-hair-glossary.md",
    "sources/README.md",
]

# The validator and its generated report are excluded because this definition
# necessarily names the patterns it checks.
SCAN_SUFFIXES = {".md", ".json", ".jsonld"}
FORBIDDEN = {
    "private system name": re.compile(r"handsos", re.I),
    "revenue metric": re.compile(r"\brevenue\b|매출|매상", re.I),
    "customer-row data": re.compile(r"customer\s*rows?|고객\s*(?:행|목록|명단)", re.I),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "credential term": re.compile(r"\b(?:password|passwd|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|secret[_ -]?key)\b", re.I),
    "large internal aggregate": re.compile(r"\b1[,.]?655\b|1천\s*655"),
}


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for relative in ("canonical/entity.json", "schema/localbusiness.jsonld"):
        path = ROOT / relative
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid JSON: {relative}: {exc}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                errors.append(f"forbidden {label}: {path.relative_to(ROOT)}")

    entity_path = ROOT / "canonical/entity.json"
    schema_path = ROOT / "schema/localbusiness.jsonld"
    if entity_path.is_file():
        entity = json.loads(entity_path.read_text(encoding="utf-8"))
        if entity.get("opening_hours", {}).get("Sunday") != "13:00-21:00":
            errors.append("canonical Sunday hours must be 13:00-21:00")
        if entity.get("opening_hours", {}).get("Tuesday") != "closed":
            errors.append("canonical Tuesday must be closed")
    if schema_path.is_file():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if "Su 13:00-21:00" not in schema.get("openingHours", []):
            errors.append("JSON-LD Sunday hours must be Su 13:00-21:00")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    print(f"Required files: {len(REQUIRED)}/{len(REQUIRED)}")
    print("JSON and JSON-LD: valid")
    print("Private-data patterns: none found")
    print("Sunday hours: 13:00-21:00")
    print("Tuesday: closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
