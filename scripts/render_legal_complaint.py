from __future__ import annotations

import argparse
import json
from pathlib import Path

from caeluviim_graph.legal_drafting import render_complaint


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a provenance-bearing complaint draft from a legal case record")
    parser.add_argument("case_record", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    record = json.loads(args.case_record.read_text(encoding="utf-8"))
    rendered = render_complaint(record)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
