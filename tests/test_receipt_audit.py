from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caeluviim_graph.receipt_audit import audit_receipts
from caeluviim_graph.receipts import build_ingestion_receipt, canonical_json, sha256_text


class ReceiptAuditTests(unittest.TestCase):
    def receipt(self) -> dict:
        return build_ingestion_receipt(
            root=Path("."),
            runtime={"runtime_id": "runtime:test", "runtime_kind": "neo4j", "database": "caeluviim"},
            manifest_path="ingest/manifests/test.json",
            manifest={"ingest_id": "ingest:test", "source": {"source_id": "source:test", "content_hash": "sha256:source"}},
            ingestion_result={"status": "ingested", "manifest_hash": "sha256:manifest", "nodes": 2, "relationships": 1},
            validation_result={"status": "valid"},
            graph_before={"nodes": 3, "relationships": 2},
            graph_after={"nodes": 5, "relationships": 3},
            timestamp="2026-08-05T06:00:00Z",
        )

    def catalog(self, manifest_hash: str = "sha256:manifest") -> dict:
        return {"status": "valid", "manifests": [{"ingest_id": "ingest:test", "manifest_hash": manifest_hash}]}

    def write(self, directory: Path, name: str, value: dict) -> None:
        (directory / name).write_text(json.dumps(value), encoding="utf-8")

    def test_valid_catalog_bound_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.write(directory, "receipt.json", self.receipt())
            result = audit_receipts(directory, catalog=self.catalog())
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["receipts"][0]["node_delta"], 2)

    def test_tampering_and_duplicates_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            receipt = self.receipt()
            self.write(directory, "one.json", receipt)
            self.write(directory, "two.json", receipt)
            result = audit_receipts(directory, catalog=self.catalog())
            self.assertEqual(result["status"], "invalid")
            self.assertEqual(result["duplicate_receipt_hashes"], [receipt["receipt_hash"]])
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            receipt = self.receipt()
            receipt["graph"]["after"]["nodes"] = 999
            self.write(directory, "tampered.json", receipt)
            self.assertEqual(audit_receipts(directory, catalog=self.catalog())["status"], "invalid")

    def test_unresolved_provenance_and_catalog_mismatch_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            receipt = self.receipt()
            receipt.pop("receipt_hash")
            receipt["source_commit"] = "unresolved"
            receipt["receipt_hash"] = sha256_text(canonical_json(receipt))
            self.write(directory, "unresolved.json", receipt)
            self.assertEqual(audit_receipts(directory, catalog=self.catalog())["status"], "invalid")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.write(directory, "receipt.json", self.receipt())
            result = audit_receipts(directory, catalog=self.catalog("sha256:different"))
            self.assertEqual(result["status"], "invalid")
            self.assertIn("manifest hash mismatch", result["errors"][0]["error"])


if __name__ == "__main__":
    unittest.main()
