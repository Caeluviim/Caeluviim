from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .catalog import build_catalog
from .client import GraphRuntime, Neo4jConfig
from .closure import check_claim_closure
from .manifest import load_manifest, load_schema, validate_manifest
from .receipts import (
    build_ingestion_receipt,
    runtime_identity,
    verify_receipt,
    verify_receipt_directory,
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


def _require_valid_catalog(directory: Path, schema_path: Path) -> dict[str, Any]:
    catalog = build_catalog(directory, schema_path)
    if catalog["status"] != "valid":
        raise RuntimeError(
            "Production manifest catalog failed closed before runtime mutation: "
            + json.dumps(catalog, sort_keys=True)
        )
    return catalog


def _ingest_with_receipt(runtime: GraphRuntime, manifest_path: Path, manifest: dict[str, Any], schema_path: Path, receipt_directory: Path) -> dict[str, Any]:
    before = runtime.stats()
    ingestion = runtime.ingest(manifest)
    after = runtime.stats()
    health = runtime.health()
    receipt = build_ingestion_receipt(
        root=ROOT,
        runtime=runtime_identity(database=runtime.config.database, server_address=health.get("server_address")),
        manifest_path=str(manifest_path),
        manifest=manifest,
        ingestion_result=ingestion,
        validation_result={"status": "valid", "schema": str(schema_path), "ingest_id": manifest["ingest_id"]},
        graph_before=before,
        graph_after=after,
    )
    verification = verify_receipt(receipt)
    if not verification["valid"]:
        raise RuntimeError(f"Generated receipt failed verification: {verification}")
    receipt_path = write_receipt(receipt, receipt_directory)
    return {"ingestion": ingestion, "receipt": receipt, "receipt_path": str(receipt_path), "receipt_verification": verification}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="caeluviim-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="Verify Neo4j connectivity")
    migrate = subparsers.add_parser("migrate", help="Apply idempotent Cypher migrations")
    migrate.add_argument("--directory", type=Path, default=DEFAULT_MIGRATIONS)
    validate = subparsers.add_parser("validate", help="Validate one ingestion manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    catalog = subparsers.add_parser("catalog", help="Audit the complete production manifest catalog")
    catalog.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS)
    catalog.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    catalog.add_argument("--output", type=Path)
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
    sync = subparsers.add_parser("sync", help="Audit, migrate, and ingest all production manifests with receipts")
    sync.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS)
    sync.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    sync.add_argument("--migrations", type=Path, default=DEFAULT_MIGRATIONS)
    sync.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    verify = subparsers.add_parser("verify-receipt", help="Verify a runtime-generated receipt hash")
    verify.add_argument("receipt", type=Path)
    verify_ledger = subparsers.add_parser("verify-receipts", help="Fail-closed audit of a runtime receipt directory")
    verify_ledger.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    subparsers.add_parser("stats", help="Return graph entity and ingestion counts")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print({"status": "valid", "ingest_id": manifest["ingest_id"]})
        return 0
    if args.command == "catalog":
        catalog = build_catalog(args.manifests, args.schema)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        _print(catalog)
        return 0 if catalog["status"] == "valid" else 1
    if args.command == "closure":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print(check_claim_closure(manifest, args.claim_id))
        return 0
    if args.command == "verify-receipt":
        result = verify_receipt(json.loads(args.receipt.read_text(encoding="utf-8")))
        _print(result)
        return 0 if result["valid"] else 1
    if args.command == "verify-receipts":
        result = verify_receipt_directory(args.receipts)
        _print(result)
        return 0 if result["status"] == "valid" else 1

    runtime = GraphRuntime(Neo4jConfig.from_env())
    if args.command == "health":
        _print(runtime.health())
    elif args.command == "migrate":
        _print(runtime.migrate(args.directory))
    elif args.command == "ingest":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        _print(_ingest_with_receipt(runtime, args.manifest, manifest, args.schema, args.receipts))
    elif args.command == "bootstrap":
        manifest = validate_manifest(load_manifest(args.manifest), load_schema(args.schema))
        migrations = runtime.migrate(args.directory)
        _print({"health": runtime.health(), "migrations": migrations, **_ingest_with_receipt(runtime, args.manifest, manifest, args.schema, args.receipts), "stats": runtime.stats()})
    elif args.command == "sync":
        catalog = _require_valid_catalog(args.manifests, args.schema)
        manifests = _validated_manifests(args.manifests, args.schema)
        migrations = runtime.migrate(args.migrations)
        results = [_ingest_with_receipt(runtime, path, manifest, args.schema, args.receipts) for path, manifest in manifests]
        _print({"catalog": catalog, "health": runtime.health(), "migrations": migrations, "ingestions": results, "manifest_count": len(manifests), "stats": runtime.stats()})
    elif args.command == "stats":
        _print(runtime.stats())
    else:
        raise AssertionError(f"Unhandled command {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
