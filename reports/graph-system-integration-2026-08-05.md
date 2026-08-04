# Caeluviim knowledge-graph integration report — 2026-08-05

## Execution scope

This change closes the evidentiary gap between repository-side ingestion capability and verified operational graph mutation by adding durable runtime-generated ingestion receipts.

## Repository changes

| Path | Change | Operational effect |
|---|---|---|
| `caeluviim_graph/receipts.py` | Added canonical receipt construction, runtime identity capture, source-commit resolution, receipt hashing, verification, and atomic file writing | Creates independently verifiable provenance for each runtime ingest |
| `caeluviim_graph/cli.py` | Integrated receipts into `ingest`, `bootstrap`, and `sync`; added `verify-receipt`; preserved migration-before-ingestion order | Makes receipt generation part of the normal graph lifecycle rather than a separate manual step |
| `schemas/runtime-ingestion-receipt.schema.json` | Added the machine-readable receipt contract | Defines the minimum evidence required for a live-graph claim |
| `tests/test_runtime_receipts.py` | Added positive, tamper-detection, graph-delta, and persistence tests | Prevents silent weakening of the receipt invariant |
| `docs/operations/runtime-receipts.md` | Added configuration, execution, interpretation, and failure procedures | Gives operators an exact procedure for creating and validating evidence |

## Semantic integration

The repository already contained validated manifests, migrations, transactional ingestion, idempotency checks, provenance links, and graph statistics. The new receipt layer binds those components into one auditable event:

`source commit -> validated manifest -> identified runtime -> transaction result -> before/after graph state -> graph delta -> validation result -> receipt hash`

This does not ratify ingested claims. It proves only what identified runtime processed what manifest from what repository state and what count-level graph change was observed.

## SSHR status

The SSHR manifests merged through PR #12 remain **merged-but-not-runtime-verified** until the laptop-host runtime executes `sync` at a resolved source commit and emits qualifying receipts for both SSHR ingestion identifiers. The repository declaration of 31 nodes and 35 relationships is input-manifest evidence, not a verified live graph delta.

## Required operational activation

On the intended laptop-host runtime:

```bash
export CAELUVIIM_RUNTIME_ID=caeluviim-laptop-primary
export CAELUVIIM_SOURCE_COMMIT=$(git rev-parse HEAD)
python -m caeluviim_graph.cli sync
python -m caeluviim_graph.cli verify-receipt runtime/receipts/<receipt>.json
```

Retain the generated receipt files with runtime logs and backup metadata. Do not commit secrets or Neo4j credentials.

## Verification state

Repository implementation is proposed on its task branch. Hosted CI on the exact pull-request head is required. No operational Neo4j runtime was available through the GitHub connector during this execution, so no live graph mutation or runtime receipt is claimed.

## Failure accounting

Unresolved cause: the connected GitHub execution surface provides repository read/write and Actions visibility but no direct session on the laptop-host Neo4j runtime.

Responsible layer: operational runtime access and deployment layer.

Required corrective action: synchronize the merged commit to the identified runtime and execute the activation commands above.

Verification procedure: require a receipt with runtime identity, exact source commit, manifest, UTC timestamp, result, before/after counts, graph delta, validation result, and a valid receipt hash; then compare it with Neo4j `stats` and the applicable backup metadata.
