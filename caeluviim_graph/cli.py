from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .client import GraphRuntime, Neo4jConfig
from .manifest import load_manifest, load_schema, validate_manifest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "ingest-manifest.schema.json"
DEFAULT_MIGRATIONS = ROOT / "graph" / "migrations"
DEFAULT_SEED = ROOT / "examples" / "ingest-manifest.valid.json"


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="caeluviim-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="Verify Neo4j connectivity")

    migrate = subparsers.add_parser("migrate", help="Apply idempotent Cypher migrations")
    migrate.add_argument("--directory", type=Path, default=DEFAULT_MIGRATIONS)

    validate = subparsers.add_parser("validate", help="Validate one ingestion manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)

    ingest = subparsers.add_parser("ingest", help="Validate and transactionally ingest a manifest")
    ingest.add_argument("manifest", type=Path)
    ingest.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)

    bootstrap = subparsers.add_parser(
        "bootstrap", help="Verify, migrate, and ingest the conforming seed manifest"
    )
    bootstrap.add_argument("--manifest", type=Path, default=DEFAULT_SEED)
    bootstrap.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    bootstrap.add_argument("--directory", type=Path, default=DEFAULT_MIGRATIONS)

    subparsers.add_parser("stats", help="Return graph entity and ingestion counts")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime = GraphRuntime(Neo4jConfig.from_env())

    if args.command == "health":
        _print(runtime.health())
    elif args.command == "migrate":
        _print(runtime.migrate(args.directory))
    elif args.command == "validate":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print({"status": "valid", "ingest_id": manifest["ingest_id"]})
    elif args.command == "ingest":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print(runtime.ingest(manifest))
    elif args.command == "bootstrap":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print(
            {
                "health": runtime.health(),
                "migrations": runtime.migrate(args.directory),
                "ingestion": runtime.ingest(manifest),
                "stats": runtime.stats(),
            }
        )
    elif args.command == "stats":
        _print(runtime.stats())
    else:
        raise AssertionError(f"Unhandled command {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
