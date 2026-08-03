from __future__ import annotations

import json
import unittest
from pathlib import Path

from caeluviim_graph.legal_drafting import LegalDraftError, render_complaint, validate_case_record


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "legal" / "minimum-case-record.json"


class LegalDraftingTests(unittest.TestCase):
    def load_example(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_validates_and_renders_deterministically(self) -> None:
        record = self.load_example()
        normalized = validate_case_record(record)
        first = render_complaint(normalized)
        second = render_complaint(normalized)
        self.assertEqual(first, second)
        self.assertIn("COMPLAINT", first)
        self.assertIn("FACTUAL ALLEGATIONS", first)
        self.assertIn("[Sources: urn:caeluviim:evidence:example-1]", first)
        self.assertIn("machine-generated draft; not filed", first)

    def test_fact_without_source_is_rejected(self) -> None:
        record = self.load_example()
        record["facts"][0]["source_ids"] = []
        with self.assertRaisesRegex(LegalDraftError, "source_ids"):
            validate_case_record(record)

    def test_unknown_fact_reference_is_rejected(self) -> None:
        record = self.load_example()
        record["causes_of_action"][0]["incorporates"] = ["F404"]
        with self.assertRaisesRegex(LegalDraftError, "unknown facts"):
            validate_case_record(record)

    def test_duplicate_fact_ids_are_rejected(self) -> None:
        record = self.load_example()
        record["facts"][1]["id"] = "F1"
        with self.assertRaisesRegex(LegalDraftError, "duplicate fact id"):
            validate_case_record(record)

    def test_missing_provenance_is_rejected(self) -> None:
        record = self.load_example()
        del record["provenance"]["source_commit"]
        with self.assertRaisesRegex(LegalDraftError, "source_commit"):
            validate_case_record(record)


if __name__ == "__main__":
    unittest.main()
