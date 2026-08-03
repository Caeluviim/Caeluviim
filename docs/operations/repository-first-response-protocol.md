# Repository-first response protocol

Status: proposed

## Purpose

Every assistant response in the Caeluviim project thread must begin from a complete repository copy pinned to an exact repository state and must be archived back to the repository through the task-branch and pull-request controls.

## Mandatory start-of-response copy

Before drafting any user-visible response:

1. Resolve repository metadata for `Caeluviim/Caeluviim`.
2. Resolve the current default branch and exact head commit SHA.
3. Create a fresh, complete local copy of the repository.
4. Check out the exact resolved head commit in detached state.
5. Verify the copy with the remote URL, `git rev-parse HEAD`, repository file count, and hashes of `AGENTS.md` and `config/repository-write-policy.json`.
6. Read `AGENTS.md` and `config/repository-write-policy.json` from that copy before any mutation.
7. Record the repository, default branch, pinned head SHA, timestamp, copy method, verification results, and copy receipt in the response archive.

Authenticated connector reads, selected-file fetches, commit searches, and metadata queries are repository evidence but are not a repository copy and do not satisfy this boundary.

When the complete copy cannot be created, the boundary has failed. The failure report must not describe connector reads as a copy or as a completed correction. The report must state the exact unresolved cause, required corrective action, responsible layer, and verification procedure. A failure report may still be archived through connector writes on a task branch, but that archive does not cure the missing start-of-response copy.

The pinned commit is the sole source boundary for repository-state claims in the response. Later repository activity is not silently incorporated.

## Response construction

The response must distinguish:

- repository evidence;
- test-ingestion evidence;
- merged-but-not-runtime-verified state;
- runtime-verified live graph state.

No live graph delta may be claimed without a runtime-generated ingestion or status receipt identifying the runtime, source commit, manifest, timestamp, result, node count, relationship count, validation result, and receipt hash.

## Mandatory end-of-response archive

At the conclusion of response construction and before transmitting the response:

1. Write the exact user-visible response body to `records/assistant-responses/YYYY/MM/DD/` on an explicitly named non-default task branch.
2. Never write directly to `main`.
3. Open or update a pull request carrying the response archive.
4. Fetch the written file from the task branch and verify its exact content and blob SHA.
5. Inspect the pull request changed-file list.
6. Verify the response-body hash recorded in the archive.
7. Report the branch, files, commit SHA, pull request, validation state, remaining merge boundary, and any unresolved start-copy failure.

The repository archive is evidence that the response was written to the repository. It is not evidence that the live graph changed.

## Failure reporting

A failure report must state either:

- the exact cause, correction applied, resulting artifact or commit, and verification result; or
- the exact unresolved cause, reason it remains unresolved, required corrective action, responsible layer, and verification procedure.

No workflow may be reported as complete while the mandatory repository copy is absent.
