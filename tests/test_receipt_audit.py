from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caeluviim_graph.receipt_audit import audit_receipts
from caeluviim_graph.receipts import build_ingestion_receipt


class ReceiptAuditTests(unittest.TestCase):
    def _receipt(self, *, ingest_id: str = "ingest:test", manifest_hash: str = "sha256:manifest") -> dict:
        return build_ingestion_receipt(
            root=Path("."),
            runtime={
                "runtime_id": "runtime:test",
                "runtime_kind": "neo4j",
                "database": "caeluviim",
                "server_address": "bolt://test",
                "host": "test",
                "platform": "test",
                "python": "3",
            },
            manifest_path="ingest/manifests/test.json",
            manifest={
                "ingest_id": ingest_id,
                "source": {"source_id": "source:test", "content_hash": "sha256:source"},
            },
            ingestion_result={
                "status": "ingested",
                "manifest_hash": manifest_hash,
                "nodes": 2,
                "relationships": 1,
            },
            validation_result={"status": "valid"},
            graph_before={"nodes": 3, "relationships": 2},
            graph_after={"nodes": 5, "relationships": 3},
            timestamp="2026-08-05T06:00:00Z",
        )

    def _catalog(self, *, manifest_hash: str = "sha256:manifest") -> dict:
        return {
            "status": "valid",
            "manifests": [
                {"ingest_id": "ingest:test", "manifest_hash": manifest_hash}
            ],
        }

    def _write(self, directory: Path, name: str, value: dict) -> None:
        (directory / name).write_text(json.dumps(value), encoding="utf-8")

    def test_valid_catalog_bound_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self._write(directory, "receipt.json", self._receipt())
            result = audit_receipts(directory, catalog=self._catalog())
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["receipt_count"], 1)
            self.assertTrue(result["catalog_bound"])
            self.assertEqual(result["receipts"][0]["node_delta"], 2)

    def test_tampered_receipt_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            receipt = self._receipt()
            receipt["graph"]["after"]["nodes"] = 999
            self._write(directory, "tampered.json", receipt)
            result = audit_receipts(directory, catalog=self._catalog())
            self.assertEqual(result["status"], "invalid")
            self.assertIn("verification failed", result["errors"][0]["error"])

    def test_duplicate_receipt_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            receipt = self._receipt()
            self._write(directory, "one.json", receipt)
            self._write(directory, "two.json", receipt)
            result = audit_receipts(directory, catalog=self._catalog())
            self.assertEqual(result["status"], "invalid")
            self.assertEqual(result["duplicate_receipt_hashes"], [receipt["receipt_hash"]])
            self.assertEqual(len(result["duplicate_runtime_events"]), 1)

    def test_unresolved_source_commit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            receipt = self._receipt()
            unsigned = dict(receipt)
            unsigned.pop("receipt_hash")
            unsigned["source_commit"] = "unresolved"
            from caeluviim_graph.receipts import canonical_json, sha256_text
            unsigned["receipt_hash"] = sha256_text(canonical_json(unsigned))
            self._write(directory, "unresolved.json", unsigned)
            result = audit_receipts(directory, catalog=self._catalog())
            self.assertEqual(result["status"], "invalid")
            self.assertIn("source_commit is unresolved", result["errors"][0]["error"])

    def test_catalog_manifest_hash_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self._write(directory, "receipt.json", self._receipt())
            result = audit_receipts(
                directory, catalog=self._catalog(manifest_hash="sha256:different")
            )
            self.assertEqual(result["status"], "invalid")
            self.assertIn("manifest hash mismatch", result["errors"][0]["error"])


if __name__ == "__main__":
    unittest.main()
