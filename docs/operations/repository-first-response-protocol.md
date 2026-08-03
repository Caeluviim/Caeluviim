# Repository-first response protocol

Status: proposed

## Purpose

Every substantive assistant response concerning Caeluviim should be grounded in a pinned repository state and archived back to the repository through the repository's task-branch and pull-request controls.

## Start-of-response boundary

Before composing the substantive response:

1. Resolve repository metadata for `Caeluviim/Caeluviim`.
2. Resolve the current default branch and exact head commit SHA.
3. Create a working copy pinned to that SHA when the execution environment permits a clone or archive download.
4. When a local copy cannot be created, use authenticated GitHub connector reads pinned to the exact head SHA and record the copy limitation, cause, correction, and verification result.
5. Read `AGENTS.md` and `config/repository-write-policy.json` before any mutation.
6. Record the repository, branch, head SHA, timestamp, snapshot method, and snapshot result in the response archive.

The pinned commit is the source boundary for repository-state claims in that response. Later repository activity is not silently incorporated.

## Response construction

The response must distinguish:

- repository evidence;
- test-ingestion evidence;
- merged-but-not-runtime-verified state;
- runtime-verified live graph state.

No live graph delta may be claimed without a runtime-generated ingestion or status receipt identifying the runtime, source commit, manifest, timestamp, result, node count, relationship count, validation result, and receipt hash.

## End-of-response boundary

After composing the response:

1. Write the assistant response to `records/assistant-responses/YYYY/MM/DD/` on an explicitly named task branch.
2. Never write directly to `main`.
3. Open or update a pull request carrying the response archive.
4. Fetch the written file from the task branch and verify its content and blob SHA.
5. Inspect the pull request's changed-file list.
6. Report the branch, files, commit SHA, pull request, validation state, and remaining merge boundary.

The repository archive is evidence that the response was written to the repository. It is not evidence that the live graph changed.

## Failure reporting

A failure report must state either:

- the exact cause, correction applied, resulting artifact or commit, and verification result; or
- the exact unresolved cause, required corrective action, responsible layer, and verification procedure.

## Current execution limitation

The response execution container may not have outbound DNS or network access to `github.com`. In that condition, a direct `git clone` cannot serve as the working-copy mechanism. The authenticated GitHub connector is the corrective repository-access path, with reads pinned to the resolved commit SHA.
