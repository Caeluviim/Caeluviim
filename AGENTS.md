# Caeluviim automated-agent repository policy

This policy applies to every automated agent, connector, script, and model operating on this repository.

## Non-negotiable write boundary

1. **Never write directly to `main`.** Every create, update, delete, tree, commit, or ref mutation must target an explicitly named non-default branch.
2. **Never omit the branch argument on a mutation.** A null, empty, inherited, or default branch is prohibited.
3. **Never use a mutation endpoint to discover capabilities, test connectivity, validate parameters, or perform a no-op.** Use read-only repository, file, branch, search, or metadata operations.
4. **Create a task-specific branch before the first write.** Confirm that the branch exists and was created from the intended base ref.
5. **Open a pull request for every repository change.** Do not move the `main` ref directly.

## Update and deletion protocol

Before updating or deleting an existing file:

1. Fetch the file from the same explicit task branch.
2. Verify the exact repository, branch, path, and current blob SHA.
3. Verify that the proposed content corresponds to the active task.
4. Reject placeholder content, probes, `noop`, `test`, or other non-artifact payloads.
5. Execute one mutation.
6. Fetch the file again from the same branch and verify the resulting contents and SHA.
7. Inspect the pull request changed-file list before reporting completion.

## Protected paths

Changes to the following require a dedicated pull request, explicit justification, and rollback plan:

- `README.md`
- `AGENTS.md`
- `.github/**`
- `config/repository-write-policy.json`
- `schemas/**`
- `graph/migrations/**`
- `caeluviim_graph/**`
- `scripts/laptop/**`
- `docker-compose.yml`
- `requirements*.txt`

The pull-request body must contain:

```text
Protected-Path-Change: acknowledged
Rollback-Plan: <specific restoration procedure>
```

## Graph-ingestion writes

Graph source records and manifests must be committed only to a task branch and submitted through a pull request. Source records, claims, evidence, validation states, and governance states must remain distinct. Passing technical validation does not verify or ratify substantive claims.

## Failure-reporting invariant

Never report a failure as a bare restatement of what failed. Every failure report must include one of the following:

1. **Corrected:** the cause, correction applied, resulting artifact or commit, and verification result.
2. **Unresolved:** the exact cause, why it could not be corrected, the required corrective action, the responsible layer or permission boundary, and the procedure that will verify resolution.

Do not report a matter as complete while a known failure remains uncorrected or lacks an explicit resolution path.

## Completion report

A repository mutation is not complete until the report states:

- repository and branch;
- files created, changed, or deleted;
- commit SHA;
- pull-request number or URL;
- validation status;
- remaining consolidation or merge boundary;
- any failure and its applied correction or exact resolution path.
