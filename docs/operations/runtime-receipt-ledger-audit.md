# Runtime receipt ledger audit

## Purpose

Caeluviim distinguishes repository and test-ingestion evidence from verified live graph mutation. A live graph change may be represented only by a runtime-generated receipt identifying the runtime, source commit, manifest, timestamp, result, graph counts and delta, validation result, and receipt hash.

## Command

```bash
python -m caeluviim_graph.cli audit-receipts \
  --output reports/generated/runtime-receipt-audit.json
```

Defaults are `runtime/receipts/`, `ingest/manifests/`, and `schemas/ingest-manifest.schema.json`. Production audits remain catalog-bound. `--without-catalog` is limited to forensic inspection when production manifests are unavailable.

## Fail-closed invariants

The audit is invalid for malformed JSON, invalid canonical receipt hashes, unsupported receipt types, unresolved runtime identity, unresolved source commit, unknown ingest identifiers, catalog manifest-hash mismatch, duplicate receipt hashes, or duplicate runtime/database/ingest/timestamp events.

## Sync integration

`sync` now audits the production manifest catalog, validates manifests, applies migrations, ingests transactionally, issues and individually verifies receipts, and then audits the complete historical receipt ledger against the same catalog. An invalid post-sync ledger blocks successful completion reporting.

A post-sync audit failure does not assert rollback of Neo4j transactions already committed. It requires correction and a new verified audit.

## Evidence boundary

A valid audit proves repository-visible receipt integrity, uniqueness, resolved provenance fields, and consistency with the current production manifest catalog. It does not independently prove that the runtime still exists, that its current graph equals a historical receipt, or that source claims are true or ratified. Current runtime equivalence requires a fresh runtime-generated status receipt or equivalent direct runtime verification.

## Rollback

Revert `caeluviim_graph/receipt_audit.py`, the CLI integration, `tests/test_receipt_audit.py`, and this document. The audit implementation does not modify existing receipt files or graph data.
