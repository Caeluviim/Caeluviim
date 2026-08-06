# Caeluviim

Caeluviim is a provenance-tracked formal architecture for representing claims, agents, relations, evidence, governance, revision, and the construction of new reachable futures.

## Implemented formal modules

| Module | Status | Primary specification | Machine constraints |
|---|---|---|---|
| Error-Mediated Generative Non-Closure | Proposed v0.1.0 | [`docs/architecture/error-mediated-generative-nonclosure.md`](docs/architecture/error-mediated-generative-nonclosure.md) | JSON Schema, OWL/RDF vocabulary, SHACL shapes, executable tests |
| RRKC closed formal calculus | Proposed v2.0.0 | [`docs/architecture/rrkc-r2-formal-specification.md`](docs/architecture/rrkc-r2-formal-specification.md) | Ott source, Lean target, executable reference, JSON Schema, OWL/RDF, SHACL, graph manifest, tests |

## Operable persistent memory

The committed repository is itself a queryable memory layer. It can reconstruct the complete graph topology directly from validated manifests without Neo4j, Docker, Codex, or another AI service:

```bash
python -m pip install -r requirements-dev.txt
python -m caeluviim_graph.cli recall "functional identity" --backend repository
python -m caeluviim_graph.cli memory-stats --backend repository
```

The repository projection includes source entities, ingestion events, every declared node, reified relationship assertions, direct relations, provenance links, assertion endpoints, and ingestion lineage. Tests verify that its projected counts remain equivalent to the ingestion topology as the corpus grows.

A manually triggered GitHub Actions workflow, **Repository memory recall**, executes the same retrieval from the committed repository and returns a JSON artifact. This permits repository-only recall from a phone without a running laptop.

## Working Neo4j runtime

The repository also contains a persistent laptop-host Neo4j ingestion system:

- Neo4j Community 2026.06 through Docker Compose
- persistent named volumes for graph state
- localhost-only HTTP and Bolt bindings by default
- idempotent Cypher migrations
- a JSON Schema ingestion contract
- transactional, append-only ingestion with content-conflict detection
- provenance links for every entity and reified relationship assertion
- a containerized operator that requires no host Python installation
- offline backup and restore commands for both `neo4j` and `system`
- CI that validates repository-only recall, starts Neo4j, synchronizes the corpus, verifies Neo4j recall, and tests backup and restore
- bounded text recall with provenance, graph context, entity retrieval, and chronology

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

## Memory backend selection

Memory commands default to `--backend auto`: Neo4j is used when reachable, otherwise the command reconstructs memory from repository manifests.

```bash
python -m caeluviim_graph.cli recall "functional identity"
python -m caeluviim_graph.cli timeline --backend repository --limit 20
docker compose --profile operator run --rm operator recall "functional identity" --backend neo4j
```

Recall is bounded by result count and graph depth, returns source provenance, and does not treat retrieval as ratification or truth. See [`docs/operations/graph-memory.md`](docs/operations/graph-memory.md) for repository-only, GitHub-hosted, and Neo4j operating procedures.

## Repository structure

- `caeluviim_graph/` — graph runtime, repository projection, validation, migrations, recall, and CLI orchestration
- `graph/migrations/` — ordered Neo4j schema migrations
- `ingest/manifests/` — production corpus manifests and durable encoded memory
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
python -m caeluviim_graph.cli recall "rrkc" --backend repository
```

## Governance state

The EMGN and RRKC modules are implemented but remain **proposed**, not ratified. Ratification requires the applicable independent validation and governance record for each module.

The repository and Neo4j memory layers are operational implementation substrates. Committing, loading, or recalling a record does not ratify its semantic or governance claims; those states must be represented explicitly in the encoded material.
