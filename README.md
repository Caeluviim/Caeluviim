# Caeluviim

Caeluviim is a provenance-tracked formal architecture for representing claims, agents, relations, evidence, governance, revision, and the construction of new reachable futures.

## Implemented formal modules

| Module | Status | Primary specification | Machine constraints |
|---|---|---|---|
| Error-Mediated Generative Non-Closure | Proposed v0.1.0 | [`docs/architecture/error-mediated-generative-nonclosure.md`](docs/architecture/error-mediated-generative-nonclosure.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests |
| RRKC closed formal calculus | Proposed v2.0.0 | [`docs/architecture/rrkc-r2-formal-specification.md`](docs/architecture/rrkc-r2-formal-specification.md) | Ott source, Lean target, executable reference, JSON Schema, OWL/RDF, SHACL, graph manifest, tests |

## Working graph runtime

The repository contains a persistent laptop-host Neo4j ingestion system:

- Neo4j Community 2026.06 through Docker Compose
- persistent named volumes for graph state
- localhost-only HTTP and Bolt bindings by default
- idempotent Cypher migrations
- a JSON Schema ingestion contract
- transactional, append-only ingestion with content-conflict detection
- provenance links for every entity and reified relationship assertion
- a containerized operator that requires no host Python installation
- offline backup and restore commands for both `neo4j` and `system`
- CI that starts Neo4j, validates the laptop configuration, synchronizes the corpus twice, and verifies idempotency

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File scripts/laptop/start.ps1
```

### macOS or Linux

```bash
bash scripts/laptop/start.sh
```

The startup command creates a protected local `.env` when absent, starts Neo4j, applies migrations, and ingests every production manifest.

See [`docs/operations/laptop-host.md`](docs/operations/laptop-host.md) for start, status, backup, restore, and shutdown procedures. See [`docs/operations/graph-ingestion.md`](docs/operations/graph-ingestion.md) for the ingestion contract and lifecycle.

## Repository structure

- `caeluviim_graph/` — graph runtime, validation, migrations, and CLI orchestration
- `graph/migrations/` — ordered Neo4j schema migrations
- `ingest/manifests/` — production corpus manifests
- `scripts/laptop/` — laptop-host lifecycle, backup, and restore commands
- `docs/architecture/` — normative architecture specifications
- `docs/operations/` — executable operating procedures
- `formal/` — formal-language sources, proof targets, and executable reference semantics
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
pyshacl -s shapes/rrkc.shacl.ttl -e ontology/rrkc.ttl examples/rrkc-r2.valid.ttl
python -m caeluviim_graph.cli validate examples/ingest-manifest.valid.json
python -m caeluviim_graph.cli validate ingest/manifests/rrkc-r2.json
```

## Governance state

The EMGN and RRKC modules are implemented but remain **proposed**, not ratified. Ratification requires the applicable independent validation and governance record for each module.

The graph runtime is an operational implementation substrate. Loading a record does not ratify its semantic or governance claims; those states must be represented explicitly in the ingested material.
