#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/laptop/restore.sh <backup-folder-name>" >&2
  exit 1
fi

backup_name="$1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

backup_root="$(cd backups && pwd)"
selected="$(cd "backups/$backup_name" && pwd)"
case "$selected" in
  "$backup_root"/*) ;;
  *) echo "Backup must be a directory beneath $backup_root." >&2; exit 1 ;;
esac

for file in neo4j.dump system.dump; do
  if [[ ! -f "$selected/$file" ]]; then
    echo "Backup is incomplete: missing $file." >&2
    exit 1
  fi
done

if [[ -f "$selected/SHA256SUMS.txt" ]]; then
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$selected" && sha256sum --check SHA256SUMS.txt)
  else
    (cd "$selected" && shasum -a 256 --check SHA256SUMS.txt)
  fi
fi

wait_for_neo4j() {
  local status=""
  for _ in $(seq 1 90); do
    status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' caeluviim-neo4j 2>/dev/null || true)"
    if [[ "$status" == "healthy" ]]; then
      return 0
    fi
    if [[ "$status" == "unhealthy" || "$status" == "exited" || "$status" == "dead" ]]; then
      docker logs --tail 100 caeluviim-neo4j >&2 || true
      echo "Neo4j entered terminal state: $status" >&2
      return 1
    fi
    sleep 2
  done

  docker logs --tail 100 caeluviim-neo4j >&2 || true
  echo "Neo4j did not become healthy within 180 seconds." >&2
  return 1
}

stopped=0
restart_graph() {
  if [[ "$stopped" -eq 1 ]]; then
    docker compose up -d neo4j >/dev/null
  fi
}
trap restart_graph EXIT

docker compose stop neo4j
stopped=1

docker compose --profile admin run --rm neo4j-admin \
  database load --from-path="/backups/$backup_name" neo4j --overwrite-destination=true

docker compose --profile admin run --rm neo4j-admin \
  database load --from-path="/backups/$backup_name" system --overwrite-destination=true

docker compose up -d neo4j
stopped=0
wait_for_neo4j

echo "Restore complete and Neo4j healthy from $selected"
