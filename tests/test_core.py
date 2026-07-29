from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caeluviim.governance import GovernanceService
from caeluviim.ledger import LedgerIntegrityError
from caeluviim.models import (
    AnalysisCandidate,
    CandidateBatch,
    CandidateReview,
    DialogueIngestRequest,
    DialogueTurn,
    DisclosureRestriction,
    InformationScope,
    Reproducibility,
    ReviewDecision,
)
from caeluviim.projection import GraphProjector
from caeluviim.service import CaeluviimCore
from caeluviim.store import ObjectAccessError
from caeluviim.validator import validate_core, validate_dap_compatibility


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEMBER_ID = "member:test"


class CaeluviimCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temporary.name)
        self.core = CaeluviimCore(self.state_dir, PROJECT_ROOT)
        self.core.initialize()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def ingest_private_dialogue(self) -> dict:
        return self.core.ingest_dialogue(
            DialogueIngestRequest(
                conversation_id="conversation:test-private",
                title="Private integration fixture",
                scope=InformationScope.PRIVATE,
                owner_id=MEMBER_ID,
                consent_basis="Explicit test-fixture instruction.",
                turns=[
                    DialogueTurn(
                        turn_id="turn:1",
                        participant_id=MEMBER_ID,
                        role="user",
                        content="A private source statement.",
                        language="en",
                    ),
                    DialogueTurn(
                        turn_id="turn:2",
                        participant_id="person:lux",
                        role="assistant",
                        content="A response that remains source content.",
                        language="en",
                    ),
                ],
            )
        )

    @staticmethod
    def candidate_for(result: dict) -> AnalysisCandidate:
        first_turn = result["turns"][0]
        first_span = result["spans"][0]
        return AnalysisCandidate(
            candidate_type="interpretation",
            label="Candidate pragmatic interpretation",
            content="The expression may function as a request.",
            source_span_ids=[first_span["span_id"]],
            evidence_ids=[first_turn["source_object_id"]],
            alternative_hypotheses=["It may instead be descriptive."],
            confidence=0.65,
            agent_id="person:lux",
            manifestation_id=GovernanceService.DEFAULT_MANIFESTATION_ID,
            model_id="fixture:model",
            prompt_version="fixture:prompt-v1",
            rule_version="fixture:rule-v1",
            ontology_version="caeluviim-core/0.1",
            reproducibility=Reproducibility.DETERMINISTIC,
            construction_rule="Constructed from the exact cited source span.",
        )

    def stage(self, result: dict, candidate: AnalysisCandidate) -> dict:
        return self.core.stage_candidates(
            CandidateBatch(
                conversation_event_id=result["conversation_event_id"],
                scope=InformationScope.PRIVATE,
                owner_id=MEMBER_ID,
                candidates=[candidate],
            )
        )

    def test_initialization_and_validation(self) -> None:
        initial_event_count = len(self.core.ledger.events())
        self.core.initialize()
        self.assertEqual(len(self.core.ledger.events()), initial_event_count)
        report = validate_core(self.core)
        self.assertTrue(report["conforms"], json.dumps(report, indent=2))
        self.assertTrue(report["shacl"]["conforms"])
        self.assertTrue(report["vocabularies"]["conforms"])
        self.assertGreaterEqual(report["ledger"]["accepted_event_count"], 5)

    def test_idempotency_key_cannot_change_meaning(self) -> None:
        existing = self.core.ledger.events()[0]
        replacement = self.core.store.put_json(
            {"different": True},
            scope=InformationScope.OFFICIAL_PUBLIC,
        )
        with self.assertRaises(LedgerIntegrityError):
            self.core.ledger.submit(
                event_type=existing["event_type"],
                signer=self.core.governance.founder_signer(),
                scope=InformationScope(existing["scope"]),
                payload_ref=replacement["object_id"],
                idempotency_key=existing["idempotency_key"],
                disposition="ACCEPTED_EFFECTIVE",
            )

    def test_private_content_is_encrypted_and_partitioned(self) -> None:
        result = self.ingest_private_dialogue()
        source_id = result["turns"][0]["source_object_id"]
        metadata = self.core.store.metadata(source_id, owner_id=MEMBER_ID)
        blob_path, _ = self.core.store._paths(source_id)

        self.assertTrue(metadata["encrypted"])
        self.assertNotIn(b"A private source statement.", blob_path.read_bytes())
        self.assertEqual(
            self.core.store.get_bytes(source_id, owner_id=MEMBER_ID).decode(),
            "A private source statement.",
        )
        with self.assertRaises(ObjectAccessError):
            self.core.store.get_bytes(source_id)

        public_graph = GraphProjector(self.core).build_dataset()
        self.assertNotIn("A private source statement.", public_graph.serialize(format="trig"))
        member_graph = GraphProjector(self.core).build_dataset(owner_id=MEMBER_ID)
        self.assertIn("A private source statement.", member_graph.serialize(format="trig"))

    def test_candidates_remain_quarantined_until_review(self) -> None:
        result = self.ingest_private_dialogue()
        staged = self.stage(result, self.candidate_for(result))
        stage_event = staged["candidates"][0]["event"]
        candidate_id = stage_event["metadata"]["candidate_id"]

        graph_before = GraphProjector(self.core).build_dataset(owner_id=MEMBER_ID)
        self.assertNotIn(candidate_id, graph_before.serialize(format="trig"))
        self.assertEqual(len(self.core.list_quarantined(owner_id=MEMBER_ID)), 1)

        reviewed = self.core.review_candidate(
            CandidateReview(
                candidate_event_id=stage_event["event_id"],
                decision=ReviewDecision.ACCEPT,
                reviewer_id=MEMBER_ID,
                reason="Accepted in a deterministic integration test.",
            ),
            owner_id=MEMBER_ID,
        )
        self.assertEqual(reviewed["event"]["metadata"]["decision"], "accept")
        self.assertFalse(self.core.list_quarantined(owner_id=MEMBER_ID))

        graph_after = GraphProjector(self.core).build_dataset(owner_id=MEMBER_ID)
        self.assertIn(candidate_id, graph_after.serialize(format="trig"))
        shacl = GraphProjector(self.core).validate_shacl(owner_id=MEMBER_ID)
        self.assertTrue(shacl["conforms"], shacl["report_text"])

    def test_trace_reaches_source_and_review(self) -> None:
        result = self.ingest_private_dialogue()
        staged = self.stage(result, self.candidate_for(result))
        stage_event = staged["candidates"][0]["event"]
        candidate_id = stage_event["metadata"]["candidate_id"]
        self.core.review_candidate(
            CandidateReview(
                candidate_event_id=stage_event["event_id"],
                decision=ReviewDecision.CONTEST,
                reviewer_id=MEMBER_ID,
                reason="The alternative interpretation remains plausible.",
            ),
            owner_id=MEMBER_ID,
        )

        trace = self.core.trace(candidate_id, owner_id=MEMBER_ID)
        event_types = {entry["event_type"] for entry in trace["events"]}
        self.assertIn("ANALYSIS_CANDIDATE_STAGE", event_types)
        self.assertIn("CANDIDATE_REVIEW", event_types)
        self.assertTrue(trace["objects"])

    def test_crypto_shred_removes_access_but_preserves_tombstone(self) -> None:
        result = self.ingest_private_dialogue()
        source_id = result["turns"][0]["source_object_id"]
        response = self.core.crypto_shred_member(MEMBER_ID, "Explicit fixture request.")

        self.assertTrue(response["key_destroyed"])
        self.assertEqual(response["event"]["event"]["event_type"], "MEMBER_CONTENT_CRYPTO_SHRED")
        with self.assertRaises(ObjectAccessError):
            self.core.store.get_bytes(source_id, owner_id=MEMBER_ID)
        self.core.ledger.verify()

    def test_disclosure_restriction_is_signed(self) -> None:
        event = self.core.governance.record_restriction(
            DisclosureRestriction(
                restriction_id="restriction:test",
                record_ids=["urn:caeluviim:object:sha256:" + "0" * 64],
                basis="personal_privacy",
                authority_id=GovernanceService.FOUNDER_ID,
                scope="The specified record only.",
                redaction_rule="Withhold exact text while preserving a public restriction record.",
                begins_at="2026-01-01T00:00:00Z",
                review_or_expires_at="2027-01-01T00:00:00Z",
                contest_path="Submit a signed contest event to the civic ledger.",
            )
        )
        self.assertEqual(event["event"]["event_type"], "DISCLOSURE_RESTRICTION_CREATE")
        self.core.ledger.verify()

    def test_tampering_breaks_append_only_log_verification(self) -> None:
        log_path = self.state_dir / "ledger" / "submissions.jsonl"
        lines = log_path.read_text(encoding="utf-8").splitlines()
        wrapper = json.loads(lines[0])
        wrapper["entry"]["metadata"]["tampered"] = True
        lines[0] = json.dumps(wrapper, sort_keys=True, separators=(",", ":"))
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with self.assertRaises(LedgerIntegrityError):
            self.core.ledger.verify()


class DapCompatibilityTests(unittest.TestCase):
    def test_python_fixtures_and_typescript_oracle(self) -> None:
        report = validate_dap_compatibility(PROJECT_ROOT)
        self.assertTrue(report["python_conforms"], json.dumps(report, indent=2))
        self.assertTrue(report["typescript_oracle_conforms"], json.dumps(report, indent=2))


if __name__ == "__main__":
    unittest.main()
