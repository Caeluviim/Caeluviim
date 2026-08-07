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
        version_parts = self.identity["version"].split(".")
        self.assertEqual(3, len(version_parts))
        self.assertTrue(all(part.isdigit() for part in version_parts))
        self.assertGreaterEqual(tuple(map(int, version_parts)), (1, 1, 0))

    def test_repository_is_authoritative_and_writeback_is_required(self):
        joined = "\n".join(self.contract["completion_invariants"])
        self.assertIn("repository remains authoritative", joined)
        self.assertIn("portable write packet", joined)
        self.assertIn("successor state", joined)

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
            {"source_commit", "execution_id", "retrieved_records", "unresolved_work"}
            <= context_fields
        )
        self.assertTrue(
            {"source_commit", "execution_id", "action", "successor_state", "writeback"}
            <= receipt_fields
        )


if __name__ == "__main__":
    unittest.main()
