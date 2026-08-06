import unittest
from pathlib import Path

from caeluviim_graph.cli import build_parser
from caeluviim_graph.memory import GraphMemory, MemoryQueryError, RecallRequest
from caeluviim_graph.repository_memory import RepositoryMemory

ROOT = Path(__file__).resolve().parents[1]


class FakeMemory(GraphMemory):
    def __init__(self):
        pass

    def search(self, text, *, limit=20, labels=None):
        return [
            {
                "id": "urn:caeluviim:test:memory-1",
                "labels": ["Claim"],
                "properties": {"text": text},
                "provenance": [],
            }
        ][:limit]

    def neighbors(self, entity_id, *, depth=1, limit=50):
        return {
            "id": entity_id,
            "neighbors": [
                {
                    "id": "urn:caeluviim:test:context-1",
                    "distance": depth,
                    "relationship_types": ["SUPPORTS"],
                }
            ][:limit],
        }


class TestRecallRequest(unittest.TestCase):
    def test_request_is_bounded_and_normalised(self):
        request = RecallRequest(
            text="  plasma standing  ",
            limit=12,
            depth=2,
            context_limit=7,
            labels=("Claim", "Claim", " Evidence "),
        ).validated()
        self.assertEqual("plasma standing", request.text)
        self.assertEqual(("Claim", "Evidence"), request.labels)
        self.assertEqual(2, request.depth)

    def test_invalid_depth_fails_closed(self):
        with self.assertRaises(MemoryQueryError):
            RecallRequest(text="x", depth=4).validated()

    def test_invalid_limit_fails_closed(self):
        with self.assertRaises(MemoryQueryError):
            RecallRequest(text="x", limit=0).validated()


class TestGraphMemoryRecall(unittest.TestCase):
    def test_recall_attaches_bounded_context(self):
        result = FakeMemory().recall(
            RecallRequest(text="identity", depth=1, context_limit=1)
        )
        self.assertEqual(1, result["match_count"])
        self.assertEqual("identity", result["matches"][0]["properties"]["text"])
        self.assertEqual(
            "urn:caeluviim:test:context-1",
            result["matches"][0]["context"][0]["id"],
        )

    def test_zero_depth_disables_context_expansion(self):
        result = FakeMemory().recall(
            RecallRequest(text="identity", depth=0, context_limit=8)
        )
        self.assertEqual([], result["matches"][0]["context"])


class TestRepositoryMemory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.memory = RepositoryMemory(
            ROOT / "ingest" / "manifests",
            ROOT / "schemas" / "ingest-manifest.schema.json",
        )

    def test_repository_projection_matches_runtime_topology(self):
        self.assertEqual(
            {"entities": 627, "relationships": 2361, "manifests": 8},
            self.memory.stats(),
        )

    def test_repository_recall_requires_no_database(self):
        result = self.memory.recall(
            RecallRequest(text="rrkc", limit=3, depth=1, context_limit=5)
        )
        self.assertEqual("repository", result["backend"])
        self.assertGreater(result["match_count"], 0)
        self.assertTrue(result["matches"][0]["context"])

    def test_relationship_assertions_are_operable_entities(self):
        matches = self.memory.search("SUPPORTS", limit=10, labels=["RelationAssertion"])
        self.assertTrue(matches)
        entity = self.memory.entity(matches[0]["id"])
        self.assertIsNotNone(entity)
        self.assertIn("RelationAssertion", entity["labels"])
        self.assertTrue(entity["provenance"])


class TestMemoryCli(unittest.TestCase):
    def test_recall_command_parses(self):
        args = build_parser().parse_args(
            [
                "recall",
                "functional identity",
                "--limit",
                "5",
                "--depth",
                "2",
                "--label",
                "Claim",
                "--backend",
                "repository",
            ]
        )
        self.assertEqual("recall", args.command)
        self.assertEqual(5, args.limit)
        self.assertEqual(2, args.depth)
        self.assertEqual(["Claim"], args.label)
        self.assertEqual("repository", args.backend)


if __name__ == "__main__":
    unittest.main()
