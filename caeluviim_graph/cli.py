from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .client import GraphRuntime, Neo4jConfig
from .closure import check_claim_closure
from .manifest import load_manifest, load_schema, validate_manifest
from .receipts import (
    build_ingestion_receipt,
    runtime_identity,
    verify_receipt,
    write_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "ingest-manifest.schema.json"
DEFAULT_MIGRATIONS = ROOT / "graph" / "migrations"
DEFAULT_SEED = ROOT / "examples" / "ingest-manifest.valid.json"
DEFAULT_MANIFESTS = ROOT / "ingest" / "manifests"
DEFAULT_RECEIPTS = ROOT / "runtime" / "receipts"


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def _validated_manifests(directory: Path, schema_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    schema = load_schema(schema_path)
    paths = sorted({*directory.glob("*.json"), *directory.glob("*.json.gz.b64")})
    return [(path, validate_manifest(load_manifest(path), schema)) for path in paths]


def _ingest_with_receipt(
    runtime: GraphRuntime,
    manifest_path: Path,
    manifest: dict[str, Any],
    receipt_directory: Path,
) -> dict[str, Any]:
    before = runtime.stats()
    ingestion = runtime.ingest(manifest)
    after = runtime.stats()
    health = runtime.health()
    receipt = build_ingestion_receipt(
        root=ROOT,
        runtime=runtime_identity(
            database=runtime.config.database,
            server_address=health.get("server_address"),
        ),
        manifest_path=str(manifest_path),
        manifest=manifest,
        ingestion_result=ingestion,
        validation_result={
            "status": "valid",
            "schema": str(DEFAULT_SCHEMA),
            "ingest_id": manifest["ingest_id"],
        },
        graph_before=before,
        graph_after=after,
    )
    verification = verify_receipt(receipt)
    if not verification["valid"]:
        raise RuntimeError(f"Generated receipt failed verification: {verification}")
    receipt_path = write_receipt(receipt, receipt_directory)
    return {
        "ingestion": ingestion,
        "receipt": receipt,
        "receipt_path": str(receipt_path),
        "receipt_verification": verification,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="caeluviim-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="Verify Neo4j connectivity")

    migrate = subparsers.add_parser("migrate", help="Apply idempotent Cypher migrations")
    migrate.add_argument("--directory", type=Path, default=DEFAULT_MIGRATIONS)

    validate = subparsers.add_parser("validate", help="Validate one ingestion manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)

    closure = subparsers.add_parser("closure", help="Compute recursive claim closure")
    closure.add_argument("manifest", type=Path)
    closure.add_argument("claim_id")
    closure.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)

    ingest = subparsers.add_parser("ingest", help="Validate and transactionally ingest a manifest")
    ingest.add_argument("manifest", type=Path)
    ingest.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    ingest.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)

    bootstrap = subparsers.add_parser("bootstrap", help="Verify, migrate, ingest seed, and issue receipt")
    bootstrap.add_argument("--manifest", type=Path, default=DEFAULT_SEED)
    bootstrap.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    bootstrap.add_argument("--directory", type=Path, default=DEFAULT_MIGRATIONS)
    bootstrap.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)

    sync = subparsers.add_parser("sync", help="Migrate and ingest all production manifests with receipts")
    sync.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS)
    sync.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    sync.add_argument("--migrations", type=Path, default=DEFAULT_MIGRATIONS)
    sync.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)

    verify = subparsers.add_parser("verify-receipt", help="Verify a runtime-generated receipt hash")
    verify.add_argument("receipt", type=Path)

    subparsers.add_parser("stats", help="Return graph entity and ingestion counts")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print({"status": "valid", "ingest_id": manifest["ingest_id"]})
        return 0

    if args.command == "closure":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print(check_claim_closure(manifest, args.claim_id))
        return 0

    if args.command == "verify-receipt":
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        result = verify_receipt(receipt)
        _print(result)
        return 0 if result["valid"] else 1

    runtime = GraphRuntime(Neo4jConfig.from_env())

    if args.command == "health":
        _print(runtime.health())
    elif args.command == "migrate":
        _print(runtime.migrate(args.directory))
    elif args.command == "ingest":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print(_ingest_with_receipt(runtime, args.manifest, manifest, args.receipts))
    elif args.command == "bootstrap":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print({
            "health": runtime.health(),
            "migrations": runtime.migrate(args.directory),
            **_ingest_with_receipt(runtime, args.manifest, manifest, args.receipts),
            "stats": runtime.stats(),
        })
    elif args.command == "sync":
        manifests = _validated_manifests(args.manifests, args.schema)
        results = [
            _ingest_with_receipt(runtime, path, manifest, args.receipts)
            for path, manifest in manifests
        ]
        _print({
            "health": runtime.health(),
            "migrations": runtime.migrate(args.migrations),
            "ingestions": results,
            "manifest_count": len(manifests),
            "stats": runtime.stats(),
        })
    elif args.command == "stats":
        _print(runtime.stats())
    else:
        raise AssertionError(f"Unhandled command {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
