#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env. Run scripts/laptop/start.sh first." >&2
  exit 1
fi

stamp="$(date -u +%Y%m%d-%H%M%S)"
host_backup="backups/$stamp"
mkdir -p "$host_backup"
stopped=0

restart_graph() {
  if [[ "$stopped" -eq 1 ]]; then
    docker compose up -d neo4j >/dev/null
  fi
}
trap restart_graph EXIT

docker compose stop neo4j
stopped=1

# The dump operation is read-only against /data. Running this container as root
# avoids host bind-mount UID/GID mismatches on Linux and Docker Desktop.
docker compose --profile admin run --rm --user root neo4j-admin \
  database dump neo4j --to-path="/backups/$stamp" --overwrite-destination=true

docker compose --profile admin run --rm --user root neo4j-admin \
  database dump system --to-path="/backups/$stamp" --overwrite-destination=true

# Normalize exported dump permissions so the host user can checksum and archive them.
docker run --rm \
  --mount "type=bind,source=$ROOT/$host_backup,target=/backup" \
  alpine:3.22 chmod -R a+rX /backup

if command -v sha256sum >/dev/null 2>&1; then
  (cd "$host_backup" && sha256sum ./*.dump > SHA256SUMS.txt)
else
  (cd "$host_backup" && shasum -a 256 ./*.dump > SHA256SUMS.txt)
fi

echo "Backup complete: $ROOT/$host_backup"
