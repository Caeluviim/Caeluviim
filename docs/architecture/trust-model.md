# Trust Model

Status: Proposed v0.1.0

## Purpose

Caeluviim represents trust as evidence-bearing, contextual graph state rather than a global reputation score.

## Principles

1. Trust is scoped to a subject, capability, domain, and time.
2. Trust records are derived from auditable observations.
3. Negative and positive evidence remain separately inspectable.
4. Trust does not create authority. Authority must be independently granted.
5. No trust score may erase contested evidence or governance findings.
6. Unknown is distinct from distrusted.

## Trust dimensions

Initial dimensions:

- `provenance_completeness`
- `validation_accuracy`
- `repair_follow_through`
- `constraint_compliance`
- `prediction_resolution`
- `conflict_disclosure`
- `audit_responsiveness`

Each assessment records a normalized value from 0 through 1, confidence from 0 through 1, evidence references, method, assessor, scope, and effective time.

## Aggregation

An aggregate trust view MAY be computed for a declared query context. The computation MUST expose:

- included observations
- excluded observations and reason
- weights
- decay function
- confidence calculation
- contested observations
- algorithm version

No aggregate value is canonical without its derivation record.

A default deterministic weighted mean MAY be used:

`T = sum(value_i * confidence_i * weight_i) / sum(confidence_i * weight_i)`

when the denominator is non-zero. Otherwise the result is `unknown`.

## Accrual

Trust may increase only through qualifying evidence, including:

- independently validated claims
- correct prediction resolution
- timely repair after identified error
- complete provenance
- faithful compliance with declared constraints

## Decay

Trust may decay through time or become stale when a context changes. Decay MUST NOT rewrite the underlying observations. The selected decay function and half-life are query parameters or governance-defined policy.

## Adverse evidence

Trust may decrease through:

- unresolved provenance defects
- repeated constraint violations
- undisclosed conflicts
- overturned validations
- failed repair commitments
- unauthorized actions

An adverse event MUST cite the underlying event or assessment. Mere disagreement is not an adverse trust event.

## Anti-gaming constraints

- self-assessments do not count as independent validation
- duplicate evidence cannot be counted more than once
- identities sharing a controlling authority cannot satisfy independence requirements
- Sybil-linked identities are grouped for quorum and weighting
- trust cannot exceed an applicable authority ceiling
- missing evidence is represented as unknown, not zero

## Graph model

Required nodes:

- `TrustObservation`
- `TrustAssessment`
- `TrustComputation`
- `TrustPolicy`

Required relations:

- `ASSESSES`
- `SUPPORTED_BY`
- `COMPUTED_FROM`
- `SCOPED_TO`
- `CONTESTED_BY`
- `SUPERSEDES`

## Governance status

This model is proposed. Initial weights, decay functions, and decision thresholds require separate governance approval and versioned policy records.