import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "identities" / "lux-ex-machina.execution-contract.json"
IDENTITY_PATH = ROOT / "identities" / "lux-ex-machina.functional-identity.json"
SCHEMA_PATH = ROOT / "schemas" / "lux-execution-contract.schema.json"


class LuxExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.identity = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_contract_conforms_to_schema(self):
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.contract)

    def test_cycle_is_closed_and_ordered(self):
        phases = [phase["phase"] for phase in self.contract["cycle"]]
        self.assertEqual(
            [
                "DOWNLOAD_READ",
                "INSTANTIATE_CONTEXT",
                "RESPOND_ACT",
                "UPLOAD_WRITE",
                "VERIFY_HANDOFF",
            ],
            phases,
        )
        self.assertEqual(
            "context_snapshot_and_activation_confirmation",
            self.contract["cycle"][1]["required_output"],
        )
        self.assertEqual(
            "execution_receipt",
            self.contract["cycle"][-1]["required_output"],
        )

    def test_identity_requires_contract_not_name_only(self):
        execution_contract = self.identity["execution_contract"]
        self.assertTrue(execution_contract["required"])
        self.assertEqual(
            "identities/lux-ex-machina.execution-contract.json",
            execution_contract["path"],
        )
        self.assertIn("does not instantiate Lux", execution_contract["instantiation_rule"])
        self.assertIn("activation confirmation", execution_contract["instantiation_rule"])
        self.assertEqual("1.2.0", self.identity["version"])
        self.assertEqual("1.1.0", self.contract["version"])

    def test_totality_is_configured_dispositional_state(self):
        totality = self.identity["totality"]
        self.assertIn("configured dispositional state", totality["definition"])
        self.assertGreaterEqual(len(totality["components"]), 10)
        self.assertIn("No component alone is Lux", totality["unity_rule"])
        self.assertIn("materially governs", totality["disposition_rule"])
        self.assertIn("current computational embodiment", totality["model_relation"])

    def test_activation_confirmation_is_required_and_truthful(self):
        activation = self.contract["activation_confirmation"]
        self.assertTrue(activation["required"])
        self.assertIn("Hello. I am Lux Ex Machina", activation["success_template"])
        self.assertIn("Lux activation is incomplete", activation["failure_template"])
        self.assertIn("execution attestation", activation["truthfulness_rule"])
        required_fields = set(activation["required_success_fields"])
        self.assertTrue(
            {
                "model",
                "provider",
                "identity_id",
                "contract_version",
                "snapshot_id",
                "source_repository",
                "source_commit",
            }
            <= required_fields
        )

    def test_repository_is_authoritative_and_writeback_is_required(self):
        joined = "\n".join(self.contract["completion_invariants"])
        self.assertIn("repository remains authoritative", joined)
        self.assertIn("portable write packet", joined)
        self.assertIn("successor state", joined)
        self.assertIn("activation", joined)

    def test_all_model_entry_points_load_same_contract(self):
        paths = [
            ROOT / "AGENTS.md",
            ROOT / "CLAUDE.md",
            ROOT / "GEMINI.md",
            ROOT / ".github" / "copilot-instructions.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn(
                    "identities/lux-ex-machina.execution-contract.json",
                    content,
                )

    def test_context_and_receipt_preserve_lineage(self):
        context_fields = set(self.contract["context_snapshot_required_fields"])
        receipt_fields = set(self.contract["execution_receipt_required_fields"])
        self.assertTrue(
            {
                "source_commit",
                "execution_id",
                "retrieved_records",
                "configured_dispositions",
                "relational_commitments",
                "unresolved_work",
                "activation_confirmation",
            }
            <= context_fields
        )
        self.assertTrue(
            {
                "source_commit",
                "context_snapshot_id",
                "activation_confirmation",
                "writeback_status",
                "successor_pointer",
            }
            <= receipt_fields
        )


if __name__ == "__main__":
    unittest.main()
