from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caeluviim_graph.receipts import (
    build_ingestion_receipt,
    verify_receipt,
    write_receipt,
)


class RuntimeReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = {
            "ingest_id": "urn:caeluviim:ingest:test",
            "source": {
                "source_id": "urn:caeluviim:source:test",
                "content_hash": "sha256:source",
            },
        }
        self.ingestion = {
            "status": "ingested",
            "manifest_hash": "sha256:manifest",
            "nodes": 2,
            "relationships": 1,
        }

    @patch("caeluviim_graph.receipts.resolve_source_commit", return_value="abc123")
    def test_receipt_contains_required_provenance_and_valid_hash(self, _mock_commit) -> None:
        receipt = build_ingestion_receipt(
            root=Path("."),
            runtime={"runtime_id": "test-runtime", "database": "neo4j"},
            manifest_path="ingest/manifests/test.json",
            manifest=self.manifest,
            ingestion_result=self.ingestion,
            validation_result={"status": "valid"},
            graph_before={"entities": 10, "relationships": 20},
            graph_after={"entities": 14, "relationships": 23},
            timestamp="2026-08-05T00:00:00Z",
        )
        self.assertEqual(receipt["source_commit"], "abc123")
        self.assertEqual(receipt["graph"]["delta"]["entities"], 4)
        self.assertEqual(receipt["graph"]["delta"]["relationships"], 3)
        self.assertTrue(verify_receipt(receipt)["valid"])

    @patch("caeluviim_graph.receipts.resolve_source_commit", return_value="abc123")
    def test_tampering_invalidates_receipt(self, _mock_commit) -> None:
        receipt = build_ingestion_receipt(
            root=Path("."),
            runtime={"runtime_id": "test-runtime", "database": "neo4j"},
            manifest_path="test.json",
            manifest=self.manifest,
            ingestion_result=self.ingestion,
            validation_result={"status": "valid"},
            graph_before={"entities": 0},
            graph_after={"entities": 2},
            timestamp="2026-08-05T00:00:00Z",
        )
        receipt["result"]["nodes_reported"] = 999
        self.assertFalse(verify_receipt(receipt)["valid"])

    @patch("caeluviim_graph.receipts.resolve_source_commit", return_value="abc123")
    def test_receipt_write_is_verifiable(self, _mock_commit) -> None:
        receipt = build_ingestion_receipt(
            root=Path("."),
            runtime={"runtime_id": "test-runtime", "database": "neo4j"},
            manifest_path="test.json",
            manifest=self.manifest,
            ingestion_result=self.ingestion,
            validation_result={"status": "valid"},
            graph_before={"entities": 0},
            graph_after={"entities": 2},
            timestamp="2026-08-05T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = write_receipt(receipt, Path(directory))
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(verify_receipt(loaded)["valid"])


if __name__ == "__main__":
    unittest.main()
