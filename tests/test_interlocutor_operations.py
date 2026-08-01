import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from pyshacl import validate
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
IO = Namespace("https://caeluviim.org/ontology/interlocutor-operations#")


class TestInterlocutorOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "schemas/interlocutor-operation.schema.json").read_text(encoding="utf-8")
        )
        cls.validator = Draft202012Validator(
            cls.schema, format_checker=FormatChecker()
        )
        cls.valid_assessment = json.loads(
            (
                ROOT
                / "examples/interlocutor-operation.truth-assessment.valid.json"
            ).read_text(encoding="utf-8")
        )
        cls.ontology = Graph().parse(
            ROOT / "ontology/interlocutor-operations.ttl", format="turtle"
        )
        cls.shapes = Graph().parse(
            ROOT / "shapes/interlocutor-operations.shacl.ttl", format="turtle"
        )
        cls.data = Graph().parse(
            ROOT / "examples/interlocutor-operations.valid.ttl", format="turtle"
        )
        cls.crosswalk = (
            ROOT / "docs/architecture/interlocutor-operation-crosswalk.md"
        ).read_text(encoding="utf-8")

    def errors_for(self, record):
        return sorted(
            self.validator.iter_errors(record), key=lambda error: list(error.path)
        )

    def test_valid_truth_assessment_conforms(self):
        errors = self.errors_for(self.valid_assessment)
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_quotation_requires_at_least_one_immutable_span(self):
        quotation = {
            "record_type": "quotation",
            "record_id": "urn:caeluviim:record:quotation:1",
            "created_at": "2026-08-01T12:00:00Z",
            "provenance_id": "urn:caeluviim:provenance:quotation:1",
            "quotation_id": "urn:caeluviim:quotation:1",
            "source_span_ids": [],
            "exact_text": "The meeting starts at noon.",
        }
        self.assertTrue(self.errors_for(quotation))

    def test_force_assignment_cannot_hide_contestability(self):
        force = {
            "record_type": "force_assignment",
            "record_id": "urn:caeluviim:record:force:1",
            "created_at": "2026-08-01T12:00:00Z",
            "provenance_id": "urn:caeluviim:provenance:force:1",
            "force_assignment_id": "urn:caeluviim:force:1",
            "target_id": "urn:caeluviim:utterance:1",
            "force_type": "assertive",
            "source_span_ids": ["urn:caeluviim:span:1"],
            "context_id": "urn:caeluviim:context:1",
            "confidence": 0.9,
            "rule_version_id": "urn:caeluviim:rule:force:0.1.0",
            "alternative_force_types": ["complaint"],
            "contestable": False,
        }
        self.assertTrue(self.errors_for(force))

    def test_truth_assessment_requires_full_context_tuple(self):
        incomplete = dict(self.valid_assessment)
        incomplete.pop("context_id")
        self.assertTrue(self.errors_for(incomplete))

    def test_truth_assessment_rejects_boolean_substitute_status(self):
        invalid = dict(self.valid_assessment)
        invalid["status"] = True
        self.assertTrue(self.errors_for(invalid))

    def test_operation_occurrence_requires_alternatives_field_when_present_to_be_ids(self):
        occurrence = {
            "record_type": "operation_occurrence",
            "record_id": "urn:caeluviim:record:operation-occurrence:1",
            "created_at": "2026-08-01T12:00:00Z",
            "provenance_id": "urn:caeluviim:provenance:operation-occurrence:1",
            "occurrence_id": "urn:caeluviim:operation-occurrence:1",
            "canonical_operation_id": "urn:caeluviim:operation:assertion",
            "target_id": "urn:caeluviim:utterance:1",
            "source_span_ids": ["urn:caeluviim:span:1"],
            "detection_mode": "model_inferred",
            "confidence": 0.74,
            "rule_version_id": "urn:caeluviim:rule:operation-detection:0.1.0",
            "alternative_operation_ids": ["not an identifier"],
            "contestable": True,
        }
        self.assertTrue(self.errors_for(occurrence))

    def test_rdf_vocabulary_and_shapes_parse(self):
        self.assertGreater(len(self.ontology), 0)
        self.assertGreater(len(self.shapes), 0)
        self.assertTrue(any(self.ontology.subjects(RDF.type, IO.Utterance)))
        self.assertTrue(any(self.ontology.subjects(RDF.type, IO.TransformationEvent)))
        self.assertTrue(any(self.ontology.subjects(RDF.type, IO.CanonicalOperation)))

    def test_valid_rdf_example_conforms_to_shapes(self):
        conforms, report_graph, report_text = validate(
            data_graph=self.data,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
        )
        self.assertTrue(conforms, report_text)
        self.assertGreater(len(report_graph), 0)

    def test_duplicate_concepts_have_one_canonical_crosswalk_row(self):
        canonical_rows = []
        for line in self.crosswalk.splitlines():
            if line.startswith("| `io:"):
                canonical_rows.append(line.split("|", 2)[1].strip(" `"))
        self.assertEqual(len(canonical_rows), len(set(canonical_rows)))
        self.assertIn("io:conceptual-metaphor", canonical_rows)
        self.assertIn("io:frame-evocation", canonical_rows)
        self.assertIn("io:adjacency-pair", canonical_rows)
        self.assertIn("io:constituency", canonical_rows)

    def test_known_karttunen_correction_is_preserved(self):
        self.assertIn("Lauri Karttunen", self.crosswalk)
        self.assertIn("prov:wasRevisionOf", self.crosswalk)


if __name__ == "__main__":
    unittest.main()
