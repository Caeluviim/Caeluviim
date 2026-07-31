from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from caeluviim.native_graph import NativeNeo4j


class NativeGraphConfigurationTests(unittest.TestCase):
    def test_credentials_are_private_and_stable(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            native = NativeNeo4j(Path(temporary))
            first = native._credentials(create=True)
            second = native._credentials(create=False)
            self.assertEqual(first, second)
            self.assertEqual(
                native.paths.credentials.stat().st_mode & 0o777,
                0o600,
            )
            self.assertEqual(first["user"], "neo4j")
            self.assertGreaterEqual(len(first["password"]), 32)

    def test_environment_uses_separate_instance_configuration(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            native = NativeNeo4j(Path(temporary))
            environment = native.environment()
            self.assertEqual(
                environment["NEO4J_CONF"],
                str(native.paths.instance / "conf"),
            )
            self.assertEqual(environment["JAVA_HOME"], str(native.paths.java_home))


if __name__ == "__main__":
    unittest.main()
