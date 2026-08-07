# Operational Value Gate

## Purpose
A repository mutation is not, by itself, an outcome. Work must be evaluated by whether it changes a user's external options, produces an executable artifact, resolves a concrete blocker, or creates verifiable evidence needed for the next consequential action.

## Gate
Before treating work as substantive, require at least one of:

1. **Executable effect** — code or automation can be run and has a defined observable result.
2. **Decision effect** — analysis resolves a concrete choice with evidence and an identified next action.
3. **External-use artifact** — a filing, form, letter, dataset, workbook, application, or other artifact is usable outside the repository.
4. **Blocker removal** — a specific dependency preventing consequential work is removed and verified.
5. **Runtime verification** — claimed integration is supported by a runtime-generated receipt or equivalent evidence, not merely repository state.

## Non-results
The following do not satisfy the gate alone:

- adding documentation about intended future work;
- adding graph/schema structure without a runtime consumer or external-use consequence;
- commits, branches, PRs, or issue churn presented as outcomes;
- tests that prove only repository-local structure while the claimed external capability remains unavailable;
- restating a problem or producing another plan when the requested deliverable can instead be produced.

## Response protocol
When the user says repository work is performative or ineffective:

1. Stop proposing graph/repository integration as the remedy unless it directly unlocks the requested external outcome.
2. Name the concrete external outcome being pursued.
3. Perform the highest-impact available action toward that outcome in the same turn.
4. Report the observable result and the remaining blocker, if any.
5. Never describe repository state as runtime state without runtime evidence.

## Verification question
For every claimed accomplishment ask: **What can now be done in the world that could not be done before this action?**

If the answer is "nothing," the action is infrastructure or bookkeeping, not completion, and must not be represented as substantive resolution.
