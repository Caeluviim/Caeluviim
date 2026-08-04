from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .manifest import load_manifest, load_schema, validate_manifest

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFESTS = ROOT / "ingest" / "manifests"
DEFAULT_SCHEMA = ROOT / "schemas" / "ingest-manifest.schema.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_catalog(manifest_directory: Path, schema_path: Path) -> dict[str, Any]:
    schema = load_schema(schema_path)
    paths = sorted({*manifest_directory.glob("*.json"), *manifest_directory.glob("*.json.gz.b64")})
    manifests: list[tuple[Path, dict[str, Any]]] = []
    errors: list[dict[str, str]] = []

    for path in paths:
        try:
            manifests.append((path, validate_manifest(load_manifest(path), schema)))
        except Exception as exc:  # audit must report every invalid artifact
            errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})

    ingest_ids = [manifest["ingest_id"] for _, manifest in manifests]
    node_ids = [node["id"] for _, manifest in manifests for node in manifest["nodes"]]
    relationship_ids = [rel["id"] for _, manifest in manifests for rel in manifest["relationships"]]
    node_id_set = set(node_ids)

    duplicate_ingest_ids = sorted(key for key, count in Counter(ingest_ids).items() if count > 1)
    duplicate_node_ids = sorted(key for key, count in Counter(node_ids).items() if count > 1)
    duplicate_relationship_ids = sorted(key for key, count in Counter(relationship_ids).items() if count > 1)

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
