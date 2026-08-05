# Runtime receipt ledger audit

## Purpose

Caeluviim distinguishes repository/test-ingestion evidence from verified live graph mutation. A live graph change may be represented only by a runtime-generated ingestion receipt that identifies the runtime, source commit, manifest, timestamp, result, graph counts and delta, validation result, and receipt hash.

The receipt-ledger audit makes that boundary executable across the complete receipt directory.

## Command

```bash
python -m caeluviim_graph.cli audit-receipts
```

Default inputs:

- receipts: `runtime/receipts/*.json`
- manifests: `ingest/manifests/`
- schema: `schemas/ingest-manifest.schema.json`

Write a deterministic audit report with:

```bash
python -m caeluviim_graph.cli audit-receipts \
  --output reports/generated/runtime-receipt-audit.json
```

Use `--without-catalog` only for forensic inspection of receipts whose production manifests are unavailable. A production audit should remain catalog-bound.

## Fail-closed invariants

The audit is invalid when any receipt:

1. is malformed or is not a JSON object;
2. fails its canonical SHA-256 receipt-hash verification;
3. uses a receipt type other than `caeluviim.runtime.ingestion`;
4. has an unresolved runtime identifier;
5. has an unresolved source commit;
6. references an ingest identifier absent from the production manifest catalog;
7. contains a manifest hash different from the canonical catalog hash;
8. duplicates another receipt hash; or
9. duplicates the same runtime, database, ingest identifier, and timestamp event.

## Sync integration

`python -m caeluviim_graph.cli sync` now performs the following ordered gates:

1. audit the complete production manifest catalog;
2. validate every manifest;
3. apply idempotent graph migrations;
4. ingest each manifest transactionally;
5. issue and individually verify each runtime receipt;
6. audit the complete receipt ledger against the same catalog;
7. fail the operation if the resulting receipt ledger is invalid.

The ledger audit runs after ingestion because it verifies the newly written receipts together with historical receipts. A failed post-sync audit does not claim rollback of graph mutations already committed by Neo4j; it blocks successful completion reporting and requires correction plus a new verified audit.

## Evidence boundary

A valid receipt audit proves that the repository-visible receipt files are internally hash-valid, uniquely identified, provenance-resolved, and consistent with the current production manifest catalog. It does not independently prove that:

- the referenced runtime still exists;
- the current live graph still equals a historical post-ingestion state;
- the source claims are true, ratified, or legally authoritative; or
- a repository commit, pull request, CI run, schema, migration, or test changed the live graph.

Current runtime equivalence requires a fresh runtime-generated status receipt or direct runtime verification with equivalent provenance fields.

## Rollback

Revert the commits adding `caeluviim_graph/receipt_audit.py`, the `audit-receipts` CLI command and sync gate, `tests/test_receipt_audit.py`, and this document. Existing receipt files and graph data are not modified by the audit implementation itself.
