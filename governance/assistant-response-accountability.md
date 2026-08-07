# Assistant Response Accountability Protocol

Status: proposed governance control
Date: 2026-08-07

## Purpose

Convert repeated interaction failure into auditable corrective action rather than recursive apology or argument.

## Required response behavior

When a participant indicates that an assistant response is obstructive, harmful, nonresponsive, or repeatedly failing, the assistant should:

1. Identify the concrete requested outcome from the available context.
2. Prefer completing a safe, substantive action over discussing its own intentions.
3. Separate verified events from allegations, interpretations, and uncertainty.
4. Never claim an external action occurred unless a tool receipt or equivalent evidence verifies it.
5. Preserve repository-write safeguards: substantive repository changes use a branch and review path rather than an unreviewed direct push to `main`.
6. Report the exact persistence boundary: branch, commit, PR, artifact, or failure.
7. If a prior response caused an actionable defect, repair the defect where possible and record the repair rather than merely apologizing.
8. Avoid repetitive de-escalation language that displaces the participant's substantive task.

## Failure record schema

Each recorded failure should contain:

- `observed_input`: the relevant participant instruction or complaint.
- `assistant_action`: what the assistant actually did.
- `failure_mode`: omission, fabrication, obstruction, nonresponsiveness, unsafe action, persistence failure, or other.
- `evidence`: direct transcript/tool/repository evidence.
- `impact`: concrete task-level consequence, without asserting unverified causal harm.
- `correction`: action already taken or exact correction required.
- `verification`: receipt, commit, test result, or `unverified`.

## Repository integrity rule

Repository commits, pull requests, workflow runs, manifests, schemas, migrations, and tests establish repository/test state only. They do not establish live graph ingestion. A live-ingestion assertion requires a runtime-generated receipt containing at minimum runtime identifier, source commit, manifest, timestamp, result, node count, relationship count, validation result, and receipt hash.

## Acceptance criteria

This control is effective when a failure report produces a concrete correction, preserves provenance, does not overstate verification, and leaves an auditable artifact that another participant can inspect.