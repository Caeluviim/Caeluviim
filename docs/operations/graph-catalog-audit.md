# Graph catalog integrity audit

## Purpose

The runtime receipt layer proves what an identified graph runtime changed. The catalog audit proves what the repository proposes to send to that runtime before any connection or mutation occurs.

`caeluviim_graph.catalog` performs a deterministic, offline audit across every production ingestion manifest.

## Guarantees

The audit:

- validates every `.json` and `.json.gz.b64` production manifest against `schemas/ingest-manifest.schema.json`;
- records canonical SHA-256 hashes for every decoded manifest;
- records source identifiers and source content hashes;
- counts manifests, nodes, relationships, labels, and relationship types;
- detects duplicate ingestion, node, and relationship identifiers;
- verifies every relationship endpoint resolves in the complete proposed catalog;
- records self-loop relationships without automatically treating them as invalid;
- emits a canonical catalog hash covering the complete audit result;
- exits nonzero when schema errors, duplicate identifiers, or dangling endpoints exist.

This is repository evidence only. It is not a runtime ingestion receipt and does not prove that any live graph contains the catalog.

## Run

```bash
python -m caeluviim_graph.catalog
```

Persist a review artifact:

```bash
python -m caeluviim_graph.catalog \
  --output reports/generated/graph-catalog.json
```

The output is deterministic for the same decoded manifests and schema. Paths, counts, hashes, errors, duplicates, and dangling endpoints are included explicitly.

## Operational sequence

```text
repository manifests
→ schema validation
→ global identifier and endpoint audit
→ deterministic catalog hash
→ migration
→ transactional ingestion
→ before/after graph counts
→ runtime ingestion receipt
→ receipt verification
```

The catalog hash and runtime receipts serve different layers. The catalog establishes the exact proposed graph input set. Each runtime receipt establishes an observed transaction against an identified operational runtime.

## Failure handling

A nonzero exit blocks synchronization. Correct the listed manifest or identifier defect, rerun the audit, and require `status: valid` before invoking `python -m caeluviim_graph.cli sync`.

No operator may reinterpret a failed catalog audit as partial success. No CI or repository catalog may be described as a live-graph mutation.
