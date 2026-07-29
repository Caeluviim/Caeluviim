import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
EMGN = Namespace("https://caeluviim.org/ontology/emgn#")


class TestEMGNArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas/emgn-record.schema.json").read_text())
        cls.record = json.loads((ROOT / "examples/emgn-record.valid.json").read_text())
        cls.graph = Graph()
        cls.graph.parse(ROOT / "ontology/emgn.ttl", format="turtle")
        cls.graph.parse(ROOT / "examples/emgn-record.valid.ttl", format="turtle")
        cls.shapes = Graph()
        cls.shapes.parse(ROOT / "shapes/emgn.shacl.ttl", format="turtle")

    def test_json_record_conforms(self):
        validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(self.record), key=lambda error: list(error.path))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_reference_integrity(self):
        agent_ids = {item["agent_id"] for item in self.record["agents"]}
        discrepancy_ids = {item["discrepancy_id"] for item in self.record["discrepancies"]}
        residue_ids = {item["residue_id"] for item in self.record["residues"]}

        self.assertTrue(set(self.record["interaction"]["participant_refs"]).issubset(agent_ids))
        self.assertTrue(all(item["agent_ref"] in agent_ids for item in self.record["discrepancies"]))
        self.assertTrue(all(item["source_discrepancy_ref"] in discrepancy_ids for item in self.record["residues"]))
        self.assertTrue(all(set(item["residue_refs"]).issubset(residue_ids) for item in self.record["remediations"]))
        self.assertTrue(set(self.record["transition_change"]["modified_by_residue_refs"]).issubset(residue_ids))

    def test_governance_independence(self):
        governance = self.record["governance"]
        validators = governance["validators"]
        self.assertGreaterEqual(len(set(validators)), 2)
        self.assertNotIn(governance["proposer_id"], validators)
        self.assertFalse(governance["proposer_is_validator"])

    def test_novelty_witness_is_operational(self):
        self.assertTrue(self.record["transition_change"]["regime_changed"])
        self.assertGreaterEqual(len(self.record["reachability_change"]["new_state_refs"]), 1)
        self.assertGreaterEqual(len(self.record["novelty_claim"]["witness_refs"]), 1)

    def test_rdf_and_shapes_parse(self):
        self.assertGreater(len(self.graph), 0)
        self.assertGreater(len(self.shapes), 0)
        self.assertTrue(any(self.graph.subjects(RDF.type, EMGN.NovelFutureClaim)))
        self.assertTrue(any(self.graph.subjects(RDF.type, EMGN.NovelFutureWitness)))

    def test_rdf_governance_invariants(self):
        decisions = list(self.graph.subjects(RDF.type, EMGN.GovernanceDecision))
        self.assertEqual(1, len(decisions))
        decision = decisions[0]
        proposers = set(self.graph.objects(decision, EMGN.proposer))
        validators = set(self.graph.objects(decision, EMGN.validator))
        self.assertEqual(1, len(proposers))
        self.assertGreaterEqual(len(validators), 2)
        self.assertTrue(proposers.isdisjoint(validators))


if __name__ == "__main__":
    unittest.main()
