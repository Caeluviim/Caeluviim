# Caeluviim persistent graph memory

## Purpose

The graph memory layer makes previously ingested records operationally available to later reasoning. It performs bounded retrieval over the persistent Neo4j graph and returns:

- matching entities;
- complete stored properties;
- source provenance;
- bounded nearby graph context;
- recent graph chronology.

Retrieval does not ratify a claim, resolve a contest, or establish truth. It exposes recorded material and its relations so that a later operator or interlocutor can reason from an explicit persistent state rather than reconstructing history from scratch.

## Prerequisite

Start and synchronize the graph runtime:

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/start.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/start.sh
```

The startup procedure validates the production manifest catalog, applies migrations, synchronizes all manifests, and writes runtime ingestion receipts.

## Recall by text

```bash
docker compose --profile operator run --rm operator recall "functional identity"
```

The default response returns up to 10 matching entities and up to 8 related entities at graph depth 1.

Bound the query explicitly:

```bash
docker compose --profile operator run --rm operator recall \
  "plasma standing" \
  --limit 5 \
  --depth 2 \
  --context-limit 12 \
  --label Claim
```

Limits:

- result limit: 1–50 for `recall`;
- context depth: 0–3;
- context entities per match: 0–50;
- repeated `--label` arguments create an inclusive label filter.

Depth 0 returns matching entities and provenance without neighborhood expansion.

## Retrieve one entity

```bash
docker compose --profile operator run --rm operator entity \
  "urn:caeluviim:claim:example"
```

The result includes:

- labels and properties;
- provenance sources;
- direct incoming relations;
- direct outgoing relations.

The command exits with status 1 when the identifier is not present.

## Retrieve a graph neighborhood

```bash
docker compose --profile operator run --rm operator neighbors \
  "urn:caeluviim:claim:example" \
  --depth 2 \
  --limit 50
```

Neighborhood expansion is deliberately bounded to depth 1–3 and at most 200 returned related entities.

## Retrieve recent graph state

```bash
docker compose --profile operator run --rm operator timeline --limit 20
```

The timeline orders entities by their graph update or creation timestamp. This is ingestion chronology, not necessarily the chronology of the represented event.

## Memory model

The operational loop is:

```text
source material
  -> validated manifest
  -> transactional graph ingestion
  -> provenance and receipt
  -> bounded recall
  -> reasoned use or revision
  -> new source material and manifest
```

A repository file is archival memory. A record becomes operative memory when it is ingested, retrieved under a later query, and materially constrains later reasoning or action.

## Failure procedure

When recall fails:

1. Run `docker compose --profile operator run --rm operator health`.
2. Run `docker compose --profile operator run --rm operator stats`.
3. Run `docker compose --profile operator run --rm operator audit-receipts`.
4. Confirm the expected source appears under `ingest/manifests/`.
5. Run `docker compose --profile operator run --rm operator sync`.
6. Repeat the recall with a broader text query or without a label filter.

A successful health check with zero or unexpectedly low entity counts indicates incomplete synchronization rather than a retrieval-layer failure.

## Security boundary

The operator connects to the local Neo4j runtime using credentials stored in `.env`. Do not commit `.env`, Neo4j credentials, generated runtime receipts containing sensitive runtime identifiers, or backup contents.
