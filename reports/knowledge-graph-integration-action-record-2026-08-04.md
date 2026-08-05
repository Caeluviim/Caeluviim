# Knowledge graph integration action record — 2026-08-04

## Scope

This record documents the repository actions taken to complete the deterministic graph-catalog integration path on pull request #40.

## Repository state inspected

- Default branch: `main`.
- Open integration pull request: #40, `graph/formal-operationalization-20260804`.
- Open server-side safeguard issue: #14.
- Existing graph components inspected: manifest validation, transactional runtime client, recursive closure, ingestion receipts, graph CLI, hosted graph-ingestion workflow, repository write policy, and production ingestion manifests.

## Defect found

The catalog audit added by pull request #40 was callable only as a separate Python module. The production `sync` command could proceed to runtime construction and migrations without first requiring the complete catalog audit to pass. The hosted graph-ingestion workflow ran unit tests but did not explicitly execute and persist the catalog preflight.

That left two integration bypasses:

1. an operator could invoke `python -m caeluviim_graph.cli sync` without a global duplicate and endpoint audit;
2. hosted validation could pass without demonstrating the production catalog command itself returned `status: valid`.

## Corrections applied

### `caeluviim_graph/cli.py`

- Added `catalog` as a first-class CLI subcommand.
- Added optional deterministic JSON output through `--output`.
- Added `_require_valid_catalog` fail-closed preflight.
- Required `sync` to complete the catalog audit before runtime migrations or ingestion.
- Included the exact catalog result and hash in successful `sync` output.
- Preserved the distinction between repository-input evidence and runtime-generated ingestion receipts.

### `.github/workflows/graph-ingestion.yml`

- Added explicit read-only workflow permissions.
- Added a bounded job timeout.
- Added a named full repository test-suite step.
- Added an explicit production catalog audit step:

  `python -m caeluviim_graph.cli catalog --output reports/generated/graph-catalog.json`

- Added clearer names to runtime, backup, restore, and status steps.
- Required runtime shutdown under `if: always()` so failed validation does not intentionally leave the CI runtime running.

## Commits created

- `f99577618f389bd90daf318692518d4ab475489c` — integrate catalog audit into graph CLI and sync preflight.
- `4cc03ee682a21720030504f10da60bcec0d20470` — run graph catalog preflight in hosted validation.
- This action record is created by the subsequent documentation commit.

## Validation state

A new hosted `Graph ingestion validation` run is required on the exact final pull-request head. The preceding run for `e5f5532cee32bcefc2ef742ff950653b7d7b07a8` became stale as soon as the integration commits changed the head.

Required exact-head checks:

```bash
python -m unittest discover -s tests -v
python -m caeluviim_graph.cli catalog --output reports/generated/graph-catalog.json
docker compose config --quiet
```

The hosted workflow must also successfully start the test runtime, ingest the production manifests, verify status, create and verify a backup, restore it, re-verify status, and stop the runtime.

## Evidence classification

All changes in this pull request are **proposed repository and test-ingestion evidence** until merged. A successful hosted workflow is still test-ingestion evidence. It does not establish that a separately hosted live Caeluviim graph changed.

A live graph change may be claimed only when a runtime-generated receipt identifies the runtime, source commit, manifest, timestamp, transaction result, node and relationship counts, validation result, and receipt hash.

## Unresolved external control

Issue #14 remains open. Repository policy and CI cannot substitute for a GitHub server-side branch ruleset that blocks authenticated direct writes to `main`, force pushes, branch deletion, and merges lacking required checks. The connected GitHub action surface does not expose branch-ruleset mutation, so that external repository-setting action was not performed here.

## Merge gate

Do not merge pull request #40 until:

1. `Graph ingestion validation` succeeds on the exact final head;
2. the changed-file list is reviewed for the protected paths `.github/**` and `caeluviim_graph/**`;
3. no unresolved review thread remains;
4. the pull request description reflects the CLI, sync-preflight, workflow, and documentation integration;
5. issue #14 is not falsely represented as resolved.

## Rollback

Close pull request #40 without merging. If merged and later found defective, revert the pull request merge commit. No direct write to `main` was made during this action.
