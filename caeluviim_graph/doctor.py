"""Executable repository self-diagnostic for Caeluviim.

This deliberately tests useful behavior rather than treating the presence of files as
proof that the system works. It is dependency-free so a fresh Python checkout can run it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(name: str, command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "ok": proc.returncode == 0,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def main() -> int:
    checks = [
        run("repository-memory-stats", [sys.executable, "-m", "caeluviim_graph.cli", "memory-stats", "--backend", "repository"]),
        run("repository-recall-rrkc", [sys.executable, "-m", "caeluviim_graph.cli", "recall", "rrkc", "--backend", "repository"]),
        run("unit-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ]
    report = {
        "ok": all(c["ok"] for c in checks),
        "root": str(ROOT),
        "python": sys.version,
        "checks": checks,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
