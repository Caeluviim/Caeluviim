from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def resolve_source_commit(root: Path) -> str:
    explicit = os.getenv("CAELUVIIM_SOURCE_COMMIT") or os.getenv("GITHUB_SHA")
    if explicit:
        return explicit
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unresolved"


def runtime_identity(*, database: str, server_address: str | None = None) -> dict[str, str]:
    return {
        "runtime_id": os.getenv("CAELUVIIM_RUNTIME_ID", socket.gethostname()),
        "runtime_kind": "neo4j",
        "database": database,
        "server_address": server_address or "unresolved",
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }


def build_ingestion_receipt(
    *,
    root: Path,
    runtime: Mapping[str, Any],
    manifest_path: str,
    manifest: Mapping[str, Any],
    ingestion_result: Mapping[str, Any],
    validation_result: Mapping[str, Any],
    graph_before: Mapping[str, Any],
    graph_after: Mapping[str, Any],
    timestamp: str | None = None,
) -> dict[str, Any]:
    created_at = timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    delta = {
        key: int(graph_after.get(key, 0)) - int(graph_before.get(key, 0))
        for key in sorted(set(graph_before) | set(graph_after))
    }
    body: dict[str, Any] = {
        "receipt_version": "1.0.0",
        "receipt_type": "caeluviim.runtime.ingestion",
        "timestamp": created_at,
        "runtime": dict(runtime),
        "source_commit": resolve_source_commit(root),
        "manifest": {
            "path": manifest_path,
            "ingest_id": manifest["ingest_id"],
            "manifest_hash": ingestion_result["manifest_hash"],
            "source_id": manifest["source"]["source_id"],
            "source_content_hash": manifest["source"]["content_hash"],
        },
        "result": {
            "status": ingestion_result["status"],
            "nodes_reported": int(ingestion_result.get("nodes", 0)),
            "relationships_reported": int(ingestion_result.get("relationships", 0)),
        },
        "graph": {
            "before": dict(graph_before),
            "after": dict(graph_after),
            "delta": delta,
        },
        "validation": dict(validation_result),
    }
    body["receipt_hash"] = sha256_text(canonical_json(body))
    return body


def verify_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "receipt_version",
        "receipt_type",
        "timestamp",
        "runtime",
        "source_commit",
        "manifest",
        "result",
        "graph",
        "validation",
        "receipt_hash",
    }
    missing = sorted(required - set(receipt))
    unsigned = dict(receipt)
    actual_hash = unsigned.pop("receipt_hash", None)
    expected_hash = sha256_text(canonical_json(unsigned))
    return {
        "valid": not missing and actual_hash == expected_hash,
        "missing_fields": missing,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
    }


def verify_receipt_directory(directory: Path) -> dict[str, Any]:
    files = sorted(directory.glob("*.json")) if directory.exists() else []
    entries: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen_hashes: dict[str, str] = {}
    seen_events: dict[tuple[str, str, str], str] = {}
    runtime_ids: set[str] = set()
    previous_timestamp: str | None = None

    for path in files:
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"path": str(path), "code": "unreadable_receipt", "detail": str(exc)})
            continue

        verification = verify_receipt(receipt)
        if not verification["valid"]:
            errors.append({"path": str(path), "code": "invalid_receipt", "detail": json.dumps(verification, sort_keys=True)})
            continue

        timestamp = str(receipt["timestamp"])
        runtime_id = str(receipt["runtime"].get("runtime_id", "unresolved"))
        ingest_id = str(receipt["manifest"].get("ingest_id", "unresolved"))
        source_commit = str(receipt.get("source_commit", "unresolved"))
        receipt_hash = str(receipt["receipt_hash"])
        event_key = (runtime_id, ingest_id, timestamp)

        if receipt_hash in seen_hashes:
            errors.append({"path": str(path), "code": "duplicate_receipt_hash", "detail": seen_hashes[receipt_hash]})
        else:
            seen_hashes[receipt_hash] = str(path)

        if event_key in seen_events:
            errors.append({"path": str(path), "code": "duplicate_runtime_event", "detail": seen_events[event_key]})
        else:
            seen_events[event_key] = str(path)

        if previous_timestamp is not None and timestamp < previous_timestamp:
            errors.append({"path": str(path), "code": "nonmonotonic_timestamp", "detail": f"{timestamp} precedes {previous_timestamp}"})
        previous_timestamp = timestamp
        runtime_ids.add(runtime_id)
        entries.append(
            {
                "path": str(path),
                "timestamp": timestamp,
                "runtime_id": runtime_id,
                "source_commit": source_commit,
                "ingest_id": ingest_id,
                "receipt_hash": receipt_hash,
                "result_status": receipt["result"].get("status"),
            }
        )

    if len(runtime_ids) > 1:
        errors.append({"path": str(directory), "code": "mixed_runtime_ids", "detail": ",".join(sorted(runtime_ids))})

    return {
        "status": "valid" if files and not errors else "invalid",
        "directory": str(directory),
        "receipt_count": len(files),
        "verified_count": len(entries),
        "runtime_ids": sorted(runtime_ids),
        "entries": entries,
        "errors": errors,
    }


def write_receipt(receipt: Mapping[str, Any], directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    ingest_slug = str(receipt["manifest"]["ingest_id"]).replace(":", "_").replace("/", "_")
    timestamp_slug = str(receipt["timestamp"]).replace(":", "-")
    path = directory / f"{timestamp_slug}__{ingest_slug}.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path
