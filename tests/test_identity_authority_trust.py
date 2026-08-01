from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


class IdentityAuthorityTrustSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority_schema = json.loads(
            (ROOT / "schemas" / "identity-authority.schema.json").read_text("utf-8")
        )
        cls.trust_schema = json.loads(
            (ROOT / "schemas" / "trust.schema.json").read_text("utf-8")
        )
        Draft202012Validator.check_schema(cls.authority_schema)
        Draft202012Validator.check_schema(cls.trust_schema)
        cls.authority_validator = Draft202012Validator(
            cls.authority_schema, format_checker=FormatChecker()
        )
        cls.trust_validator = Draft202012Validator(
            cls.trust_schema, format_checker=FormatChecker()
        )

    def assert_valid(self, validator: Draft202012Validator, instance: dict) -> None:
        errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def assert_invalid(self, validator: Draft202012Validator, instance: dict) -> None:
        self.assertTrue(list(validator.iter_errors(instance)))

    def test_active_identity_is_valid(self) -> None:
        self.assert_valid(
            self.authority_validator,
            {
                "record_type": "identity",
                "record_id": "identity-record:validator:1",
                "provenance_id": "provenance:identity:1",
                "created_at": "2026-08-01T00:00:00Z",
                "identity_id": "identity:validator:1",
                "identity_type": "validator",
                "status": "active",
                "key_ids": ["key:validator:1"],
            },
        )

    def test_delegation_requires_authority_basis(self) -> None:
        record = {
            "record_type": "delegation",
            "record_id": "delegation-record:1",
            "provenance_id": "provenance:delegation:1",
            "created_at": "2026-08-01T00:00:00Z",
            "delegation_id": "delegation:1",
            "grantor_identity_id": "identity:steward:1",
            "grantee_identity_id": "identity:operator:1",
            "capability_ids": ["capability:ingest"],
            "scope": "repository:Caeluviim/Caeluviim",
            "effective_at": "2026-08-01T00:00:00Z",
            "delegation_depth": 0,
        }
        self.assert_invalid(self.authority_validator, record)

    def test_trust_observation_requires_evidence_and_method(self) -> None:
        record = {
            "record_type": "trust_observation",
            "record_id": "trust-observation:1",
            "subject_identity_id": "identity:validator:1",
            "dimension": "constraint_compliance",
            "scope": "module:emgn",
            "value": 1.0,
            "confidence": 0.9,
            "provenance_id": "provenance:trust:1",
            "created_at": "2026-08-01T00:00:00Z",
        }
        self.assert_invalid(self.trust_validator, record)

    def test_trust_value_outside_unit_interval_is_invalid(self) -> None:
        record = {
            "record_type": "trust_assessment",
            "record_id": "trust-assessment:1",
            "subject_identity_id": "identity:validator:1",
            "dimension": "validation_accuracy",
            "scope": "module:emgn",
            "value": 1.1,
            "confidence": 0.8,
            "assessor_identity_id": "identity:steward:1",
            "evidence_ids": ["evidence:validation:1"],
            "method": "independent-review",
            "provenance_id": "provenance:trust:2",
            "created_at": "2026-08-01T00:00:00Z",
        }
        self.assert_invalid(self.trust_validator, record)


if __name__ == "__main__":
    unittest.main()
