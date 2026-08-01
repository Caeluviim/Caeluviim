import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Dataset, Graph, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sicrp_runtime import (  # noqa: E402
    GraphCollisionError,
    LocalSICRPStore,
    evaluate_record,
    validate_json_record,
    validate_rdf_record,
    verify_cross_format_alignment,
)
from sicrp_runtime.canonical import sha256_json  # noqa: E402

SICRP = Namespace("https://caeluviim.org/ontology/sicrp#")
RUNTIME = Namespace("https://caeluviim.org/ontology/sicrp/runtime#")


class TestSICRPRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record_path = ROOT / "examples/sicrp-record.valid.json"
        cls.rdf_path = ROOT / "examples/sicrp-record.valid.ttl"
        cls.record_schema_path = ROOT / "schemas/sicrp-record.schema.json"
        cls.assessment_schema_path = ROOT / "schemas/sicrp-assessment.schema.json"
        cls.assessment_example_path = (
            ROOT / "examples/sicrp-assessment.provisional.json"
        )
        cls.shapes_path = ROOT / "shapes/sicrp.shacl.ttl"
        cls.ontology_path = ROOT / "ontology/sicrp.ttl"
        cls.assessment_shapes_path = ROOT / "shapes/sicrp-assessment.shacl.ttl"
        cls.runtime_ontology_path = ROOT / "ontology/sicrp-runtime.ttl"
        cls.query_path = ROOT / "queries/sicrp-resolution-blockers.rq"
        cls.record = json.loads(cls.record_path.read_text("utf-8"))
        cls.record_schema = json.loads(cls.record_schema_path.read_text("utf-8"))
        cls.assessment_schema = json.loads(
            cls.assessment_schema_path.read_text("utf-8")
        )
        cls.runtime_status_schema = json.loads(
            (ROOT / "schemas/sicrp-runtime-status.schema.json").read_text("utf-8")
        )
        cls.runtime_status = json.loads(
            (ROOT / "governance/sicrp-runtime-v0.1.0.status.json").read_text(
                "utf-8"
            )
        )

    def evaluate(self, record=None):
        return evaluate_record(
            copy.deepcopy(record or self.record),
            schema=self.record_schema,
        )

    @staticmethod
    def result(assessment, obligation_id):
        return next(
            item
            for item in assessment["obligations"]
            if item["obligation_id"] == obligation_id
        )

    def make_store(self, directory):
        return LocalSICRPStore(Path(directory) / "sicrp.trig")

    def ingest(self, store, *, record_path=None, graph_uri=None):
        return store.ingest(
            record_path=record_path or self.record_path,
            rdf_path=self.rdf_path,
            graph_uri=graph_uri or "urn:caeluviim:graph:sicrp:runtime-test",
            record_schema_path=self.record_schema_path,
            assessment_schema_path=self.assessment_schema_path,
            shapes_path=self.shapes_path,
            ontology_path=self.ontology_path,
            assessment_shapes_path=self.assessment_shapes_path,
            runtime_ontology_path=self.runtime_ontology_path,
        )

    def test_assessment_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(self.assessment_schema)
        Draft202012Validator.check_schema(self.runtime_status_schema)

    def test_runtime_status_is_proposed_and_manifest_is_exact(self):
        validator = Draft202012Validator(
            self.runtime_status_schema, format_checker=FormatChecker()
        )
        errors = list(validator.iter_errors(self.runtime_status))
        self.assertEqual([], errors, "\n".join(item.message for item in errors))
        self.assertEqual("implemented", self.runtime_status["implementation_status"])
        self.assertEqual("proposed", self.runtime_status["governance_status"])
        self.assertFalse(self.runtime_status["self_ratification_permitted"])
        self.assertFalse(self.runtime_status["ratification_claimed"])
        self.assertNotIn(
            self.runtime_status["proposer_id"],
            self.runtime_status["independent_validators"],
        )
        for item in self.runtime_status["artifact_manifest"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(
                item["sha256"],
                hashlib.sha256(path.read_bytes()).hexdigest(),
                item["path"],
            )

    def test_evaluation_is_deterministic_and_digest_bound(self):
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first, second)
        digest_source = copy.deepcopy(first)
        digest_source.pop("assessment_id")
        digest_source.pop("assessment_digest")
        self.assertEqual(first["assessment_digest"], sha256_json(digest_source))
        self.assertEqual(
            first["assessment_id"],
            "urn:caeluviim:assessment:sicrp-runtime:"
            + first["assessment_digest"],
        )

    def test_assessment_conforms_to_machine_contract(self):
        assessment = self.evaluate()
        result = validate_json_record(assessment, self.assessment_schema)
        self.assertTrue(result["conforms"], result["errors"])

    def test_committed_assessment_is_exact_deterministic_output(self):
        committed = json.loads(self.assessment_example_path.read_text("utf-8"))
        self.assertEqual(self.evaluate(), committed)

    def test_example_supports_condition_but_not_collective_resolution(self):
        assessment = self.evaluate()
        self.assertTrue(assessment["record_conforms"])
        self.assertEqual(
            "supported", assessment["structural_insolvency"]["verdict"]
        )
        self.assertEqual(
            "not_established",
            assessment["collective_resolution"]["verdict"],
        )
        self.assertEqual(
            {
                "CONDITION_UNVALIDATED",
                "COVERAGE_INCOMPLETE",
                "DECLARED_CRITERIA_INCOMPLETE",
                "INTERVENTION_UNVERIFIED",
                "RESIDUAL_INSOLVENCY_REMAINS",
                "VALIDATOR_QUORUM_MISSING",
            },
            set(
                assessment["collective_resolution"][
                    "blocking_obligation_codes"
                ]
            ),
        )

    def test_coverage_and_residual_obligations_are_explicit(self):
        assessment = self.evaluate()
        coverage = self.result(assessment, "O-COLLECTIVE-COVERAGE")
        residual_disclosure = self.result(
            assessment, "O-RESIDUAL-DISCLOSURE"
        )
        residual_resolution = self.result(
            assessment, "O-RESIDUAL-RESOLUTION"
        )
        self.assertEqual(("fail", "COVERAGE_INCOMPLETE"), (coverage["status"], coverage["code"]))
        self.assertEqual("pass", residual_disclosure["status"])
        self.assertEqual(
            ("fail", "RESIDUAL_INSOLVENCY_REMAINS"),
            (residual_resolution["status"], residual_resolution["code"]),
        )
        self.assertTrue(residual_resolution["evidence_refs"])

    def test_arithmetic_failure_is_evidence_bearing_and_blocks_conformance(self):
        candidate = copy.deepcopy(self.record)
        candidate["material_deficits"][0]["shortfall_quantity"] = 59
        assessment = self.evaluate(candidate)
        arithmetic = self.result(assessment, "O-DEFICIT-ARITHMETIC")
        self.assertFalse(assessment["record_conforms"])
        self.assertEqual("fail", arithmetic["status"])
        self.assertEqual("DEFICIT_ARITHMETIC_FAILED", arithmetic["code"])
        self.assertIn(
            candidate["material_deficits"][0]["deficit_id"],
            arithmetic["subject_refs"],
        )

    def test_reference_failure_is_evidence_bearing_and_blocks_conformance(self):
        candidate = copy.deepcopy(self.record)
        missing = "urn:caeluviim:mechanism:missing"
        candidate["interventions"][0]["target_mechanism_refs"][0] = missing
        assessment = self.evaluate(candidate)
        reference = self.result(assessment, "O-REFERENCE-INTEGRITY")
        self.assertFalse(assessment["record_conforms"])
        self.assertEqual("REFERENCE_INTEGRITY_FAILED", reference["code"])
        self.assertIn(missing, reference["message"])

    def test_validator_independence_failure_is_exposed(self):
        candidate = copy.deepcopy(self.record)
        candidate["resolution_observations"][0]["assessor_ref"] = candidate[
            "interventions"
        ][0]["responsible_actor_refs"][0]
        assessment = self.evaluate(candidate)
        independence = self.result(assessment, "O-VALIDATOR-INDEPENDENCE")
        self.assertFalse(assessment["record_conforms"])
        self.assertEqual("VALIDATOR_INDEPENDENCE_FAILED", independence["code"])
        self.assertIn(
            candidate["resolution_observations"][0]["observation_id"],
            independence["subject_refs"],
        )

    def test_no_evaluation_can_confer_ratification_or_novelty(self):
        assessment = self.evaluate()
        self.assertEqual("provisional", assessment["governance"]["assessment_status"])
        self.assertFalse(assessment["governance"]["self_ratification_permitted"])
        self.assertFalse(assessment["governance"]["ratification_conferred"])
        self.assertFalse(
            assessment["collective_resolution"]["ratification_conferred"]
        )
        self.assertFalse(assessment["emgn_alignment"]["novelty_validated"])

    def test_satisfied_requirements_still_produce_only_provisional_assessment(self):
        candidate = copy.deepcopy(self.record)
        candidate["record_status"] = "ratified"
        candidate["structural_insolvency_conditions"][0]["status"] = "validated"
        candidate["interventions"][0]["status"] = "verified"
        candidate["residual_insolvency"][0]["status"] = "closed"
        candidate["collective_resolution_claim"]["status"] = "validated"
        for criterion in candidate["collective_resolution_claim"]["criteria"]:
            candidate["collective_resolution_claim"]["criteria"][criterion] = True
        second = copy.deepcopy(candidate["validator_assessments"][0])
        second["assessment_id"] = "urn:caeluviim:assessment:resolution-002"
        second["validator_ref"] = "urn:caeluviim:agent:validator-2"
        second["evidence_refs"] = [
            "urn:caeluviim:evidence:validator-assessment-002"
        ]
        candidate["validator_assessments"].append(second)
        candidate["collective_resolution_claim"][
            "validator_assessment_refs"
        ].append(second["assessment_id"])
        candidate["governance"]["validators"].append(second["validator_ref"])
        candidate["governance"]["status"] = "ratified"
        candidate["governance"]["ratification_claimed"] = True

        schema_result = validate_json_record(candidate, self.record_schema)
        self.assertTrue(schema_result["conforms"], schema_result["errors"])
        assessment = self.evaluate(candidate)
        self.assertTrue(assessment["record_conforms"])
        self.assertEqual(
            "requirements_satisfied",
            assessment["collective_resolution"]["verdict"],
        )
        self.assertEqual([], assessment["collective_resolution"]["blocking_obligation_codes"])
        self.assertEqual("provisional", assessment["governance"]["assessment_status"])
        self.assertFalse(assessment["governance"]["ratification_conferred"])
        self.assertFalse(
            assessment["collective_resolution"]["ratification_conferred"]
        )

    def test_json_rdf_shacl_and_alignment_all_conform(self):
        json_result = validate_json_record(self.record, self.record_schema)
        rdf_result = validate_rdf_record(
            self.rdf_path,
            shapes_path=self.shapes_path,
            ontology_path=self.ontology_path,
        )
        alignment = verify_cross_format_alignment(self.record, self.rdf_path)
        self.assertTrue(json_result["conforms"], json_result["errors"])
        self.assertTrue(rdf_result["conforms"], rdf_result["report_text"])
        self.assertTrue(alignment["conforms"], alignment)

    def test_cross_format_alignment_detects_missing_typed_entity(self):
        graph = Graph().parse(self.rdf_path, format="turtle")
        condition = URIRef(
            self.record["structural_insolvency_conditions"][0]["condition_id"]
        )
        graph.remove((condition, RDF.type, SICRP.StructuralInsolvencyCondition))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "misaligned.ttl"
            graph.serialize(destination=path, format="turtle")
            alignment = verify_cross_format_alignment(self.record, path)
        self.assertFalse(alignment["conforms"])
        self.assertEqual(
            str(condition),
            alignment["missing_typed_entities"][0]["json_ref"],
        )

    def test_shacl_detects_right_without_exercisable_action(self):
        graph = Graph().parse(self.rdf_path, format="turtle")
        right = URIRef(self.record["intervention_rights"][0]["right_id"])
        graph.remove((right, SICRP.hasExercisableAction, None))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.ttl"
            graph.serialize(destination=path, format="turtle")
            result = validate_rdf_record(
                path,
                shapes_path=self.shapes_path,
                ontology_path=self.ontology_path,
            )
        self.assertFalse(result["conforms"])
        self.assertIn("hasExercisableAction", result["report_text"])

    def test_atomic_ingestion_preserves_record_and_assessment_graphs(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            result = self.ingest(store)
            status = store.inspect()
            self.assertEqual("ingested", result["status"])
            self.assertEqual(3, status["named_graph_count"])
            self.assertGreater(result["record_triples"], 300)
            self.assertGreater(result["assessment_triples"], 100)
            self.assertTrue(result["assessment_graph_conforms"])
            self.assertTrue(store.path.is_file())
            self.assertFalse(result["ratification_conferred"])

            dataset = Dataset(default_union=True)
            dataset.parse(store.path, format="trig")
            self.assertTrue(
                any(
                    dataset.subjects(
                        RUNTIME.collectiveResolutionVerdict,
                        None,
                    )
                )
            )
            claim_ref = URIRef(
                self.record["collective_resolution_claim"]["claim_id"]
            )
            self.assertIn(
                (
                    claim_ref,
                    RDF.type,
                    SICRP.CollectiveResolutionClaim,
                ),
                dataset,
            )
            self.assertNotIn(
                (
                    URIRef(result["record_ref"]),
                    RDF.type,
                    SICRP.CollectiveResolutionClaim,
                ),
                dataset,
            )

    def test_ingestion_is_idempotent_but_rejects_graph_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            first = self.ingest(store)
            second = self.ingest(store)
            self.assertEqual("ingested", first["status"])
            self.assertEqual("already_present", second["status"])

            candidate = copy.deepcopy(self.record)
            candidate["provenance"]["content_hash"] = "d" * 64
            candidate_path = Path(directory) / "different.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaises(GraphCollisionError):
                self.ingest(store, record_path=candidate_path)

    def test_blocker_query_returns_exact_operational_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            self.ingest(store)
            result = store.query(self.query_path.read_text("utf-8"))
        self.assertEqual("SELECT", result["type"])
        codes = [row["code"]["value"] for row in result["rows"]]
        self.assertEqual(
            [
                "CONDITION_UNVALIDATED",
                "COVERAGE_INCOMPLETE",
                "DECLARED_CRITERIA_INCOMPLETE",
                "INTERVENTION_UNVERIFIED",
                "RESIDUAL_INSOLVENCY_REMAINS",
                "VALIDATOR_QUORUM_MISSING",
            ],
            codes,
        )

    def test_cli_validates_evaluates_ingests_and_queries_locally(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            validation_path = directory_path / "validation.json"
            assessment_path = directory_path / "assessment.json"
            ingestion_path = directory_path / "ingestion.json"
            query_path = directory_path / "query.json"
            store_path = directory_path / "store.trig"
            base = [
                sys.executable,
                str(ROOT / "scripts/sicrp_runtime.py"),
                "--project-root",
                str(ROOT),
            ]
            commands = [
                base
                + [
                    "validate",
                    "--record",
                    str(self.record_path),
                    "--rdf",
                    str(self.rdf_path),
                    "--output",
                    str(validation_path),
                ],
                base
                + [
                    "evaluate",
                    "--record",
                    str(self.record_path),
                    "--output",
                    str(assessment_path),
                ],
                base
                + [
                    "ingest",
                    "--record",
                    str(self.record_path),
                    "--rdf",
                    str(self.rdf_path),
                    "--store",
                    str(store_path),
                    "--graph",
                    "urn:caeluviim:graph:sicrp:cli-test",
                    "--output",
                    str(ingestion_path),
                ],
                base
                + [
                    "query",
                    "--store",
                    str(store_path),
                    "--sparql-file",
                    str(self.query_path),
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
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(json.loads(validation_path.read_text())["conforms"])
            self.assertEqual(
                "not_established",
                json.loads(assessment_path.read_text())["collective_resolution"][
                    "verdict"
                ],
            )
            self.assertEqual(
                "ingested",
                json.loads(ingestion_path.read_text())["status"],
            )
            self.assertEqual(6, len(json.loads(query_path.read_text())["rows"]))


if __name__ == "__main__":
    unittest.main()
