import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate as shacl_validate
from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence_intake import (  # noqa: E402
    GraphCollisionError,
    LocalEvidenceIntakeStore,
    evaluate_manifest,
    released_payload,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)
from evidence_intake.canonical import sha256_json  # noqa: E402

INTAKE = Namespace("https://caeluviim.org/ontology/evidence-intake#")


class TestEvidenceIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = (
            ROOT / "examples/evidence-intake-manifest.valid.json"
        )
        cls.rdf_path = (
            ROOT / "examples/evidence-intake-manifest.valid.ttl"
        )
        cls.assessment_path = (
            ROOT / "examples/evidence-intake-assessment.json"
        )
        cls.manifest_schema_path = (
            ROOT / "schemas/evidence-intake-manifest.schema.json"
        )
        cls.assessment_schema_path = (
            ROOT / "schemas/evidence-intake-assessment.schema.json"
        )
        cls.status_schema_path = (
            ROOT / "schemas/evidence-intake-status.schema.json"
        )
        cls.status_path = (
            ROOT / "governance/evidence-intake-v0.1.0.status.json"
        )
        cls.ontology_path = ROOT / "ontology/evidence-intake.ttl"
        cls.shapes_path = ROOT / "shapes/evidence-intake.shacl.ttl"
        cls.assessment_shapes_path = (
            ROOT / "shapes/evidence-intake-assessment.shacl.ttl"
        )
        cls.quarantine_query_path = (
            ROOT / "queries/evidence-intake-quarantine.rq"
        )
        cls.released_query_path = (
            ROOT / "queries/evidence-intake-released-assertions.rq"
        )
        cls.manifest = json.loads(cls.manifest_path.read_text("utf-8"))
        cls.manifest_schema = json.loads(
            cls.manifest_schema_path.read_text("utf-8")
        )
        cls.assessment_schema = json.loads(
            cls.assessment_schema_path.read_text("utf-8")
        )

    def evaluate(self, manifest=None, project_root=None):
        return evaluate_manifest(
            copy.deepcopy(manifest or self.manifest),
            schema=self.manifest_schema,
            project_root=project_root or ROOT,
        )

    @staticmethod
    def claim_result(assessment, claim_ref):
        return next(
            item
            for item in assessment["claim_results"]
            if item["claim_ref"] == claim_ref
        )

    @staticmethod
    def quarantine_recorded_claim(manifest, claim_index=0):
        claim = manifest["extracted_claims"][claim_index]
        claim["claim_state"] = "quarantined"
        decision = next(
            item
            for item in manifest["release_decisions"]
            if item["claim_ref"] == claim["claim_id"]
        )
        decision["decision"] = "denied"
        return claim["claim_id"]

    def make_store(self, directory):
        return LocalEvidenceIntakeStore(
            Path(directory) / "evidence-intake.trig"
        )

    def ingest(
        self,
        store,
        *,
        manifest_path=None,
        graph_base=None,
    ):
        return store.ingest(
            manifest_path=manifest_path or self.manifest_path,
            rdf_path=self.rdf_path,
            base_graph_uri=(
                graph_base
                or "urn:caeluviim:graph:evidence-intake:test"
            ),
            project_root=ROOT,
            manifest_schema_path=self.manifest_schema_path,
            assessment_schema_path=self.assessment_schema_path,
            shapes_path=self.shapes_path,
            ontology_path=self.ontology_path,
            assessment_shapes_path=self.assessment_shapes_path,
        )

    def test_schemas_are_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(self.manifest_schema)
        Draft202012Validator.check_schema(self.assessment_schema)
        Draft202012Validator.check_schema(
            json.loads(self.status_schema_path.read_text("utf-8"))
        )

    def test_manifest_conforms_to_json_schema(self):
        result = validate_json_document(
            self.manifest,
            self.manifest_schema,
        )
        self.assertTrue(result["conforms"], result["errors"])

    def test_ontology_contains_core_entities_and_all_claim_states(self):
        graph = Graph().parse(self.ontology_path, format="turtle")
        classes = [
            "SourceArtifact",
            "SourceSnapshot",
            "SourceLocator",
            "ExtractedClaim",
            "ClaimSpan",
            "SupportRelation",
            "ContradictionRelation",
            "SourceAuthorityAssessment",
            "EvidenceBundle",
            "UnsupportedClaim",
            "QuarantineRecord",
            "ReleaseDecision",
            "IntakeManifest",
        ]
        for class_name in classes:
            self.assertIn(
                (
                    INTAKE[class_name],
                    RDF.type,
                    URIRef("http://www.w3.org/2002/07/owl#Class"),
                ),
                graph,
                class_name,
            )
        for state in (
            "captured",
            "supported",
            "partially_supported",
            "contradicted",
            "unverifiable",
            "quarantined",
            "released",
        ):
            self.assertIn(
                (INTAKE[state], RDF.type, INTAKE.ClaimState),
                graph,
                state,
            )

    def test_rdf_shacl_and_cross_format_alignment_conform(self):
        rdf_result = validate_rdf_manifest(
            self.rdf_path,
            shapes_path=self.shapes_path,
            ontology_path=self.ontology_path,
        )
        alignment = verify_cross_format_alignment(
            self.manifest,
            self.rdf_path,
        )
        self.assertTrue(rdf_result["conforms"], rdf_result["report_text"])
        self.assertTrue(alignment["conforms"], alignment)

    def test_evaluation_is_deterministic_and_digest_bound(self):
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first, second)
        digest_source = copy.deepcopy(first)
        digest_source.pop("assessment_id")
        digest_source.pop("assessment_digest")
        self.assertEqual(
            first["assessment_digest"],
            sha256_json(digest_source),
        )
        self.assertEqual(
            first["assessment_id"],
            "urn:caeluviim:assessment:evidence-intake:"
            + first["assessment_digest"],
        )

    def test_assessment_conforms_and_matches_committed_result(self):
        assessment = self.evaluate()
        result = validate_json_document(
            assessment,
            self.assessment_schema,
        )
        self.assertTrue(result["conforms"], result["errors"])
        committed = json.loads(self.assessment_path.read_text("utf-8"))
        self.assertEqual(assessment, committed)

    def test_example_releases_one_claim_and_quarantines_compound_claim(self):
        assessment = self.evaluate()
        self.assertEqual("released_with_quarantine", assessment["pipeline_result"])
        self.assertEqual(
            ["urn:caeluviim:claim:intake:rule-replaced"],
            assessment["released_claim_refs"],
        )
        self.assertEqual(
            ["urn:caeluviim:claim:intake:compound-coverage"],
            assessment["quarantined_claim_refs"],
        )
        compound = self.claim_result(
            assessment,
            "urn:caeluviim:claim:intake:compound-coverage",
        )
        self.assertEqual("contradicted", compound["support_state"])
        self.assertIn(
            "PARTIAL_COMPOUND_SUPPORT",
            compound["failure_codes"],
        )
        self.assertIn(
            "UNRESOLVED_CONTRADICTION",
            compound["failure_codes"],
        )

    def test_release_payload_contains_released_claims_only(self):
        assessment = self.evaluate()
        payload = released_payload(self.manifest, assessment)
        serialized = json.dumps(payload, sort_keys=True)
        self.assertIn(
            "urn:caeluviim:claim:intake:rule-replaced",
            serialized,
        )
        self.assertNotIn(
            "urn:caeluviim:claim:intake:compound-coverage",
            serialized,
        )
        self.assertEqual(1, len(payload["released_claims"]))
        self.assertEqual(1, len(payload["eligible_sicrp_assertions"]))

    def test_citation_that_does_not_support_claim_is_quarantined(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["support_relations"][0][
            "support_verdict"
        ] = "does_not_support"
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertEqual("quarantined", result["evaluated_state"])
        self.assertIn(
            "CITATION_DOES_NOT_SUPPORT_CLAIM",
            result["failure_codes"],
        )

    def test_partial_compound_claim_cannot_be_released(self):
        assessment = self.evaluate()
        result = self.claim_result(
            assessment,
            "urn:caeluviim:claim:intake:compound-coverage",
        )
        self.assertFalse(result["release_allowed"])
        self.assertEqual(
            ["urn:caeluviim:claim-segment:no-uncovered-households"],
            result["uncovered_segment_refs"],
        )

    def test_unstable_locator_is_quarantined(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["source_locators"][0]["snapshot_bound"] = False
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn("LOCATOR_UNSTABLE", result["failure_codes"])

    def test_changed_snapshot_is_detected_by_digest_and_length(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = (
                root
                / "examples/evidence-intake/source/"
                "allocation-bulletin-2026q3.txt"
            )
            path.parent.mkdir(parents=True)
            path.write_bytes(
                (
                    ROOT
                    / "examples/evidence-intake/source/"
                    "allocation-bulletin-2026q3.txt"
                ).read_bytes()
                + b"changed"
            )
            result = self.claim_result(
                self.evaluate(candidate, project_root=root),
                claim_ref,
            )
        self.assertIn(
            "SNAPSHOT_DIGEST_MISMATCH",
            result["failure_codes"],
        )
        self.assertIn(
            "SNAPSHOT_LENGTH_MISMATCH",
            result["failure_codes"],
        )

    def test_quote_that_differs_from_snapshot_is_quarantined(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["source_locators"][0]["quoted_text"] += " altered"
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn(
            "QUOTE_SNAPSHOT_MISMATCH",
            result["failure_codes"],
        )

    def test_unsupported_inference_presented_as_observation_is_rejected(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["support_relations"][0]["support_mode"] = "inferential"
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn(
            "UNSUPPORTED_INFERENCE_AS_OBSERVATION",
            result["failure_codes"],
        )

    def test_authority_assessment_cannot_substitute_for_support(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["evidence_bundles"][0]["support_relation_refs"] = []
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn(
            "AUTHORITY_SUBSTITUTED_FOR_SUPPORT",
            result["failure_codes"],
        )
        self.assertIn(
            "SUPPORT_RELATION_MISSING",
            result["failure_codes"],
        )

    def test_generated_text_cannot_be_treated_as_external_source(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["source_artifacts"][0]["generated_content"] = True
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn(
            "GENERATED_TEXT_AS_EXTERNAL_SOURCE",
            result["failure_codes"],
        )

    def test_omitted_contradiction_is_an_explicit_failure_fact(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["evidence_bundles"][1][
            "contradiction_relation_refs"
        ] = []
        result = self.claim_result(
            self.evaluate(candidate),
            "urn:caeluviim:claim:intake:compound-coverage",
        )
        self.assertIn(
            "CONTRADICTORY_EVIDENCE_OMITTED",
            result["failure_codes"],
        )

    def test_evidence_reuse_beyond_scope_is_rejected(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = self.quarantine_recorded_claim(candidate)
        candidate["source_locators"][0]["support_scope_claim_refs"] = [
            "urn:caeluviim:claim:intake:compound-coverage"
        ]
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn(
            "SUPPORT_SCOPE_EXCEEDED",
            result["failure_codes"],
        )

    def test_missing_release_decision_fails_closed(self):
        candidate = copy.deepcopy(self.manifest)
        claim_ref = candidate["extracted_claims"][0]["claim_id"]
        candidate["extracted_claims"][0]["claim_state"] = "quarantined"
        candidate["release_decisions"] = [
            item
            for item in candidate["release_decisions"]
            if item["claim_ref"] != claim_ref
        ]
        result = self.claim_result(self.evaluate(candidate), claim_ref)
        self.assertIn(
            "RELEASE_AUTHORITY_MISSING",
            result["failure_codes"],
        )
        self.assertEqual("quarantined", result["evaluated_state"])

    def test_cross_format_alignment_detects_missing_typed_entity(self):
        graph = Graph().parse(self.rdf_path, format="turtle")
        claim_ref = URIRef(
            "urn:caeluviim:claim:intake:rule-replaced"
        )
        graph.remove((claim_ref, RDF.type, INTAKE.ExtractedClaim))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "misaligned.ttl"
            graph.serialize(destination=path, format="turtle")
            result = verify_cross_format_alignment(
                self.manifest,
                path,
            )
        self.assertFalse(result["conforms"])
        self.assertEqual(
            str(claim_ref),
            result["missing_typed_entities"][0]["json_ref"],
        )

    def test_shacl_rejects_generated_external_source(self):
        graph = Graph().parse(self.rdf_path, format="turtle")
        artifact = URIRef(
            "urn:caeluviim:source:allocation-bulletin-2026q3"
        )
        graph.set((artifact, INTAKE.generatedContent, Literal(True)))
        shapes = Graph().parse(self.shapes_path, format="turtle")
        ontology = Graph().parse(self.ontology_path, format="turtle")
        conforms, _, report = shacl_validate(
            data_graph=graph,
            shacl_graph=shapes,
            ont_graph=ontology,
            inference="rdfs",
            advanced=True,
        )
        self.assertFalse(conforms)
        self.assertIn(
            "Generated content must not be classified",
            str(report),
        )

    def test_store_preserves_hard_graph_separation(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            result = self.ingest(store)
            dataset = Dataset(default_union=True)
            dataset.parse(store.path, format="trig")
            asserted = dataset.graph(
                URIRef(result["graph_uris"]["asserted"])
            )
            quarantine = dataset.graph(
                URIRef(result["graph_uris"]["quarantine"])
            )
            self.assertTrue(set(asserted).isdisjoint(set(quarantine)))
            released = URIRef(
                "urn:caeluviim:claim:intake:rule-replaced"
            )
            quarantined = URIRef(
                "urn:caeluviim:claim:intake:compound-coverage"
            )
            self.assertTrue(
                any(
                    asserted.triples(
                        (
                            released,
                            INTAKE.evaluatedClaimState,
                            None,
                        )
                    )
                )
            )
            self.assertFalse(
                any(
                    asserted.triples(
                        (
                            quarantined,
                            INTAKE.evaluatedClaimState,
                            None,
                        )
                    )
                )
            )
            self.assertTrue(
                any(
                    quarantine.triples(
                        (
                            quarantined,
                            INTAKE.evaluatedClaimState,
                            None,
                        )
                    )
                )
            )
            self.assertTrue(result["graphs_disjoint"])

    def test_ingestion_is_idempotent_and_rejects_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            first = self.ingest(store)
            second = self.ingest(store)
            self.assertEqual("ingested", first["status"])
            self.assertEqual("already_present", second["status"])

            candidate = copy.deepcopy(self.manifest)
            candidate["created_at"] = "2026-07-29T17:00:01Z"
            candidate_path = Path(directory) / "different.json"
            candidate_path.write_text(
                json.dumps(candidate),
                encoding="utf-8",
            )
            with self.assertRaises(GraphCollisionError):
                self.ingest(store, manifest_path=candidate_path)

    def test_checked_queries_expose_quarantine_and_released_assertions(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            self.ingest(store)
            quarantine = store.query(
                self.quarantine_query_path.read_text("utf-8")
            )
            released = store.query(
                self.released_query_path.read_text("utf-8")
            )
        codes = {row["code"]["value"] for row in quarantine["rows"]}
        self.assertEqual(
            {
                "ACTIVE_QUARANTINE",
                "COMPLETE_SUPPORT_NOT_DECLARED",
                "PARTIAL_COMPOUND_SUPPORT",
                "RELEASE_DECISION_DENIED",
                "UNRESOLVED_CONTRADICTION",
            },
            codes,
        )
        self.assertEqual(1, len(released["rows"]))
        self.assertEqual(
            "urn:caeluviim:claim:intake:rule-replaced",
            released["rows"][0]["claim"]["value"],
        )

    def test_governance_status_is_proposed_and_hash_manifest_is_exact(self):
        status_schema = json.loads(
            self.status_schema_path.read_text("utf-8")
        )
        status_record = json.loads(self.status_path.read_text("utf-8"))
        validator = Draft202012Validator(
            status_schema,
            format_checker=FormatChecker(),
        )
        errors = list(validator.iter_errors(status_record))
        self.assertEqual([], errors, "\n".join(item.message for item in errors))
        self.assertEqual("implemented", status_record["implementation_status"])
        self.assertEqual("proposed", status_record["governance_status"])
        self.assertFalse(status_record["self_ratification_permitted"])
        self.assertFalse(status_record["ratification_claimed"])
        for item in status_record["artifact_manifest"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(
                item["sha256"],
                hashlib.sha256(path.read_bytes()).hexdigest(),
                item["path"],
            )

    def test_cli_validates_releases_ingests_and_queries(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            validation_path = directory_path / "validation.json"
            assessment_path = directory_path / "assessment.json"
            release_path = directory_path / "release.json"
            ingestion_path = directory_path / "ingestion.json"
            query_path = directory_path / "query.json"
            store_path = directory_path / "store.trig"
            base = [
                sys.executable,
                str(ROOT / "scripts/evidence_intake.py"),
                "--project-root",
                str(ROOT),
            ]
            commands = [
                base
                + [
                    "validate",
                    "--manifest",
                    str(self.manifest_path),
                    "--rdf",
                    str(self.rdf_path),
                    "--output",
                    str(validation_path),
                ],
                base
                + [
                    "evaluate",
                    "--manifest",
                    str(self.manifest_path),
                    "--output",
                    str(assessment_path),
                ],
                base
                + [
                    "release",
                    "--manifest",
                    str(self.manifest_path),
                    "--output",
                    str(release_path),
                ],
                base
                + [
                    "ingest",
                    "--manifest",
                    str(self.manifest_path),
                    "--rdf",
                    str(self.rdf_path),
                    "--store",
                    str(store_path),
                    "--graph-base",
                    "urn:caeluviim:graph:evidence-intake:cli",
                    "--output",
                    str(ingestion_path),
                ],
                base
                + [
                    "query",
                    "--store",
                    str(store_path),
                    "--sparql-file",
                    str(self.released_query_path),
                    "--output",
                    str(query_path),
                ],
            ]
            for command in commands:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    0,
                    result.returncode,
                    result.stdout + result.stderr,
                )
            self.assertTrue(
                json.loads(validation_path.read_text())["conforms"]
            )
            self.assertEqual(
                "released_with_quarantine",
                json.loads(assessment_path.read_text())["pipeline_result"],
            )
            release_text = release_path.read_text("utf-8")
            self.assertNotIn("compound-coverage", release_text)
            self.assertTrue(
                json.loads(ingestion_path.read_text())["graphs_disjoint"]
            )
            self.assertEqual(
                1,
                len(json.loads(query_path.read_text())["rows"]),
            )


if __name__ == "__main__":
    unittest.main()
