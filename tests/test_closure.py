import unittest
from pathlib import Path

from caeluviim_graph.closure import ClosureCheckError, check_claim_closure
from caeluviim_graph.manifest import load_manifest, load_schema, validate_manifest

ROOT = Path(__file__).resolve().parents[1]


def sample_manifest():
    claim_id = "urn:caeluviim:test:claim:root"
    antecedent_id = "urn:caeluviim:test:claim:antecedent"
    dependent_id = "urn:caeluviim:test:claim:dependent"
    evidence_id = "urn:caeluviim:test:evidence:one"
    return {
        "manifest_version": "0.1.0",
        "ingest_id": "urn:caeluviim:test:ingest:closure",
        "source": {
            "source_id": "urn:caeluviim:test:source:closure",
            "source_type": "document",
            "title": "Closure test source",
            "content_hash": "sha256:" + "0" * 64,
            "captured_at": "2026-08-03T01:28:00Z",
            "authority": "test fixture",
        },
        "nodes": [
            {
                "id": claim_id,
                "labels": ["Claim"],
                "properties": {
                    "required_relation_types": ["DEPENDS_ON", "EVIDENCED_BY"],
                    "required_target_ids": [antecedent_id],
                    "minimum_evidence_count": 1,
                    "require_provenance": True,
                },
            },
            {
                "id": antecedent_id,
                "labels": ["Claim"],
                "properties": {},
            },
            {
                "id": dependent_id,
                "labels": ["Claim"],
                "properties": {},
            },
            {
                "id": evidence_id,
                "labels": ["Evidence"],
                "properties": {},
            },
        ],
        "relationships": [
            {
                "id": "urn:caeluviim:test:relation:depends",
                "type": "DEPENDS_ON",
                "from": claim_id,
                "to": antecedent_id,
                "properties": {},
            },
            {
                "id": "urn:caeluviim:test:relation:evidence",
                "type": "EVIDENCED_BY",
                "from": claim_id,
                "to": evidence_id,
                "properties": {},
            },
            {
                "id": "urn:caeluviim:test:relation:dependent",
                "type": "DEPENDS_ON",
                "from": dependent_id,
                "to": claim_id,
                "properties": {},
            },
        ],
    }


class TestClosureChecker(unittest.TestCase):
    def test_complete_closure_reports_backnest_and_forward_dependents(self):
        result = check_claim_closure(
            sample_manifest(), "urn:caeluviim:test:claim:root"
        )
        self.assertTrue(result["closure_complete"])
        self.assertIn(
            "urn:caeluviim:test:claim:antecedent", result["backnest"]
        )
        self.assertIn(
            "urn:caeluviim:test:evidence:one", result["backnest"]
        )
        self.assertIn(
            "urn:caeluviim:test:claim:dependent", result["forwardnest"]
        )
        self.assertFalse(result["truth_assessed"])
        self.assertFalse(result["ratification_assessed"])

    def test_missing_evidence_is_reported_without_truth_claim(self):
        manifest = sample_manifest()
        manifest["relationships"] = [
            relationship
            for relationship in manifest["relationships"]
            if relationship["type"] != "EVIDENCED_BY"
        ]
        result = check_claim_closure(
            manifest, "urn:caeluviim:test:claim:root"
        )
        self.assertFalse(result["closure_complete"])
        self.assertEqual(["EVIDENCED_BY"], result["missing_relation_types"])
        self.assertFalse(result["evidence_requirement_met"])
        self.assertFalse(result["truth_assessed"])

    def test_missing_required_target_is_reported(self):
        manifest = sample_manifest()
        manifest["nodes"][0]["properties"]["required_target_ids"] = [
            "urn:caeluviim:test:claim:not-reachable"
        ]
        result = check_claim_closure(
            manifest, "urn:caeluviim:test:claim:root"
        )
        self.assertEqual(
            ["urn:caeluviim:test:claim:not-reachable"],
            result["missing_target_ids"],
        )

    def test_non_claim_entity_is_rejected(self):
        with self.assertRaises(ClosureCheckError):
            check_claim_closure(
                sample_manifest(), "urn:caeluviim:test:evidence:one"
            )

    def test_kernel_manifest_decodes_conforms_and_master_thesis_closes(self):
        schema = load_schema(ROOT / "schemas" / "ingest-manifest.schema.json")
        manifest = validate_manifest(
            load_manifest(
                ROOT
                / "ingest"
                / "manifests"
                / "lux-kernel-core-v0.1.0.json.gz.b64"
            ),
            schema,
        )
        self.assertEqual(145, len(manifest["nodes"]))
        self.assertEqual(293, len(manifest["relationships"]))
        result = check_claim_closure(
            manifest, "urn:caeluviim:kernel:principle:master-thesis"
        )
        self.assertTrue(result["closure_complete"])
        self.assertGreaterEqual(result["closure_count"], 7)
        self.assertFalse(result["truth_assessed"])
        self.assertFalse(result["ratification_assessed"])


if __name__ == "__main__":
    unittest.main()
