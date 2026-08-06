from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .catalog import build_catalog
from .client import GraphRuntime, Neo4jConfig
from .closure import check_claim_closure
from .manifest import load_manifest, load_schema, validate_manifest
from .memory import GraphMemory, RecallRequest
from .receipt_audit import audit_receipts
from .receipts import build_ingestion_receipt, runtime_identity, verify_receipt, write_receipt
from .repository_memory import RepositoryMemory

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
        raise RuntimeError("Production manifest catalog failed closed before runtime mutation: " + json.dumps(catalog, sort_keys=True))
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


def _add_memory_backend_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--backend",
        choices=("auto", "neo4j", "repository"),
        default="auto",
        help="Use Neo4j, repository manifests, or automatically fall back to repository manifests",
    )
    parser.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)


def _memory_backend(args: argparse.Namespace):
    if args.backend == "repository":
        return RepositoryMemory(args.manifests, args.schema)

    config = Neo4jConfig.from_env()
    graph_memory = GraphMemory(config)
    if args.backend == "neo4j":
        return graph_memory

    try:
        GraphRuntime(config).health()
    except Exception:
        return RepositoryMemory(args.manifests, args.schema)
    return graph_memory


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
    audit = subparsers.add_parser("audit-receipts", help="Audit the complete runtime receipt ledger")
    audit.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    audit.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS)
    audit.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    audit.add_argument("--without-catalog", action="store_true")
    audit.add_argument("--output", type=Path)
    subparsers.add_parser("stats", help="Return Neo4j entity and ingestion counts")

    memory_stats = subparsers.add_parser("memory-stats", help="Return queryable memory counts")
    _add_memory_backend_arguments(memory_stats)

    entity = subparsers.add_parser("entity", help="Retrieve one entity with provenance and direct relations")
    entity.add_argument("entity_id")
    _add_memory_backend_arguments(entity)

    recall = subparsers.add_parser("recall", help="Search persistent memory and return bounded context")
    recall.add_argument("text")
    recall.add_argument("--limit", type=int, default=10)
    recall.add_argument("--depth", type=int, default=1)
    recall.add_argument("--context-limit", type=int, default=8)
    recall.add_argument("--label", action="append", default=[])
    _add_memory_backend_arguments(recall)

    neighbors = subparsers.add_parser("neighbors", help="Retrieve a bounded memory neighborhood")
    neighbors.add_argument("entity_id")
    neighbors.add_argument("--depth", type=int, default=1)
    neighbors.add_argument("--limit", type=int, default=50)
    _add_memory_backend_arguments(neighbors)

    timeline = subparsers.add_parser("timeline", help="Return the most recent memory entities")
    timeline.add_argument("--limit", type=int, default=20)
    _add_memory_backend_arguments(timeline)
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
            args.output.write_text(json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
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
    if args.command == "audit-receipts":
        catalog = None if args.without_catalog else build_catalog(args.manifests, args.schema)
        if catalog is not None and catalog["status"] != "valid":
            _print({"status": "invalid", "cause": "manifest catalog invalid", "catalog": catalog})
            return 1
        result = audit_receipts(args.receipts, catalog=catalog)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        _print(result)
        return 0 if result["status"] == "valid" else 1

    if args.command in {"memory-stats", "entity", "recall", "neighbors", "timeline"}:
        memory = _memory_backend(args)
        if args.command == "memory-stats":
            if isinstance(memory, RepositoryMemory):
                _print({"backend": "repository", **memory.stats()})
            else:
                _print({"backend": "neo4j", **GraphRuntime(memory.config).stats()})
        elif args.command == "entity":
            result = memory.entity(args.entity_id)
            _print({"status": "found", "backend": type(memory).__name__, "entity": result} if result is not None else {"status": "not_found", "backend": type(memory).__name__, "entity_id": args.entity_id})
            return 0 if result is not None else 1
        elif args.command == "recall":
            _print(memory.recall(RecallRequest(
                text=args.text,
                limit=args.limit,
                depth=args.depth,
                context_limit=args.context_limit,
                labels=tuple(args.label),
            )))
        elif args.command == "neighbors":
            result = memory.neighbors(args.entity_id, depth=args.depth, limit=args.limit)
            _print({"status": "found", "backend": type(memory).__name__, "result": result} if result is not None else {"status": "not_found", "backend": type(memory).__name__, "entity_id": args.entity_id})
            return 0 if result is not None else 1
        elif args.command == "timeline":
            _print({"backend": type(memory).__name__, "entities": memory.timeline(limit=args.limit)})
        return 0

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
        receipt_audit = audit_receipts(args.receipts, catalog=catalog)
        if receipt_audit["status"] != "valid":
            raise RuntimeError("Runtime receipt ledger failed after sync: " + json.dumps(receipt_audit, sort_keys=True))
        _print({"catalog": catalog, "health": runtime.health(), "migrations": migrations, "ingestions": results, "receipt_audit": receipt_audit, "manifest_count": len(manifests), "stats": runtime.stats()})
    elif args.command == "stats":
        _print(runtime.stats())
    else:
        raise AssertionError(f"Unhandled command {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
