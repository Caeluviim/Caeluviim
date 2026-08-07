"""Direct module entry point for Caeluviim's graph runtime.

This makes `python -m caeluviim_graph ...` execute the existing CLI instead of
requiring callers to know the internal `caeluviim_graph.cli` module path.
"""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
