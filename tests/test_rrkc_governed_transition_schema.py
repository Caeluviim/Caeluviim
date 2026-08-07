import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec/rrkc/governed-transition-event.schema.json"
EXAMPLES_DIR = ROOT / "spec/rrkc/examples"


class TestRRKCGovernedTransitionSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(
            cls.schema,
            format_checker=FormatChecker(),
        )
        cls.ratify = json.loads(
            (EXAMPLES_DIR / "ratify-authorized.example.json").read_text(encoding="utf-8")
        )
        cls.blocked = json.loads(
            (EXAMPLES_DIR / "veto-blocked.example.json").read_text(encoding="utf-8")
        )

    def assertConforms(self, instance):
        errors = sorted(
            self.validator.iter_errors(instance),
            key=lambda error: [str(part) for part in error.absolute_path],
        )
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def assertRejected(self, instance):
        self.assertTrue(
            list(self.validator.iter_errors(instance)),
            "expected instance to violate the governed-transition schema",
        )

    def test_authorized_ratification_fixture_conforms(self):
        self.assertConforms(self.ratify)

    def test_active_veto_blocked_fixture_conforms(self):
        self.assertConforms(self.blocked)

    def test_blocked_transition_requires_active_veto(self):
        invalid = copy.deepcopy(self.blocked)
        invalid["governance"]["vetoes"][0]["status"] = "withdrawn"
        self.assertRejected(invalid)

    def test_inadmissible_transition_requires_reason(self):
        invalid = copy.deepcopy(self.ratify)
        invalid["admissibility"]["status"] = "inadmissible"
        invalid["admissibility"]["reasons"] = []
        self.assertRejected(invalid)

    def test_truth_and_authority_remain_independent_dimensions(self):
        independent = copy.deepcopy(self.ratify)
        independent["admissibility"]["status"] = "contested"
        independent["governance"]["authorization"]["status"] = "authorized"
        self.assertConforms(independent)

    def test_state_references_must_be_state_kind(self):
        invalid = copy.deepcopy(self.ratify)
        invalid["post_state"]["kind"] = "Claim"
        self.assertRejected(invalid)


if __name__ == "__main__":
    unittest.main()
