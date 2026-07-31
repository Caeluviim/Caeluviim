import unittest
from pathlib import Path

from caeluviim_graph.manifest import (
    load_manifest,
    load_schema,
    sha256_record,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = load_schema(ROOT / "schemas" / "ingest-manifest.schema.json")


class TestProductionIngestManifests(unittest.TestCase):
    def test_all_production_manifests_conform(self):
        manifests = sorted((ROOT / "ingest" / "manifests").glob("*.json"))
        self.assertGreaterEqual(len(manifests), 1)
        for path in manifests:
            with self.subTest(path=path.name):
                validate_manifest(load_manifest(path), SCHEMA)

    def test_emgn_inventory_hash_matches_manifest_source(self):
        inventory_path = (
            ROOT / "ingest" / "inventories" / "emgn-module.v0.1.0.inventory.json"
        )
        manifest_path = ROOT / "ingest" / "manifests" / "emgn-module.v0.1.0.json"
        inventory = load_manifest(inventory_path)
        manifest = load_manifest(manifest_path)
        self.assertEqual(
            sha256_record(inventory),
            manifest["source"]["content_hash"],
        )


if __name__ == "__main__":
    unittest.main()
