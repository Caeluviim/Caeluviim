# Caeluviim persistent graph memory

## Purpose

The memory layer makes previously encoded records operationally available to later reasoning. It returns:

- matching entities;
- complete stored properties;
- source provenance;
- bounded nearby graph context;
- recent capture or ingestion chronology.

Retrieval does not ratify a claim, resolve a contest, or establish truth. It exposes recorded material and its relations so that a later operator or interlocutor can reason from an explicit persistent state rather than reconstructing history from scratch.

## Backends

### Repository backend

The repository backend reconstructs the complete queryable topology directly from validated files under `ingest/manifests/`. It requires no Neo4j server, Docker runtime, Codex session, or external AI service.

It materializes in memory:

- source entities;
- ingestion-event entities;
- every declared node;
- every reified relationship assertion;
- direct declared relationships;
- provenance links;
- assertion endpoint links;
- ingestion lineage.

The projection is deterministic and read-only. The test suite verifies that its entity and relationship counts equal the topology produced by the ingestion algorithm for the current corpus.

### Neo4j backend

The Neo4j backend uses the persistent database runtime. It adds database indexes, durable local state, runtime-generated ingestion receipts, conflict detection against existing records, backup and restore, and better scaling for larger traversals.

### Automatic selection

Memory commands default to `--backend auto`:

1. use Neo4j when the configured runtime is reachable;
2. otherwise reconstruct memory from the repository manifests.

Use `--backend neo4j` or `--backend repository` when verification must target one specific layer.

## Repository-only recall

Install the Python dependencies once:

```bash
python -m pip install -r requirements-dev.txt
```

Recall without Docker or Neo4j:

```bash
python -m caeluviim_graph.cli recall \
  "functional identity" \
  --backend repository
```

Bound and filter the query:

```bash
python -m caeluviim_graph.cli recall \
  "plasma standing" \
  --backend repository \
  --limit 5 \
  --depth 2 \
  --context-limit 12 \
  --label Claim
```

## GitHub-only recall from a phone

The workflow `.github/workflows/repository-memory.yml` executes repository memory without a laptop runtime.

1. Open the repository in GitHub.
2. Open **Actions**.
3. Select **Repository memory recall**.
4. Select **Run workflow**.
5. Enter the query and optional label, limit, depth, and context limit.
6. Open the completed workflow run.
7. Read the JSON in the **Recall committed memory** log or download the `repository-memory-result` artifact.

This path uses GitHub Actions and committed repository files. It does not use Codex or Neo4j.

## Neo4j startup

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/start.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/start.sh
```

The startup procedure validates the production manifest catalog, applies migrations, synchronizes all manifests, and writes runtime ingestion receipts.

Recall explicitly from Neo4j:

```bash
docker compose --profile operator run --rm operator recall \
  "functional identity" \
  --backend neo4j
```

## Query limits

- recall result limit: 1–50;
- search result limit: 1–100;
- context depth: 0–3;
- context entities per match: 0–50;
- neighborhood result limit: 1–200;
- repeated `--label` arguments create an inclusive label filter.

Depth 0 returns matching entities and provenance without neighborhood expansion.

## Retrieve one entity

Repository backend:

```bash
python -m caeluviim_graph.cli entity \
  "urn:caeluviim:claim:example" \
  --backend repository
```

Neo4j backend:

```bash
docker compose --profile operator run --rm operator entity \
  "urn:caeluviim:claim:example" \
  --backend neo4j
```

The result includes labels, properties, provenance sources, and direct incoming and outgoing relations. The command exits with status 1 when the identifier is not present.

## Retrieve a neighborhood

```bash
python -m caeluviim_graph.cli neighbors \
  "urn:caeluviim:claim:example" \
  --backend repository \
  --depth 2 \
  --limit 50
```

## Retrieve recent memory state

```bash
python -m caeluviim_graph.cli timeline \
  --backend repository \
  --limit 20
```

Repository chronology uses source capture timestamps. Neo4j chronology uses graph creation or update timestamps. Neither necessarily equals the chronology of the represented event.

## Inspect capacity

```bash
python -m caeluviim_graph.cli memory-stats --backend repository
```

The output reports the number of validated manifests, projected entities, and projected relationships. Capacity grows with committed manifests; the projection is not limited to the current corpus size.

## Memory model

```text
source material
  -> validated manifest
  -> committed repository memory
  -> repository recall
  -> optional Neo4j synchronization and runtime receipt
  -> bounded recall
  -> reasoned use or revision
  -> new source material and manifest
```

A committed manifest is durable encoded memory. It becomes operative memory when retrieval exposes it under a later query and it materially constrains later reasoning or action.

## Failure procedure

Repository backend:

1. Run `python -m caeluviim_graph.cli catalog`.
2. Run `python -m caeluviim_graph.cli memory-stats --backend repository`.
3. Confirm the expected source appears under `ingest/manifests/`.
4. Repeat recall with broader text or without a label filter.

Neo4j backend:

1. Run `docker compose --profile operator run --rm operator health`.
2. Run `docker compose --profile operator run --rm operator stats`.
3. Run `docker compose --profile operator run --rm operator audit-receipts`.
4. Run `docker compose --profile operator run --rm operator sync`.
5. Repeat recall with `--backend neo4j`.

A successful repository recall with a failed Neo4j recall isolates the problem to runtime activation or synchronization rather than the committed memory corpus.

## Security boundary

The repository backend reads only committed manifests and schemas. The Neo4j operator connects using credentials stored in `.env`. Do not commit `.env`, Neo4j credentials, sensitive runtime identifiers, or backup contents.
