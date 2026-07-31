import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "repository-write-policy.json"
AGENTS_PATH = ROOT / "AGENTS.md"
README_PATH = ROOT / "README.md"


class TestRepositoryWritePolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_default_branch_is_never_a_write_target(self) -> None:
        self.assertEqual(self.policy["default_branch"], "main")
        self.assertFalse(self.policy["direct_default_branch_writes_allowed"])
        self.assertTrue(self.policy["require_explicit_branch_on_every_mutation"])
        self.assertTrue(self.policy["require_task_branch_before_write"])
        self.assertTrue(self.policy["require_pull_request"])

    def test_mutations_cannot_be_used_as_probes(self) -> None:
        self.assertFalse(self.policy["mutation_as_probe_allowed"])
        self.assertFalse(self.policy["placeholder_payloads_allowed"])
        forbidden = {value.lower() for value in self.policy["forbidden_placeholder_values"]}
        self.assertIn("noop", forbidden)
        self.assertIn("# noop", forbidden)

    def test_update_and_delete_require_verification(self) -> None:
        self.assertTrue(self.policy["require_prewrite_fetch_for_update_or_delete"])
        self.assertTrue(self.policy["require_postwrite_fetch_verification"])
        self.assertTrue(self.policy["require_changed_file_review"])

    def test_readme_is_not_placeholder_content(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("# Caeluviim\n"))
        self.assertGreater(len(content), 500)
        self.assertNotEqual(content.strip().lower(), "# noop")

    def test_agent_policy_contains_failure_reporting_invariant(self) -> None:
        content = AGENTS_PATH.read_text(encoding="utf-8")
        self.assertIn("Never report a failure as a bare restatement", content)
        self.assertIn("correction applied", content)
        self.assertIn("required corrective action", content)

    def test_protected_paths_require_acknowledgment_and_rollback(self) -> None:
        requirements = self.policy["protected_path_requirements"]
        self.assertTrue(requirements["dedicated_pull_request"])
        self.assertEqual(
            requirements["acknowledgment_marker"],
            "Protected-Path-Change: acknowledged",
        )
        self.assertEqual(requirements["rollback_plan_marker"], "Rollback-Plan:")


if __name__ == "__main__":
    unittest.main()
