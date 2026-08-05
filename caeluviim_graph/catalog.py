from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from .manifest import (
    ALLOWED_LABELS,
    ALLOWED_RELATIONSHIP_TYPES,
    RESERVED_PROPERTIES,
    ManifestValidationError,
    load_manifest,
    load_schema,
    safe_relationship_type,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFESTS = ROOT / "ingest" / "manifests"
DEFAULT_SCHEMA = ROOT / "schemas" / "ingest-manifest.schema.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _duplicates(values: list[str]) -> list[str]:
    return sorted(key for key, count in Counter(values).items() if count > 1)


def _schema_errors(
    manifest: Mapping[str, Any], schema: Mapping[str, Any]
) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(manifest), key=lambda item: list(item.absolute_path)
        )
    ]


def _validate_catalog_manifest(
    manifest: Mapping[str, Any], schema: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate one manifest without imposing manifest-local endpoint closure.

    Runtime ingestion requires every relationship endpoint to exist in the same
    manifest. The repository catalog has a broader purpose: it audits the union
    of all production manifests, so cross-manifest references must remain
    visible until the global endpoint pass below.
    """

    candidate = deepcopy(dict(manifest))
    errors = _schema_errors(candidate, schema)
    if errors:
        raise ManifestValidationError(errors)

    node_ids = [node["id"] for node in candidate["nodes"]]
    relationship_ids = [relationship["id"] for relationship in candidate["relationships"]]
    entity_ids = node_ids + relationship_ids + [candidate["source"]["source_id"], candidate["ingest_id"]]

    for kind, values in (
        ("node", node_ids),
        ("relationship", relationship_ids),
        ("entity", entity_ids),
    ):
        duplicate_ids = _duplicates(values)
        if duplicate_ids:
            errors.append(f"duplicate {kind} identifiers: {', '.join(duplicate_ids)}")

    for node in candidate["nodes"]:
        invalid = sorted(set(node.get("properties", {})).intersection(RESERVED_PROPERTIES))
        if invalid:
            errors.append(f"node {node['id']} uses reserved properties: {', '.join(invalid)}")
        for label in node["labels"]:
            if label not in ALLOWED_LABELS:
                errors.append(f"node {node['id']} uses unsupported label {label}")

    for relationship in candidate["relationships"]:
        invalid = sorted(
            set(relationship.get("properties", {})).intersection(RESERVED_PROPERTIES)
        )
        if invalid:
            errors.append(
                f"relationship {relationship['id']} uses reserved properties: {', '.join(invalid)}"
            )
        try:
            safe_relationship_type(relationship["type"])
        except ValueError as exc:
            errors.append(f"relationship {relationship['id']}: {exc}")

    if errors:
        raise ManifestValidationError(errors)
    return candidate


def build_catalog(manifest_directory: Path, schema_path: Path) -> dict[str, Any]:
    schema = load_schema(schema_path)
    paths = sorted({*manifest_directory.glob("*.json"), *manifest_directory.glob("*.json.gz.b64")})
    manifests: list[tuple[Path, dict[str, Any]]] = []
    errors: list[dict[str, str]] = []

    for path in paths:
        try:
            raw_manifest = load_manifest(path)
        except Exception as exc:
            errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})
            continue

        structural_errors = _schema_errors(raw_manifest, schema)
        if structural_errors:
            errors.append(
                {
                    "path": str(path),
                    "error": f"ManifestValidationError: {ManifestValidationError(structural_errors)}",
                }
            )
            continue

        # Structurally valid manifests must remain in the catalog-wide audit even
        # when a manifest-local semantic invariant fails. Excluding them would
        # hide cross-manifest duplicate identifiers and dangling endpoints.
        manifests.append((path, deepcopy(raw_manifest)))
        try:
            _validate_catalog_manifest(raw_manifest, schema)
        except Exception as exc:
            errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})

    ingest_ids = [manifest["ingest_id"] for _, manifest in manifests]
    node_ids = [node["id"] for _, manifest in manifests for node in manifest["nodes"]]
    relationship_ids = [rel["id"] for _, manifest in manifests for rel in manifest["relationships"]]
    node_id_set = set(node_ids)

    duplicate_ingest_ids = _duplicates(ingest_ids)
    duplicate_node_ids = _duplicates(node_ids)
    duplicate_relationship_ids = _duplicates(relationship_ids)

    dangling: list[dict[str, str]] = []
    self_loops: list[str] = []
    relationship_type_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()

    for _, manifest in manifests:
        for node in manifest["nodes"]:
            label_counts.update(node["labels"])
        for rel in manifest["relationships"]:
            relationship_type_counts[rel["type"]] += 1
            if rel["from"] not in node_id_set:
                dangling.append({"relationship_id": rel["id"], "endpoint": "from", "node_id": rel["from"]})
            if rel["to"] not in node_id_set:
                dangling.append({"relationship_id": rel["id"], "endpoint": "to", "node_id": rel["to"]})
            if rel["from"] == rel["to"]:
                self_loops.append(rel["id"])

    records = [
        {
            "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "ingest_id": manifest["ingest_id"],
            "source_id": manifest["source"]["source_id"],
            "source_hash": manifest["source"]["content_hash"],
            "node_count": len(manifest["nodes"]),
            "relationship_count": len(manifest["relationships"]),
            "manifest_hash": "sha256:" + hashlib.sha256(_canonical(manifest)).hexdigest(),
        }
        for path, manifest in manifests
    ]

    valid = not any((errors, duplicate_ingest_ids, duplicate_node_ids, duplicate_relationship_ids, dangling))
    catalog: dict[str, Any] = {
        "catalog_version": "0.1.0",
        "status": "valid" if valid else "invalid",
        "manifest_directory": str(manifest_directory),
        "schema": str(schema_path),
        "manifest_count": len(manifests),
        "node_count": len(node_ids),
        "relationship_count": len(relationship_ids),
        "manifests": records,
        "label_counts": dict(sorted(label_counts.items())),
        "relationship_type_counts": dict(sorted(relationship_type_counts.items())),
        "errors": errors,
        "duplicate_ingest_ids": duplicate_ingest_ids,
        "duplicate_node_ids": duplicate_node_ids,
        "duplicate_relationship_ids": duplicate_relationship_ids,
        "dangling_relationship_endpoints": sorted(dangling, key=lambda item: (item["relationship_id"], item["endpoint"])),
        "self_loop_relationship_ids": sorted(self_loops),
    }
    catalog["catalog_hash"] = "sha256:" + hashlib.sha256(_canonical(catalog)).hexdigest()
    return catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="caeluviim-graph-catalog")
    parser.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    catalog = build_catalog(args.manifests, args.schema)
    rendered = json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if catalog["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
