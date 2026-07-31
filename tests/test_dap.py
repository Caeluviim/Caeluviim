from __future__ import annotations

import unittest

from caeluviim.dap import (
    UNKNOWN,
    aggregate_authority,
    evaluate_expression,
    ratio_satisfied,
    resolve_path,
    scope_contains,
)


class DapPrimitiveTests(unittest.TestCase):
    def test_paths_and_three_valued_logic(self) -> None:
        context = {
            "candidate": {"status": "active", "weights": [2, 3, 3]},
            "now": "2026-07-25T12:00:00Z",
        }
        self.assertEqual(resolve_path(context, "/candidate/status"), "active")
        self.assertIs(resolve_path(context, "/candidate/missing"), UNKNOWN)
        self.assertTrue(
            evaluate_expression(
                {
                    "all": [
                        {"eq": [{"path": "/candidate/status"}, "active"]},
                        {"gte": [{"path": "/now"}, "2026-01-01T00:00:00Z"]},
                    ]
                },
                context,
            )
        )
        self.assertIs(
            evaluate_expression(
                {"all": [True, {"path": "/candidate/missing"}]}, context
            ),
            UNKNOWN,
        )

    def test_scope_ratio_and_authority_aggregation(self) -> None:
        self.assertTrue(scope_contains(["district", "alpha"], ["district", "alpha", "case"]))
        self.assertFalse(scope_contains(["district", "*"], ["district", "alpha"]))
        self.assertTrue(
            scope_contains(["district", "*"], ["district", "alpha"], wildcard_enabled=True)
        )
        self.assertTrue(ratio_satisfied(7, 10, {"numerator": 2, "denominator": 3}))
        self.assertFalse(ratio_satisfied(6, 10, {"numerator": 2, "denominator": 3}))
        self.assertEqual(
            aggregate_authority(
                [
                    {"rootIssuer": "issuer:a", "weight": 40},
                    {"rootIssuer": "issuer:a", "weight": 30},
                    {"rootIssuer": "issuer:b", "weight": 45},
                ],
                "sum_capped",
                100,
                minimum_weight=35,
            ),
            {"weight": 85, "rootIssuers": 2, "qualifyingRootIssuers": 2},
        )


if __name__ == "__main__":
    unittest.main()
