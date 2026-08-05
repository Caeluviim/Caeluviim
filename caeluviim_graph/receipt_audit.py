from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from .receipts import verify_receipt


def _load_receipt(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("receipt root must be a JSON object")
    return value


def audit_receipts(directory: Path, *, catalog: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Audit a directory of runtime receipts without contacting the graph runtime."""
    paths = sorted(directory.glob("*.json"))
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    catalog_by_ingest = {
        item["ingest_id"]: item for item in (catalog or {}).get("manifests", [])
    }

    for path in paths:
        try:
            receipt = _load_receipt(path)
            verification = verify_receipt(receipt)
            if not verification["valid"]:
                raise ValueError("receipt verification failed: " + json.dumps(verification, sort_keys=True))
            if receipt.get("receipt_type") != "caeluviim.runtime.ingestion":
                raise ValueError(f"unsupported receipt_type {receipt.get('receipt_type')!r}")
            runtime = receipt.get("runtime", {})
            manifest = receipt.get("manifest", {})
            if runtime.get("runtime_id") in (None, "", "unresolved"):
                raise ValueError("runtime.runtime_id is unresolved")
            if receipt.get("source_commit") in (None, "", "unresolved"):
                raise ValueError("source_commit is unresolved")
            ingest_id = manifest.get("ingest_id")
            manifest_hash = manifest.get("manifest_hash")
            if catalog is not None:
                expected = catalog_by_ingest.get(ingest_id)
                if expected is None:
                    raise ValueError(f"ingest_id {ingest_id!r} is absent from catalog")
                if expected.get("manifest_hash") != manifest_hash:
                    raise ValueError(
                        f"manifest hash mismatch for {ingest_id}: receipt={manifest_hash} catalog={expected.get('manifest_hash')}"
                    )
            records.append({
                "path": str(path), "timestamp": receipt["timestamp"],
                "receipt_hash": receipt["receipt_hash"], "runtime_id": runtime["runtime_id"],
                "database": runtime.get("database"), "source_commit": receipt["source_commit"],
                "ingest_id": ingest_id, "manifest_hash": manifest_hash,
                "status": receipt.get("result", {}).get("status"),
                "node_delta": receipt.get("graph", {}).get("delta", {}).get("nodes", 0),
                "relationship_delta": receipt.get("graph", {}).get("delta", {}).get("relationships", 0),
            })
        except Exception as exc:
            errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})

    duplicate_hashes = sorted(value for value, count in Counter(r["receipt_hash"] for r in records).items() if count > 1)
    event_keys = [f"{r['runtime_id']}|{r['database']}|{r['ingest_id']}|{r['timestamp']}" for r in records]
    duplicate_events = sorted(value for value, count in Counter(event_keys).items() if count > 1)
    valid = not errors and not duplicate_hashes and not duplicate_events
    return {
        "audit_version": "1.0.0", "status": "valid" if valid else "invalid",
        "directory": str(directory), "receipt_count": len(records),
        "catalog_bound": catalog is not None,
        "receipts": sorted(records, key=lambda item: (item["timestamp"], item["path"])),
        "duplicate_receipt_hashes": duplicate_hashes,
        "duplicate_runtime_events": duplicate_events, "errors": errors,
    }
