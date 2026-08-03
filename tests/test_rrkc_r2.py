import importlib.util
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "formal/rrkc/reference_model.py"
spec = importlib.util.spec_from_file_location("rrkc_reference_model", MODEL_PATH)
rrkc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rrkc
assert spec.loader is not None
spec.loader.exec_module(rrkc)

RRKC = Namespace("https://caeluviim.org/ontology/rrkc#")


class TestRRKCR2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas/rrkc-r2.schema.json").read_text())
        cls.record = json.loads((ROOT / "examples/rrkc-r2.valid.json").read_text())
        cls.graph = Graph()
        cls.graph.parse(ROOT / "ontology/rrkc.ttl", format="turtle")
        cls.graph.parse(ROOT / "examples/rrkc-r2.valid.ttl", format="turtle")
        cls.shapes = Graph()
        cls.shapes.parse(ROOT / "shapes/rrkc.shacl.ttl", format="turtle")

        cls.signature = rrkc.Signature(
            relations={
                "supports": rrkc.RelationProfile(rrkc.EVIDENCE, rrkc.CLAIM)
            },
            operations={
                "publish": rrkc.OperationProfile((rrkc.CLAIM,), rrkc.ACTIVITY)
            },
        )

    def test_json_record_conforms(self):
        validator = Draft202012Validator(
            self.schema,
            format_checker=FormatChecker(),
        )
        errors = sorted(
            validator.iter_errors(self.record),
            key=lambda error: list(error.path),
        )
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_binders_make_fv_bv_nontrivial(self):
        x = rrkc.Var("x", rrkc.CLAIM)
        y = rrkc.Var("y", rrkc.CLAIM)
        term = rrkc.Lam(x, rrkc.Lam(y, x))
        self.assertEqual(frozenset(), rrkc.free_vars(term))
        self.assertEqual(frozenset({"x", "y"}), rrkc.bound_vars(term))

    def test_substitution_avoids_capture(self):
        x = rrkc.Var("x", rrkc.CLAIM)
        y = rrkc.Var("y", rrkc.CLAIM)
        term = rrkc.Lam(y, x)
        result = rrkc.substitute(term, "x", y)
        self.assertIsInstance(result, rrkc.Lam)
        self.assertNotEqual("y", result.variable.name)
        self.assertEqual(frozenset({"y"}), rrkc.free_vars(result))

    def test_signature_indexed_relation_and_activity(self):
        context = {"c": rrkc.CLAIM, "d": rrkc.EVIDENCE}
        relation = rrkc.Rel(
            "supports",
            rrkc.Var("d", rrkc.EVIDENCE),
            rrkc.Var("c", rrkc.CLAIM),
        )
        activity = rrkc.Act("publish", (rrkc.Var("c", rrkc.CLAIM),))
        self.assertEqual(
            rrkc.RELATION,
            rrkc.type_of(context, relation, self.signature),
        )
        self.assertEqual(
            rrkc.ACTIVITY,
            rrkc.type_of(context, activity, self.signature),
        )
        with self.assertRaises(rrkc.TypeErrorRRKC):
            rrkc.type_of(
                context,
                rrkc.Rel(
                    "supports",
                    rrkc.Var("c", rrkc.CLAIM),
                    rrkc.Var("d", rrkc.EVIDENCE),
                ),
                self.signature,
            )

    def test_revision_requires_equal_sort_and_governance(self):
        old = rrkc.Var("old", rrkc.CLAIM)
        new = rrkc.Var("new", rrkc.CLAIM)
        context = {"old": rrkc.CLAIM, "new": rrkc.CLAIM}
        revision = rrkc.Revise(old, new)
        self.assertEqual(
            rrkc.CLAIM,
            rrkc.type_of(context, revision, self.signature),
        )
        blocked = rrkc.step(revision, rrkc.GovernanceState())
        self.assertEqual(rrkc.StepKind.BLOCKED, blocked.kind)
        admitted = rrkc.GovernanceState(
            admissible_revisions=frozenset({(old, new)})
        )
        reduced = rrkc.step(revision, admitted)
        self.assertEqual(rrkc.StepKind.REDUCED, reduced.kind)
        self.assertEqual(new, reduced.term)

    def test_eval_is_partial_and_canonical_quote_reduces(self):
        c = rrkc.Var("c", rrkc.CLAIM)
        context = {
            "c": rrkc.CLAIM,
            "code": rrkc.Code(rrkc.CLAIM),
        }
        quoted = rrkc.Quote(c)
        self.assertEqual(
            rrkc.Code(rrkc.CLAIM),
            rrkc.type_of(context, quoted, self.signature),
        )
        result = rrkc.step(rrkc.Eval(quoted), rrkc.GovernanceState())
        self.assertEqual(rrkc.StepKind.REDUCED, result.kind)
        self.assertEqual(c, result.term)
        noncanonical = rrkc.Eval(
            rrkc.Var("code", rrkc.Code(rrkc.CLAIM))
        )
        self.assertEqual(
            rrkc.StepKind.STUCK,
            rrkc.step(noncanonical, rrkc.GovernanceState()).kind,
        )

    def test_executable_t2_t6_t7_instances(self):
        x = rrkc.Var("x", rrkc.CLAIM)
        replacement = rrkc.Var("r", rrkc.CLAIM)
        context = {"r": rrkc.CLAIM}
        body = rrkc.ClaimEntity(x)
        self.assertTrue(
            rrkc.substitution_preserves_sort(
                context,
                body,
                x,
                replacement,
                self.signature,
            )
        )

        identity = rrkc.Lam(x, x)
        beta = rrkc.App(identity, replacement)
        self.assertTrue(
            rrkc.preservation_holds(
                context,
                beta,
                self.signature,
                rrkc.GovernanceState(),
            )
        )
        self.assertTrue(
            rrkc.governed_progress_holds(
                context,
                beta,
                self.signature,
                rrkc.GovernanceState(),
            )
        )

        revision = rrkc.Revise(replacement, replacement)
        self.assertTrue(
            rrkc.governed_progress_holds(
                context,
                revision,
                self.signature,
                rrkc.GovernanceState(),
            )
        )

    def test_provenance_replay_isomorphic_and_acyclic(self):
        graph = rrkc.ProvenanceGraph(
            events=(
                rrkc.ProvenanceEvent("n1", "quote", (), ("code",)),
                rrkc.ProvenanceEvent("n2", "eval", ("code",), ("claim",)),
            ),
            precedence=frozenset({("n1", "n2")}),
        )
        replay = graph.replay()
        self.assertIsNot(graph, replay)
        self.assertTrue(graph.isomorphic_to(replay))

        cyclic = rrkc.ProvenanceGraph(
            graph.events,
            frozenset({("n1", "n2"), ("n2", "n1")}),
        )
        with self.assertRaises(rrkc.ProvenanceError):
            cyclic.validate()

    def test_rdf_and_shapes_parse(self):
        self.assertGreater(len(self.graph), 0)
        self.assertGreater(len(self.shapes), 0)
        self.assertTrue(any(self.graph.subjects(RDF.type, RRKC.FormalModule)))
        self.assertTrue(
            any(self.graph.subjects(RDF.type, RRKC.TerminationFragment))
        )


if __name__ == "__main__":
    unittest.main()
