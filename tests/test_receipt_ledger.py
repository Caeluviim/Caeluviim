from __future__ import annotations

import json
from pathlib import Path

from caeluviim_graph.receipts import build_ingestion_receipt, verify_receipt_directory, write_receipt


def _receipt(root: Path, *, ingest_id: str, timestamp: str, runtime_id: str = "runtime-a") -> dict:
    manifest = {
        "ingest_id": ingest_id,
        "source": {"source_id": f"source:{ingest_id}", "content_hash": "sha256:source"},
    }
    return build_ingestion_receipt(
        root=root,
        runtime={
            "runtime_id": runtime_id,
            "runtime_kind": "neo4j",
            "database": "caeluviim",
            "server_address": "neo4j://localhost:7687",
            "host": "test-host",
            "platform": "test",
            "python": "3",
        },
        manifest_path=f"ingest/manifests/{ingest_id}.json",
        manifest=manifest,
        ingestion_result={
            "status": "created",
            "manifest_hash": f"sha256:{ingest_id}",
            "nodes": 1,
            "relationships": 1,
        },
        validation_result={"status": "valid", "ingest_id": ingest_id},
        graph_before={"nodes": 0, "relationships": 0},
        graph_after={"nodes": 1, "relationships": 1},
        timestamp=timestamp,
    )


def test_receipt_directory_accepts_ordered_single_runtime_ledger(tmp_path: Path) -> None:
    write_receipt(_receipt(tmp_path, ingest_id="a", timestamp="2026-08-05T01:00:00Z"), tmp_path)
    write_receipt(_receipt(tmp_path, ingest_id="b", timestamp="2026-08-05T01:01:00Z"), tmp_path)

    result = verify_receipt_directory(tmp_path)

    assert result["status"] == "valid"
    assert result["receipt_count"] == 2
    assert result["verified_count"] == 2
    assert result["runtime_ids"] == ["runtime-a"]
    assert result["errors"] == []


def test_receipt_directory_fails_on_tampering(tmp_path: Path) -> None:
    path = write_receipt(_receipt(tmp_path, ingest_id="a", timestamp="2026-08-05T01:00:00Z"), tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["result"]["nodes_reported"] = 999
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = verify_receipt_directory(tmp_path)

    assert result["status"] == "invalid"
    assert any(error["code"] == "invalid_receipt" for error in result["errors"])


def test_receipt_directory_fails_on_duplicate_hash(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path, ingest_id="a", timestamp="2026-08-05T01:00:00Z")
    first = write_receipt(receipt, tmp_path)
    (tmp_path / "copy.json").write_text(first.read_text(encoding="utf-8"), encoding="utf-8")

    result = verify_receipt_directory(tmp_path)

    assert result["status"] == "invalid"
    assert any(error["code"] == "duplicate_receipt_hash" for error in result["errors"])


def test_receipt_directory_fails_on_mixed_runtime_ids(tmp_path: Path) -> None:
    write_receipt(_receipt(tmp_path, ingest_id="a", timestamp="2026-08-05T01:00:00Z"), tmp_path)
    write_receipt(
        _receipt(tmp_path, ingest_id="b", timestamp="2026-08-05T01:01:00Z", runtime_id="runtime-b"),
        tmp_path,
    )

    result = verify_receipt_directory(tmp_path)

    assert result["status"] == "invalid"
    assert any(error["code"] == "mixed_runtime_ids" for error in result["errors"])


def test_receipt_directory_fails_closed_when_empty(tmp_path: Path) -> None:
    result = verify_receipt_directory(tmp_path)

    assert result["status"] == "invalid"
    assert result["receipt_count"] == 0
