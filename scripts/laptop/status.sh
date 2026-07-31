#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

docker compose ps
state="$(docker inspect --format '{{.State.Status}}' caeluviim-neo4j 2>/dev/null || true)"
if [[ "$state" != "running" ]]; then
  echo "The Caeluviim Neo4j container is not running." >&2
  exit 1
fi

docker compose --profile operator run --rm --no-deps operator health
docker compose --profile operator run --rm --no-deps operator stats
