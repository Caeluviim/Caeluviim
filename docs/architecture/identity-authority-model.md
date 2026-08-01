# Identity and Authority Model

Status: Proposed v0.1.0

## Purpose

This specification defines how Caeluviim represents participant identity, capability, delegated authority, revocation, and authority ceilings. It applies to human, synthetic, institutional, validator, observer, witness, and steward participants.

## Core entities

### Identity

An Identity is a stable protocol subject identified by an immutable `identity_id`. Display names, providers, model identifiers, and deployment identifiers are mutable attributes and MUST NOT be used as identity keys.

Required fields:

- `identity_id`
- `identity_type`
- `status`
- `created_at`
- `provenance_id`
- one or more active key references

### Capability

A Capability is a narrowly scoped permission named by a stable `capability_id`. Capabilities MUST be explicit, deny-by-default, and independently revocable.

### Delegation

A Delegation grants one or more capabilities from a grantor to a grantee for a declared scope and time interval. A delegation MUST identify:

- grantor and grantee
- delegated capabilities
- authority basis
- scope
- start and expiry or review time
- delegation depth
- provenance

A grantee MUST NOT delegate a capability unless the parent delegation explicitly permits subdelegation.

### Revocation

A Revocation terminates a key, capability, or delegation. Revocations are append-only events. Historical actions remain auditable but no new action may rely on revoked authority after the revocation effective time.

## Authority resolution

An action is authorized only when all of the following hold:

1. The acting identity is active.
2. The signing key is active and bound to that identity.
3. A direct or delegated capability authorizes the action type.
4. The action scope is within the capability scope.
5. The authority has not expired or been revoked.
6. Delegation depth does not exceed the declared ceiling.
7. Any governance-specific independence requirements are satisfied.
8. The action does not exceed an explicit authority ceiling.

Failure of any condition is fail-closed.

## Authority ceilings

Authority ceilings are non-overridable protocol constraints. Initial ceilings:

- no proposer may validate the same proposal
- no validator may count twice through multiple identities or keys
- no delegated authority may exceed its parent authority
- no local operator capability implies governance ratification authority
- no ingestion capability implies semantic acceptance authority
- no synthetic manifestation may exceed the capabilities delegated to its root identity
- no revocation may be silently deleted or rewritten

## Identity classes

| Class | Purpose | Default authority |
|---|---|---|
| Human | Natural-person participant | None beyond self-authored submissions |
| Synthetic | Synthetic participant recognized by Caeluviim | None beyond explicit delegation |
| Institution | Collective or legal organization | None beyond chartered capability |
| Validator | Independent assessment participant | Validate only assigned proposal scopes |
| Observer | Read and attest | No mutation authority |
| Witness | Sign observations or integrity anchors | No semantic ratification authority |
| Steward | Maintain protocol-defined operational surfaces | No unilateral constitutional authority |

## Required graph relations

- `IDENTIFIED_BY`
- `BOUND_TO_KEY`
- `HAS_CAPABILITY`
- `DELEGATED_TO`
- `DERIVES_FROM`
- `REVOKED_BY`
- `GOVERNED_BY`
- `SUPPORTED_BY_PROVENANCE`

## Determinism

Identity, capability, delegation, and revocation records MUST be canonically serialized before hashing. Equivalent records MUST produce equivalent content identifiers.

## Governance status

This document is proposed. It does not ratify identities or grant capabilities by itself. Effective grants require valid signed records conforming to the machine constraints and governance process.