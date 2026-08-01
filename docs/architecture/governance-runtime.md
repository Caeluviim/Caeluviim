# Governance Runtime

Status: Proposed v0.1.0

## Objective

This specification converts governance requirements into an auditable deterministic state machine.

## States

`DRAFT -> SUBMITTED -> VALIDATION_OPEN -> DECISION_READY -> ACCEPTED | REJECTED | CONTESTED | EXPIRED | WITHDRAWN`

No transition may skip required evidence or independence checks.

## Proposal record

A proposal MUST declare:

- stable proposal identifier
- proposer identity
- affected modules and protected paths
- requested action
- normative and machine-readable artifacts
- provenance references
- risk classification
- rollback or supersession plan
- validator requirements
- submission timestamp

## Validator selection

Validators MUST be selected under a versioned policy. The runtime MUST exclude:

- the proposer
- identities controlled by the proposer
- duplicate manifestations of the same controlling identity
- identities with an unresolved material conflict
- identities lacking the required validation capability

## Validation record

Each validation MUST declare disposition, reasoning, evidence, scope, validator identity, signing key, algorithm or review method, and timestamp.

Permitted dispositions:

- `APPROVE`
- `APPROVE_WITH_CONDITIONS`
- `REQUEST_CHANGES`
- `REJECT`
- `ABSTAIN_CONFLICT`
- `CONTEST`

## Decision function

A proposal is decision-ready only when:

1. required checks passed on the exact proposal content hash
2. required independent validator count is satisfied
3. protected-path acknowledgments are present
4. unresolved blocking requests are absent
5. the proposal has not expired or been withdrawn
6. the decision authority is valid at decision time

The decision record MUST preserve the complete input set and policy version.

## Execution

An accepted decision produces a separate execution event. Acceptance does not itself prove execution. Execution MUST record:

- decision identifier
- exact artifact hashes applied
- actor identity and capability
- pre-state root
- post-state root
- execution result
- rollback reference when applicable

## Failure handling

Any failed authorization, invariant, signature, hash, or independence check places the proposal in a non-effective state and records a machine-readable failure reason. Failures MUST NOT be silently coerced into acceptance.

## Reconsideration and supersession

Decisions are append-only. A later decision may supersede an earlier one but MUST reference it and preserve its historical effect interval.

## Initial policy

Until separately ratified, semantic module ratification requires two independent approving validators who are not the proposer. Operational changes may use a separately versioned repository policy but cannot confer semantic ratification.