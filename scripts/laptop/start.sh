#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker Desktop or Docker Engine is not installed or docker is not on PATH." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop or Docker Engine and run this command again." >&2
  exit 1
fi

if [[ ! -f .env ]]; then
  if command -v openssl >/dev/null 2>&1; then
    password="$(openssl rand -hex 24)"
  else
    password="$(od -An -N24 -tx1 /dev/urandom | tr -d ' \n')"
  fi

  cat > .env <<EOF
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=$password
NEO4J_DATABASE=neo4j
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
NEO4J_HEAP_INITIAL=512m
NEO4J_HEAP_MAX=1G
NEO4J_PAGECACHE=512m
EOF
  chmod 600 .env 2>/dev/null || true
  echo "Created .env with a generated local Neo4j password."
fi

if grep -q '^NEO4J_PASSWORD=replace-with-a-strong-local-password$' .env; then
  echo "Replace the placeholder NEO4J_PASSWORD in .env before starting the graph." >&2
  exit 1
fi

mkdir -p backups

docker compose config --quiet
docker compose up -d neo4j
docker compose build operator
docker compose --profile operator run --rm operator sync

echo
echo "Caeluviim graph host is operational."
echo "Neo4j Browser: http://localhost:7474"
echo "Bolt endpoint: neo4j://localhost:7687"
echo "Credentials are stored only in .env on this laptop."
