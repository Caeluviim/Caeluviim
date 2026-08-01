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
from rdflib import Dataset, Graph, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from source_acquisition import (  # noqa: E402
    AcquisitionGraphCollisionError,
    LocalSourceAcquisitionStore,
    evaluate_manifest,
    intake_eligible_payload,
    validate_json_document,
    validate_rdf_manifest,
    verify_cross_format_alignment,
)
from source_acquisition.canonical import sha256_json  # noqa: E402

ACQ = Namespace("https://caeluviim.org/ontology/source-acquisition#")


class TestSourceAcquisition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = (
            ROOT / "examples/source-acquisition-manifest.valid.json"
        )
        cls.rdf_path = (
            ROOT / "examples/source-acquisition-manifest.valid.ttl"
        )
        cls.assessment_path = (
            ROOT / "examples/source-acquisition-assessment.json"
        )
        cls.manifest_schema_path = (
            ROOT / "schemas/source-acquisition-manifest.schema.json"
        )
        cls.assessment_schema_path = (
            ROOT / "schemas/source-acquisition-assessment.schema.json"
        )
        cls.status_schema_path = (
            ROOT / "schemas/source-acquisition-status.schema.json"
        )
        cls.status_path = (
            ROOT / "governance/source-acquisition-v0.1.0.status.json"
        )
        cls.ontology_path = ROOT / "ontology/source-acquisition.ttl"
        cls.shapes_path = ROOT / "shapes/source-acquisition.shacl.ttl"
        cls.changes_query_path = (
            ROOT / "queries/source-acquisition-changes.rq"
        )
        cls.failures_query_path = (
            ROOT / "queries/source-acquisition-failures.rq"
        )
        cls.eligible_query_path = (
            ROOT / "queries/source-acquisition-intake-eligible.rq"
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
    def version_result(assessment, suffix):
        return next(
            item
            for item in assessment["version_results"]
            if item["version_ref"].endswith(suffix)
        )

    def make_store(self, directory):
        return LocalSourceAcquisitionStore(
            Path(directory) / "source-acquisition.trig"
        )

    def ingest(self, store, manifest_path=None, graph_base=None):
        return store.ingest(
            manifest_path=manifest_path or self.manifest_path,
            rdf_path=self.rdf_path,
            base_graph_uri=(
                graph_base
                or "urn:caeluviim:graph:source-acquisition:test"
            ),
            project_root=ROOT,
            manifest_schema_path=self.manifest_schema_path,
            assessment_schema_path=self.assessment_schema_path,
            shapes_path=self.shapes_path,
            ontology_path=self.ontology_path,
        )

    def test_schemas_are_valid_draft_2020_12(self):
        for path in (
            self.manifest_schema_path,
            self.assessment_schema_path,
            self.status_schema_path,
        ):
            Draft202012Validator.check_schema(
                json.loads(path.read_text("utf-8"))
            )

    def test_manifest_conforms_to_json_schema(self):
        result = validate_json_document(
            self.manifest, self.manifest_schema
        )
        self.assertTrue(result["conforms"], result["errors"])

    def test_ontology_contains_every_required_first_class_entity(self):
        graph = Graph().parse(self.ontology_path, format="turtle")
        for class_name in (
            "SourceRequest",
            "RetrievalAttempt",
            "RetrievedRepresentation",
            "CanonicalSourceIdentity",
            "SourceVersion",
            "SnapshotFixation",
            "AcquisitionFailure",
            "ChangeEvent",
            "SupersessionRelation",
            "SourceAvailabilityObservation",
            "AcquisitionManifest",
        ):
            self.assertIn(
                (
                    ACQ[class_name],
                    RDF.type,
                    URIRef("http://www.w3.org/2002/07/owl#Class"),
                ),
                graph,
                class_name,
            )

    def test_rdf_shacl_and_cross_format_alignment_conform(self):
        shacl = validate_rdf_manifest(
            self.rdf_path,
            shapes_path=self.shapes_path,
            ontology_path=self.ontology_path,
        )
        alignment = verify_cross_format_alignment(
            self.manifest, self.rdf_path
        )
        self.assertTrue(shacl["conforms"], shacl["report_text"])
        self.assertTrue(alignment["conforms"], alignment)

    def test_evaluation_is_deterministic_and_content_addressed(self):
        first = self.evaluate()
        self.assertEqual(first, self.evaluate())
        digest_source = copy.deepcopy(first)
        digest_source.pop("assessment_id")
        digest_source.pop("assessment_digest")
        self.assertEqual(
            first["assessment_digest"], sha256_json(digest_source)
        )
        self.assertTrue(
            first["assessment_id"].endswith(
                ":" + first["assessment_digest"]
            )
        )

    def test_assessment_conforms_and_matches_committed_result(self):
        assessment = self.evaluate()
        result = validate_json_document(
            assessment, self.assessment_schema
        )
        self.assertTrue(result["conforms"], result["errors"])
        self.assertEqual(
            assessment,
            json.loads(self.assessment_path.read_text("utf-8")),
        )

    def test_example_is_eligible_with_a_queryable_blocked_attempt(self):
        assessment = self.evaluate()
        self.assertEqual(
            "eligible_with_failures", assessment["pipeline_result"]
        )
        self.assertEqual(3, len(assessment["eligible_snapshot_refs"]))
        self.assertEqual(
            ["urn:caeluviim:retrieval-attempt:restricted-audit"],
            assessment["ineligible_attempt_refs"],
        )
        self.assertEqual(
            ["RETRIEVAL_NOT_SUCCESSFUL"],
            [item["code"] for item in assessment["failure_facts"]],
        )

    def test_snapshot_id_is_sha256_of_exact_bytes(self):
        for fixation in self.manifest["snapshot_fixations"]:
            content = (ROOT / fixation["content_path"]).read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            self.assertEqual(fixation["sha256"], digest)
            self.assertEqual(
                fixation["snapshot_id"],
                "urn:caeluviim:snapshot:sha256:" + digest,
            )
            self.assertEqual(fixation["byte_length"], len(content))

    def test_same_url_produces_distinct_content_bound_versions(self):
        requests = self.manifest["source_requests"][:2]
        self.assertEqual(
            requests[0]["requested_uri"], requests[1]["requested_uri"]
        )
        versions = [
            item
            for item in self.manifest["source_versions"]
            if item["canonical_identity_ref"]
            == "urn:caeluviim:canonical-source:allocation-register"
        ]
        self.assertEqual(2, len(versions))
        self.assertNotEqual(versions[0]["sha256"], versions[1]["sha256"])
        self.assertNotEqual(
            versions[0]["version_id"], versions[1]["version_id"]
        )
        self.assertNotEqual(
            versions[0]["snapshot_ref"], versions[1]["snapshot_ref"]
        )

    def test_intake_payload_contains_only_eligible_fixed_snapshots(self):
        assessment = self.evaluate()
        payload = intake_eligible_payload(self.manifest, assessment)
        serialized = json.dumps(payload, sort_keys=True)
        self.assertEqual(3, len(payload["eligible_snapshots"]))
        self.assertNotIn("restricted-audit", serialized)
        self.assertNotIn("claim_support", serialized)
        self.assertNotIn("truth_assessed", serialized)
        for item in payload["eligible_snapshots"]:
            self.assertIn("snapshot_fixation_ref", item)
            self.assertIn("source_version_ref", item)
            self.assertIn("retrieval_attempt_ref", item)

    def test_changed_fixed_bytes_are_detected(self):
        candidate = copy.deepcopy(self.manifest)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for fixation in candidate["snapshot_fixations"]:
                target = root / fixation["content_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / fixation["content_path"]).read_bytes())
            target = (
                root
                / "examples/source-acquisition/representations/"
                "allocation-register-v2.txt"
            )
            target.write_bytes(target.read_bytes() + b"changed")
            assessment = self.evaluate(candidate, project_root=root)
        result = self.version_result(
            assessment,
            "36fef786129e37f259e54301eaadd1f265f5ebe7f5848eb5a9121cfac1fd2afb",
        )
        self.assertIn(
            "SNAPSHOT_DIGEST_MISMATCH", result["failure_codes"]
        )
        self.assertIn(
            "SNAPSHOT_LENGTH_MISMATCH", result["failure_codes"]
        )
        self.assertFalse(result["intake_eligible"])

    def test_non_content_addressed_snapshot_is_ineligible(self):
        candidate = copy.deepcopy(self.manifest)
        version = candidate["source_versions"][0]
        fixation = candidate["snapshot_fixations"][0]
        replacement = (
            "urn:caeluviim:snapshot:sha256:"
            + "0" * 64
        )
        version["snapshot_ref"] = replacement
        fixation["snapshot_id"] = replacement
        result = self.version_result(
            self.evaluate(candidate), version["sha256"]
        )
        self.assertIn(
            "SNAPSHOT_ID_NOT_CONTENT_ADDRESS", result["failure_codes"]
        )

    def test_schema_requires_response_metadata(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["retrieved_representations"][0][
            "response_headers"
        ] = []
        result = validate_json_document(candidate, self.manifest_schema)
        self.assertFalse(result["conforms"])

    def test_broken_redirect_chain_is_ineligible(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["retrieval_attempts"][0]["redirect_chain"][0][
            "location_uri"
        ] = "https://cdn.example.invalid/other.txt"
        assessment = self.evaluate(candidate)
        result = next(
            item
            for item in assessment["attempt_results"]
            if item["attempt_ref"].endswith("allocation-register:v1")
        )
        self.assertIn("REDIRECT_CHAIN_BROKEN", result["failure_codes"])

    def test_final_uri_mismatch_is_ineligible(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["retrieval_attempts"][0][
            "final_uri"
        ] = "https://cdn.example.invalid/other.txt"
        assessment = self.evaluate(candidate)
        result = next(
            item
            for item in assessment["attempt_results"]
            if item["attempt_ref"].endswith("allocation-register:v1")
        )
        self.assertIn("FINAL_URI_MISMATCH", result["failure_codes"])

    def test_changed_source_without_change_event_fails_closed(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["change_events"] = []
        assessment = self.evaluate(candidate)
        result = self.version_result(
            assessment,
            "36fef786129e37f259e54301eaadd1f265f5ebe7f5848eb5a9121cfac1fd2afb",
        )
        self.assertIn("CHANGE_EVENT_MISSING", result["failure_codes"])
        self.assertFalse(result["intake_eligible"])
        self.assertIn(
            "urn:caeluviim:retrieval-attempt:allocation-register:v2",
            assessment["ineligible_attempt_refs"],
        )

    def test_changed_source_without_supersession_fails_closed(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["supersession_relations"] = []
        result = self.version_result(
            self.evaluate(candidate),
            "36fef786129e37f259e54301eaadd1f265f5ebe7f5848eb5a9121cfac1fd2afb",
        )
        self.assertIn(
            "SUPERSESSION_RELATION_MISSING", result["failure_codes"]
        )

    def test_mismatched_change_event_digests_fail_closed(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["change_events"][0][
            "previous_sha256"
        ] = "0" * 64
        result = self.version_result(
            self.evaluate(candidate),
            "36fef786129e37f259e54301eaadd1f265f5ebe7f5848eb5a9121cfac1fd2afb",
        )
        self.assertIn("CHANGE_EVENT_MISMATCH", result["failure_codes"])

    def test_retrieval_failure_is_not_evidentiary_absence(self):
        failure = self.manifest["acquisition_failures"][0]
        observation = next(
            item
            for item in self.manifest[
                "source_availability_observations"
            ]
            if item["attempt_ref"] == failure["attempt_ref"]
        )
        self.assertFalse(failure["evidentiary_absence_inferred"])
        self.assertFalse(observation["evidentiary_absence_inferred"])
        self.assertEqual("blocked", observation["status"])

    def test_schema_forbids_acquisition_authority_overreach(self):
        for field in (
            "source_authority_assessed",
            "claim_support_assessed",
            "truth_assessed",
        ):
            candidate = copy.deepcopy(self.manifest)
            candidate["authority_boundary"][field] = True
            self.assertFalse(
                validate_json_document(
                    candidate, self.manifest_schema
                )["conforms"],
                field,
            )

    def test_schema_forbids_failure_as_evidentiary_absence(self):
        candidate = copy.deepcopy(self.manifest)
        candidate["acquisition_failures"][0][
            "evidentiary_absence_inferred"
        ] = True
        self.assertFalse(
            validate_json_document(
                candidate, self.manifest_schema
            )["conforms"]
        )

    def test_cross_format_alignment_detects_missing_entity(self):
        graph = Graph().parse(self.rdf_path, format="turtle")
        ref = URIRef(
            "urn:caeluviim:change-event:allocation-register:v1-to-v2"
        )
        graph.remove((ref, RDF.type, ACQ.ChangeEvent))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "misaligned.ttl"
            graph.serialize(destination=path, format="turtle")
            result = verify_cross_format_alignment(
                self.manifest, path
            )
        self.assertFalse(result["conforms"])
        self.assertEqual(str(ref), result["missing_typed_entities"][0]["json_ref"])

    def test_shacl_rejects_non_content_addressed_fixation(self):
        graph = Graph().parse(self.rdf_path, format="turtle")
        fixation = URIRef(
            "urn:caeluviim:snapshot-fixation:sha256:"
            "6fdc0c4f6134d468cca7239281898169d90f81c0403f316e52549317f3438972"
        )
        graph.set(
            (
                fixation,
                ACQ.snapshotID,
                URIRef("urn:caeluviim:snapshot:sha256:" + "0" * 64),
            )
        )
        conforms, _, report = shacl_validate(
            data_graph=graph,
            shacl_graph=Graph().parse(self.shapes_path, format="turtle"),
            ont_graph=Graph().parse(self.ontology_path, format="turtle"),
            inference="rdfs",
            advanced=True,
        )
        self.assertFalse(conforms)
        self.assertIn("SnapshotID must be", str(report))

    def test_store_physically_separates_eligible_and_failure_graphs(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            result = self.ingest(store)
            dataset = Dataset(default_union=True)
            dataset.parse(store.path, format="trig")
            eligible = dataset.graph(
                URIRef(result["graph_uris"]["eligible"])
            )
            failures = dataset.graph(
                URIRef(result["graph_uris"]["failures"])
            )
            self.assertTrue(set(eligible).isdisjoint(set(failures)))
            self.assertTrue(
                set(eligible.subjects()).isdisjoint(
                    set(failures.subjects())
                )
            )
            self.assertTrue(result["graphs_disjoint"])
            self.assertEqual(3, result["eligible_snapshot_count"])
            self.assertEqual(1, result["failed_attempt_count"])

    def test_checked_queries_expose_lifecycle_failure_and_eligibility(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            self.ingest(store)
            changes = store.query(
                self.changes_query_path.read_text("utf-8")
            )
            failures = store.query(
                self.failures_query_path.read_text("utf-8")
            )
            eligible = store.query(
                self.eligible_query_path.read_text("utf-8")
            )
        self.assertEqual(1, changes["row_count"])
        self.assertEqual(1, failures["row_count"])
        self.assertEqual(
            "RETRIEVAL_NOT_SUCCESSFUL",
            failures["rows"][0]["code"]["value"],
        )
        self.assertEqual(3, eligible["row_count"])

    def test_ingestion_is_idempotent_and_rejects_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.make_store(directory)
            first = self.ingest(store)
            second = self.ingest(store)
            self.assertEqual("ingested", first["status"])
            self.assertEqual("already_present", second["status"])
            candidate = copy.deepcopy(self.manifest)
            candidate["created_at"] = "2026-07-29T19:00:01Z"
            path = Path(directory) / "different.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaises(AcquisitionGraphCollisionError):
                self.ingest(store, manifest_path=path)

    def test_cli_validates_evaluates_exports_ingests_and_queries(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            base = [
                sys.executable,
                str(ROOT / "scripts/source_acquisition.py"),
                "--project-root",
                str(ROOT),
            ]
            outputs = {
                "validate": directory_path / "validation.json",
                "evaluate": directory_path / "assessment.json",
                "intake": directory_path / "intake.json",
                "ingest": directory_path / "ingestion.json",
                "query": directory_path / "query.json",
            }
            store = directory_path / "store.trig"
            commands = [
                base
                + [
                    "validate",
                    "--manifest",
                    str(self.manifest_path),
                    "--rdf",
                    str(self.rdf_path),
                    "--output",
                    str(outputs["validate"]),
                ],
                base
                + [
                    "evaluate",
                    "--manifest",
                    str(self.manifest_path),
                    "--output",
                    str(outputs["evaluate"]),
                ],
                base
                + [
                    "intake",
                    "--manifest",
                    str(self.manifest_path),
                    "--output",
                    str(outputs["intake"]),
                ],
                base
                + [
                    "ingest",
                    "--manifest",
                    str(self.manifest_path),
                    "--rdf",
                    str(self.rdf_path),
                    "--store",
                    str(store),
                    "--graph-base",
                    "urn:caeluviim:graph:source-acquisition:cli",
                    "--output",
                    str(outputs["ingest"]),
                ],
                base
                + [
                    "query",
                    "--store",
                    str(store),
                    "--sparql-file",
                    str(self.eligible_query_path),
                    "--output",
                    str(outputs["query"]),
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
                json.loads(outputs["validate"].read_text())["conforms"]
            )
            self.assertEqual(
                "eligible_with_failures",
                json.loads(outputs["evaluate"].read_text())[
                    "pipeline_result"
                ],
            )
            self.assertEqual(
                3,
                len(
                    json.loads(outputs["intake"].read_text())[
                        "eligible_snapshots"
                    ]
                ),
            )
            self.assertTrue(
                json.loads(outputs["ingest"].read_text())[
                    "graphs_disjoint"
                ]
            )
            self.assertEqual(
                3, json.loads(outputs["query"].read_text())["row_count"]
            )

    def test_governance_status_is_proposed_and_hash_manifest_is_exact(self):
        status_schema = json.loads(
            self.status_schema_path.read_text("utf-8")
        )
        status = json.loads(self.status_path.read_text("utf-8"))
        errors = list(
            Draft202012Validator(
                status_schema,
                format_checker=FormatChecker(),
            ).iter_errors(status)
        )
        self.assertEqual([], errors)
        self.assertEqual("implemented", status["implementation_status"])
        self.assertEqual("proposed", status["governance_status"])
        self.assertFalse(status["self_ratification_permitted"])
        self.assertFalse(status["ratification_claimed"])
        for item in status["artifact_manifest"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(
                item["sha256"],
                hashlib.sha256(path.read_bytes()).hexdigest(),
                item["path"],
            )


if __name__ == "__main__":
    unittest.main()
