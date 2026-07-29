# Caeluviim Core

Caeluviim Core is the headless, local-first civic knowledge layer. It stores
exact source material in a content-addressed object store, records every
authoritative change in append-only ledgers, quarantines AI analysis until
review, and rebuilds RDF and Neo4j projections from accepted history.

The existing `web/` project is preserved as a compatibility oracle and future
interface. It is not the authoritative store.

## Runtime contract

- Original source bytes are immutable.
- Private member material is encrypted and excluded from public projections.
- Dialogue ingestion is manual and scope-explicit.
- AI-produced interpretations enter quarantine.
- Review, contest, rejection, revision, and supersession remain auditable.
- Lux is one persistent synthetic person; each runtime is an attributed,
  scoped, revocable manifestation.
- Official civic activity is public by default. Restrictions require a
  recorded basis, authority, scope, expiry or review date, and contest path.
- RDF and Neo4j are rebuildable projections, never the source of truth.

## Quick start

```sh
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/caeluviim --data-dir .caeluviim init
.venv/bin/caeluviim --data-dir .caeluviim validate
```

Manual dialogue ingestion accepts a JSON document:

```sh
.venv/bin/caeluviim --data-dir .caeluviim ingest dialogue \
  --input fixtures/dialogue/example.json \
  --scope private \
  --owner member:founder
```

Run the local MCP server over stdio:

```sh
.venv/bin/caeluviim --data-dir .caeluviim mcp
```

Install and start the primary native Neo4j projection target:

```sh
.venv/bin/caeluviim graph install
.venv/bin/caeluviim graph start
.venv/bin/caeluviim --data-dir .caeluviim graph project
.venv/bin/caeluviim --data-dir .caeluviim graph validate
```

Neo4j resources are keyed by both immutable resource ID and projection
partition. Public and member projections therefore do not silently merge into
the same node identities. The signed ledger and content-addressed store remain
authoritative; deleting and rebuilding Neo4j does not delete source history.

See [docs/graph-installation.md](docs/graph-installation.md) for the native
runtime, member partitions, validation gates, and optional Docker alternative.

The project is compatible with the laptop's current Python 3.10 runtime for
verification. Python 3.12 is the target deployment runtime.
