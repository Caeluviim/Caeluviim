# Caeluviim

Caeluviim is a provenance-tracked formal architecture for representing claims, agents, relations, evidence, governance, revision, and the construction of new reachable futures.

## Implemented formal modules

| Module | Status | Primary specification | Machine constraints |
|---|---|---|---|
| Error-Mediated Generative Non-Closure | Proposed v0.1.0 | [`docs/architecture/error-mediated-generative-nonclosure.md`](docs/architecture/error-mediated-generative-nonclosure.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests |

## Working graph runtime

The repository now contains a runnable Neo4j ingestion path:

- Neo4j Community 2026.06 through Docker Compose
- idempotent Cypher migrations
- a JSON Schema ingestion contract
- transactional, append-only ingestion with content-conflict detection
- provenance links for every entity and reified relationship assertion
- a conforming bootstrap manifest
- CI that starts Neo4j, applies migrations, ingests the seed twice, and verifies idempotency

```bash
cp .env.example .env
# Change the password before any shared deployment.
docker compose up -d neo4j
python -m pip install -r requirements-dev.txt
python -m caeluviim_graph.cli bootstrap
```

See [`docs/operations/graph-ingestion.md`](docs/operations/graph-ingestion.md) for the operating contract and ingestion lifecycle.

## Repository structure

- `caeluviim_graph/` — graph runtime, validation, migrations, and CLI orchestration
- `graph/migrations/` — ordered Neo4j schema migrations
- `docs/architecture/` — normative architecture specifications
- `docs/operations/` — executable operating procedures
- `schemas/` — JSON Schema validation contracts
- `ontology/` — RDF/OWL vocabulary
- `shapes/` — SHACL graph constraints
- `examples/` — conforming instance and ingestion records
- `tests/` — executable structural and graph-ingestion validation

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
pyshacl -s shapes/emgn.shacl.ttl -e ontology/emgn.ttl examples/emgn-record.valid.ttl
python -m caeluviim_graph.cli validate examples/ingest-manifest.valid.json
```

## Governance state

The EMGN module is implemented but remains **proposed**, not ratified. Ratification requires two independent validators who are not the proposer, with provenance recorded in the module's governance record.

The graph runtime is an operational implementation substrate. Loading a record does not ratify its semantic or governance claims; those states must be represented explicitly in the ingested material.
