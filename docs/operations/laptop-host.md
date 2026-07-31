# Caeluviim laptop graph host

The laptop is the persistent Neo4j host. GitHub remains the source of truth for code, schemas, migrations, and ingestion manifests. Notion remains the operations control plane.

## Prerequisite

Install and start Docker Desktop on Windows or macOS, or Docker Engine with Compose on Linux. No separate Python installation is required: graph operations run inside the `operator` container.

## First start and corpus synchronization

From the repository root:

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/start.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/start.sh
```

The startup command:

1. verifies that Docker is running;
2. creates `.env` with a cryptographically generated local password when absent;
3. validates the Compose configuration;
4. starts Neo4j with persistent named volumes;
5. builds the containerized graph operator;
6. applies all migrations; and
7. validates and ingests every production manifest in `ingest/manifests/`.

Neo4j Browser is available at `http://localhost:7474`. Bolt is available at `neo4j://localhost:7687`.

Both ports bind to `127.0.0.1` by default. Other devices cannot connect unless the Compose configuration is deliberately changed.

## Synchronize after repository updates

The start command is idempotent and may be run again after pulling new repository content. Existing migrations and manifests are reported as already applied or already ingested when their hashes match.

Direct operator command:

```bash
docker compose build operator
docker compose --profile operator run --rm operator sync
```

## Status

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/status.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/status.sh
```

The status command checks container state, Neo4j connectivity, and current graph counts.

## Offline backup

Neo4j Community Edition database dumps require the DBMS to be offline. The backup command stops Neo4j, dumps both the `neo4j` and `system` databases, writes SHA-256 checksums, and restarts Neo4j.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/backup.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/backup.sh
```

Backups are written under `backups/<UTC timestamp>/` and are excluded from Git.

## Restore

Use the timestamp directory name shown by the backup command.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/restore.ps1 -BackupName 20260731-170000
```

### macOS or Linux

```bash
bash scripts/laptop/restore.sh 20260731-170000
```

Restore verifies checksums when present, stops Neo4j, loads both databases with overwrite enabled, and restarts the service.

## Stop without deleting data

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/stop.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/stop.sh
```

The named volumes remain intact. Do not run `docker compose down --volumes` unless permanent deletion of the laptop graph is intended.

## Persistent storage

The following fixed Docker volumes constitute the persistent host state:

- `caeluviim_neo4j_data`
- `caeluviim_neo4j_logs`
- `caeluviim_neo4j_import`
- `caeluviim_neo4j_plugins`

Container replacement, repository pulls, and ordinary `docker compose down` operations preserve these volumes. The data volume is removed only by an explicit volume-deletion operation.

## Port conflicts and memory

Edit `.env` when ports `7474` or `7687` are already occupied. The internal container ports remain unchanged.

The default memory allocation is conservative for a laptop:

- initial heap: `512m`
- maximum heap: `1G`
- page cache: `512m`

These values can be raised in `.env` after observing corpus size and laptop memory pressure.
