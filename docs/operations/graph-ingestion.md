# Caeluviim graph ingestion operations

## System boundary

- The repository is the source of truth for schemas, migrations, validation contracts, examples, tests, and runtime code.
- Neo4j is the authoritative operational graph and analytical projection.
- Notion coordinates work and records pointers; it is not the semantic graph.
- Whiteboard objects remain proposals until represented by a validated ingestion manifest.

## Start the graph

```bash
cp .env.example .env
# Change NEO4J_PASSWORD before any shared or internet-reachable deployment.
docker compose up -d neo4j
python -m pip install -r requirements-dev.txt
python -m caeluviim_graph.cli bootstrap
```

Neo4j Browser is available at `http://localhost:7474`. Bolt is available at `neo4j://localhost:7687`.

## Ingestion lifecycle

1. Capture source material without editing the source.
2. Compute and record a SHA-256 content hash.
3. Assign stable URI identifiers to the ingestion event, source, nodes, and relationship assertions.
4. Validate the manifest against `schemas/ingest-manifest.schema.json`.
5. Apply graph migrations.
6. Execute the entire ingest in one Neo4j transaction.
7. Reject identifier reuse when the stored record hash differs.
8. Link every ingested entity and reified relationship assertion to its source and ingestion event.
9. Record revisions as new entities connected with `REVISES` or `SUPERSEDES`; do not overwrite prior assertions.

## Commands

```bash
python -m caeluviim_graph.cli health
python -m caeluviim_graph.cli migrate
python -m caeluviim_graph.cli validate examples/ingest-manifest.valid.json
python -m caeluviim_graph.cli ingest examples/ingest-manifest.valid.json
python -m caeluviim_graph.cli stats
```

`bootstrap` combines health verification, migrations, seed ingestion, and graph counts.

## Safety invariants

- Dynamic labels and relationship types are accepted only from explicit allowlists.
- All semantic nodes carry the common `Entity` label and globally unique `id`.
- Every relationship is accompanied by a globally addressable `RelationAssertion` node.
- Ingestions and migrations are idempotent when content hashes match.
- Reusing an identifier with different content fails the transaction.
- User properties cannot overwrite reserved provenance, hash, identity, or timestamp fields.
- A failed ingest leaves no partial graph mutation.
