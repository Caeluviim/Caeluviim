#!/usr/bin/env python3
"""Fail closed when repository claims outrun machine-verifiable evidence."""
from __future__ import annotations
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT_DIRS = [ROOT / "receipts", ROOT / "runtime" / "receipts", ROOT / "data" / "receipts"]
REQUIRED = {
    "runtime_identifier", "source_commit", "manifest", "timestamp", "result",
    "node_count", "relationship_count", "validation_result", "receipt_hash"
}


def receipts():
    for directory in RECEIPT_DIRS:
        if directory.is_dir():
            yield from directory.rglob("*.json")


def main() -> int:
    checked = 0
    valid = []
    invalid = []
    for path in receipts():
        checked += 1
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            invalid.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
            continue
        missing = sorted(REQUIRED - set(obj))
        if missing:
            invalid.append({"path": str(path.relative_to(ROOT)), "missing": missing})
        else:
            valid.append(str(path.relative_to(ROOT)))

    report = {
        "status": "PASS" if valid and not invalid else "FAIL",
        "receipt_files_checked": checked,
        "valid_runtime_receipts": valid,
        "invalid_receipts": invalid,
        "rule": "Repository artifacts are not proof of live graph state; a complete runtime receipt is required."
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
