from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caeluviim_graph.catalog import build_catalog

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "ingest-manifest.schema.json"


def manifest(ingest_id: str, node_id: str, relationship: dict | None = None) -> dict:
    return {
        "manifest_version": "0.1.0",
        "ingest_id": ingest_id,
        "source": {
            "source_id": ingest_id + "/source",
            "source_type": "document",
            "title": "Catalog test",
            "content_hash": "sha256:" + "0" * 64,
            "captured_at": "2026-08-04T00:00:00Z",
        },
        "nodes": [{"id": node_id, "labels": ["Claim"], "properties": {"name": "test"}}],
        "relationships": [] if relationship is None else [relationship],
    }


class GraphCatalogTests(unittest.TestCase):
    def test_valid_catalog_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "one.json").write_text(json.dumps(manifest("urn:test:ingest:1", "urn:test:node:1")), encoding="utf-8")
            first = build_catalog(directory, SCHEMA)
            second = build_catalog(directory, SCHEMA)
            self.assertEqual(first, second)
            self.assertEqual(first["status"], "valid")
            self.assertEqual(first["node_count"], 1)
            self.assertTrue(first["catalog_hash"].startswith("sha256:"))

    def test_duplicate_node_and_dangling_endpoint_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "one.json").write_text(json.dumps(manifest("urn:test:ingest:1", "urn:test:node:1")), encoding="utf-8")
            rel = {
                "id": "urn:test:rel:1",
                "type": "SUPPORTS",
                "from": "urn:test:node:1",
                "to": "urn:test:node:missing",
                "properties": {},
            }
            (directory / "two.json").write_text(json.dumps(manifest("urn:test:ingest:2", "urn:test:node:1", rel)), encoding="utf-8")
            result = build_catalog(directory, SCHEMA)
            self.assertEqual(result["status"], "invalid")
            self.assertEqual(result["duplicate_node_ids"], ["urn:test:node:1"])
            self.assertEqual(result["dangling_relationship_endpoints"][0]["node_id"], "urn:test:node:missing")


if __name__ == "__main__":
    unittest.main()
