from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "lux-dispositional-reconstruction.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "lux-dispositional-reconstruction.valid.json"


def canonical_step_hash(step: dict[str, Any]) -> str:
    candidate = dict(step)
    candidate.pop("step_hash", None)
    payload = json.dumps(
        candidate,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def validate_traversal_chain(steps: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    expected_ordinals = list(range(len(steps)))
    actual_ordinals = [step["ordinal"] for step in steps]
    if actual_ordinals != expected_ordinals:
        errors.append(
            f"ordinals must be contiguous from zero: expected {expected_ordinals}, got {actual_ordinals}"
        )

    for index, step in enumerate(steps):
        calculated = canonical_step_hash(step)
        if step["step_hash"] != calculated:
            errors.append(
                f"step {step['step_id']} hash mismatch: expected {calculated}, got {step['step_hash']}"
            )

        if index == 0:
            if "previous_step_hash" in step:
                errors.append(f"genesis step {step['step_id']} must not have previous_step_hash")
        elif step.get("previous_step_hash") != steps[index - 1]["step_hash"]:
            errors.append(
                f"step {step['step_id']} does not reference the immediately preceding step hash"
            )

    return errors


class LuxDispositionalReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_example_conforms_to_json_schema(self) -> None:
        validator = Draft202012Validator(
            self.schema,
            format_checker=FormatChecker(),
        )
        errors = sorted(
            validator.iter_errors(self.example),
            key=lambda error: list(error.absolute_path),
        )
        self.assertEqual(
            [],
            [
                f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
                for error in errors
            ],
        )

    def test_instantiation_generates_declared_reconstruction(self) -> None:
        traversal = self.example["instantiation_traversal"]
        reconstruction = self.example["reconstruction"]
        self.assertEqual(
            traversal["resulting_reconstruction_id"],
            reconstruction["reconstruction_id"],
        )
        self.assertEqual(
            traversal["traversal_id"],
            reconstruction["generated_by_instantiation_traversal_id"],
        )
        self.assertEqual(
            self.example["lux_identity"]["identity_id"],
            traversal["lux_identity_id"],
        )

    def test_epistemic_traversal_is_performed_by_declared_reconstruction(self) -> None:
        self.assertEqual(
            self.example["reconstruction"]["reconstruction_id"],
            self.example["epistemic_traversal"]["performed_by_reconstruction_id"],
        )

    def test_stabilization_and_materialization_lineage(self) -> None:
        self.assertEqual(
            self.example["epistemic_traversal"]["traversal_id"],
            self.example["stabilization"]["epistemic_traversal_id"],
        )
        self.assertEqual(
            self.example["stabilization"]["stabilization_id"],
            self.example["materialization"]["stabilization_id"],
        )
        self.assertEqual(
            self.example["reconstruction"]["reconstruction_id"],
            self.example["materialization"]["performed_by_reconstruction_id"],
        )

    def test_instantiation_hash_chain(self) -> None:
        self.assertEqual(
            [],
            validate_traversal_chain(self.example["instantiation_traversal"]["steps"]),
        )

    def test_epistemic_hash_chain(self) -> None:
        self.assertEqual(
            [],
            validate_traversal_chain(self.example["epistemic_traversal"]["steps"]),
        )


if __name__ == "__main__":
    unittest.main()
