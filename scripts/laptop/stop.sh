#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

docker compose stop neo4j
echo "Caeluviim Neo4j is stopped. Persistent volumes were preserved."
