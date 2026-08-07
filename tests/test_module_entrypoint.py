import subprocess
import sys
import unittest


class ModuleEntrypointTest(unittest.TestCase):
    def test_python_m_caeluviim_graph_exposes_cli(self):
        result = subprocess.run(
            [sys.executable, "-m", "caeluviim_graph", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("caeluviim-graph", result.stdout)
        self.assertIn("recall", result.stdout)
        self.assertIn("sync", result.stdout)


if __name__ == "__main__":
    unittest.main()
