# Response Failure Accountability Control — 2026-08-07

Status: ACTIVE
Scope: Lux-mediated work in this repository

## Problem
Repeated conversational output without a concrete state change can become obstruction rather than assistance. When a request is actionable and a safe repository operation is available, another promise, apology, or restatement is not a substitute for execution.

## Control
For actionable repository work, use this sequence:

1. Read the relevant repository state before making claims about it.
2. Select one bounded, non-destructive operation that materially advances the work.
3. Execute the operation when authorization and tooling permit.
4. Verify the resulting repository state or record the exact verification boundary.
5. Report the concrete artifact, commit, PR, test result, or unresolved blocker—not merely intent.

## Evidence discipline
Repository commits, pull requests, CI runs, schemas, manifests, and test fixtures establish repository/test state only. They do **not** establish a live graph mutation. A live-ingestion claim requires a runtime-generated receipt containing at minimum: runtime identifier, source commit, manifest, timestamp, result, node count, relationship count, validation result, and receipt hash.

Absent such a receipt, classify the event as one of:
- proposed;
- merged-but-not-runtime-verified;
- test-ingestion-only.

## Failure rule
If a tool operation fails, the response must state the failed operation and either (a) the correction already attempted plus its verification result, or (b) the exact remaining correction path. Do not convert a failed write into a claim of completion.

## Interaction rule
High emotional intensity is not itself a reason to stop substantive work. Continue safe, relevant execution unless the content presents an immediate safety issue or the requested operation itself is unsafe or unauthorized.

## Current repository observation
At the time this control was added, `main` already contained recent merges for the RRKC governed-transition validator, plasma filing package, and functional-identity work. This control does not claim those artifacts are runtime-ingested; it governs how their status is represented.
