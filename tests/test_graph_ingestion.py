import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from caeluviim_graph.client import read_cypher_statements
from caeluviim_graph.manifest import (
    ManifestValidationError,
    canonical_json,
    load_manifest,
    load_schema,
    safe_label_clause,
    safe_relationship_type,
    sha256_record,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


class TestGraphManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema(ROOT / "schemas" / "ingest-manifest.schema.json")
        cls.manifest = load_manifest(ROOT / "examples" / "ingest-manifest.valid.json")

    def test_seed_manifest_conforms(self):
        result = validate_manifest(self.manifest, self.schema)
        self.assertEqual("urn:caeluviim:ingest:bootstrap-001", result["ingest_id"])

    def test_integer_properties_conform(self):
        manifest = deepcopy(self.manifest)
        manifest["nodes"][0]["properties"]["sequence"] = 1
        validate_manifest(manifest, self.schema)

    def test_hashing_is_deterministic(self):
        left = {"b": 2, "a": [1, 3]}
        right = {"a": [1, 3], "b": 2}
        self.assertEqual(canonical_json(left), canonical_json(right))
        self.assertEqual(sha256_record(left), sha256_record(right))

    def test_dangling_relationship_is_rejected(self):
        manifest = deepcopy(self.manifest)
        manifest["relationships"][0]["to"] = "urn:caeluviim:missing"
        with self.assertRaises(ManifestValidationError) as context:
            validate_manifest(manifest, self.schema)
        self.assertIn("references missing to node", str(context.exception))

    def test_identifier_collision_is_rejected(self):
        manifest = deepcopy(self.manifest)
        manifest["relationships"][0]["id"] = manifest["nodes"][0]["id"]
        with self.assertRaises(ManifestValidationError) as context:
            validate_manifest(manifest, self.schema)
        self.assertIn("duplicate entity identifiers", str(context.exception))

    def test_reserved_properties_are_rejected(self):
        manifest = deepcopy(self.manifest)
        manifest["nodes"][0]["properties"]["record_hash"] = "forbidden"
        with self.assertRaises(ManifestValidationError) as context:
            validate_manifest(manifest, self.schema)
        self.assertIn("uses reserved properties", str(context.exception))

    def test_dynamic_identifiers_are_allowlisted(self):
        self.assertEqual("Entity:Claim:Evidence", safe_label_clause(["Claim", "Evidence"]))
        self.assertEqual("SUPPORTS", safe_relationship_type("SUPPORTS"))
        with self.assertRaises(ValueError):
            safe_relationship_type("SUPPORTS`) MATCH (n) DETACH DELETE n //")


class TestMigrations(unittest.TestCase):
    def test_core_migration_is_split_and_contains_constraint(self):
        statements = read_cypher_statements(ROOT / "graph" / "migrations" / "001_core.cypher")
        self.assertGreaterEqual(len(statements), 8)
        self.assertTrue(any("entity_id_unique" in statement for statement in statements))
        self.assertTrue(all(not statement.startswith("//") for statement in statements))

    def test_block_comments_are_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.cypher"
            path.write_text(
                "/* ignore; this */ CREATE INDEX x IF NOT EXISTS FOR (n:X) ON (n.id);",
                encoding="utf-8",
            )
            self.assertEqual(1, len(read_cypher_statements(path)))


if __name__ == "__main__":
    unittest.main()
