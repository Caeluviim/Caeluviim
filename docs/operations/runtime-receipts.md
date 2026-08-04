# Runtime ingestion receipts

## Purpose

Repository commits, manifests, migrations, pull requests, workflow runs, and test-ingestion results do not prove that a live Caeluviim runtime changed. A live-graph claim requires a runtime-generated receipt produced during the transactional ingestion operation.

## Required receipt fields

Every receipt records:

- runtime identity, Neo4j database, server address, host, platform, and Python version;
- repository source commit resolved from `CAELUVIIM_SOURCE_COMMIT`, `GITHUB_SHA`, or local Git;
- manifest path, ingestion identifier, manifest hash, source identifier, and source content hash;
- UTC timestamp;
- ingestion result;
- graph counts before and after ingestion;
- computed graph-count delta;
- manifest validation result and schema path; and
- a SHA-256 hash over canonical JSON for every preceding receipt field.

The receipt contract is `schemas/runtime-ingestion-receipt.schema.json`.

## Runtime identity configuration

Set a stable runtime identifier before bootstrap or synchronization:

```bash
export CAELUVIIM_RUNTIME_ID=caeluviim-laptop-primary
export CAELUVIIM_SOURCE_COMMIT=$(git rev-parse HEAD)
```

PowerShell:

```powershell
$env:CAELUVIIM_RUNTIME_ID = "caeluviim-laptop-primary"
$env:CAELUVIIM_SOURCE_COMMIT = git rev-parse HEAD
```

A receipt with `source_commit: unresolved` is structurally verifiable but insufficient to prove which repository state was executed.

## Commands

Ingestion, bootstrap, and synchronization now generate receipts automatically:

```bash
python -m caeluviim_graph.cli ingest ingest/manifests/example.json
python -m caeluviim_graph.cli bootstrap
python -m caeluviim_graph.cli sync
```

The default output directory is `runtime/receipts/`. Override it with `--receipts PATH`.

Verify a receipt independently:

```bash
python -m caeluviim_graph.cli verify-receipt runtime/receipts/<receipt>.json
```

A successful verification requires that all mandatory top-level fields exist and that `receipt_hash` matches the canonical receipt body.

## Interpretation

- `result.status = ingested` with positive graph deltas is runtime-verified ingestion evidence.
- `result.status = already_ingested` with zero graph delta is runtime-verified idempotency evidence.
- A repository manifest without a receipt is proposed or merged-but-not-runtime-verified.
- A CI-created temporary Neo4j receipt proves test ingestion only unless its runtime identity identifies the actual operational graph.
- Node and relationship counts in manifests are declared input sizes. The receipt's `graph.delta` records observed graph-count changes and must not be silently substituted for the manifest declarations.

## Failure handling

If receipt generation fails after ingestion, do not claim a verified live graph change. Preserve stdout and Neo4j logs, run `stats`, regenerate evidence only through a controlled re-ingestion or idempotency check, and verify the resulting receipt hash. The responsible layer is the runtime orchestration layer unless Neo4j transaction or connectivity logs establish a database-layer failure.
