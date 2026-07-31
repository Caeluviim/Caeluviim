from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from caeluviim.batch_ingest import IngestionBatch, ingest_batch
from caeluviim.projection import GraphProjector
from caeluviim.service import CaeluviimCore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class IngestionBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.core = CaeluviimCore(Path(self.temporary.name), PROJECT_ROOT)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def manifest() -> IngestionBatch:
        return IngestionBatch.model_validate(
            {
                "batch_id": "batch:activation-test:0.1",
                "title": "Graph activation fixture",
                "scope": "official_public",
                "consent_basis": "Explicit deterministic test fixture.",
                "started_at": "2026-07-31T12:00:00Z",
                "sources": [
                    {
                        "source_id": "source:activation-test:1",
                        "participant_id": "member:founder",
                        "content": "A source artifact supports an explicit graph mapping.",
                        "language": "en",
                    }
                ],
                "mappings": [
                    {
                        "mapping_id": "mapping:activation-test:1",
                        "source_id": "source:activation-test:1",
                        "candidate_type": "proposition",
                        "label": "Activation mapping",
                        "content": "The source artifact is represented by a reviewed proposition.",
                        "alternative_hypotheses": [
                            "The source may require a narrower mapping."
                        ],
                        "confidence": "0.90",
                        "review": {
                            "decision": "accept",
                            "reviewer_id": "member:founder",
                            "reason": "Accepted as a deterministic activation fixture.",
                        },
                    }
                ],
            }
        )

    def test_batch_creates_replayable_activation_and_projected_mapping(self) -> None:
        first = ingest_batch(self.core, self.manifest())
        event_count = len(self.core.ledger.events())
        second = ingest_batch(self.core, self.manifest())

        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(first["activation_event_id"], second["activation_event_id"])
        self.assertEqual(len(self.core.ledger.events()), event_count)
        self.assertEqual(first["accepted_mapping_count"], 1)
        self.assertEqual(first["quarantined_mapping_count"], 0)
        self.assertTrue(first["projection"]["shacl_conforms"])
        self.assertGreater(first["projection"]["triple_count"], 0)

        receipt = self.core.store.get_json(first["receipt_object_id"])
        candidate_id = receipt["mapping_results"][0]["candidate_id"]
        dataset = GraphProjector(self.core).build_dataset()
        serialized = dataset.serialize(format="trig")
        self.assertIn(candidate_id, serialized)
        self.assertIn("INGESTION_BATCH_ACTIVATE", serialized)

    def test_batch_reviewer_must_match_signing_identity(self) -> None:
        payload = self.manifest().model_dump(mode="json")
        payload["mappings"][0]["review"]["reviewer_id"] = "member:other"
        with self.assertRaises(ValidationError):
            IngestionBatch.model_validate(payload)

    def test_unreviewed_mapping_remains_quarantined(self) -> None:
        payload = self.manifest().model_dump(mode="json")
        payload["batch_id"] = "batch:activation-test:quarantine"
        payload["mappings"][0]["mapping_id"] = "mapping:activation-test:quarantine"
        payload["mappings"][0]["review"] = None
        result = ingest_batch(self.core, IngestionBatch.model_validate(payload))

        self.assertEqual(result["accepted_mapping_count"], 0)
        self.assertEqual(result["quarantined_mapping_count"], 1)
        self.assertEqual(len(self.core.list_quarantined()), 1)


if __name__ == "__main__":
    unittest.main()
